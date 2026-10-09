#!/usr/bin/python3 -I
"""Root-only installer bridge; requires fresh PolicyKit administrator approval."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

MAX_BYTES = 2 * 1024 * 1024 * 1024
ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C.UTF-8',
       'HOME': '/root', 'DEBIAN_FRONTEND': 'noninteractive'}


def copy_verified(source, sha, uid, destination):
    if not re.fullmatch('[0-9a-f]{64}', sha):
        raise ValueError('Invalid expected SHA-256.')
    fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as incoming:
        info = os.fstat(incoming.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != uid or not 0 < info.st_size <= MAX_BYTES:
            raise ValueError('Installer must be a regular file owned by the requesting user.')
        digest, total = hashlib.sha256(), 0
        with destination.open('xb') as outgoing:
            os.chmod(destination, 0o600)
            for block in iter(lambda: incoming.read(1024 * 1024), b''):
                total += len(block)
                if total > MAX_BYTES:
                    raise ValueError('Installer is too large.')
                digest.update(block)
                outgoing.write(block)
        if total != info.st_size or digest.hexdigest() != sha:
            raise ValueError('Installer changed or failed SHA-256 verification.')


def verify_identity(path, expected):
    if not re.fullmatch(r'[0-9][A-Za-z0-9.+:~\-]{0,127}', expected):
        raise ValueError('Invalid package version.')
    result = subprocess.check_output(['/usr/bin/dpkg-deb', '-f', str(path),
        'Package', 'Version', 'Architecture'], text=True, env=ENV)
    fields = dict(line.split(': ', 1) for line in result.splitlines() if ': ' in line)
    if fields != {'Package': 'stellarys-viewer', 'Version': expected, 'Architecture': 'amd64'}:
        raise ValueError('Installer package identity/version did not match.')


def main():
    if os.geteuid() != 0 or len(sys.argv) != 4:
        raise ValueError('Use the Stellarys updater to request administrator approval.')
    uid = int(os.environ.get('PKEXEC_UID', '-1'))
    if uid <= 0:
        raise ValueError('Missing non-root PolicyKit caller identity.')
    source, sha, expected = sys.argv[1:]
    if not Path(source).is_absolute():
        raise ValueError('Installer path must be absolute.')
    cache = Path('/var/cache/stellarys-viewer')
    if cache.is_symlink():
        raise ValueError('Installer staging directory must not be a symlink.')
    cache.mkdir(mode=0o700, exist_ok=True)
    if cache.stat().st_uid != 0:
        raise ValueError('Installer staging directory must belong to root.')
    cache.chmod(0o700)
    with tempfile.TemporaryDirectory(prefix='update-', dir=cache) as folder:
        destination = Path(folder) / 'stellarys-update.deb'
        copy_verified(source, sha, uid, destination)
        verify_identity(destination, expected)
        # A root-owned copy avoids changing the installer after validation.
        subprocess.run(['/usr/bin/apt-get', 'install', '--yes', '--no-remove',
                        str(destination)], check=True, env=ENV)
    try:
        cache.rmdir()
    except OSError:
        pass


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
