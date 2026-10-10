#!/usr/bin/python3
"""Stellarys Linux update window. Downloads are verified before installation."""
import os
import sys

# The viewer's bundled libraries must not affect GTK, dpkg or PolicyKit.
if any(name in os.environ for name in ('LD_LIBRARY_PATH', 'LD_PRELOAD')):
    clean = {k: v for k, v in os.environ.items() if k not in ('LD_LIBRARY_PATH', 'LD_PRELOAD')}
    os.execve('/usr/bin/python3', ['/usr/bin/python3', *sys.argv], clean)

import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import threading
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import stellarys_updater_core as core

APP = Path(__file__).resolve().parent
PORTABLE = json.loads((APP / 'stellarys-version.json').read_text()).get('install_kind') == 'portable' if (APP / 'stellarys-version.json').is_file() else False
if PORTABLE:
    import stellarys_portable_core as core
HELPER = '/usr/lib/stellarys-viewer/install-update.py'


def viewer_alive(pid):
    try:
        return Path(f'/proc/{pid}/exe').resolve(strict=True) == (APP / 'bin/stellarys-bin').resolve()
    except (OSError, RuntimeError):
        return False


class Updater(Gtk.Window):
    def __init__(self, args, installed, preferences):
        super().__init__(title='Stellarys Viewer — Updates')
        self.args, self.installed, self.preferences = args, installed, preferences
        self.update = None
        self.downloaded = None
        self.busy = False
        self.installing = False
        self.cancelled = threading.Event()
        self.set_default_size(550, 390)
        self.set_border_width(22)
        if (APP / 'Stellarys.png').exists():
            self.set_icon_from_file(str(APP / 'Stellarys.png'))
        self.connect('delete-event', self.close)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(box)
        self.heading = Gtk.Label(xalign=0)
        self.heading.set_markup('<span size="x-large" weight="bold">Stellarys updates</span>')
        box.pack_start(self.heading, False, False, 0)
        current = Gtk.Label(label='Installed: ' + installed['display_version'], xalign=0)
        current.get_style_context().add_class('dim-label')
        box.pack_start(current, False, False, 0)
        self.status = Gtk.Label(label='Checking for Linux updates…', xalign=0)
        self.status.set_line_wrap(True)
        box.pack_start(self.status, False, False, 0)
        self.changes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)
        box.pack_start(self.changes, True, True, 0)
        self.notes = Gtk.LinkButton.new_with_label(core.RELEASES, 'Full release notes ↗')
        self.notes.set_halign(Gtk.Align.START)
        box.pack_start(self.notes, False, False, 0)
        self.progress = Gtk.ProgressBar(show_text=True)
        box.pack_start(self.progress, False, False, 0)
        self.auto_install = Gtk.CheckButton(label='Close Stellarys and install after download')
        self.auto_install.set_tooltip_text('Uses normal logout, retains the previous application and preserves settings/cache.' if PORTABLE else 'Uses normal logout. Linux will ask for administrator approval.')
        box.pack_start(self.auto_install, False, False, 0)
        self.startup = Gtk.CheckButton(label='Check for updates when Stellarys starts')
        self.startup.set_active(preferences.get('check_at_startup', True))
        self.startup.connect('toggled', self.save_preference)
        box.pack_start(self.startup, False, False, 0)
        buttons = Gtk.Box(spacing=10)
        self.action = Gtk.Button(label='Download update')
        self.action.set_sensitive(False)
        self.action.get_style_context().add_class('suggested-action')
        self.action.connect('clicked', self.start_action)
        self.close_button = Gtk.Button(label='Close')
        self.close_button.connect('clicked', self.close)
        buttons.pack_end(self.close_button, False, False, 0)
        buttons.pack_end(self.action, False, False, 0)
        box.pack_end(buttons, False, False, 0)
        if not args.startup:
            self.show_all()
            self.progress.hide()
        threading.Thread(target=self.check, daemon=True).start()

    def save_preference(self, checkbox):
        self.preferences['check_at_startup'] = checkbox.get_active()
        path = self.args.profile_dir / 'user_settings/stellarys-linux-updater.json'
        temp = path.with_suffix('.new')
        try:
            with temp.open('w', encoding='utf-8') as stream:
                os.chmod(temp, 0o600)
                json.dump(self.preferences, stream)
            temp.replace(path)
        except OSError:
            self.status.set_text('Could not save the update preference.')

    def check(self):
        try:
            if self.args.preview_json:
                update = json.loads(self.args.preview_json.read_text())
            else:
                update = core.check_release(self.installed[getattr(core, 'VERSION_KEY', 'debian_version')])
            GLib.idle_add(self.checked, update, None)
        except Exception as error:
            GLib.idle_add(self.checked, None, str(error))

    def checked(self, update, error):
        if not update:
            if self.args.startup:
                Gtk.main_quit()
                return False
            self.status.set_text('Could not check for updates: ' + error if error else
                                 ('You have the latest published portable Linux release.' if PORTABLE else 'You have the latest published Linux installer.'))
            self.auto_install.set_sensitive(False)
            return False
        self.update = update
        self.heading.set_text('Stellarys ' + update['display_version'])
        self.heading.set_markup('<span size="x-large" weight="bold">' +
                               GLib.markup_escape_text(self.heading.get_text()) + '</span>')
        self.status.set_text('A Linux update is available.' if not self.args.preview_json else
                             'Window preview — downloading is disabled.')
        for text in core.highlights(update['notes']):
            label = Gtk.Label(label='•  ' + text, xalign=0)
            label.set_line_wrap(True)
            label.set_max_width_chars(65)
            self.changes.pack_start(label, False, False, 0)
        self.notes.set_uri(update['notes_url'])
        self.action.set_sensitive(not bool(self.args.preview_json))
        self.show_all()
        self.progress.hide()
        return False

    def close(self, *unused):
        if self.installing:
            return True
        self.cancelled.set()
        if PORTABLE and getattr(self, 'worker', None) and self.worker.is_alive():
            self.status.set_text('Cancelling safely…')
            self.close_button.set_sensitive(False)
            GLib.timeout_add(100, self.finish_close)
        else:
            Gtk.main_quit()
        return True

    def finish_close(self):
        if self.worker.is_alive():
            return True
        Gtk.main_quit()
        return False

    def start_action(self, button):
        if self.busy:
            return
        self.busy = True
        self.action.set_sensitive(False)
        self.auto_install.set_sensitive(False)
        self.progress.show()
        self.worker = threading.Thread(target=self.work, args=(self.auto_install.get_active(),), daemon=True)
        self.worker.start()

    def display_status(self, message):
        GLib.idle_add(self.status.set_text, message)

    def download_progress(self, value):
        GLib.idle_add(self.progress.set_fraction, value)
        GLib.idle_add(self.progress.set_text, f'{value:.0%}')

    def work(self, auto):
        prepared = None
        try:
            if self.downloaded is None:
                GLib.idle_add(self.progress.set_fraction, 0)
                self.display_status('Downloading and verifying the installer…')
                cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
                if not cache.is_absolute():
                    raise ValueError('XDG_CACHE_HOME must be an absolute path.')
                self.downloaded = core.download(self.update, cache / 'stellarys-updater',
                                                 self.cancelled, self.download_progress)
                if not auto:
                    GLib.idle_add(self.ready_to_install)
                    return
            if self.cancelled.is_set():
                return
            if PORTABLE:
                self.display_status('Preparing and verifying the portable application…')
                prepared = core.PreparedUpdate(APP, self.downloaded, self.update, self.cancelled)
            if self.cancelled.is_set():
                return
            if viewer_alive(self.args.viewer_pid):
                self.display_status('Closing Stellarys normally before installation…')
                subprocess.run(['/usr/bin/gdbus', 'call', '--session', '--dest',
                    f'org.stellarys.ViewerUpdater.p{self.args.viewer_pid}',
                    '--object-path', '/org/stellarys/ViewerAppAPI', '--method',
                    'org.stellarys.ViewerAppAPI.RequestUpdateQuit'], check=True,
                    capture_output=True, timeout=10)
                deadline = time.monotonic() + 60
                while viewer_alive(self.args.viewer_pid):
                    if self.cancelled.wait(.25):
                        return
                    if time.monotonic() > deadline:
                        raise ValueError('Stellarys is still open. Finish or cancel any save prompts, '
                                         'close the viewer, then click Install update again.')
            if self.cancelled.is_set():
                return
            self.installing = True
            GLib.idle_add(self.close_button.set_sensitive, False)
            if PORTABLE:
                self.display_status('Installing the verified portable update…')
                # The launcher holds a shared lock until its child has fully exited.
                # Give that wrapper a brief chance to finish normal shutdown.
                deadline = time.monotonic() + 3
                while True:
                    try:
                        self.backup_path = prepared.commit()
                        break
                    except core.InstallationBusy:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(.15)
            else:
                self.display_status('Waiting for administrator approval and installation…')
                result = subprocess.run(['/usr/bin/pkexec', HELPER, str(self.downloaded),
                    self.update['sha256'], self.update['debian_version']], capture_output=True,
                    text=True)
                if result.returncode:
                    detail = (result.stderr or result.stdout).strip()[-1600:]
                    raise ValueError('Installation was cancelled or failed. ' + detail)
            GLib.idle_add(self.finished)
        except Exception as error:
            GLib.idle_add(self.failed, str(error))
        finally:
            if prepared is not None:
                prepared.cleanup()
            self.installing = False

    def ready_to_install(self):
        self.busy = False
        self.status.set_text('Archive verified. Install update will close this viewer normally, retain the previous application and preserve settings/cache.' if PORTABLE else 'Installer verified. Install update will close this viewer normally and ask for administrator approval.')
        self.action.set_label('Install update')
        self.action.set_sensitive(True)
        self.progress.hide()
        return False

    def failed(self, error):
        self.busy = False
        self.installing = False
        self.close_button.set_sensitive(True)
        self.status.set_text(error)
        self.action.set_label('Install update' if self.downloaded else 'Retry download')
        self.action.set_sensitive(True)
        return False

    def finished(self):
        self.busy = False
        self.close_button.set_sensitive(True)
        self.progress.hide()
        self.status.set_text('Update installed. Previous application retained in a backup folder beside Stellarys. Your settings/cache are preserved.' if PORTABLE else 'Update installed. Open Stellarys from your application menu.')
        self.action.set_label('Open Stellarys')
        self.action.disconnect_by_func(self.start_action)
        self.action.connect('clicked', lambda button: self.launch())
        self.action.set_sensitive(True)
        return False

    def launch(self):
        subprocess.Popen([str(APP / 'stellarys') if PORTABLE else '/usr/bin/stellarys'], start_new_session=True)
        Gtk.main_quit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--startup', action='store_true')
    parser.add_argument('--manual', action='store_true')
    parser.add_argument('--viewer-pid', type=int, default=0)
    parser.add_argument('--profile-dir', type=Path, default=Path.home() / '.stellarys_x64')
    parser.add_argument('--preview-json', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit('Run the updater as your normal Linux user.')
    if not args.profile_dir.is_absolute():
        raise SystemExit('Profile directory must be absolute.')
    settings = args.profile_dir / 'user_settings'
    settings.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = (settings / 'stellarys-linux-updater.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    try:
        preferences = json.loads((settings / 'stellarys-linux-updater.json').read_text())
        if not isinstance(preferences, dict):
            preferences = {}
    except (ValueError, OSError):
        preferences = {}
    if args.startup and not preferences.get('check_at_startup', True):
        return
    installed = json.loads((APP / 'stellarys-version.json').read_text())
    window = Updater(args, installed, preferences)
    Gtk.main()


if __name__ == '__main__':
    main()
