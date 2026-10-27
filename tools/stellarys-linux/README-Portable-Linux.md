# Stellarys Viewer 0.1.9 — Linux portable preview 1

Based on Firestorm 7.2.5.81788. Experimental native x86_64 Linux application.
This software is not provided or supported by Linden Lab, the makers of Second Life.
Stellarys is an independent non-commercial hobby project, also unsupported by
the Firestorm team. Read the bundled DISCLOSURES.md and PRIVACY.md before use.
Support: https://github.com/NekoMisa/stellarys-viewer/issues, as time permits.
Never post credentials, private conversations or unredacted logs.

## Which download?

Use **Stellarys-Viewer-0.1.9-Linux-x86_64-portable-preview1.tar.xz** to run it.
The **Source.tar.xz** download contains developer source code, not a runnable app.
This portable build does not use .deb, APT, RPM, root privileges or a system
installation. It is intended for Bazzite/Fedora volunteer testing, and also runs
on compatible Ubuntu-based desktops. Bazzite/Fedora hardware is not yet validated.
It does not make the .deb updater compatible with those distributions.

## Install and launch

1. Download the portable application archive and extract the entire folder using
   your file manager. Keep it in a stable folder you own, for example
   `~/Applications/StellarysViewer`. Avoid shared writable folders and removable
   filesystems that cannot atomically exchange directories. Do not use sudo/root.
2. Inside that folder, run **stellarys**. Your file manager may ask you to choose
   **Run/Execute**, or to allow executable files in its preferences. Keep every
   file together; do not run `bin/stellarys-bin` directly.
3. Read the first-run project/privacy information, then sign in normally.

If your file manager opens the launcher as text, open a terminal in the extracted
folder and run `./stellarys` once. Optional application-menu shortcut:
`./install-desktop.py`. Optional Second Life/Hop links:
`./install-desktop.py --register-links` (there is a space before the option).
Shortcuts point to this folder; moving it requires running desktop setup again.

The system needs Python 3.10 or newer, GTK 3/Python GObject bindings for the update
window, `gdbus` for normal viewer shutdown, standard desktop/audio libraries and
working OpenGL drivers. These are system runtime dependencies, not another viewer.
On conventional Fedora, GTK bindings are normally provided by `python3-gobject`
and `gtk3`. Bazzite's image provides its system packages; do not use Ubuntu's APT
commands there. Report missing dependency names and OS/GPU details for testing.
The inherited voice helper is 32-bit and may need compatible system runtimes;
voice/media and native graphics still require volunteer testing.

## Updates

Use **Help > Check for Updates**. The portable updater selects only portable Linux
archives from the Stellarys GitHub repository; Windows and .deb packages are ignored.
Startup checking can be disabled. Nothing is downloaded/installed without approval.

Click **Download update**, then **Install update** after verification. Alternatively,
select **Close Stellarys and install after download** before downloading. This uses
normal logout and saving; finish any unsaved-edit prompts. Close every instance of
this portable installation before installing. The updater never force-kills viewers.

The archive and complete payload are verified before replacing the application.
Replacement uses a per-user lock and an atomic directory exchange. The previous
application is retained in a `StellarysViewer-backup-*` folder beside the current
folder. Ordinary replacement failures restore the original application. Unsupported
filesystems, unrelated folders, unsafe links and running instances are refused.
No administrator approval or system package manager is used. The application path
stays the same, so its existing desktop shortcut keeps working.

Settings/cache stay in their separate per-user locations, normally
`~/.stellarys_x64`, or the custom locations you selected. Do not put personal data
inside the application folder. Once a new version works, you can remove an old
application backup through the file manager. Backups are not deleted automatically.
If you need manual recovery, close Stellarys and rename/move the retained previous
application back to the original application path. Never overwrite/delete profiles
as part of this process. Releases are unsigned; SHA-256 verifies integrity, not an
independent publisher identity.

## Remove

Close Stellarys and delete its extracted application folder and any application
backups you no longer need. This preserves settings/cache. You may also remove the
Stellarys shortcut in `~/.local/share/applications`, and select another link handler
if you registered Stellarys. Profile removal is separate and manual; other viewers'
profiles are untouched. See the matching validation notes for checks actually run.
