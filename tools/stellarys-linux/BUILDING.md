# Experimental Stellarys Linux x86_64 build

Base: Stellarys 0.1.8, Firestorm 7.2.4.80712. The Linux preview keeps
the rendering, AMD workaround, posing and photography implementations. Linux's
D-Bus message identity is separate from Firestorm. Debian and portable packages
have separate update feeds and installation backends, described below.
A Linux-only compiler adaptation treats directly linked OpenGL entry points as
available; the existing GL-version and binary-format checks remain in place.
Windows keeps its existing function-pointer checks. Local HTML pages use escaped
file URIs on Linux so the bundled Stellarys welcome page loads correctly.

Use Ubuntu 22.04 x86_64 and GCC/G++ 11; see `doc/building_linux.md` for the
upstream dependency list. Install Ninja, Python venv support and zstd too.
Use a Python virtual environment and install `requirements.txt`,
`cmake>=3.28,<4` and `zstandard`. The initial build used CMake 3.31.10 and
autobuild 3.10.2. Clone FirestormViewer/fs-build-variables separately and point
`AUTOBUILD_VARIABLES_FILE` at its `variables` file. The preview uses revision
`c17312d38377c003977cf5b6dcc83c6042eba194`. Set `CC=gcc-11`, `CXX=g++-11`,
`AUTOBUILD_ADDRSIZE=64` and `AUTOBUILD_BUILD_ID=80712`. Put the dependency cache
and temporary directory on the build volume using `AUTOBUILD_INSTALLABLE_CACHE`
and `TMPDIR`.

From the source root:

```sh
autobuild configure -A 64 -c Release -- \
  -DINSTALL_PROPRIETARY=OFF -DUSE_KDU=OFF -DHAVOK=OFF -DHAVOK_TPV=OFF \
  -DOPENSIM=OFF -DUSE_FMODSTUDIO=OFF -DUSE_OPENAL=ON -DUSE_TRACY=OFF \
  -DBUGSPLAT_DB= -DPACKAGE=OFF -DLL_TESTS=OFF \
  '-DSTELLARYS_CHANNEL_VARIANT=Linux Preview 1' -DUNATTENDED=ON
cmake --build build-linux-x86_64 --parallel 3
python tools/stellarys-linux/package_linux.py --output /absolute/new/output-folder
```

Use a fresh output folder. The packager uses the existing upstream Linux
application manifest, then supplies Stellarys branding, a launcher with proper
URL argument handling and an opt-in desktop setup script. It removes the
inherited Firestorm installation/automatic link-registration scripts. It strips
debug symbols only from the staged executable, retaining the original build for
debugging. Archive ownership and timestamps are normalized. Runtime profiles
must stay outside staging and source archives.

The desktop fixture test needs `desktop-file-utils`, `xdg-utils`, GLib's `gio`,
`dbus-x11` and `xvfb`. Run as a normal user:

```sh
dbus-run-session -- xvfb-run -a python tools/stellarys-linux/test_desktop.py
python tools/stellarys-linux/test_launcher.py
```

Test the compiled poser consent and shot validation fixtures as described in
their respective tools directories. A successful build and isolated startup
are not native Linux hardware or in-world validation. Keep preview labeling
until Linux volunteers have tested graphics, posing, photography, voice and media.

## Ubuntu Debian installer and updater

The Debian installer uses a clean application stage and the current compiled Linux
viewer. A small Linux-only viewer hook launches the GTK updater and provides a
per-process D-Bus request for normal logout. No rendering, posing or photography
code changes are needed for this installer/updater revision.

Install `dpkg-dev`, `desktop-file-utils`, `python3-gi`, `gir1.2-gtk-3.0`,
`policykit-1` and `xdg-utils` for packaging/testing. The package declares runtime
dependencies derived from every bundled 64-bit ELF plus explicit Python, GTK,
GStreamer, PulseAudio and amd64 multilib dependencies. Python is also a Pre-Depends
because the pre-install safety check uses it. The upstream legacy voice UUID and
IDN runtimes are bundled. No foreign architecture is enabled by maintainer scripts.

