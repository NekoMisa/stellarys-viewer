# Stellarys Viewer

Stellarys is a hobby project based on Firestorm, built for people who enjoy
Second Life photography, posing and experimenting with extra viewer features.
The idea is to keep the familiar Firestorm experience while adding useful tools
and graphics fixes as the project grows.

**Stellarys Viewer 0.1.7 for Windows — based on Firestorm 7.2.4.80712.**
The Stellarys version is separate from the Firestorm base version.

## What's new in 0.1.7 (Windows)

- Corrected registration for Second Life and Hop browser links in Windows.
- Consistent, version-free **Stellarys** names in the Windows link chooser.
- Clear instructions when Windows opens the general Default apps page.

Open **Preferences > Network & Files > Stellarys > Open Second Life links with
Stellarys**, then **Set up SL links**. If Windows opens its general Default apps
page, use the **file/link-type search at the top**: enter `secondlife`, choose
Stellarys, then repeat for `hop`. Choosing a default remains your decision.
See the [release notes](doc/RELEASE-NOTES-0.1.7.md).

This is a Windows-only maintenance release. Linux Debian and portable previews
remain at **0.1.6**, with their existing update feeds. Settings, cache, trusted
and blocked lists, and link-checking preferences are preserved. Experimental
link controls remain off by default. Rendering, posing and photography are unchanged.

**This software is not provided or supported by Linden Lab, the makers of Second Life.**
Read [Before installing Stellarys](DISCLOSURES.md) and the
[privacy policy](PRIVACY.md). Support is provided through GitHub Issues as time
permits; do not post passwords, private conversations or unredacted logs.

## Features

- **AMD flicker fix:** changes aimed at fixing texture and shadow flickering on
  affected meshes with AMD graphics cards.
- **Pose other avatars:** use the poser to adjust nearby avatars with their
  permission, making it easier to arrange photos and group scenes.
- **Built-in update checks:** check for releases from within the viewer and
  choose when to download and install them. Read short release highlights or
  follow the link to the full release notes.
- **Photography tools together:** the **Photo** menu gives quick access to
  snapshots, camera controls, Camera Tools, Photo Tools, the poser and avatar reset
  actions. Familiar toolbar customization remains available.
- **Complete shot presets:** save camera position, lens/blur controls, local
  lighting and image dimensions together, then restore a shot in its original
  region. See the [shot preset guide](tools/stellarys-photography/README.md).
- **Optional link controls:** local trusted/blocked domain lists with warnings or
  blocked-list-only mode; off by default and labelled Experimental.
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

## Linux

Linux packages are native x86_64 experimental builds for Ubuntu 22.04-compatible
systems such as Linux Mint. Download the .deb and matching source from
[Linux preview 1](https://github.com/NekoMisa/stellarys-viewer/releases/tag/linux-v0.1.6-preview1).
The Linux build is version 0.1.6, based on Firestorm 7.2.4.80712.
Read [Before installing](DISCLOSURES.md) and [Privacy](PRIVACY.md).
Linux installation instructions are included with that release and on the
`stellarys-linux` branch. The Linux updater selects Linux packages from this
repository and ignores Windows installers. Settings and cache survive package removal.

For Fedora/Bazzite testing, use the separate
[portable Linux preview](https://github.com/NekoMisa/stellarys-viewer/releases/tag/linux-v0.1.6-portable-preview1).
Download the application `.tar.xz`, not the source archive. Extract it into a
private folder you own and run `stellarys`. Its built-in updater verifies and
replaces portable archives without a system package manager, preserving settings
and cache and retaining the previous application. Python 3.10+, GTK 3/PyGObject,
gdbus and the normal viewer runtimes are required. Native Fedora/Bazzite testing
is still needed. See the [portable guide](https://github.com/NekoMisa/stellarys-viewer/blob/stellarys-linux/tools/stellarys-linux/README-Portable-Linux.md).

## My viewer projects

- [Stellarys Viewer](https://github.com/NekoMisa/stellarys-viewer) is a
  Firestorm-based hobby viewer with the AMD flicker fix, permission-based posing
  of other avatars and built-in update checks, with more features as it develops.
- [Black Dragon — Black Kitty Fix](https://github.com/NekoMisa/Black-Dragon---Black-Kitty-Fix)
  is a Black Dragon build focused on the AMD texture and shadow flicker fix,
  preserving Black Dragon's features and adding built-in update checks.

Both are independent hobby projects with their own settings, cache and updates.

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
