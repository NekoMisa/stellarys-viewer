#!/usr/bin/python3
"""Package a clean portable application with its own verified update feed."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application', type=Path, required=True)
    parser.add_argument('--viewer-binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    tools = Path(__file__).resolve().parent
    source = json.loads((repo / 'stellarys-source.json').read_text())
    release = source['linux_portable_version']
    import stellarys_portable_core as core
    tag, filename = core.release_names(release)
    parts = core.version(release)
    base = '.'.join(map(str, parts[:3]))
    assert base == source['stellarys_version']
    channel = f'Stellarys Viewer {base} Linux Portable Preview {parts[3]}'
    binary = args.viewer_binary.resolve()
    header = (binary.parent / 'fsversionvalues.h').read_text()
    assert f'#define LL_VIEWER_CHANNEL {channel}\n' in header, 'Compile the matching portable channel first.'
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Use a new output folder; existing applications will not be overwritten.')
    original = args.application.resolve()
    assert (original / 'stellarys-install.txt').read_text().splitlines()[0] == 'StellarysViewer'
    for p in original.rglob('*'):
        if set(p.relative_to(original).parts) & core.FORBIDDEN or p.suffix.lower() in {'.log','.dmp','.pdb','.key','.pfx','.p12'}:
            raise ValueError('Runtime/private files found in input application.')
        if p.is_symlink() and not p.resolve().is_relative_to(original):
            raise ValueError('Input application link escapes staging.')
    output.mkdir()
    app = output / 'StellarysViewer'
    # Dereference only the verified internal links. Updates accept ordinary files,
    # which keeps extraction independent of archive link semantics.
    shutil.copytree(original, app, symlinks=False)
    shutil.copy2(binary, app / 'bin/stellarys-bin')
    subprocess.run(['strip', '--strip-unneeded', str(app / 'bin/stellarys-bin')], check=True)
    (app / 'stellarys').rename(app / 'stellarys-launcher')
    shutil.copy2(tools / 'portable-launcher.py', app / 'stellarys')
    for name in ('stellarys-updater.py', 'stellarys_updater_core.py', 'stellarys_portable_core.py'):
        shutil.copy2(tools / name, app / name)
    for name in ('PRIVACY.md', 'DISCLOSURES.md', 'SOURCE-PROVENANCE.md'):
        shutil.copy2(repo / name, app / name)
    shutil.copy2(tools / 'README-Portable-Linux.md', app / 'README-Portable-Linux.txt')
    shutil.copy2(tools / 'README-Portable-Linux.md', app / 'README-Linux.txt')
    installed = dict(name='Stellarys Viewer', version=base, base_version='7.2.5.81788',
                     platform='linux-x86_64', install_kind='portable',
                     portable_version=release, viewer_channel=channel,
                     display_version=f'{base} Linux portable preview {parts[3]}',
                     profile='~/.stellarys_x64', updates='verified portable archive updates')
    (app / 'stellarys-version.json').write_text(json.dumps(installed, indent=2) + '\n')
    (app / core.MARKER).write_text(json.dumps(core.PRODUCT, indent=2) + '\n')
    files = []
    for p in sorted(app.rglob('*')):
        if p.is_symlink():
            raise ValueError('Portable payload must contain only regular files/directories.')
        if p.is_dir():
            p.chmod(0o755)
        elif p.is_file():
            rel = str(p.relative_to(app)); core.relative_path(rel)
            with p.open('rb') as stream:
                elf = stream.read(4) == b'\x7fELF'
            mode = 0o755 if elf or rel in {'stellarys','stellarys-launcher','install-desktop.py','etc/launch_url.sh'} else 0o644
            p.chmod(mode)
            files.append(dict(path=rel, bytes=p.stat().st_size, sha256=sha(p), mode=mode))
        else:
            raise ValueError('Unexpected portable payload type.')
    app.chmod(0o755)
    (app / core.INVENTORY).write_text(json.dumps(dict(schema=1, files=files), indent=2) + '\n')
    (app / core.INVENTORY).chmod(0o644)
    archive = output / filename
    env = dict(os.environ, XZ_OPT='-T3 -6')
    subprocess.run(['tar','--sort=name','--mtime=@0','--owner=0','--group=0','--numeric-owner',
                    '-C',str(output),'-cJf',str(archive),'StellarysViewer'], env=env, check=True)
    core.inspect_archive(archive, release)
    feed = dict(schema=1, package='stellarys-viewer-portable', architecture='x86_64',
                portable_version=release, display_version=installed['display_version'],
                filename=filename, bytes=archive.stat().st_size, sha256=sha(archive))
    (output / core.MANIFEST_NAME).write_text(json.dumps(feed, indent=2) + '\n')
    shutil.copy2(tools / 'README-Portable-Linux.md', output / 'README-Portable-Linux.txt')
    print(json.dumps(dict(archive=filename, sha256=feed['sha256'], bytes=feed['bytes'],
                         payload_files=len(files) + 1, viewer_channel=channel)), flush=True)


if __name__ == '__main__':
    main()
