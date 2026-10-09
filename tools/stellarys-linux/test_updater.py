#!/usr/bin/python3
"""Exercise Linux feed selection, real Debian validation and download failures."""
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

import stellarys_updater_core as core

spec = importlib.util.spec_from_file_location('installer', Path(__file__).with_name('install-update.py'))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class Updates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        stage = cls.root / 'package'
        (stage / 'DEBIAN').mkdir(parents=True)
        (stage / 'DEBIAN/control').write_text('Package: stellarys-viewer\nVersion: 0.1.4~linuxpreview1-1\n'
            'Architecture: amd64\nMaintainer: NekoMisa <NekoMisa@users.noreply.github.com>\nDescription: Fixture only\n')
        cls.deb = cls.root / 'fixture.deb'
        subprocess.run(['dpkg-deb', '--build', str(stage), str(cls.deb)], check=True, capture_output=True)
        cls.content = cls.deb.read_bytes()
        cls.feed = {'schema': 1, 'package': 'stellarys-viewer', 'architecture': 'amd64',
            'debian_version': '0.1.4~linuxpreview1-1', 'display_version': '0.1.4 preview',
            'filename': 'fixture.deb', 'bytes': len(cls.content),
            'sha256': hashlib.sha256(cls.content).hexdigest()}
        cls.release = {'html_url': core.RELEASES + '/tag/linux-fixture',
            'prerelease': True, 'body': '## Changes\n- A readable update window.\n- Linux installer.',
            'assets': [{'name': 'fixture.deb', 'size': len(cls.content),
                        'browser_download_url': core.RELEASES + '/download/linux-fixture/fixture.deb'},
                       {'name': core.MANIFEST_NAME, 'browser_download_url':
                        core.RELEASES + '/download/linux-fixture/' + core.MANIFEST_NAME}]}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def candidate(self):
        return core.validate_manifest(self.feed, self.release)

    def test_debian_version_order(self):
        self.assertTrue(core.newer('0.1.3~linuxpreview2-1', '0.1.3~linuxpreview1-1'))
        self.assertTrue(core.newer('0.1.3', '0.1.3~linuxpreview2-1'))
        self.assertFalse(core.newer('0.1.3~linuxpreview2-1', '0.1.3~linuxpreview2-1'))
        for value in ('../x', '-x', '1:', '1 2', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                core.version(value)

    def test_repository_boundary(self):
        for url in ('http://github.com/NekoMisa/stellarys-viewer/releases/download/t/a.deb',
                    'https://github.com.evil.test/NekoMisa/stellarys-viewer/releases/download/t/a.deb',
                    'https://github.com/other/repo/releases/download/t/a.deb',
                    core.RELEASES + '/download/t/../a.deb',
                    core.RELEASES + '/download/t/%2e%2e/a.deb',
                    core.RELEASES + '/download/t/a.deb?other=1'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                core.github_asset(url)

    def test_manifest_rejects_wrong_identity_and_path(self):
        for key, value in (('schema', 2), ('package', 'firestorm'), ('architecture', 'arm64'),
                           ('filename', '../fixture.deb'), ('sha256', 'x' * 64),
                           ('bytes', 0), ('bytes', True)):
            feed = dict(self.feed, **{key: value})
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                core.validate_manifest(feed, self.release)

    def test_manifest_requires_unique_matching_asset(self):
        for assets in ([], [self.release['assets'][0]] * 2):
            with self.assertRaises(ValueError):
                core.validate_manifest(self.feed, dict(self.release, assets=assets))
        release = copy.deepcopy(self.release)
        release['assets'][0]['size'] += 1
        with self.assertRaises(ValueError):
            core.validate_manifest(self.feed, release)

    def test_windows_only_releases_are_ignored_and_linux_preview_selected(self):
        releases = [{'assets': [{'name': 'Windows-Setup.exe'}]}, self.release]
        with patch.object(core, 'read_json', side_effect=[releases, self.feed]):
            self.assertEqual(core.check_release('0.1.3~linuxpreview2-1')['filename'], 'fixture.deb')
        with patch.object(core, 'read_json', return_value=[releases[0]]):
            self.assertIsNone(core.check_release('0.1.3~linuxpreview2-1'))
        with patch.object(core, 'read_json', side_effect=[[self.release], self.feed]):
            self.assertIsNone(core.check_release('0.1.4~linuxpreview1-1'))

    def test_drafts_ignored(self):
        with patch.object(core, 'read_json', return_value=[dict(self.release, draft=True)]):
            self.assertIsNone(core.check_release('0.1.3'))

    def test_real_deb_identity(self):
        core.verify_deb(self.deb, self.feed['debian_version'])
        installer.verify_identity(self.deb, self.feed['debian_version'])
        with self.assertRaises(ValueError):
            core.verify_deb(self.deb, '0.1.2')
        with self.assertRaises(ValueError):
            installer.verify_identity(self.deb, '0.1.2')

    def test_verified_download_and_cached_reuse(self):
        cache = self.root / 'cache-valid'
        with patch.object(core, 'open_url', return_value=io.BytesIO(self.content)) as opener:
            target = core.download(self.candidate(), cache, threading.Event())
            self.assertEqual(target.read_bytes(), self.content)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertEqual(cache.stat().st_mode & 0o777, 0o700)
            core.download(self.candidate(), cache, threading.Event())
            self.assertEqual(opener.call_count, 1)

    def test_hash_size_and_cancel_fail_without_installer(self):
        for case, data in [('hash', self.content[:-1] + bytes([self.content[-1] ^ 1])),
                           ('short', self.content[:-3]), ('long', self.content + b'extra'),
                           ('cancel', self.content)]:
            cache = self.root / ('cache-' + case)
            event = threading.Event()
            if case == 'cancel':
                event.set()
            with self.subTest(case=case), patch.object(core, 'open_url', return_value=io.BytesIO(data)):
                with self.assertRaises(ValueError):
                    core.download(self.candidate(), cache, event)
                self.assertFalse((cache / 'fixture.deb').exists())
                self.assertFalse(list(cache.glob('*.part')))

    def test_interrupted_part_does_not_block_retry(self):
        cache = self.root / 'cache-interrupted'
        cache.mkdir()
        (cache / 'fixture.deb.part').write_text('interrupted')
        with patch.object(core, 'open_url', return_value=io.BytesIO(self.content)):
            self.assertEqual(core.download(self.candidate(), cache, threading.Event()).read_bytes(), self.content)

    def test_privileged_copy_revalidates_hash_owner_and_symlink(self):
        target = self.root / 'root-copy.deb'
        installer.copy_verified(str(self.deb), self.feed['sha256'], os.getuid(), target)
        self.assertEqual(target.read_bytes(), self.content)
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(ValueError):
            installer.copy_verified(str(self.deb), '0' * 64, os.getuid(), self.root / 'bad-copy')
        with self.assertRaises(ValueError):
            installer.copy_verified(str(self.deb), self.feed['sha256'], os.getuid() + 1, self.root / 'bad-owner')
        symlink = self.root / 'symlink.deb'
        symlink.symlink_to(self.deb)
        with self.assertRaises(OSError):
            installer.copy_verified(str(symlink), self.feed['sha256'], os.getuid(), self.root / 'bad-link')

    def test_plain_highlights(self):
        self.assertEqual(core.highlights(self.release['body']),
                         ['A readable update window.', 'Linux installer.'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
