# Stellarys Viewer 0.1.4 — Linux portable preview 1

Based on Firestorm 7.2.4.80712. Independent non-commercial hobby project.
This software is not provided or supported by Linden Lab, the makers of Second Life.
It is also unsupported by the Firestorm team.

## Changes

- Native portable Linux application for Fedora/Bazzite volunteer testing.
- Built-in portable updates: verified downloads, normal shutdown and application replacement.
- Keeps settings/cache and retains the previous application for recovery.
- Separate portable feed; Windows and Debian updates are unchanged.

Rendering, the AMD workaround, poser and photography features are unchanged.
This is an experimental packaging/updater revision, not a new rendering version.

## Download and run

Download **Stellarys-Viewer-0.1.4-Linux-x86_64-portable-preview1.tar.xz**.
Extract the complete folder into a private, writable location you own, such as
`~/Applications/StellarysViewer`, and run **stellarys**. The Source archive is
developer code, not a runnable application. Do not use sudo or run the binary
directly. Python 3.10+, GTK 3/PyGObject, gdbus, normal audio/desktop runtimes and
OpenGL drivers are required; legacy voice may need 32-bit runtimes.

**Help > Check for Updates** will offer future portable releases. Download and
installation require approval. You can choose normal viewer shutdown followed
by installation after download. All instances must close; save prompts still
apply. Unsupported filesystems and unsafe/unrelated destinations are refused.
An old application backup is retained beside the stable application folder;
settings/cache outside that folder are preserved. Releases are unsigned.

Read the attached **README-Portable-Linux.txt**, **VALIDATION.md**,
[project disclosures](https://github.com/NekoMisa/stellarys-viewer/blob/stellarys-linux/DISCLOSURES.md)
and [privacy policy](https://github.com/NekoMisa/stellarys-viewer/blob/stellarys-linux/PRIVACY.md).
Report bugs through GitHub Issues without account details or private logs.

## Test scope

Compiled startup and a complete local-archive update/restart workflow were tested
in WSL/Xvfb with software graphics and a blank profile. Older-version selection
used synthetic installed metadata, not a previously released portable build.
Native Fedora/Bazzite graphics, login, voice/media and a future public
portable version-to-version upgrade have not been tested. Volunteers should
report their distribution/version and GPU along with the result.
