# Stellarys 0.1.4 Linux portable preview 1 — validation

Base: Firestorm 7.2.4.80712. Portable version: 0.1.4-portable.1.
Compiled channel: Stellarys Viewer 0.1.4 Linux Portable Preview 1.
This is a native Linux build; WSL/Xvfb was used for local testing.

## Checks performed before publication

- Native GCC build completed successfully with the separate portable channel.
- 15 portable core/filesystem test groups and 5 portable GTK workflow groups passed.
  These cover version/feed separation, hashes, sizes, cancellation, unsafe archive
  paths/links/devices/permissions, payload corruption, ownership/markers,
  running-instance refusal, launcher lock lifetime and non-inheritance,
  real atomic exchange, retained backup, rollback and unsupported exchange.
- 12 existing Debian updater core and 5 Debian GTK regression groups passed.
- All 23756 application files and 24187 archive paths were checked against the
  clean stage, payload hashes, sizes, modes and normalized archive ownership/time.
  Packaged updater/core/launcher bytes match the corresponding source files.
- The actual compiled viewer was launched through its portable wrapper with a
  blank profile under Xvfb/Mesa software graphics and no audio. The first-run
  gate opened, Continue led to blank sign-in, and the updater verified the full
  application archive, requested normal per-PID D-Bus shutdown (exit 0), performed
  atomic replacement, retained the old app and preserved profile/cache sentinels.
  The updated launcher restarted at the original path and exited normally again.
  Network transport was replaced by a local copy of the actual final archive;
  the old version was a synthetic metadata label on the current compiled viewer.
  No account was entered. Blank sign-in screenshots were inspected.
  An initial headless attempt was cancelled; a fresh fixture completed the flow.
- Known private-marker scan: 51127 selected source/payload files, zero matches.
  Matching source archive and SHA-256 checksums generated; all source member bytes
  and archive paths/ownership/time verified. No profiles, accounts, runtime logs,
  credential files or caches are included in the clean application package.

## Not tested / limits

Native Bazzite/Fedora installation, their fresh dependency availability, GPU and
in-world behavior, voice/media, real account login, and a future public portable
version-to-version installation have not been tested. The portable build requires
Python 3.10+, GTK 3/PyGObject, gdbus and normal viewer/legacy voice runtimes.
Do not infer distribution compatibility from the WSL/software graphics check.

Ordinary failed-replacement rollback is tested. Sudden power loss and storage
failure recovery are not guaranteed or tested. The previous application is kept;
backups are not deleted automatically. Profiles/cache must stay outside the app.
Unsupported atomic-exchange filesystems and unsafe/unrelated destinations are
refused. Updates require user approval and use no root/system package manager.
Releases are unsigned; SHA-256 checks integrity, not publisher identity.

Rendering, the AMD fix, poser and photography code were not changed for portable
packaging. Previously published Windows/Debian assets and installed viewers were
not modified. No full independent security/legal audit or Linden Lab approval is
claimed. Public feed/download checks are reported separately after publication.
