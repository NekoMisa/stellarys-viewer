#!/usr/bin/python3
"""Portable GTK workflow with real disposable archives and folder replacement."""
import argparse
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from test_portable_updater import PortableUpdates
import stellarys_portable_core as core

spec=importlib.util.spec_from_file_location('gui',Path(__file__).with_name('stellarys-updater.py'))
gui=importlib.util.module_from_spec(spec);spec.loader.exec_module(gui)


def drain():
    context=gui.GLib.MainContext.default()
    while context.pending():context.iteration(False)


class Workflow(unittest.TestCase):
    def setUp(self):
        self.fixture=PortableUpdates();self.fixture.setUp()
        self.fixture.profile.joinpath('user_settings').mkdir()
        self.patches=[patch.object(gui,'APP',self.fixture.app),patch.object(gui,'PORTABLE',True),
                      patch.object(gui,'core',core),patch.dict(os.environ,{'XDG_CACHE_HOME':str(self.fixture.root/'downloads')})]
        for p in self.patches:p.start()
        args=argparse.Namespace(startup=False,preview_json=None,profile_dir=self.fixture.profile,viewer_pid=1234)
        with patch.object(gui.Updater,'check',lambda window:None):
            self.window=gui.Updater(args,core.validate_install(self.fixture.app),{})
        self.window.checked(self.fixture.update,None);drain()

    def tearDown(self):
        self.window.destroy();drain()
        for p in reversed(self.patches):p.stop()
        self.fixture.tearDown()

    def test_download_then_real_install_preserves_profile_and_backup(self):
        with patch.object(core,'open_url',return_value=io.BytesIO(self.fixture.archive.read_bytes())):
            self.window.work(False)
        drain();self.assertEqual(self.window.action.get_label(),'Install update')
        self.assertEqual((self.fixture.app/'payload.txt').read_text(),'old application')
        with patch.object(gui,'viewer_alive',return_value=False),patch.object(gui.subprocess,'run',side_effect=AssertionError('No system installer allowed')):
            self.window.work(False)
        drain();self.assertEqual(self.window.action.get_label(),'Open Stellarys')
        self.assertEqual((self.fixture.app/'payload.txt').read_text(),'new application')
        self.assertEqual((self.window.backup_path/'payload.txt').read_text(),'old application')
        self.assertTrue((self.fixture.profile/'settings.txt').is_file())

    def test_auto_install_uses_only_normal_quit_after_payload_validation(self):
        with patch.object(core,'open_url',return_value=io.BytesIO(self.fixture.archive.read_bytes())),\
             patch.object(gui,'viewer_alive',side_effect=[True,False]),\
             patch.object(gui.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'(true,)','')) as run:
            self.window.work(True)
        drain();self.assertEqual(run.call_count,1)
        self.assertEqual(run.call_args.args[0][0],'/usr/bin/gdbus')
        self.assertIn('org.stellarys.ViewerAppAPI.RequestUpdateQuit',run.call_args.args[0])
        self.assertEqual(self.window.action.get_label(),'Open Stellarys')

    def test_corrupt_payload_never_requests_quit_or_installs(self):
        (self.fixture.new/'payload.txt').write_text('bad application');self.fixture.pack()
        self.window.update=self.fixture.update
        with patch.object(core,'open_url',return_value=io.BytesIO(self.fixture.archive.read_bytes())),\
             patch.object(gui,'viewer_alive') as alive,patch.object(gui.subprocess,'run') as run:
            self.window.work(True)
        drain();alive.assert_not_called();run.assert_not_called()
        self.assertIn('checksum mismatch',self.window.status.get_text())
        self.assertEqual((self.fixture.app/'payload.txt').read_text(),'old application')

    def test_busy_installation_is_recoverable(self):
        self.window.downloaded=self.fixture.archive
        lock=core.open_lock(self.fixture.app,False)
        try:
            with patch.object(gui,'viewer_alive',return_value=False),patch.object(gui.time,'monotonic',side_effect=[0,4]):
                self.window.work(False)
            drain();self.assertIn('Close every instance',self.window.status.get_text())
            self.assertTrue(self.window.action.get_sensitive())
            self.assertEqual((self.fixture.app/'payload.txt').read_text(),'old application')
        finally:os.close(lock)

    def test_restart_uses_updated_portable_folder(self):
        with patch.object(gui.subprocess,'Popen') as launch,patch.object(gui.Gtk,'main_quit'):
            self.window.launch()
        self.assertEqual(launch.call_args.args[0],[str(self.fixture.app/'stellarys')])


if __name__=='__main__':unittest.main(defaultTest='Workflow',verbosity=2)
