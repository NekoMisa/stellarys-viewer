#!/usr/bin/python3
"""GTK workflow tests with real fixture .deb verification; no root install or login."""
import argparse
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_updater import Updates
import stellarys_updater_core as core

spec = importlib.util.spec_from_file_location('gui', Path(__file__).with_name('stellarys-updater.py'))
gui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gui)


def drain():
    context = gui.GLib.MainContext.default()
    while context.pending():
        context.iteration(False)


class Workflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Updates.setUpClass()

    @classmethod
    def tearDownClass(cls):
        Updates.tearDownClass()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        profile = self.root / 'profile'
        (profile / 'user_settings').mkdir(parents=True)
        self.args = argparse.Namespace(startup=False, preview_json=None, profile_dir=profile, viewer_pid=1234)
        with patch.object(gui.Updater, 'check', lambda window: None):
            self.window = gui.Updater(self.args, {'display_version': '0.1.3 Linux preview 2',
                                                  'debian_version': '0.1.3~linuxpreview2-1'}, {})
        self.update = core.validate_manifest(Updates.feed, Updates.release)
        self.window.checked(self.update, None)
        self.environment = patch.dict(os.environ, {'XDG_CACHE_HOME': str(self.root / 'cache')})
        self.environment.start()
        drain()

    def tearDown(self):
        self.window.destroy()
        drain()
        self.environment.stop()
        self.temp.cleanup()

    def test_download_then_explicit_install(self):
        with patch.object(core, 'open_url', return_value=io.BytesIO(Updates.content)):
            self.window.work(False)
        drain()
        self.assertEqual(self.window.action.get_label(), 'Install update')
        self.assertEqual(self.window.downloaded.read_bytes(), Updates.content)
        with patch.object(gui, 'viewer_alive', return_value=False), patch.object(gui.subprocess, 'run',
                return_value=subprocess.CompletedProcess([], 0, '', '')) as run:
            self.window.work(False)
        drain()
        self.assertEqual(run.call_args.args[0], ['/usr/bin/pkexec', gui.HELPER,
            str(self.window.downloaded), self.update['sha256'], self.update['debian_version']])
        self.assertEqual(self.window.action.get_label(), 'Open Stellarys')

    def test_auto_install_requests_normal_quit_after_verification(self):
        original_run = subprocess.run
        calls = []

        def run(args, **kwargs):
            if args[0] in ('/usr/bin/gdbus', '/usr/bin/pkexec'):
                calls.append(args)
                return subprocess.CompletedProcess(args, 0, '(true,)\n', '')
            return original_run(args, **kwargs)

        with patch.object(core, 'open_url', return_value=io.BytesIO(Updates.content)), \
                patch.object(gui, 'viewer_alive', side_effect=[True, False]), \
                patch.object(gui.subprocess, 'run', side_effect=run):
            self.window.work(True)
        drain()
        self.assertEqual(calls[0][0], '/usr/bin/gdbus')
        self.assertIn('org.stellarys.ViewerUpdater.p1234', calls[0])
        self.assertIn('org.stellarys.ViewerAppAPI.RequestUpdateQuit', calls[0])
        self.assertEqual(calls[1][0], '/usr/bin/pkexec')
        self.assertEqual(self.window.action.get_label(), 'Open Stellarys')

    def test_bad_download_never_quits_or_installs(self):
        with patch.object(core, 'open_url', return_value=io.BytesIO(b'broken')), \
                patch.object(gui, 'viewer_alive') as alive:
            self.window.work(True)
        drain()
        alive.assert_not_called()
        self.assertIsNone(self.window.downloaded)
        self.assertIn('verification failed', self.window.status.get_text())
        self.assertEqual(self.window.action.get_label(), 'Retry download')

    def test_authentication_cancel_is_recoverable(self):
        self.window.downloaded = Updates.deb
        with patch.object(gui, 'viewer_alive', return_value=False), patch.object(gui.subprocess, 'run',
                return_value=subprocess.CompletedProcess([], 126, '', 'Authentication cancelled')):
            self.window.work(False)
        drain()
        self.assertIn('cancelled', self.window.status.get_text())
        self.assertTrue(self.window.close_button.get_sensitive())
        self.assertTrue(self.window.action.get_sensitive())
        self.assertEqual(self.window.action.get_label(), 'Install update')

    def test_update_preference_is_private_and_profile_specific(self):
        self.window.startup.set_active(False)
        path = self.args.profile_dir / 'user_settings/stellarys-linux-updater.json'
        self.assertFalse(json.loads(path.read_text())['check_at_startup'])
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main(defaultTest='Workflow', verbosity=2)
