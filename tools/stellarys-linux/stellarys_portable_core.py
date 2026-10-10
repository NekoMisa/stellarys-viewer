"""Verified per-user archive updates. Never invokes a system package manager."""
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tarfile
import tempfile
import time

from stellarys_updater_core import (API, RELEASES, read_json, github_asset,
                                    open_url, file_sha, highlights)

MANIFEST_NAME = 'Stellarys-Linux-Portable-Update.json'
VERSION_KEY = 'portable_version'
MAX_PACKAGE = 2 * 1024**3
MAX_EXPANDED = 4 * 1024**3
MAX_FILES = 60000
MAX_METADATA = 16 * 1024**2
PRODUCT = {'schema': 1, 'product': 'org.stellarys.Viewer', 'installation': 'portable'}
MARKER = 'stellarys-portable.json'
INVENTORY = 'stellarys-portable-payload.json'
FORBIDDEN = {'.git', 'user_settings', 'logs', 'cache', 'browser_profile', 'texturecache'}


def version(value):
    if not isinstance(value, str):
        raise ValueError('Invalid portable release version.')
    match = re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)-portable\.([1-9][0-9]*)', value or '')
    if not match or len(value) > 100:
        raise ValueError('Invalid portable release version.')
    return tuple(map(int, match.groups()))


def newer(candidate, current):
    return version(candidate) > version(current)


def release_names(value):
    major, minor, patch, preview = version(value)
    base = f'{major}.{minor}.{patch}'
    return (f'linux-v{base}-portable-preview{preview}',
            f'Stellarys-Viewer-{base}-Linux-x86_64-portable-preview{preview}.tar.xz')


def validate_manifest(data, release):
    if not isinstance(data, dict) or data.get('schema') != 1 or data.get('package') != 'stellarys-viewer-portable' or data.get('architecture') != 'x86_64':
        raise ValueError('Not a Stellarys Linux x86_64 portable update.')
    result = dict(data)
    tag, filename = release_names(data.get(VERSION_KEY))
    if release.get('draft') or release.get('tag_name') != tag or data.get('filename') != filename:
        raise ValueError('Portable release identity does not match its tag or filename.')
    size, digest = data.get('bytes'), data.get('sha256')
    if type(size) is not int or not 0 < size <= MAX_PACKAGE or not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('Invalid portable archive hash or size.')
    matches = [a for a in release.get('assets', []) if a.get('name') == filename]
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous portable archive.')
    asset = matches[0]
    expected_url = RELEASES + '/download/' + tag + '/' + filename
    if asset.get('state') != 'uploaded' or asset.get('size') != size or asset.get('digest') != 'sha256:' + digest or github_asset(asset.get('browser_download_url', '')) != expected_url:
        raise ValueError('Portable archive metadata does not match GitHub.')
    if release.get('html_url') != RELEASES + '/tag/' + tag:
        raise ValueError('Invalid release notes link.')
    result.update(url=expected_url, notes_url=release['html_url'],
                  notes=str(release.get('body') or '')[:20000],
                  display_version=str(data.get('display_version') or data[VERSION_KEY])[:100])
    return result


def check_release(current):
    version(current)
    releases = read_json(API)
    if not isinstance(releases, list):
        raise ValueError('Invalid releases response.')
    selected, errors = None, []
    for release in releases:
        if release.get('draft'):
            continue
        manifests = [a for a in release.get('assets', []) if a.get('name') == MANIFEST_NAME]
        if not manifests:
            continue  # Debian, Windows and other package formats are separate.
        try:
            if len(manifests) != 1:
                raise ValueError('Ambiguous portable update manifest.')
            tag = release.get('tag_name', '')
            url = RELEASES + '/download/' + tag + '/' + MANIFEST_NAME
            if github_asset(manifests[0].get('browser_download_url', '')) != url:
                raise ValueError('Portable manifest is outside its release.')
            candidate = validate_manifest(read_json(url), release)
            if newer(candidate[VERSION_KEY], current) and (selected is None or newer(candidate[VERSION_KEY], selected[VERSION_KEY])):
                selected = candidate
        except (ValueError, OSError, TypeError) as error:
            errors.append(str(error))
    if selected is None and errors:
        raise ValueError(errors[0])
    return selected


def relative_path(name):
    if not isinstance(name, str) or not name or '\\' in name or '\x00' in name:
        raise ValueError('Invalid archive path.')
    path = PurePosixPath(name)
    if path.is_absolute() or any(p in ('.', '..') for p in name.split('/')) or str(path) != name or set(path.parts) & FORBIDDEN:
        raise ValueError('Unsafe archive path.')
    return path


def metadata(data, expected=None):
    if not isinstance(data, dict) or data.get('install_kind') != 'portable' or data.get('platform') != 'linux-x86_64':
        raise ValueError('Not a marked portable installation.')
    parts = version(data.get(VERSION_KEY))
    base = '.'.join(map(str, parts[:3]))
    if data.get('version') != base or data.get('viewer_channel') != f'Stellarys Viewer {base} Linux Portable Preview {parts[3]}':
        raise ValueError('Portable viewer identity is inconsistent.')
    if expected is not None and data[VERSION_KEY] != expected:
        raise ValueError('Archive contains a different portable release.')
    return data


