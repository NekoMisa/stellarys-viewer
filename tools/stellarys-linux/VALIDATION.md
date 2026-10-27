# Stellarys 0.1.3 — Linux installer preview 2

Official base: Firestorm 7.2.4.80712. Debian package:
`stellarys-viewer 0.1.3~linuxpreview2-1`, amd64. This is a native Linux viewer,
not a Windows viewer running through Wine. Linux remains experimental.

## Build and application checks

- GCC/G++ 11.4 Release build completed with CMake 3.31.10 and autobuild 3.10.2,
  using Firestorm build variables `c17312d38377c003977cf5b6dcc83c6042eba194`.
  OpenAL is enabled; proprietary FMOD/Havok/KDU and AVX2 builds are disabled.
  The installer/updater revision rebuilt only the two changed Linux viewer hooks
  and relinked the viewer. Rendering, AMD changes, posing and photography code
  were not changed by this revision. Windows code and installed viewers were kept.
- The packaged viewer opened the welcome/login screen with blank account fields
  using a disposable profile, Xvfb and Mesa llvmpipe OpenGL 4.5. The welcome page
  and icon were visually inspected. A real per-process updater D-Bus request
  closed the viewer through its normal quit path, with exit code 0.
- Earlier preview checks remain applicable to unchanged logic: 26 compiled poser
  consent checks, 77 compiled shot validation checks, 13 desktop/MIME fixtures and
  11 launcher fixtures passed. Those were performed for preview 1 and were not
  needlessly repeated as evidence of new feature behavior.
- A volunteer reported that the earlier native tar preview ran and that its
  desktop entry and explicit map-link registration worked. This was not a detailed
  GPU, posing, photography, voice or media validation report.

## Installer checks performed

- APT installed the actual `.deb` in Ubuntu 22.04.5 under WSL2. Tests used
  disposable Linux users/profiles; all source, tools, build files and test state
  stayed on the D: build volume. Windows installations were not changed.
- A fresh Ubuntu 22.04 amd64 minimal chroot installed the package and its declared
  dependencies through APT, without enabling any foreign architecture. GTK Python
  imports succeeded. All bundled ELF dependencies, including the 32-bit legacy
  voice helper's direct dependencies, resolved in that clean environment.
  This does not prove working voice service, microphone or media playback.
- The actual pre-install script refused a symlink destination and an unrelated
  nonempty destination, preserving their contents. The destination marker was
  checked after installation. System desktop entry validation and all six icons
  passed. Application files use a fixed `/opt/stellarys-viewer` destination.
- With the actual installed viewer running, the pre-install check refused an
  update. Real `dpkg -i` update/reinstall and `dpkg --remove` operations were
  refused by the running-viewer guards. After normal viewer shutdown, reinstall
  and removal succeeded.
- Explicit per-user link registration selected the system desktop ID for
  `secondlife:` and `hop:`. A marked older tar-preview entry was backed up;
  unrelated entries and symlinks were refused. Installation itself did not
  create per-user entries or change users' default link handlers.
- A real privileged installer-helper invocation upgraded a disposable earlier
  Debian-version fixture to this full package. The helper refused wrong SHA-256
  and wrong-version inputs without changing the installed version. The successful
  path made a root-owned verified copy and invoked APT with `--no-remove`.
- Settings, texture-cache and downloaded-update-cache sentinel files survived
  installation, removal, upgrade and purge. Existing per-user MIME preference
  files were unchanged by package upgrade/removal. System application, desktop
  entry and PolicyKit integration were removed by uninstall/purge.
- PolicyKit loaded the shipped action and reported `auth_admin` for active and
  inactive sessions, with no implicit authorization for arbitrary sessions.
  A native desktop administrator/password prompt has not been tested.

## Updater checks performed

- Twelve core test groups passed, covering Debian version ordering, repository
  boundaries, Linux manifests and package identity, ignoring Windows-only/draft
  releases, selecting newer Linux prereleases, real fixture `.deb` validation,
  download/cache verification, SHA/size/cancellation failures, interrupted-download
  retry, root-copy ownership/symlink checks and plain release-note highlights.
- Five GTK workflow tests passed: verified download followed by explicit install;
  verified download followed by a normal per-process quit request and installation;
  bad downloads never requesting quit/install; recoverable administrator cancellation;
  and private, profile-specific startup preferences. Downloads used fixture streams
  and installer/authentication calls were simulated in these GUI workflow tests.
- The actual GTK window was rendered under Xvfb and visually checked for a version
  heading, readable bullets, full notes link and explicit installation/startup
  checkboxes. The read-only preview could not download or install.
- Normal viewer quit and the privileged APT installation bridge were also tested
  separately with real processes/packages, as described above. These separate
  checks are not a claim of a public GitHub-to-desktop automatic upgrade.

## Package hygiene

The application starts from the clean upstream application manifest. The Debian
package adds only application/updater/system integration files and bundled runtime
libraries. It excludes settings, credentials, account data, logs, caches, Git history,
debug dumps and build directories. Known private-marker source/payload scans found
zero matches across 51,108 source/payload files. Build/runtime logs and disposable test profiles remain outside the
downloadable package/source archive.

A payload manifest records file SHA-256, size, mode and symlinks. The extracted
installer passed checks against all 24,218 payload entries, including hashes,
permissions and symlinks. Package ownership and timestamps are normalized.
The clean source archive uses Git's tracked/nonignored source files. SHA256SUMS.txt
covers the installer, source, Linux update feed and accompanying documentation.

## Still needs testing

- A newer **published** Linux release downloaded and installed through the updater
  on a normal Linux desktop, including its real administrator authentication prompt.
- Native AMD/NVIDIA/Intel GPU drivers, in-world login, posing permissions, photo and
  shot restoration, voice calls, microphone/audio, media and multi-monitor behavior.
- Other Linux distributions, particularly non-Debian distributions. This `.deb`
  specifically targets Ubuntu 22.04 amd64 and compatible systems.
- Real user-cancelled editor/save prompts or slow logout during an in-world update.
  The updater uses normal quit, never forcibly kills the viewer, and installation
  still refuses while any installed viewer remains open.

No Linux flicker-fix success is claimed. SHA-256 checks detect corruption; these
unsigned packages do not have an independent publisher signature. This installer
preview is prepared locally and has not been published as a GitHub release. The
existing Windows stable release and its updater metadata remain unchanged.
