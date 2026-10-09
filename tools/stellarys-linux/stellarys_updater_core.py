"""Linux release checks and verified downloads; no GUI or account data."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request

REPO = 'NekoMisa/stellarys-viewer'
API = f'https://api.github.com/repos/{REPO}/releases?per_page=30'
RELEASES = f'https://github.com/{REPO}/releases'
MANIFEST_NAME = 'Stellarys-Linux-Update.json'
MAX_JSON = 4 * 1024 * 1024
MAX_PACKAGE = 2 * 1024 * 1024 * 1024
VERSION_PATTERN = re.compile(r'[0-9][A-Za-z0-9.+:~\-]{0,127}\Z')
SHA_PATTERN = re.compile(r'[0-9a-f]{64}\Z')


def version(value):
    if not isinstance(value, str) or not VERSION_PATTERN.fullmatch(value):
        raise ValueError('Invalid Debian package version.')
    if subprocess.run(['dpkg', '--validate-version', value], capture_output=True).returncode:
        raise ValueError('Invalid Debian package version.')
    return value


def newer(candidate, current):
    return subprocess.run(['dpkg', '--compare-versions', version(candidate), 'gt',
                           version(current)], check=False).returncode == 0


def github_asset(url):
    parsed = urllib.parse.urlsplit(url)
    prefix = f'/{REPO}/releases/download/'
    if (parsed.scheme != 'https' or parsed.netloc != 'github.com'
            or not parsed.path.startswith(prefix) or parsed.query or parsed.fragment
            or '..' in urllib.parse.unquote(parsed.path).split('/')):
        raise ValueError('Update assets must come from this Stellarys repository.')
    return url


class GithubRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        hosts = {'github.com', 'api.github.com', 'release-assets.githubusercontent.com',
                 'objects.githubusercontent.com', 'github-releases.githubusercontent.com'}
        if parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.username:
            raise ValueError('Refusing an unexpected update download redirect.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_url(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': 'Stellarys-Linux-Updater', 'Accept': 'application/vnd.github+json'})
    return urllib.request.build_opener(GithubRedirect()).open(request, timeout=25)


def read_json(url):
    with open_url(url) as response:
        data = response.read(MAX_JSON + 1)
    if len(data) > MAX_JSON:
        raise ValueError('Update metadata is too large.')
    return json.loads(data)


def validate_manifest(data, release):
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('Unsupported Linux update metadata.')
    if data.get('package') != 'stellarys-viewer' or data.get('architecture') != 'amd64':
        raise ValueError('The update is not a Stellarys Linux amd64 package.')
    result = dict(data)
    result['debian_version'] = version(data.get('debian_version'))
    name = data.get('filename')
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_.+~\-]+\.deb', name):
        raise ValueError('Invalid Linux installer filename.')
    if not isinstance(data.get('sha256'), str) or not SHA_PATTERN.fullmatch(data['sha256']):
        raise ValueError('Missing or invalid installer SHA-256.')
    size = data.get('bytes')
    if type(size) is not int or not 0 < size <= MAX_PACKAGE:
        raise ValueError('Invalid installer size.')
    assets = release.get('assets', [])
    matches = [a for a in assets if a.get('name') == name]
    if len(matches) != 1:
        raise ValueError('The named installer is absent or ambiguous in this release.')
    asset = matches[0]
    result['url'] = github_asset(asset.get('browser_download_url', ''))
    if asset.get('size') != size:
        raise ValueError('Installer size does not match its release asset.')
    notes = release.get('html_url', '')
    if not notes.startswith(RELEASES + '/tag/') or urllib.parse.urlsplit(notes).netloc != 'github.com':
        raise ValueError('Invalid release notes link.')
    result['notes_url'] = notes
    result['notes'] = str(release.get('body') or '')[:20000]
    result['display_version'] = str(data.get('display_version') or result['debian_version'])[:100]
    return result


def check_release(current):
    releases = read_json(API)
    if not isinstance(releases, list):
        raise ValueError('Invalid GitHub releases response.')
    selected = None
    errors = []
    for release in releases:
        if release.get('draft'):
            continue
        manifests = [a for a in release.get('assets', []) if a.get('name') == MANIFEST_NAME]
        if not manifests:
            continue  # Windows-only releases are deliberately ignored.
        try:
            if len(manifests) != 1:
                raise ValueError('Ambiguous Linux update metadata.')
            data = read_json(github_asset(manifests[0].get('browser_download_url', '')))
            candidate = validate_manifest(data, release)
            if newer(candidate['debian_version'], current) and (
                    selected is None or newer(candidate['debian_version'], selected['debian_version'])):
                selected = candidate
        except (ValueError, OSError) as error:
            errors.append(str(error))
    if selected is None and errors:
        raise ValueError(errors[0])
    return selected


def highlights(body):
    lines = []
    for raw in body.splitlines():
        text = raw.strip()
        if not text or text.startswith('#') or text.startswith('```'):
            continue
        text = re.sub(r'^[-*+]\s+|^\d+\.\s+', '', text)
        text = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', text)
        text = text.replace('**', '').replace('`', '')
        lines.append(text[:220])
        if len(lines) == 5:
            break
    return lines or ['See the full release notes for details.']


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_deb(path, expected_version):
    fields = subprocess.check_output(['dpkg-deb', '-f', str(path), 'Package',
                                      'Version', 'Architecture'], text=True)
    found = dict(line.split(': ', 1) for line in fields.splitlines() if ': ' in line)
    if found != {'Package': 'stellarys-viewer', 'Version': version(expected_version),
                 'Architecture': 'amd64'}:
        raise ValueError('Downloaded installer package identity/version did not match.')


def download(update, cache, cancelled, progress=lambda value: None):
    github_asset(update['url'])
    if not re.fullmatch(r'[A-Za-z0-9_.+~\-]+\.deb', update['filename']):
        raise ValueError('Invalid Linux installer filename.')
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    cache.chmod(0o700)
    target = cache / update['filename']
    if (target.is_file() and not target.is_symlink() and target.stat().st_size == update['bytes']
            and file_sha(target) == update['sha256']):
        verify_deb(target, update['debian_version'])
        return target
    fd, temporary_name = tempfile.mkstemp(prefix='download-', suffix='.part', dir=cache)
    temporary = Path(temporary_name)
    try:
        digest = hashlib.sha256()
        total = 0
        with os.fdopen(fd, 'wb') as stream, open_url(update['url']) as response:
            while True:
                if cancelled.is_set():
                    raise ValueError('Download cancelled.')
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > update['bytes']:
                    raise ValueError('Installer exceeded its declared size.')
                digest.update(block)
                stream.write(block)
                progress(total / update['bytes'])
        if total != update['bytes'] or digest.hexdigest() != update['sha256']:
            raise ValueError('Installer verification failed; installation was refused.')
        verify_deb(temporary, update['debian_version'])
        temporary.replace(target)
        return target
    finally:
        temporary.unlink(missing_ok=True)