def inspect_archive(path, expected):
    members, names, total = [], set(), 0
    with tarfile.open(path, 'r:xz') as archive:
        for member in archive:
            name = member.name.rstrip('/') if member.isdir() else member.name
            rel = relative_path(name)
            if rel.parts[0] != 'StellarysViewer' or name in names or len(members) >= MAX_FILES:
                raise ValueError('Invalid or duplicate archive entry.')
            if member.issparse() or not (member.isdir() or member.isfile()) or member.mode not in (0o644, 0o755) or (member.isdir() and member.mode != 0o755):
                raise ValueError('Links, devices and special permissions are not allowed.')
            if member.size < 0 or (member.isdir() and member.size):
                raise ValueError('Invalid archive entry size.')
            total += member.size
            if total > MAX_EXPANDED:
                raise ValueError('Expanded archive is too large.')
            names.add(name); members.append(member)
        def read_small(name):
            member = archive.getmember('StellarysViewer/' + name)
            if not member.isfile() or member.size > MAX_METADATA:
                raise ValueError('Invalid portable metadata.')
            return json.load(archive.extractfile(member))
        if read_small(MARKER) != PRODUCT:
            raise ValueError('The archive is not a Stellarys portable package.')
        installed = metadata(read_small('stellarys-version.json'), expected)
        inventory = read_small(INVENTORY)
        if not isinstance(inventory, dict) or inventory.get('schema') != 1 or not isinstance(inventory.get('files'), list):
            raise ValueError('Invalid portable payload inventory.')
        files = {}
        for item in inventory['files']:
            rel = str(relative_path(item.get('path')))
            if rel == INVENTORY or rel in files or type(item.get('bytes')) is not int or item['bytes'] < 0 or not re.fullmatch('[0-9a-f]{64}', item.get('sha256', '')) or item.get('mode') not in (0o644, 0o755):
                raise ValueError('Invalid payload inventory entry.')
            files[rel] = item
        actual = {m.name.removeprefix('StellarysViewer/'): m for m in members if m.isfile()}
        if actual.keys() != files.keys() | {INVENTORY}:
            raise ValueError('Archive files differ from its inventory.')
        for name, item in files.items():
            if actual[name].size != item['bytes'] or actual[name].mode != item['mode']:
                raise ValueError('Archive file size or permissions differ.')
        for required in ('stellarys', 'stellarys-launcher', 'bin/stellarys-bin', 'stellarys-updater.py', MARKER, 'stellarys-version.json'):
            if required not in files:
                raise ValueError('Portable package is incomplete.')
        if any(files[name]['mode'] != 0o755 for name in ('stellarys', 'stellarys-launcher', 'bin/stellarys-bin')):
            raise ValueError('Portable launcher or viewer is not executable.')
    return members, files, total, installed


def verify_package(path, update):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size != update['bytes'] or file_sha(path) != update['sha256']:
        raise ValueError('Archive verification failed. Nothing was installed.')
    return inspect_archive(path, update[VERSION_KEY])


def download(update, cache, cancelled, progress=lambda value: None):
    _, expected = release_names(update[VERSION_KEY])
    if update['filename'] != expected or github_asset(update['url']) != RELEASES + '/download/' + release_names(update[VERSION_KEY])[0] + '/' + expected:
        raise ValueError('Invalid portable download destination.')
    cache = Path(cache); cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = cache / expected
    if target.exists() and not target.is_symlink():
        try:
            verify_package(target, update)
            return target
        except (ValueError, OSError, tarfile.TarError):
            pass
    fd, name = tempfile.mkstemp(prefix='portable-download-', suffix='.part', dir=cache)
    temporary = Path(name)
    try:
        total = 0; digest = hashlib.sha256()
        with os.fdopen(fd, 'wb') as stream, open_url(update['url']) as response:
            while True:
                if cancelled.is_set():
                    raise ValueError('Download cancelled.')
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > update['bytes']:
                    raise ValueError('Archive exceeds its declared size.')
                digest.update(block); stream.write(block); progress(total / update['bytes'])
        if total != update['bytes'] or digest.hexdigest() != update['sha256']:
            raise ValueError('Archive verification failed. Nothing was installed.')
        inspect_archive(temporary, update[VERSION_KEY])
        temporary.replace(target)
        return target
    finally:
        temporary.unlink(missing_ok=True)


def validate_install(app):
    app = Path(app)
    if os.geteuid() == 0 or app.is_symlink() or not app.is_dir() or app.absolute() != app.resolve():
        raise ValueError('Portable updates need a normal folder owned by this Linux user.')
    for path in (app, app.parent):
        s = path.stat()
        if s.st_uid != os.getuid() or s.st_mode & 0o022 or not s.st_mode & stat.S_IWUSR:
            raise ValueError('Move the complete portable application into a private writable folder you own.')
    for name in (MARKER, 'stellarys-version.json', 'stellarys', 'bin/stellarys-bin'):
        path = app / name
        if path.is_symlink() or not path.is_file() or path.stat().st_uid != os.getuid():
            raise ValueError('Portable installation marker or application is missing/unrelated.')
    if json.loads((app / MARKER).read_text()) != PRODUCT:
        raise ValueError('Refusing to replace an unrelated application folder.')
    return metadata(json.loads((app / 'stellarys-version.json').read_text()))


