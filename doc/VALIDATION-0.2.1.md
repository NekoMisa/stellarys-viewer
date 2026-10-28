# Stellarys 0.2.1 Windows validation

This hotfix retains the Firestorm 7.2.5.81788 base and the existing rendering, posing and photography implementation.

## Skin checks

The maintainer confirmed the private group profile layout looked correct. Subsequent minimap and own-chat colour changes were installed in the private test files; no separate explicit visual sign-off for those final changes is claimed.

Static checks verify all 15 radar/minimap avatar colour roles against the resolved Firestorm palette, including green other avatars and yellow friends. UserChatColor is white, matching Firestorm. The complete group panel layout matches Firestorm, with Midnight’s shared background and controls. Explicit saved user/contact-set customisations are preserved.

## Installer checks

39 guard fixture tests passed, including the exact root ReShade file-link exception, case-insensitive matching, refusal of nested links, refusal of links replacing packaged executables, and refusal of a real directory junction named opengl32.dll. Registry and process checks use mocks; files are confined to disposable fixtures.

The root opengl32.dll is never packaged. The installer file planner checks only packaged paths, and uninstall deletes its explicit application inventory, preserving the extra DLL. A packaging assertion prevents accidentally claiming that file in a future build. Other reparse points include their exact path/attributes in refusal messages.

Creating a real file symlink in the local non-administrator test process was refused by Windows. Consequently a real ReShade file-link upgrade/uninstall and the reporter’s PC are not tested here; no workaround was applied to their machine. Predicate fixtures and a real directory junction are distinct from such an end-to-end test.

Final native build, regression tests, source/payload privacy scans, installer manifest inspection and source/archive integrity checks are recorded with release assembly. A successful build/static check does not establish a successful interactive installation. No real installed viewers, user profiles or Windows protocol defaults are modified during preparation. Linux is not built or tested as part of this Windows hotfix.

The current Windows custom regression suite passed: camera paths, shot presets, poser consent, link policy, 32 updater validation checks, 45 link-registration fixtures and graceful shutdown IPC. The updater’s future-version test data was advanced independently of the production version.

The native Windows 0.2.1 build passed with the exact versioned channel and unchanged numeric upstream base. All 10 release identity cases and 52 experimental-channel/version/feed/profile checks passed. All 39 file-planning/security tests passed, including preservation of an extra wrapper file during normal and repair planning; these are not a real ReShade installation test.
