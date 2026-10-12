#!/usr/bin/python3
"""Build an Ubuntu 22.04 amd64 installer from a clean Stellarys application stage."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parents[1]
PACKAGE = 'stellarys-viewer'
DEB_VERSION = '0.1.5~linuxpreview1-1'
DISPLAY_VERSION = '0.1.5 Linux preview 1'
FILENAME = 'Stellarys-Viewer-0.1.5-Linux-amd64-preview1.deb'

GUARD = '''/usr/bin/python3 - <<'PY'
import os
from pathlib import Path
import sys
expected = '/opt/stellarys-viewer/bin/stellarys-bin'
for item in Path('/proc').iterdir():
    if not item.name.isdecimal():
        continue
    try:
        executable = os.readlink(item / 'exe')
    except (FileNotFoundError, ProcessLookupError):
        continue
    except PermissionError:
        sys.exit('Cannot verify that Stellarys is closed; installation/removal refused.')
    if executable.removesuffix(' (deleted)') == expected:
        sys.exit('Close every installed Stellarys Viewer window before updating or removing it.')
PY
'''

PREINST = '''#!/bin/sh
set -eu
''' + GUARD + '''/usr/bin/python3 - <<'PY'
from pathlib import Path
import sys
folder = Path('/opt/stellarys-viewer')
marker = folder / '.stellarys-deb-install'
if folder.is_symlink():
    sys.exit('Refusing to install over a symlink at /opt/stellarys-viewer.')
if folder.exists():
    if not folder.is_dir():
        sys.exit('/opt/stellarys-viewer is not a directory.')
    if any(folder.iterdir()) and (marker.is_symlink() or not marker.is_file()
            or marker.read_text() != 'StellarysDebPackage=stellarys-viewer\\n'):
        sys.exit('Refusing to overwrite an unrelated nonempty /opt/stellarys-viewer folder.')
PY
exit 0
'''
PRERM = '''#!/bin/sh
set -eu
case "${1:-}" in
 remove|upgrade|deconfigure)
''' + GUARD + ''' ;;
esac
exit 0
'''
CACHES = '''#!/bin/sh
set -eu
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t /usr/share/icons/hicolor || true
fi
exit 0
'''
WRAPPER = '''#!/bin/sh
if [ "${1:-}" = "--register-links" ]; then
    shift
    if [ "$#" -ne 0 ]; then
        echo 'Usage: stellarys --register-links' >&2
        exit 2
    fi
    exec /usr/bin/python3 /opt/stellarys-viewer/register-links.py
fi
exec /opt/stellarys-viewer/stellarys "$@"
'''
DESKTOP = '''[Desktop Entry]
Type=Application
Name=Stellarys Viewer
Comment=Second Life photography and permission-based posing
Exec=/usr/bin/stellarys %u
TryExec=/usr/bin/stellarys
Icon=stellarys-viewer
Terminal=false
Categories=Network;
StartupNotify=true
StartupWMClass=stellarys-bin
MimeType=x-scheme-handler/secondlife;x-scheme-handler/hop;
X-Stellarys-Desktop-Entry=true
'''


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write(path, data, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')
    path.chmod(0o755 if executable else 0o644)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application', type=Path, required=True)
    parser.add_argument('--viewer-binary', type=Path, required=True)
    parser.add_argument('--build', type=Path, default=REPO / 'build-linux-x86_64')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Use a fresh output directory.')
    output.mkdir(parents=True)
    root = output / 'package-root'
    app = root / 'opt/stellarys-viewer'
    shutil.copytree(args.application, app, symlinks=True)
    shutil.copy2(args.viewer_binary, app / 'bin/stellarys-bin')
    subprocess.run(['strip', '--strip-unneeded', str(app / 'bin/stellarys-bin')], check=True)
    for name in ('stellarys-updater.py', 'stellarys_updater_core.py', 'register-links.py'):
        shutil.copy2(TOOLS / name, app / name)
        (app / name).chmod(0o755 if name != 'stellarys_updater_core.py' else 0o644)
    (app / 'install-desktop.py').unlink(missing_ok=True)
    for library in (args.build / 'packages/lib32').glob('libuuid.so.1*'):
        shutil.copy2(library, app / 'lib32' / library.name, follow_symlinks=False)
    for name in ('PRIVACY.md','DISCLOSURES.md','SOURCE-PROVENANCE.md'):
        shutil.copy2(REPO / name, app / name)
    header=(args.build / 'newview/fsversionvalues.h').read_text()
    expected='Stellarys Viewer 0.1.5 Linux Preview 1'
    if ('#define LL_VIEWER_CHANNEL '+expected+'\n') not in header:
        raise SystemExit('Build/release identity mismatch; configure and compile first.')
    write(app / '.stellarys-deb-install', 'StellarysDebPackage=stellarys-viewer\n')
    metadata = {'name': 'Stellarys Viewer', 'version': '0.1.5',
        'viewer_channel': expected, 'base_version': '7.2.4.80712', 'platform': 'linux-x86_64',
        'status': 'experimental preview 1', 'profile': '~/.stellarys_x64',
        'debian_version': DEB_VERSION, 'display_version': DISPLAY_VERSION,
        'updates': 'GitHub Linux installer feed; administrator approval required'}
    write(app / 'stellarys-version.json', json.dumps(metadata, indent=2) + '\n')
    shutil.copy2(TOOLS / 'README-Debian.md', app / 'README-Linux.txt')
    (app / 'README-Linux.txt').chmod(0o644)
    write(root / 'usr/bin/stellarys', WRAPPER, True)
    helper = root / 'usr/lib/stellarys-viewer/install-update.py'
    helper.parent.mkdir(parents=True)
    shutil.copy2(TOOLS / 'install-update.py', helper)
    helper.chmod(0o755)
    policy = root / 'usr/share/polkit-1/actions/org.stellarys.viewer.install-update.policy'
    policy.parent.mkdir(parents=True)
    shutil.copy2(TOOLS / policy.name, policy)
    policy.chmod(0o644)
    write(root / 'usr/share/applications/org.stellarys.Viewer.desktop', DESKTOP)
    subprocess.run(['desktop-file-validate', str(root / 'usr/share/applications/org.stellarys.Viewer.desktop')], check=True)
    for size in (16, 32, 48, 128, 256, 512):
        icon = root / f'usr/share/icons/hicolor/{size}x{size}/apps/stellarys-viewer.png'
        icon.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / f'indra/newview/icons/stellarys/firestorm_{size}.png', icon)
    doc = root / 'usr/share/doc/stellarys-viewer'
    doc.mkdir(parents=True)
    shutil.copy2(TOOLS / 'README-Debian.md', doc / 'README.Debian')
    (doc / 'README.Debian').chmod(0o644)
    write(doc / 'copyright', 'Stellarys Viewer is based on Firestorm and the Second Life Viewer.\n'
          'Viewer source is distributed under LGPL-2.1, with separately licensed components.\n'
          'Full notices and component licenses are included in /opt/stellarys-viewer.\n'
          'Source: https://github.com/NekoMisa/stellarys-viewer\n')
    control = root / 'DEBIAN'
    control.mkdir()
    write(control / 'preinst', PREINST, True)
    write(control / 'prerm', PRERM, True)
    write(control / 'postinst', CACHES, True)
    write(control / 'postrm', CACHES, True)
    # Analyze every bundled 64-bit ELF; 32-bit legacy voice has explicit deps below.
    elfs = []
    for path in app.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        with path.open('rb') as stream:
            header = stream.read(5)
        if header == b'\x7fELF\x02':
            elfs.append(str(path))
    analysis = output / 'dependency-analysis'
    write(analysis / 'debian/control', 'Source: stellarys-viewer\nSection: net\nPriority: optional\n'
          'Maintainer: NekoMisa <NekoMisa@users.noreply.github.com>\n\n'
          'Package: stellarys-viewer\nArchitecture: amd64\nDescription: Stellarys Viewer\n')
    result = subprocess.run(['dpkg-shlibdeps', '--ignore-missing-info', '-O',
        '-l' + str(app / 'lib'), *elfs], cwd=analysis, capture_output=True, text=True)
    write(output / 'dependency-analysis.log', result.stdout + result.stderr)
    if result.returncode:
        raise SystemExit('ELF dependency analysis failed; inspect dependency-analysis.log.')
    deps = result.stdout.strip().removeprefix('shlibs:Depends=')
    extra = ['python3 (>= 3.10)', 'python3-gi', 'gir1.2-gtk-3.0', 'policykit-1',
        'xdg-utils', 'desktop-file-utils', 'libglib2.0-bin', 'libpulse0',
        'libgstreamer1.0-0', 'libgstreamer-plugins-base1.0-0',
        'libc6-i386', 'lib32stdc++6', 'lib32z1']
    installed_size = sum(p.stat().st_size for p in root.rglob('*')
                         if p.is_file() and not p.is_symlink()) // 1024 + 1
    write(control / 'control', f'Package: {PACKAGE}\nVersion: {DEB_VERSION}\nArchitecture: amd64\n'
        'Maintainer: NekoMisa <NekoMisa@users.noreply.github.com>\nSection: net\nPriority: optional\n'
        'Pre-Depends: python3 (>= 3.10)\n'
        f'Installed-Size: {installed_size}\nDepends: {deps}, ' + ', '.join(extra) + '\n'
        'Recommends: gstreamer1.0-plugins-base, gstreamer1.0-plugins-good, gstreamer1.0-libav\n'
        'Homepage: https://github.com/NekoMisa/stellarys-viewer\n'
        'Description: Stellarys Viewer for Second Life (experimental Linux preview)\n'
        ' A native viewer based on Firestorm 7.2.4.80712 with permission-based\n'
        ' posing, photography controls and the Stellarys AMD changes.\n'
        ' Includes verified manual-approval updates. User settings are preserved.\n')
    manifest, md5s = [], []
    forbidden = {'.git', '__pycache__', 'user_settings', 'logs', 'cache', 'browser_profile', 'texturecache'}
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if set(rel.parts) & forbidden or path.suffix.lower() in {'.log', '.dmp', '.pdb', '.key', '.pfx', '.p12', '.pyc'}:
            raise SystemExit('Forbidden data in application payload: ' + str(rel))
        if rel.parts[0] == 'DEBIAN':
            continue
        item = {'path': str(rel), 'mode': oct(path.lstat().st_mode & 0o777)}
        if path.is_symlink():
            link = os.readlink(path)
            if Path(link).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
                raise SystemExit('Unsafe package symlink: ' + str(rel))
            item['symlink'] = link
        elif path.is_file():
            item.update(bytes=path.stat().st_size, sha256=sha(path))
            md5s.append(hashlib.md5(path.read_bytes()).hexdigest() + '  ' + str(rel))
        else:
            item['directory'] = True
        manifest.append(item)
    write(control / 'md5sums', '\n'.join(md5s) + '\n')
    write(output / 'PAYLOAD-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    env = dict(os.environ, SOURCE_DATE_EPOCH='0', XZ_DEFAULTS='-T4')
    installer = output / FILENAME
    subprocess.run(['dpkg-deb', '--root-owner-group', '-Zxz', '-z6', '--build',
                    str(root), str(installer)], check=True, env=env)
    feed = dict(schema=1, package=PACKAGE, architecture='amd64', debian_version=DEB_VERSION,
                display_version=DISPLAY_VERSION, filename=FILENAME, sha256=sha(installer),
                bytes=installer.stat().st_size)
    write(output / 'Stellarys-Linux-Update.json', json.dumps(feed, indent=2) + '\n')
    print(json.dumps(dict(installer=str(installer), bytes=feed['bytes'], elf_files=len(elfs))))


if __name__ == '__main__':
    main()
