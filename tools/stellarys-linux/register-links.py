#!/usr/bin/python3
"""Choose the system Stellarys desktop entry for this user's map links."""
import os
from pathlib import Path
import subprocess
import time

DESKTOP_ID = 'org.stellarys.Viewer.desktop'
MARKER = 'X-Stellarys-Desktop-Entry=true'


def main():
    if os.geteuid() == 0:
        raise SystemExit('Run stellarys --register-links as your normal Linux user, without sudo.')
    system = Path('/usr/share/applications') / DESKTOP_ID
    if not system.is_file() or MARKER not in system.read_text():
        raise SystemExit('The Stellarys system desktop entry is missing.')
    data_home = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    if not data_home.is_absolute():
        raise SystemExit('XDG_DATA_HOME must be absolute.')
    legacy = data_home / 'applications' / DESKTOP_ID
    if legacy.is_symlink():
        raise SystemExit('Refusing to replace a desktop-entry symlink. Review it manually.')
    backup = None
    if legacy.exists():
        if MARKER not in legacy.read_text():
            raise SystemExit('An unrelated per-user desktop entry has this name; review it manually.')
        backup = legacy.with_name(DESKTOP_ID + f'.before-deb-{time.time_ns()}.bak')
        legacy.rename(backup)
        subprocess.run(['/usr/bin/update-desktop-database', str(legacy.parent)], check=True)
    try:
        for scheme in ('secondlife', 'hop'):
            subprocess.run(['/usr/bin/xdg-mime', 'default', DESKTOP_ID,
                            'x-scheme-handler/' + scheme], check=True)
    except subprocess.SubprocessError:
        if backup:
            backup.rename(legacy)
            subprocess.run(['/usr/bin/update-desktop-database', str(legacy.parent)], check=False)
        raise
    print('Stellarys selected for this user’s secondlife and hop links.')
    if backup:
        print('The old per-user desktop entry was backed up; the old application folder was kept.')


if __name__ == '__main__':
    main()