```sh
python3 tools/stellarys-linux/package_deb.py \
  --application /absolute/clean/StellarysViewer \
  --viewer-binary build-linux-x86_64/newview/firestorm-bin \
  --output /absolute/new/debian-output
python3 tools/stellarys-linux/test_updater.py
```

The input application may be staged with `package_linux.py` as above. Use a fresh
output directory; do not package an installed or previously launched application.
The packager replaces only the staged viewer binary, adds updater/integration
files, strips the staged binary and creates a clean payload manifest. The package
installs to `/opt/stellarys-viewer`, with `/usr/bin/stellarys`, a system desktop
entry/icons and an administrator-approved PolicyKit installer bridge.

`preinst` refuses an unrelated nonempty or symlink destination. `preinst` and
`prerm` check the actual executable path under `/proc` and refuse updates/removal
while an installed viewer is running. Maintainer scripts only refresh system
desktop/icon caches and never change users' MIME defaults or remove home files.
The explicit per-user `stellarys --register-links` command migrates a marked old
tar desktop entry by backing it up; it refuses unrelated entries and symlinks.

The privileged bridge copies the requesting user's regular, non-symlink installer
into a private root-owned temporary directory, rechecks SHA-256 and Debian package
identity, then invokes APT with `--no-remove`. It uses an isolated Python interpreter
and a fixed environment. The PolicyKit action requires fresh administrator approval;
there is no retained authorization or silent root service.

### Publishing Linux updates in the existing repository

For each Linux installer version, update `DEB_VERSION`, `DISPLAY_VERSION` and
`FILENAME` in `package_deb.py`. Keep the official Firestorm base and Stellarys
application version accurate. The current Debian preview is `0.1.8~linuxpreview1-1`; the tilde keeps
Debian preview versions below a future stable `0.1.8` package.

Attach the generated `.deb` and **Stellarys-Linux-Update.json** to the same GitHub
release in `NekoMisa/stellarys-viewer`, along with matching source, documentation
and SHA-256 checksums. Do not edit the manifest's hash/size by hand. Linux's feed
scans the repository's releases for this manifest, includes Linux prereleases,
ignores drafts and Windows-only releases, and selects the highest newer Debian
version. Use a prerelease for experimental Linux builds to keep the existing
Windows stable release unchanged. The Windows updater and metadata are untouched.

SHA-256 is an integrity check, not an independent publisher signature. No package
signing or APT repository is required by this design. Validate a real public
Linux update and authentication on a volunteer's desktop before claiming the
complete public update path has passed.

## Portable installer and updater

Configure with `-DSTELLARYS_CHANNEL_VARIANT=Linux Portable Preview 1` for this
release, then rebuild. The official base remains 7.2.4.80712. Keep the root
`linux_portable_version` consistent with the application version and variant.
Package only a clean, never-launched application stage:

```sh
python3 tools/stellarys-linux/package_portable.py \
  --application /absolute/clean/StellarysViewer \
  --viewer-binary build-linux-x86_64/newview/firestorm-bin \
  --output /absolute/new/portable-output
python3 tools/stellarys-linux/test_portable_updater.py
dbus-run-session -- xvfb-run -a python3 tools/stellarys-linux/test_portable_gui.py
```

The generated archive contains its portable marker and full payload inventory.
Internal staging links become regular files; archive links and special files
are refused during updates. Python 3.10+, GTK 3/PyGObject and gdbus are required.
The launcher keeps a shared lock in its parent process, without passing that
descriptor to the viewer. Updates stage and verify the whole replacement before
requesting normal logout, require all instances to close, then use an exclusive
lock and Linux renameat2(RENAME_EXCHANGE). Unsupported filesystems are refused.
The previous application is retained beside the current folder. Settings and
cache outside the application folder are preserved. No package manager or root
service is involved. See [the portable user guide](README-Portable-Linux.md).

Publish the generated archive and `Stellarys-Linux-Portable-Update.json` together
in the existing repository, with matching source/docs/checksums. Version
`0.1.8-portable.1` maps to tag `linux-v0.1.8-portable-preview1`. The portable feed
ignores Debian and Windows releases, and vice versa. Keep experimental builds
as prereleases so Windows stable remains unchanged. SHA-256 is integrity checking,
not an independent publisher signature. Native Fedora/Bazzite testing and a
future public portable version-to-version upgrade remain separate validation.
