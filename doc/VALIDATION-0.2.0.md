# Stellarys 0.2.0 Windows validation

Stable Windows release retaining Firestorm 7.2.5.81788 as the separate upstream
base. Linux packaging and runtime checks are separate work.

## User testing

The maintainer tested the private Midnight skin and confirmed the softer blue
unread IM highlights after restarting the private viewer. Received Items colours
and distinct folder icons were checked visually. Existing Firestorm and StarLight
skins remain selectable. This is not exhaustive coverage of every panel or scale.

Earlier 0.1.9 beta testing confirmed the AMD mesh, media/sound and voice, general
feature operation, clothing layer reordering, and an apparent fix for the
reproduced mirror patches on the RX 7900 XTX. These are inherited test results,
not fresh exhaustive tests of every feature in the final 0.2.0 executable.

## Automated checks

The Windows regression run during release preparation passed the camera-path,
shot-preset, poser-consent, link-policy and graceful-shutdown suites, 32 updater
validation checks and 45 link-registration fixture checks. These fixtures do not
modify actual Windows associations, user profiles or logged-in sessions.

Inherited Beta 2 tests passed 73,810 numeric layer moves, 147,620 drag placements
and 1,414 guarded mirror shader draws. They establish the tested ordering and
sampling behaviour, not universal hardware compatibility.

The skin preserves complete widget definitions, fonts and control geometry.
Original skin assets remain available. Local login/teleport tips replace the
previous promotional messages without adding a remote advertising service.

## Release checks and limits

Final native build, identity, payload/source privacy scans, installer manifest
inspection and artifact checksums are recorded with the assembled release.
Only completed checks are claimed in that record. Compilation and static
inspection do not establish a successful installation, upgrade or uninstall.
No new interactive installation on the maintainer's normal installation is
claimed. Existing installations, settings and protocol defaults are untouched
while preparing release files. Authentication is always performed by the user.

This release does not claim Linden Lab approval or directory listing. About,
licences, source provenance, disclosures and privacy information are retained.

## Completed 0.2.0 build and source checks

- Native MSVC v143 build completed with channel `Stellarys Viewer 0.2.0`; the numeric upstream version remains `7.2.5.81788`.
- All 10 CMake release-identity cases and 52 experimental-channel/version/feed/profile checks passed for the updated source.
- Source privacy scan: 28,202 selected files, zero private-marker matches and zero credential-pattern matches.
- Midnight XML, colour/texture references, complete widget definitions and control geometry passed validation against the clean staged application. 13835 existing skin files match their prior SHA-256 values.
- The staged application matches the final Midnight skin sources. No Linux runtime test or final 0.2.0 interactive installer test is implied.
