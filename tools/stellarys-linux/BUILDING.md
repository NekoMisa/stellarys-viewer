# Experimental Stellarys Linux x86_64 build

Base: Stellarys 0.1.3, Firestorm 7.2.4.80712. This first Linux preview keeps
the rendering, AMD workaround, posing and photography implementations. Linux's
D-Bus message identity is separate from Firestorm. Updates are manual.
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
  '-DVIEWER_CHANNEL=Stellarys Viewer' -DUNATTENDED=ON
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
