#!/usr/bin/env python3
"""Install Stellarys's own per-user desktop entry; default links are opt-in."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

DESKTOP_ID = 'org.stellarys.Viewer.desktop'
MARKER = 'X-Stellarys-Desktop-Entry=true'


def escape_value(value):
    return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def escape_exec(value):
    # Exec is parsed by the desktop, never by a shell. Percent is a field code.
    value = str(value).replace('%', '%%')
    for char in ('\\', '"', '`', '$'):
        value = value.replace(char, '\\' + char)
    return '"' + escape_value(value) + '"'


def desktop_entry(prefix):
    return '\n'.join([
        '[Desktop Entry]', 'Type=Application', 'Name=Stellarys',
        'Comment=Second Life photography and permission-based posing',
        'Exec=/usr/bin/env ' + escape_exec(prefix / 'stellarys') + ' %u',
        'TryExec=' + escape_value(prefix / 'stellarys'),
        'Icon=' + escape_value(prefix / 'Stellarys.png'),
        'Terminal=false', 'Categories=Network;', 'StartupNotify=true',
        'StartupWMClass=stellarys-bin',
        'MimeType=x-scheme-handler/secondlife;x-scheme-handler/hop;', MARKER, '',
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--register-links', action='store_true',
                        help='also choose Stellarys as this user\'s secondlife/hop handler')
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit('Run desktop setup as your normal Linux user, without sudo.')
    prefix = Path(__file__).resolve().parent
    if not (prefix / 'stellarys').is_file() or not (prefix / 'bin/stellarys-bin').is_file():
        raise SystemExit('Run the script from the complete extracted Stellarys package.')
    if args.register_links and not shutil.which('xdg-mime'):
        raise SystemExit('Install xdg-utils before using --register-links.')
    data_home = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    if not data_home.is_absolute():
        raise SystemExit('XDG_DATA_HOME must be an absolute directory.')
    target = data_home / 'applications' / DESKTOP_ID
    if target.exists() and MARKER not in target.read_text(encoding='utf-8'):
        raise SystemExit('Refusing to overwrite an unrelated desktop entry.')
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix('.desktop.new')
    with temp.open('x', encoding='utf-8') as stream:
        stream.write(desktop_entry(prefix))
    temp.chmod(0o644)
    temp.replace(target)
    if shutil.which('update-desktop-database'):
        subprocess.run(['update-desktop-database', str(target.parent)], check=True)
    if args.register_links:
        for scheme in ('secondlife', 'hop'):
            subprocess.run(['xdg-mime', 'default', DESKTOP_ID, 'x-scheme-handler/' + scheme], check=True)
    print('Stellarys desktop entry installed for this Linux user.')
    if args.register_links:
        print('Stellarys selected for secondlife and hop links.')
    else:
        print('Existing default link handlers were preserved. Use --register-links to choose Stellarys.')


if __name__ == '__main__':
    main()