def open_lock(app, exclusive):
    app = Path(app)
    name = app.parent / ('.' + app.name + '.stellarys-update.lock')
    fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        s = os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid() or s.st_nlink != 1:
            raise ValueError('Unsafe portable update lock.')
        fcntl.flock(fd, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        return fd
    except BaseException:
        os.close(fd); raise


def running(app):
    binary = (Path(app) / 'bin/stellarys-bin').stat()
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            s = (proc / 'exe').stat()
            if (s.st_dev, s.st_ino) == (binary.st_dev, binary.st_ino):
                return True
        except (OSError, RuntimeError):
            continue
    return False


def exchange(left, right):
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, 'renameat2', None)
    if function is None:
        raise ValueError('This system cannot safely replace a portable application atomically.')
    function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    function.restype = ctypes.c_int
    if function(-100, os.fsencode(left), -100, os.fsencode(right), 2):
        code = ctypes.get_errno()
        raise OSError(code, 'Atomic application replacement was refused; original files remain available.')


class InstallationBusy(ValueError):
    pass


class PreparedUpdate:
    def __init__(self, app, path, update, cancelled):
        self.app = Path(app); self.container = None; self.swapped = False
        self.before = validate_install(self.app)
        if not newer(update[VERSION_KEY], self.before[VERSION_KEY]):
            raise ValueError('This update is not newer than the installed portable viewer.')
        self.update = update
        members, files, total, unused = verify_package(path, update)
        if shutil.disk_usage(self.app.parent).free < total + 50 * 1024**2:
            raise ValueError('Not enough space beside Stellarys to stage the update and retain a backup.')
        self.container = Path(tempfile.mkdtemp(prefix='.stellarys-stage-', dir=self.app.parent))
        self.staged = self.container / 'StellarysViewer'
        try:
            with tarfile.open(path, 'r:xz') as archive:
                for member in members:
                    if cancelled.is_set():
                        raise ValueError('Update preparation cancelled.')
                    destination = self.container / member.name
                    if member.isdir():
                        destination.mkdir(parents=True, exist_ok=True); destination.chmod(0o755)
                        continue
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    digest = hashlib.sha256(); size = 0
                    with archive.extractfile(member) as source, destination.open('xb') as output:
                        for block in iter(lambda: source.read(1024 * 1024), b''):
                            if cancelled.is_set():
                                raise ValueError('Update preparation cancelled.')
                            size += len(block); digest.update(block); output.write(block)
                    destination.chmod(member.mode)
                    if size != member.size:
                        raise ValueError('Truncated archive file.')
                    rel = member.name.removeprefix('StellarysViewer/')
                    if rel != INVENTORY and digest.hexdigest() != files[rel]['sha256']:
                        raise ValueError('Portable payload checksum mismatch.')
            metadata(json.loads((self.staged / 'stellarys-version.json').read_text()), update[VERSION_KEY])
        except BaseException:
            self.cleanup(); raise

    def cleanup(self):
        if self.container and self.container.exists() and not self.swapped:
            if self.container.is_symlink() or self.container.parent != self.app.parent or not self.container.name.startswith('.stellarys-stage-') or self.container.stat().st_uid != os.getuid():
                raise ValueError('Refusing unsafe temporary cleanup.')
            shutil.rmtree(self.container)
            self.container = None

    def commit(self):
        if validate_install(self.app)[VERSION_KEY] != self.before[VERSION_KEY]:
            raise ValueError('The installed version changed. Reopen the updater.')
        try:
            lock = open_lock(self.app, True)
        except BlockingIOError:
            raise InstallationBusy('Close every instance of this portable Stellarys before installing.') from None
        backup = None
        try:
            if running(self.app):
                raise InstallationBusy('Close every instance of this portable Stellarys before installing.')
            if validate_install(self.app)[VERSION_KEY] != self.before[VERSION_KEY]:
                raise ValueError('The installed version changed. Reopen the updater.')
            backup = Path(tempfile.mkdtemp(prefix=self.app.name + '-backup-', dir=self.app.parent))
            exchange(self.app, self.staged)
            self.swapped = True
            try:
                metadata(json.loads((self.app / 'stellarys-version.json').read_text()), self.update[VERSION_KEY])
                self.staged.rename(backup / 'StellarysViewer')
            except BaseException:
                exchange(self.app, self.staged)
                self.swapped = False
                raise
            self.swapped = False
            self.cleanup()
            return backup / 'StellarysViewer'
        finally:
            os.close(lock)
            if backup and backup.exists() and not any(backup.iterdir()):
                backup.rmdir()
