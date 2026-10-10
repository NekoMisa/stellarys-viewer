#!/usr/bin/env python3
"""Stage the upstream Linux application and package Stellarys without profiles."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            result.update(data)
    return result.hexdigest()


def make_launcher(launcher):
    for old in ('test -x ./etc/register_hopprotocol.sh && ./etc/register_hopprotocol.sh',
                'test -x ./etc/register_secondlifeprotocol.sh && ./etc/register_secondlifeprotocol.sh'):
        launcher = launcher.replace(old, '# Stellarys never changes default handlers on startup.')
    launcher = launcher.replace('bin/do-not-directly-run-firestorm-bin', 'bin/stellarys-bin')
    launcher = launcher.replace('ARGS=()', '''# Desktop launch with no URL starts normally; a single map URL is one argument.
if [[ $# -eq 1 && ( "${1,,}" == secondlife://* || "${1,,}" == hop://* ) ]]; then
    set -- --url "$1"
fi
ARGS=()''')
    # Make the launcher's result reflect application failure, rather than echo's exit code.
    launcher += '\nexit "$LL_RUN_ERR"\n'
    return launcher


def main():
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, default=repo / 'build-linux-x86_64')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--skip-archive', action='store_true', help='Stage only, for Debian packaging')
    args = parser.parse_args()
    build, output = args.build.resolve(), args.output.resolve()
    version = json.loads((repo / 'stellarys-source.json').read_text())['stellarys_version']
    stage = output / 'StellarysViewer'
    if stage.exists():
        raise SystemExit('Use a fresh output folder; existing application files will not be overwritten.')
    output.mkdir(parents=True, exist_ok=True)
    source = repo / 'indra/newview'
    sys.path.insert(0, str(source))
    spec = importlib.util.spec_from_file_location('viewer_manifest', source / 'viewer_manifest.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Upstream collects the application/dependencies; custom packaging below
    # handles names, symbols and archive ownership instead of Firestorm's release pipeline.
    def finish(self):
        self.package_file = 'StellarysViewer'
    module.Linux_x86_64_Manifest.package_finish = finish
    os.chdir(build / 'newview')
    sys.argv = [str(source / 'viewer_manifest.py'), '--actions=copy package',
        '--platform=linux', '--arch=x86_64', '--configuration=Release', '--buildtype=Release',
        '--channel=Stellarys Viewer '+version+' Linux Preview 1', '--viewer_flavor=oss', '--grid=agni', '--bugsplat=',
        '--discord=OFF', '--fmodstudio=OFF', '--openal=ON', '--tracy=OFF', '--avx2=OFF',
        '--source=' + str(source), '--artwork=' + str(source), '--build=' + str(build / 'newview'),
        '--dest=' + str(stage), '--versionfile=' + str(build / 'newview/viewer_version.txt')]
    module.main(extra=[dict(name=n, description=n, default=d) for n, d in
        [('bugsplat',''), ('discord','OFF'), ('fmodstudio','OFF'), ('openal','ON'),
         ('tracy','OFF'), ('velopack','OFF'), ('avx2','OFF')]])
    # The legacy 32-bit Vivox helper requires this older SONAME; Ubuntu 22.04
    # provides libidn.so.12 instead. Use the matching upstream runtime bundle.
    for library in (build / 'packages/lib32').glob('libidn.so.11*'):
        shutil.copy2(library, stage / 'lib32' / library.name)
    (stage / 'bin/do-not-directly-run-firestorm-bin').rename(stage / 'bin/stellarys-bin')
    launcher = make_launcher((stage / 'firestorm').read_text())
    (stage / 'stellarys').write_text(launcher)
    (stage / 'firestorm').unlink()
    for rel in ('install.sh', 'FIRESTORM_DESKTOPINSTALL.txt',
                'etc/register_secondlifeprotocol.sh', 'etc/register_hopprotocol.sh',
                'etc/handle_secondlifeprotocol.sh', 'etc/refresh_desktop_app_entry.sh'):
        (stage / rel).unlink(missing_ok=True)
    shutil.copy2(Path(__file__).with_name('install-desktop.py'), stage / 'install-desktop.py')
    shutil.copy2(Path(__file__).with_name('README-Linux.txt'), stage / 'README-Linux.txt')
    (stage / 'README-linux.txt').unlink(missing_ok=True)
    for name in ('PRIVACY.md','DISCLOSURES.md','SOURCE-PROVENANCE.md'):
        shutil.copy2(repo/name,stage/name)
    artwork = source / 'icons/stellarys'
    shutil.copy2(artwork / 'firestorm_256.png', stage / 'Stellarys.png')
    shutil.copy2(artwork / 'firestorm_256.png', stage / 'firestorm_icon.png')
    shutil.copy2(artwork / 'firestorm_48.png', stage / 'firestorm_48.png')
    shutil.copy2(artwork / 'firestorm_256.bmp', stage / 'res-sdl/ll_icon.BMP')
    (stage / 'stellarys-install.txt').write_text('StellarysViewer\nVersion=' + version + '\nBase=7.2.4.80712\nPlatform=linux-x86_64\n')
    (stage / 'stellarys-version.json').write_text(json.dumps({
        'name':'Stellarys Viewer', 'version':version, 'base_version':'7.2.4.80712',
        'platform':'linux-x86_64', 'status':'experimental preview 1',
        'profile':'~/.stellarys_x64', 'updates':'manual downloads'}, indent=2))
    subprocess.run(['strip', '--strip-unneeded', str(stage / 'bin/stellarys-bin')], check=True)
    forbidden = {'.git', 'user_settings', 'logs', 'cache', 'browser_profile', 'texturecache'}
    manifest = []
    for path in sorted(stage.rglob('*')):
        rel = path.relative_to(stage)
        if set(rel.parts) & forbidden or path.suffix.lower() in {'.log','.dmp','.pdb','.key','.pfx','.p12'}:
            raise RuntimeError('Non-application file in staging; packaging refused.')
        if path.is_symlink():
            if not path.resolve().is_relative_to(stage):
                raise RuntimeError('Application symlink escapes staging.')
            manifest.append({'path':str(rel), 'link':os.readlink(path)})
        elif path.is_file():
            with path.open('rb') as stream:
                executable = stream.read(4) == b'\x7fELF'
            path.chmod(0o755 if path.name in {'stellarys','install-desktop.py'} or rel == Path('etc/launch_url.sh') or executable else 0o644)
            manifest.append({'path':str(rel), 'bytes':path.stat().st_size, 'sha256':sha(path)})
        elif path.is_dir():
            path.chmod(0o755)
    (output / 'PAYLOAD-MANIFEST.json').write_text(json.dumps(manifest, indent=2))
    if args.skip_archive:
        print('Clean Linux application stage created:',len(manifest),flush=True)
        return
    archive = output / ('Stellarys-Viewer-' + version + '-Linux-x86_64-preview1.tar.xz')
    archive_env = os.environ.copy()
    archive_env['XZ_OPT'] = '-T3 -6'
    subprocess.run(['tar', '--sort=name', '--mtime=@0', '--owner=0', '--group=0',
        '--numeric-owner', '-C', str(output), '-cJf', str(archive), 'StellarysViewer'],
        env=archive_env, check=True)
    shutil.copy2(stage / 'README-Linux.txt', output / 'README-Linux.txt')
    (output / 'SHA256SUMS.txt').write_text(sha(archive) + '  ' + archive.name + '\n')
    print('Linux archive created; application entries:', len(manifest), flush=True)


if __name__ == '__main__':
    main()
