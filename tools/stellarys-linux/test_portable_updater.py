#!/usr/bin/python3
"""Real archive/filesystem transactions using disposable per-user fixtures."""
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import threading
import unittest
from unittest.mock import patch

import stellarys_portable_core as core

TOOLS = Path(__file__).resolve().parent


def fixture(app, release, content):
    app.mkdir(parents=True)
    parts = core.version(release); base = '.'.join(map(str, parts[:3]))
    metadata = dict(name='Stellarys Viewer', version=base, base_version='7.2.4.80712',
                    platform='linux-x86_64', install_kind='portable', portable_version=release,
                    viewer_channel=f'Stellarys Viewer {base} Linux Portable Preview {parts[3]}',
                    display_version=release)
    data = {core.MARKER: json.dumps(core.PRODUCT), 'stellarys-version.json': json.dumps(metadata),
            'payload.txt': content, 'bin/stellarys-bin': '#!/bin/sh\nexit 0\n',
            'stellarys-launcher': '#!/bin/sh\nexec "$(dirname "$0")/bin/stellarys-bin" "$@"\n',
            'stellarys-updater.py': '# Fixture updater\n'}
    for name, text in data.items():
        p = app/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    for source, target in [('portable-launcher.py','stellarys'), ('stellarys_portable_core.py','stellarys_portable_core.py'), ('stellarys_updater_core.py','stellarys_updater_core.py')]:
        shutil.copyfile(TOOLS/source, app/target)
    files=[]
    for p in app.rglob('*'):
        if p.is_dir():p.chmod(0o755)
        else:
            rel=str(p.relative_to(app));mode=0o755 if rel in ('stellarys','stellarys-launcher','bin/stellarys-bin') else 0o644
            p.chmod(mode);files.append(dict(path=rel,bytes=p.stat().st_size,sha256=core.file_sha(p),mode=mode))
    app.chmod(0o755)
    (app/core.INVENTORY).write_text(json.dumps(dict(schema=1,files=files)))
    (app/core.INVENTORY).chmod(0o644)


