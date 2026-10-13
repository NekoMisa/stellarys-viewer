# Stellarys Viewer 0.1.7 — Windows release checks

Prepared 13 October 2026. Official Firestorm base: 7.2.4.80712.
This maintenance release applies to Windows only. Linux Debian and portable
previews remain at 0.1.6 with their existing feeds and artifacts.

## Checks performed

- Windows v143 release build completed successfully. The viewer was rebuilt to
  compile the 0.1.7 channel/version labels; rendering, the AMD adaptation, poser,
  photography and motion-blur source are unchanged from 0.1.6.
- 45 real disposable-registry tests passed for the production registration code:
  matching capabilities/registered names, the Default apps URI, alias migration,
  repeated registration, ownership/stale-uninstall protections, unrelated aliases,
  preservation of other commands and synthetic UserChoice, missing viewer
  rejection, existing protocol-marker preservation and missing marker creation
  without writing shared protocol defaults or commands. Owned ProgIDs carry
  version-free Stellarys application labels.
- All 25 updater validation checks and eight CMake release-identity cases passed.
- The final packaged link dialog was opened and visually inspected at the local
  Windows UI scale. Its two instruction lines fit without clipping. It was
  closed without clicking registration; no test payload was registered as a
  viewer. Other UI scales have not been checked.
- Shared production link-policy/store tests passed, including saved-list
  persistence, removed defaults, scoped GitHub entries and blocked precedence.
  The site catalogue and default modes are unchanged: 31 official Second Life
  domains, 59 Common sites entries, 38 new-profile trusted entries; master off.
- All 27 installer guard fixtures passed. Optional-data-removal fixtures verified
  scoped removal, preservation of another viewer's data, missing-profile handling
  and refusal of a nested junction. These fixtures never target real profiles.
- During a user-authorized local test, only the installed updater helper was
  replaced after a verified backup on D:. The installed viewer binary remained
  unchanged. Machine/current-user registration was refreshed using the helper.
  Windows 11 Pro build 26300 showed Stellarys in its app list and HOP chooser.
  The Second Life chooser label read Stellarys. Duplicate app entries remained.
- Both app-specific Windows Settings URI variants still opened the general
  Default apps page, including after closing and reopening Settings. The source
  dialog and guides now explain the file/link-type search fallback. This release
  does not claim to fix that Windows Settings navigation limitation.
- The user tested a browser link and reported that it opened installed Stellarys
  0.1.6 with the corrected helper. An automated browser test was stopped because
  Computer Use could not reliably identify the browser URL. Neither result is
  presented as an automated browser test of the final 0.1.7 viewer.

Final per-package VALIDATION.json records payload/hash verification, the installer
administrator manifest, default destination/directory guard wiring, explicit
uninstall inventory, clean-source selection and privacy scan counts. Matching
source and SHA-256 checksums accompany the installer. The previous public updater
is checked against release metadata and the actual installer before/after
publication. Public-download verification is recorded separately after release.

## Preserved behavior and limits

Updates retain per-user settings/cache, shot presets, trusted/blocked lists and
chosen link mode. The installer still uses its full application payload; smaller
updates are deferred. Uninstall preserves per-user data by default; explicit
removal remains opt-in. Registration does not write Windows UserChoice or choose
another viewer. Shared URL Protocol declarations remain after uninstall.

No clean Windows VM, other Windows build, cross-user/alternate-administrator test,
complete installed 0.1.6-to-0.1.7 update/uninstall cycle, final-version browser
dispatch, or renewed in-world rendering/AMD/poser/photography test was performed.
Linux was not rebuilt or tested for this Windows release. The original reporter's
confirmation is still pending. No AppImage or Flatpak package was produced.

Only selected source and clean application files are packaged. Known private
account-marker and private-key/GitHub-token pattern scans are targeted checks,
not a comprehensive security audit. No personal settings, accounts, credentials,
runtime logs, cache or screenshots of the Windows account sidebar are included.
Build logs and private test/backups remain outside release assets.

Releases remain unsigned; SHA-256 verifies integrity, not publisher identity.
No independent security/legal audit or Linden Lab approval is claimed.
