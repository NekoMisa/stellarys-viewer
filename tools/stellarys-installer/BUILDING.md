# Stellarys Windows packaging

Use the [current Windows build helper and guide](../stellarys-build/README.md)
with MSVC v143 and a Windows SDK. Keep the source, build work and application
staging separate from installed viewers and runtime profiles. Installed files
use `StellarysViewer.exe`; profiles/cache use `Stellarys_x64`. The compiled
Stellarys channel remains separate from the official Firestorm numeric base.

Run `package_windows.py` with the configured Python environment after building.
`STELLARYS_BUILD` selects the CMake build directory (default
`C:\FK-Poser-Test\build-vs18-v143`). `STELLARYS_WORK` selects the staging/tool
directory (default: the repository's parent). Put NSIS 3.12 under
`STELLARYS_WORK\installer\nsis-3.12`, or adapt its one tool path. Outputs go to
the sibling `outputs\Stellarys-Viewer-VERSION` folder. Packaging invokes the
upstream manifest, adds the .NET updater and native Explorer link-setup helper, creates an explicit file manifest and
compiles NSIS. No settings are copied from a user profile.

`STELLARYS_PAYLOAD` optionally selects a separate clean application staging
folder, useful when an earlier test build is still running. Keep runtime test
profiles outside this folder.
`STELLARYS_OUTPUT` can place the complete output directory on a different drive.

For Windows experimental builds, `windows_beta` must be positive and
`windows_update_channel` must be `experimental` in `stellarys-source.json`.
Match `Release.Current` and `Release.CurrentBeta` in the updater. Compile with
`--channel-variant "Windows Beta N"`. Packaging checks the exact channel and
updater identity, and uses `VERSION-beta.N` in the installer filename, marker
and uninstall display version. The final release uses beta zero, channel
`stable`, and no variant. Stable and beta installers use the same installation
ownership and profile rules; the updater never downgrades automatically.

## File-preserving Windows installation

`InstallerFiles.cs` is compiled into an embedded setup helper, not installed as
an application file. The generated manifest and `StellarysFile` macro calls use
the same sorted order. The helper emits one ASCII decision byte per packaged
file: `1` keeps an identical file, `0` installs it. Missing/corrupt files are
replaced. Setup checks the decision count and verifies all packaged files after
copying, before completing registration. It does not use timestamps as proof
of matching content and does not prune unrelated files.

NSIS uses separate LZMA blocks rather than `/SOLID`, so skipping a File command
does not require extracting the whole compressed payload. The complete installer
still contains every file. Full reinstall / repair forces all decisions to `0`;
`/REPAIR` preselects that checkbox. `/D` remains the final command-line argument.
Both modes retain the same ownership/process guards and per-user data policy.

Compile `InstallerFilesTests.cs` with `InstallerFiles.cs`, target exe,
`/main:InstallerFilesTests`, and `System.Web.Extensions.dll`. Supply a new
disposable fixture directory. Test actual `InstallFiles.nsh` extraction and
failure behavior using a separate user-level NSIS harness that has no registry,
shortcut or real profile actions. Report that distinctly from production
administrator installation and uninstall testing.

The current upstream dependency manifest still refers to the separately built
local FMOD archive. Supply that licensed dependency and the tools documented
in the historical build notes; they are not included in the source archive.

The release channel is generated from `stellarys-source.json`; never reuse a
version/variant for different source releases. Run `test_release_identity.py`
with the configured CMake executable. `package_windows.py` refuses a mismatched
compiled channel. If PRIVACY.md or DISCLOSURES.md changes, run
`update_disclosures.py` to regenerate the checked-in offline first-run text and
HTML. Setup includes both documents before installation. The first-run gate also
applies to automatic sign-in and is separate from Second Life's ToS acceptance.

Run `Test-InstallerGuard.ps1` with a new fixture directory and report filename.
Its process/registry adapters are mocked; filesystem checks use real fixtures.
The default production guard refuses unknown nonempty folders, links/junctions,
running viewers and a different registered machine-wide installation.

Uninstallation uses explicit packaged file paths. Profile/cache removal is a
separate, unchecked opt-in page and invokes `RemoveUserData.ps1`; its dedicated
tests never target real profiles. Silent uninstall preserves all profile data.
