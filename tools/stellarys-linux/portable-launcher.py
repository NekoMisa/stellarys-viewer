#!/usr/bin/python3
"""Keep application starts out of the portable update transaction."""
from pathlib import Path
import os
import subprocess
import sys
import stellarys_portable_core as portable


def main():
    app = Path(__file__).resolve().parent
    portable.validate_install(app)
    try:
        lock = portable.open_lock(app, False)
    except BlockingIOError:
        raise SystemExit('Stellarys is being updated. Wait for installation to finish and try again.')
    try:
        # This parent retains the lock while waiting. Do not pass it to children:
        # an updater launched by the viewer must survive logout without inheriting
        # a shared lock that would prevent its own exclusive installation lock.
        return subprocess.call([str(app / 'stellarys-launcher'), *sys.argv[1:]])
    finally:
        os.close(lock)


if __name__ == '__main__':
    raise SystemExit(main())
