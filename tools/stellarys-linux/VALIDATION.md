# Stellarys Viewer 0.1.3 — Linux x86_64 experimental preview 1

Based on Firestorm 7.2.4.80712 and the published Stellarys v0.1.3 source tree
(`15dad3659af5c8d152787e6da3462a573efa84c8`). This is a native Linux build,
not a Windows viewer running through Wine. Ubuntu 22.04.5 under WSL2 was the
build/test environment; installations, source, tools and artifacts were kept
on D:. Installed Windows viewers were not modified.

## Checks performed

- GCC/G++ 11.4.0 Release build completed, using CMake 3.31.10 and autobuild 3.10.2.
  Firestorm build variables revision: `c17312d38377c003977cf5b6dcc83c6042eba194`.
  OpenAL enabled; FMOD, Havok/KDU proprietary components and AVX2 build disabled.
- The staged package and a fresh extraction of the actual application archive
  both opened the Stellarys login screen and exited with code 0 after 45 seconds.
  The welcome page, approved icon and blank login controls were visually checked.
  Tests used Xvfb and Mesa llvmpipe OpenGL 4.5, with disposable profiles and no
  account login. This is software rendering, not native GPU validation.
- Compiled fixtures: 26 poser consent checks and 77 shared shot-validation checks
  passed. These verify logic; they do not establish in-world feature behavior.
- 13 isolated desktop-entry/MIME checks passed through desktop-file-validate,
  real GIO launches and xdg-mime. Existing link defaults were preserved unless
  registration was explicitly requested. An unrelated desktop entry was refused.
- 11 launcher checks passed for map URLs, spaces/special characters in application
  paths, existing argument handling and propagation of the viewer exit status.
- All 33 bundled ELF executables/libraries resolved their dynamic dependencies in
  this Ubuntu environment. This includes CEF, the media plugins and native voice
  helper. The older libidn.so.11 needed by Vivox comes from the upstream bundle.
- Application staging is collected from the upstream manifest, with a SHA-256
  payload manifest. Runtime settings, logs, caches, sign-ins and credentials are
  excluded. Known private-marker scans covered 51,075 source/payload files and
  returned zero matches. Build/runtime logs and test profiles are kept privately
  outside the application/source archives.
- Archive ownership and timestamps are normalized. The source archive uses Git's
  tracked/nonignored file list and excludes Git history, build output and profiles.
  SHA256SUMS.txt covers the downloadable application, source and companion files.

## Linux adaptations

The existing renderer, AMD patch, poser and photography implementations are
retained. A Linux-only compiler adjustment handles directly linked GL symbols,
while retaining the GL-version and program-binary-format checks. A Linux-only
file-URI adjustment lets CEF open local HTML pages correctly. Windows behavior
is unchanged by both conditional adjustments.

Linux uses its own org.stellarys D-Bus identity and desktop entry. Desktop setup
is per-user and optional; the launcher does not change default link handlers.
Settings/cache remain separate under ~/.stellarys_x64. This preview uses manual
archive updates; Help > Check for Updates opens GitHub releases. No Linux
automatic replacement/install workflow has been implemented yet.

## Not tested

Native Linux AMD/NVIDIA/Intel GPU drivers, in-world login, texture/shadow flicker,
posing permissions between live viewers, photography/shot restoration in-world,
voice calls, microphone/audio playback, streaming media, multiple-monitor desktop
behavior and distributions other than this Ubuntu environment need volunteers.
No Linux flicker-fix success is claimed. The software-only startup logged CEF GPU
fallback/background-service warnings; the local page rendered successfully.

The legacy 32-bit voice helper and optional inherited Wine voice-proxy settings
are retained. Wine is not required to run the viewer or its default native helper;
working voice service compatibility has not been established by these checks.

This preview is prepared locally for testing. It has not been published as a
GitHub release and does not replace the existing Windows release.
