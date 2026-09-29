# Stellarys Viewer

Stellarys is a hobby project based on Firestorm, built for people who enjoy
Second Life photography, posing and experimenting with extra viewer features.
The idea is to keep the familiar Firestorm experience while adding useful tools
and graphics fixes as the project grows.

**Stellarys Viewer 0.1.1 — based on Firestorm 7.2.4.80712.**
The Stellarys version is separate from the Firestorm base version.

## Features

- **AMD flicker fix:** changes aimed at fixing texture and shadow flickering on
  affected meshes with AMD graphics cards.
- **Pose other avatars:** use the poser to adjust nearby avatars with their
  permission, making it easier to arrange photos and group scenes.
- **Built-in update checks:** check for releases from within the viewer and
  choose when to download and install them.
- **Separate settings and cache:** Stellarys keeps its own profile alongside
  your other viewers.

Posing another avatar requires their explicit permission. This currently works
with Stellarys and Black Dragon, including permission requests between the two
viewers. Poses are only visible in the viewer applying them and are not
synchronised with other viewers.

## Download and updates

Get the Windows x64 installer from the
[latest release](https://github.com/NekoMisa/stellarys-viewer/releases/latest).
Source archives and SHA-256 checksums are available with each release.

If Stellarys is already installed, use **Help → Check for Updates**.
Downloading and installing an update requires your approval. The installer is
unsigned and requests Windows administrator permission.

Updates preserve settings and cache. Uninstalling also preserves them by default,
with optional removal. See the
[installation notes](tools/stellarys-installer/README-Stellarys.txt) for details.

## Feedback and contributions

This is an independent hobby project. Suggestions, bug reports and contributions
are welcome through [GitHub Issues](https://github.com/NekoMisa/stellarys-viewer/issues)
and pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help.
Development and support happen as time allows.

## Building and testing

Developers can find the [Windows build instructions](doc/building_windows.md),
[local build notes](tools/kitty-prototype/BUILDING.md) and
[packaging instructions](tools/stellarys-installer/BUILDING.md) in this repository.
Build helpers need paths and external dependencies configured for your machine.

## Credits and licensing

Stellarys builds on the work of Firestorm and Linden Lab. Its poser permission
implementation also draws on Black Dragon. Original credits, copyright and
licence notices are retained.

Stellarys is not an official Firestorm or Linden Lab release and is not supported
by those teams. The root licence is [LGPL 2.1](LICENSE); individual components
may have their own licence terms. See [source provenance](SOURCE-PROVENANCE.md)
for attribution and source details.