class PortableUpdates(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.app=self.root/'installed'/'StellarysViewer'
        fixture(self.app,'0.1.4-portable.1','old application')
        self.new=self.root/'package'/'StellarysViewer'
        fixture(self.new,'0.1.4-portable.2','new application')
        self.archive=self.root/core.release_names('0.1.4-portable.2')[1]
        self.pack()
        self.profile=self.root/'profile';self.profile.mkdir();(self.profile/'settings.txt').write_text('private fixture setting')
        self.cache=self.root/'separate-cache';self.cache.mkdir();(self.cache/'sentinel').write_text('cached fixture data')
        self.cancelled=threading.Event()

    def tearDown(self):self.temp.cleanup()

    def pack(self):
        with tarfile.open(self.archive,'w:xz') as t:t.add(self.new,arcname='StellarysViewer')
        self.feed=dict(schema=1,package='stellarys-viewer-portable',architecture='x86_64',
                       portable_version='0.1.4-portable.2',filename=self.archive.name,
                       bytes=self.archive.stat().st_size,sha256=core.file_sha(self.archive))
        tag=core.release_names(self.feed[core.VERSION_KEY])[0]
        self.release=dict(tag_name=tag,html_url=core.RELEASES+'/tag/'+tag,prerelease=True,
            body='## Changes\n- Fixture update.',assets=[
            dict(name=self.archive.name,state='uploaded',size=self.feed['bytes'],digest='sha256:'+self.feed['sha256'],
                 browser_download_url=core.RELEASES+'/download/'+tag+'/'+self.archive.name),
            dict(name=core.MANIFEST_NAME,browser_download_url=core.RELEASES+'/download/'+tag+'/'+core.MANIFEST_NAME)])
        self.update=core.validate_manifest(self.feed,self.release)

    def prepared(self):return core.PreparedUpdate(self.app,self.archive,self.update,self.cancelled)

    def test_version_order_without_dpkg(self):
        with patch('subprocess.run',side_effect=AssertionError('No package-manager calls allowed')):
            self.assertTrue(core.newer('0.1.4-portable.2','0.1.4-portable.1'))
            self.assertTrue(core.newer('0.1.5-portable.1','0.1.4-portable.99'))
            self.assertFalse(core.newer('0.1.4-portable.1','0.1.4-portable.1'))
        for value in (None,True,12,'0.1.4','../x','01.1.4-portable.1','0.1.4-portable.0'):
            with self.subTest(value=value),self.assertRaises(ValueError):core.version(value)

    def test_manifest_requires_exact_identity_asset_hash_and_url(self):
        for key,value in [('schema',2),('package','firestorm'),('architecture','arm64'),
                          ('portable_version','0.1.4-portable.1'),('filename','../a.tar.xz'),
                          ('bytes',True),('sha256','X'*64)]:
            with self.subTest(key=key),self.assertRaises(ValueError):core.validate_manifest(dict(self.feed,**{key:value}),self.release)
        for key,value in [('state','new'),('size',0),('digest','sha256:'+'0'*64),
                          ('browser_download_url','https://example.com/update.tar.xz')]:
            release=copy.deepcopy(self.release);release['assets'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):core.validate_manifest(self.feed,release)
        release=copy.deepcopy(self.release);release['assets'].append(release['assets'][0])
        with self.assertRaises(ValueError):core.validate_manifest(self.feed,release)

    def test_feed_separates_debian_windows_and_portable(self):
        others=[dict(assets=[dict(name='Stellarys-Linux-Update.json')]),dict(assets=[dict(name='Windows-Setup.exe')])]
        with patch.object(core,'read_json',side_effect=[others+[self.release],self.feed]):
            self.assertEqual(core.check_release('0.1.4-portable.1')[core.VERSION_KEY],'0.1.4-portable.2')
        with patch.object(core,'read_json',side_effect=[[self.release],self.feed]):
            self.assertIsNone(core.check_release('0.1.4-portable.2'))
        with patch.object(core,'read_json',return_value=others+[dict(self.release,draft=True)]):
            self.assertIsNone(core.check_release('0.1.4-portable.1'))

    def test_download_verified_and_cached(self):
        with patch.object(core,'open_url',return_value=io.BytesIO(self.archive.read_bytes())) as opener:
            result=core.download(self.update,self.root/'downloads',self.cancelled)
            self.assertEqual(result.read_bytes(),self.archive.read_bytes())
            self.assertEqual(result.stat().st_mode&0o777,0o600)
            self.assertEqual(core.download(self.update,self.root/'downloads',self.cancelled),result)
            self.assertEqual(opener.call_count,1)

    def test_wrong_hash_size_and_cancel_never_leave_an_update(self):
        for case,data in [('hash',b'x'*self.archive.stat().st_size),('short',b'x'),('long',self.archive.read_bytes()+b'x'),('cancel',self.archive.read_bytes())]:
            event=threading.Event()
            if case=='cancel':event.set()
            cache=self.root/('bad-'+case)
            with patch.object(core,'open_url',return_value=io.BytesIO(data)),self.assertRaises(ValueError):
                core.download(self.update,cache,event)
            self.assertFalse(list(cache.iterdir()))
            self.assertEqual((self.app/'payload.txt').read_text(),'old application')

    def test_archive_refuses_traversal_links_devices_duplicates_and_permissions(self):
        cases=[('../escape','file',0o644),('/escape','file',0o644),('Other/file','file',0o644),
               ('StellarysViewer/link','symlink',0o644),('StellarysViewer/link','hardlink',0o644),
               ('StellarysViewer/pipe','fifo',0o644),('StellarysViewer/bad','file',0o4755),
               ('StellarysViewer/user_settings/data','file',0o644),('StellarysViewer','dir',0o755),
               ('StellarysViewer/dir','dir',0o644)]
        for index,(name,kind,mode) in enumerate(cases):
            target=self.root/f'unsafe-{index}.tar.xz'
            with tarfile.open(target,'w:xz') as t:
                root=tarfile.TarInfo('StellarysViewer');root.type=tarfile.DIRTYPE;root.mode=0o755;t.addfile(root)
                entry=tarfile.TarInfo(name);entry.mode=mode
                entry.type={'file':tarfile.REGTYPE,'symlink':tarfile.SYMTYPE,'hardlink':tarfile.LNKTYPE,'fifo':tarfile.FIFOTYPE,'dir':tarfile.DIRTYPE}[kind]
                if kind in ('symlink','hardlink'):entry.linkname='/tmp/escape'
                t.addfile(entry,io.BytesIO(b''))
            with self.subTest(name=name,kind=kind),self.assertRaises(ValueError):core.inspect_archive(target,'0.1.4-portable.2')

    def test_payload_checksum_failure_preserves_old_folder(self):
        (self.new/'payload.txt').write_text('bad application');self.pack()
        with self.assertRaises(ValueError):self.prepared()
        self.assertEqual((self.app/'payload.txt').read_text(),'old application')
        self.assertFalse(list(self.app.parent.glob('.stellarys-stage-*')))

    def test_real_atomic_update_retains_previous_and_preserves_profile_cache(self):
        prepared=self.prepared()
        with patch('subprocess.run',side_effect=AssertionError('No package-manager calls allowed')):
            backup=prepared.commit()
        self.assertEqual((self.app/'payload.txt').read_text(),'new application')
        self.assertEqual((backup/'payload.txt').read_text(),'old application')
        self.assertEqual(core.validate_install(self.app)[core.VERSION_KEY],'0.1.4-portable.2')
        self.assertEqual((self.profile/'settings.txt').read_text(),'private fixture setting')
        self.assertEqual((self.cache/'sentinel').read_text(),'cached fixture data')
        self.assertFalse(list(self.app.parent.glob('.stellarys-stage-*')))

    def test_failure_after_swap_rolls_back(self):
        prepared=self.prepared();rename=Path.rename
        def fail_backup(path,target):
            if 'backup-' in str(target):raise OSError('Fixture backup transfer failure')
            return rename(path,target)
        try:
            with patch.object(Path,'rename',fail_backup),self.assertRaises(OSError):prepared.commit()
            self.assertEqual((self.app/'payload.txt').read_text(),'old application')
            self.assertEqual(core.validate_install(self.app)[core.VERSION_KEY],'0.1.4-portable.1')
        finally:prepared.cleanup()
        self.assertFalse(list(self.app.parent.glob('*backup-*')))

    def test_unsupported_exchange_preserves_original(self):
        prepared=self.prepared()
        try:
            with patch.object(core,'exchange',side_effect=OSError('Unsupported filesystem')),self.assertRaises(OSError):prepared.commit()
            self.assertEqual((self.app/'payload.txt').read_text(),'old application')
        finally:prepared.cleanup()

    def test_lock_refuses_update_and_launcher_during_transaction(self):
        prepared=self.prepared();lock=core.open_lock(self.app,False)
        try:
            with self.assertRaises(core.InstallationBusy):prepared.commit()
        finally:os.close(lock)
        lock=core.open_lock(self.app,True)
        try:
            result=subprocess.run([str(self.app/'stellarys')],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('being updated',result.stderr)
        finally:os.close(lock);prepared.cleanup()

    def test_running_executable_refuses_update(self):
        shutil.copyfile('/usr/bin/sleep',self.app/'bin/stellarys-bin')
        (self.app/'bin/stellarys-bin').chmod(0o755)
        process=subprocess.Popen([str(self.app/'bin/stellarys-bin'),'30'])
        prepared=self.prepared()
        try:
            self.assertTrue(core.running(self.app))
            with self.assertRaises(core.InstallationBusy):prepared.commit()
        finally:process.terminate();process.wait();prepared.cleanup()
        self.assertEqual((self.app/'payload.txt').read_text(),'old application')

    def test_launcher_holds_shared_lock_until_child_exits(self):
        import time
        shutil.copyfile('/usr/bin/sleep',self.app/'bin/stellarys-bin')
        (self.app/'bin/stellarys-bin').chmod(0o755)
        child=subprocess.Popen([str(self.app/'stellarys'),'1'])
        try:
            deadline=time.monotonic()+3
            while not core.running(self.app) and time.monotonic()<deadline:time.sleep(.01)
            self.assertTrue(core.running(self.app))
            binary=(self.app/'bin/stellarys-bin').stat()
            for proc in Path('/proc').iterdir():
                if not proc.name.isdigit():continue
                try:
                    s=(proc/'exe').stat()
                    if (s.st_dev,s.st_ino)!=(binary.st_dev,binary.st_ino):continue
                    for fd in (proc/'fd').iterdir():
                        self.assertFalse(str(fd.readlink()).endswith('.stellarys-update.lock'))
                except (OSError,RuntimeError):continue
            with self.assertRaises(BlockingIOError):core.open_lock(self.app,True)
            self.assertEqual(child.wait(timeout=4),0)
            lock=core.open_lock(self.app,True);os.close(lock)
        finally:
            if child.poll() is None:child.terminate();child.wait()

    def test_unrelated_symlink_and_shared_folders_refused(self):
        (self.app/core.MARKER).unlink()
        with self.assertRaises(ValueError):self.prepared()
        (self.app/core.MARKER).write_text(json.dumps(core.PRODUCT))
        alias=self.app.parent/'alias';alias.symlink_to(self.app,target_is_directory=True)
        with self.assertRaises(ValueError):core.validate_install(alias)
        before=self.app.parent.stat().st_mode&0o777;self.app.parent.chmod(0o777)
        try:
            with self.assertRaises(ValueError):self.prepared()
        finally:self.app.parent.chmod(before)

    def test_cancel_disk_space_and_changed_version_are_safe(self):
        self.cancelled.set()
        with self.assertRaises(ValueError):self.prepared()
        self.cancelled.clear()
        with patch.object(core.shutil,'disk_usage',return_value=shutil._ntuple_diskusage(1,1,0)),self.assertRaises(ValueError):self.prepared()
        prepared=self.prepared()
        data=json.loads((self.app/'stellarys-version.json').read_text())
        data[core.VERSION_KEY]='0.1.4-portable.3';data['viewer_channel']='Stellarys Viewer 0.1.4 Linux Portable Preview 3'
        (self.app/'stellarys-version.json').write_text(json.dumps(data))
        try:
            with self.assertRaises(ValueError):prepared.commit()
        finally:prepared.cleanup()
        self.assertEqual((self.app/'payload.txt').read_text(),'old application')


if __name__=='__main__':unittest.main(verbosity=2)
