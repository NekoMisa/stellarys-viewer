# Stellarys Viewer 0.1.6 — release checks

Prepared 13 October 2026. Firestorm base: 7.2.4.80712. Windows stable,
Debian Linux preview 1 and portable Linux preview 1 remain separate channels.
There is no AppImage or Flatpak package in this release.

## Checks performed

- Windows v143 and native GCC 11 release builds, with separately compiled Debian
  and portable Linux identities. Per-package VALIDATION.json records the final
  channel and startup checks; installed viewers and personal profiles were untouched.
- Shared production C++17 policy/store tests on both platforms, including exact
  domains, all six Marketplace language parameters, GitHub account/repository
  boundaries, HTTPS/port restrictions, encoded/dot-segment paths and lookalikes.
  The catalogue contains 31 official Second Life domains, 59 optional entries
  and 38 new-profile trusted entries. Master enable remains off by default.
- Persistence tests read a legacy version-1 list without byte changes or new
  defaults. Personal entries and blocks survived. Scoped imports did not remove
  a GitHub block; after explicit block removal they retained other entries and
  wrote format 2. Domain blocks removed scoped trust; removing a block did not
  resurrect trust. Invalid/future/oversized files, stale edits, locking, failed
  saves and explicit selected imports were exercised.
- Private compiled Linux UI checks inspected the manager and picker, removed
  and explicitly reimported NekoMisa's GitHub scope, verified saved defaults and
  exited normally. No account or external test link was used. These private
  checks carried a 0.1.5 label; see the separate private validation record.
- Correct automatic native window titles are checked against the final compiled
  Linux channel despite a legacy channel override. Packaged first-run disclosure
  checks use disposable profiles, Xvfb/Mesa software OpenGL and disabled audio;
  sign-in is blocked until acknowledgment, and Exit returns status 0. These are
  not native desktop or in-world tests.
- Windows executable resource description and product name are `Stellarys`;
  numeric file/product versions retain the official base. All 30 disposable
  registry fixture checks passed, including replacing a legacy display label,
  stable identifiers, ownership protections and preservation of other defaults.
  Translated About headers use the runtime channel; changed XML was parsed.
  The final portable English About page was also visually inspected and showed
  Stellarys 0.1.6 with the unchanged Firestorm base; its blank-profile test exited 0.
- Eight release identity cases, 25 Windows updater checks, 27 installer guard
  fixtures and disposable optional-data-removal checks passed. Final installer
  administrator manifest, destination guard wiring, explicit uninstall inventory
  and unchecked data-removal defaults are verified. These fixtures do not install
  the full viewer or exercise a live UAC/Windows chooser dialog.
- Final payload inventories, hashes, metadata, source policy documents and update
  feed hash/size are verified. Debian extraction additionally checks modes and
  internal symlinks; portable verification uses the shipped archive validator.
  Source snapshots are checked against their selected Git source files.
- Known private account-marker scans and complete private-key/GitHub-token
  pattern scans report counts only. No personal profiles, settings, accounts,
  credentials, runtime logs or cache are packaged. These are targeted scans and
  controlled application/source selection, not a comprehensive security audit.

Linux updater core code is unchanged from 0.1.5, where its 64 core/portable/GUI
tests passed. Public 0.1.6 feed selection and anonymous package-download checks
are performed after publication and recorded separately; this pre-publication
document does not claim an actual installation cycle.

Rendering, AMD fix, poser, photography and motion-blur code were not changed.
Normal updates retain per-user settings/cache/lists. Existing lists are not
merged with new defaults. Explicit GitHub scopes use format 2; older 0.1.5
readers leave it intact and refuse checked links rather than resetting data.
Keep a backup before any downgrade of a profile containing scoped entries.

## Not tested or claimed

- A full installed public 0.1.5-to-0.1.6 update/uninstall/downgrade cycle carrying
  personal lists, a clean Windows VM or cross-user/alternate-account elevation.
- The actual installed Windows app chooser after refreshing its cached label,
  every translated About page/skin/UI scale or native Linux desktop integration.
- Native Mint/Fedora/Bazzite GPU, audio, voice/media, in-world rendering/posing/
  photography, or fresh distribution dependency installation in these packages.
- Redirect destinations, embedded browser pages, parcel media, all network
  traffic, universal phishing/malware protection or sudden power-loss durability.
- An independent legal/security audit or Linden Lab approval. Releases are unsigned;
  SHA-256 confirms integrity, not publisher identity.
