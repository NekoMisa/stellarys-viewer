# Building the current Stellarys Windows source

Use a separate source checkout and build work directory. Do not build into an
installed viewer or copy runtime profiles into source or staging.

Requirements: Git, Python 3.11+, autobuild, compatible CMake, Visual Studio 2022
or 2026 with MSVC v143 and a Windows SDK, Firestorm build variables, and the
third-party packages declared in autobuild.xml. The Windows configuration uses
the existing locally built FMOD 2.03.14 package; change its local archive URL to
your own licensed package when rebuilding on a different PC. Read the FMOD
licence. It is not supplied as an SDK in the source archive. The maintainer's
project is non-commercial. Havok/KDU, Velopack and crash uploading are disabled.

Example with an existing build-tool virtual environment:

```powershell
python tools/stellarys-build/build_windows.py `
  --work-dir D:/StellarysBuild `
  --tools C:/FS-AMD-Test/python-tools `
  --build-variables C:/FS-AMD-Test/variables/variables `
  --channel-variant "Windows Beta 1"
```

The helper reads Stellarys and Firestorm versions from stellarys-source.json,
selects installed v143 tools, and keeps dependencies, objects and temporary
files inside the chosen work directory. `--jobs` controls MSBuild projects;
`--compiler-jobs` controls compilation within each project. Keep their product
modest on machines also running a viewer.

`--configure-only` and `--build-only` allow incremental work. An optional
`--certificate-bundle` accepts a trusted PEM CA bundle if the build Python lacks
the required issuer certificates; TLS verification is never disabled. Missing
private API-key files must not be copied from someone else's installation.
The upstream build generates its Flickr header from the tracked template.

Keep a distinct preview channel for each source variant tested with login.
Use `--channel-variant ""` only for the final release source. Changing the channel
requires reconfiguration and rebuilding the version-bearing files.

The result is `build-windows/newview/Release/firestorm-bin.exe` plus its build
dependencies. Use the clean Stellarys packaging helper to assemble the runnable
application and installer; the executable alone is not a distributable viewer.
Review package contents, licence notices and checksums before sharing. A build
does not establish visual AMD correctness or validate live posing/photography.

Linux build and package instructions are in `../stellarys-linux/BUILDING.md`.
