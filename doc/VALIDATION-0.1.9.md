# Stellarys 0.1.9 Beta 2 validation

Windows experimental release based on Firestorm **7.2.5.81788**
(`4ac201fdc56127de27de34567286885f4e75d194`). This is not a stable promotion
or a Linux release. The official numeric base version is retained separately.

## User tests

- The maintainer reported that the private Edit Outfit layer controls worked.
  This is general in-world confirmation, not a separate sign-off for every
  edge case, same-asset copy or save/relog persistence scenario.
- The maintainer reproduced coloured patches with Mirrors on, confirmed that
  disabling Mirrors removed them and re-enabling brought them back, and reported
  that the isolated guarded shader appeared to fix the issue in the test scene.
  Hardware: AMD Radeon RX 7900 XTX. This does not establish a universal GPU fix.
- In Beta 1 testing, the maintainer confirmed the affected AMD mesh, media/sound
  and voice worked and gave positive general feature feedback. Those results
  remain distinct from exhaustive poser, photography or driver coverage.

## Automated checks

- Layer-order C++17 tests run with MSVC v143, `/W4 /WX` and assertions enabled:
  **73,810 numeric moves and 147,620 drag placements**, including invalid bounds,
  no-op positions and stable ordering of unaffected items, passed.
- Native OpenGL regression tests extract the actual mirror sampling function,
  deliberately poison unused mip levels with extreme colours or NaNs, and check
  seven mip counts and 101 gloss values. All **1,414 guarded draws** passed on
  the RX 7900 XTX; the original function gave 738 mismatches in comparison draws.
  This demonstrates the sampling guard, not the real scene's GPU memory contents.
- Both modified/new Edit Outfit XML files parse, have unique control names and
  match their C++ menu/floater wiring. Source whitespace checks passed.
- The separate mirror test reached the login screen with no shader compilation
  error patterns in its startup log. Test profiles and cache were isolated.

## Release checks

- Native MSVC v143 Windows build completed with the exact channel
  `Stellarys Viewer 0.1.9 Windows Beta 2`; numeric viewer version remains
  `7.2.5.81788`. The staged executable and feature assets match the build/source.
- All 10 CMake identity cases, 52 experimental updater checks, 32 updater
  validation checks and 45 link-registration fixture checks passed. The existing
  camera path, shot preset, poser consent, link policy and shutdown suites passed.
  Fixture tests left real profiles, associations and user sessions untouched.
- All 28,142 selected source files passed the private-marker scan. The clean
  application inventory contains 24,524 files, each verified by size and SHA-256;
  its private-marker scan also found zero matches.
- Eighteen existing feature, AMD shader, installer and updater implementation
  files were verified unchanged from Beta 1.

Installer manifest/version inspection, final source ZIP inventory and checksums
are appended to the release's attached VALIDATION.md after artifact assembly.
No successful installation or uninstall test is implied by compilation, static
checks or manifest inspection.

## Limits and preserved behavior

- No Linux build or Linux runtime validation of these Beta 2 additions is claimed.
- No new interactive Beta 2 installer/update/uninstall test on the maintainer's
  real installation is claimed. Installed applications, real profiles and
  protocol defaults remain untouched during release preparation.
- Installer ownership/process guards, per-user data preservation/removal,
  file comparison and link registration implementations are unchanged from Beta 1.
- The AMD avatar shader, posing consent, photography, motion blur and existing
  updater channel behavior are preserved; the beta number advances to 2.
- No exhaustive drag scrolling/cancellation, stale dialog, duplicate-asset,
  outfit persistence or cross-driver reflection compatibility claim is made.
- No actual Beta 1-to-Beta 2 user download/install cycle is claimed merely by
  checking the published update feed. Any such test must be reported separately.

Private screenshots, profiles, credentials, account identifiers and runtime logs
are excluded from source/application release staging. Privacy scan results are
reported as aggregate counts; they are not a malware or antivirus certification.
