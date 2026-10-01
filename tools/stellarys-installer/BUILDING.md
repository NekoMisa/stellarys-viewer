# Stellarys Windows packaging

The source uses MSVC v143 with Windows SDK 10.0.26100 and the existing upstream
dependency configuration. `tools/kitty-prototype/build_prototype.py` is the
historical build helper, now configured with channel `Stellarys Viewer`.
Its default short source path is `C:\FK-Poser-Test\source`; synchronize the exact
current source there before building. The folder name is historical, not the
runtime identity. Installed files use `StellarysViewer.exe`; profiles/cache use
`Stellarys_x64`. The compiled channel remains separate from the base version.

Run `package_windows.py` with the configured Python environment after building.
`STELLARYS_BUILD` selects the CMake build directory (default
`C:\FK-Poser-Test\build-vs18-v143`). `STELLARYS_WORK` selects the staging/tool
directory (default: the repository's parent). Put NSIS 3.12 under
`STELLARYS_WORK\installer\nsis-3.12`, or adapt its one tool path. Outputs go to
the sibling `outputs\Stellarys-Viewer-0.1.2` folder. Packaging invokes the
upstream manifest, adds the .NET updater, creates an explicit file manifest and
compiles NSIS. No settings are copied from a user profile.

`STELLARYS_PAYLOAD` optionally selects a separate clean application staging
folder, useful when an earlier test build is still running. Keep runtime test
profiles outside this folder.

The current upstream dependency manifest still refers to the separately built
local FMOD archive. Supply that licensed dependency and the tools documented
in the historical build notes; they are not included in the source archive.

Run `Test-InstallerGuard.ps1` with a new fixture directory and report filename.
Its process/registry adapters are mocked; filesystem checks use real fixtures.
The default production guard refuses unknown nonempty folders, links/junctions,
running viewers and a different registered machine-wide installation.

Uninstallation uses explicit packaged file paths. Profile/cache removal is a
separate, unchecked opt-in page and invokes `RemoveUserData.ps1`; its dedicated
tests never target real profiles. Silent uninstall preserves all profile data.
