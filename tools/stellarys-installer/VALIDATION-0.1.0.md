# Stellarys 0.1.0 Windows validation — 2026-09-29

Base: Firestorm 7.2.4.80712. Stellarys release version: 0.1.0.
MSVC v143 / Windows SDK 10.0.26100, Release x64 AVX2, FMOD enabled.

Checks performed:
- Viewer compilation succeeded. The login screen was reached on an RX 7900 XTX
  with a fresh isolated profile, without logging into Second Life.
- The local Stellarys login page, title, Help commands and About version/credits
  were inspected. Separate roaming and local Stellarys_x64 directories appeared.
- Help > Check for Updates launched the bundled updater and correctly reported
  that no public Stellarys releases are available yet. Startup launch was logged.
- 17 updater core validation checks passed (metadata, versions, URL host policy,
  SHA-256 and size checks, including negative cases).
- 27 installer guard fixture checks passed. Registry/process adapters were
  mocked; directory, marker and reparse-point checks used real fixtures.
- The production installer guard refused installation while the actual separate
  test viewer was running.
- A tiny compiled NSIS fixture using the same installer/guard code and separate
  test registry/shortcut names installed, updated and uninstalled successfully.
  An unrelated file remained after uninstall. No real viewer was installed over.
- Optional profile removal was tested only against generated fixtures, including
  keeping an older prototype profile and refusing a nested junction.

Limits:
- No full live download-and-install upgrade between public releases was tested.
  A stable GitHub Release must be published before normal update distribution
  can start; newer versions need matching installer assets and SHA-256 digests.
- No clean VM, alternate-account elevation or concurrent cross-user test was run.
- This final build was not logged into Second Life. In-world posing and flicker
  behaviour still require user testing; earlier prototype user confirmation does
  not substitute for a final-build visual test.
- Existing artwork/skins and upstream credits remain. Some inherited upstream
  auxiliary services still run. Login smoke logs include an upstream defaults
  service HTTP 403 and an expired-certificate warning; login and affected
  upstream services were not tested. The Stellarys updater check itself worked.

The delivered output folder contains the extracted administrator manifest,
complete clean application payload hashes, source archive, SHA256SUMS.txt and
VALIDATION.json for artifact-specific checks performed during final packaging.
Unsigned installer; update approval and Windows administrator approval required.
Uninstall keeps data by default, with two unchecked Stellarys-only removal options.
