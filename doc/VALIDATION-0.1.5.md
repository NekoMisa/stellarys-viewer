# Stellarys Viewer 0.1.5 â€” release checks

Firestorm base: 7.2.4.80712. Prepared on 12 October 2026.
Windows is stable; Debian and portable Linux retain separate preview channels.

## Checks performed

- Full Windows v143 and native Linux GCC 11 builds completed successfully.
  Both Linux channel variants were compiled and packaged separately.
- Shared C++17 production link policy/store tests passed on Windows and Linux.
  Checks cover strict domain parsing, block precedence, defaults-off behavior,
  blocked-list-only mode, persistence, removed defaults, selected imports,
  simultaneous/stale edits and refusal to replace invalid stored data.
- Disposable compiled Linux UI fixtures exercised Open once, trust, direct
  block, blocked notices, both text-link browser context choices, the Common
  sites picker and normal restart persistence. A local HTTP fixture verified
  that blocked/cancelled links made no request, while the explicitly permitted
  unlisted link opened without the choice prompt in blocked-list-only mode.
- Pre-login controls and list editors were inspected. The user reported that
  the private Windows test build works. This is distinct from an independent
  exhaustive logged-in chat/IM test. Private fixtures used a 0.1.4 version label;
  the public version introducing these controls is 0.1.5.
- Eight release identity/configuration tests, 25 Windows updater checks and
  64 Linux updater/portable updater/GUI tests passed.
- Windows installer administrator manifest, destination-page guard wiring,
  explicit uninstall file inventory and unchecked data-removal defaults were
  verified. All 27 installer guard fixture tests and disposable data-removal
  tests passed. These fixtures do not install the full viewer or exercise UAC.
- Final Windows payload hashes match the inventory and compiled viewer. Debian
  extraction paths, hashes, modes and internal symlinks match its inventory.
  Portable archive paths, hashes, normalized ownership/timestamps and packaged
  updater sources were checked using the shipped archive validator.
- Final packaged Linux startup checks used disposable profiles, Xvfb/Mesa
  software OpenGL and disabled audio. Both retained their compiled 0.1.5 identity
  despite a legacy channel override, stopped at the first-run disclosure before
  sign-in, and exited normally. No account or real in-world login was used.
- Known private account-marker scans of source/application files found no
  matches. GitHub token and complete private-key pattern scans found none.
  A bundled SFTP library matched an isolated key-header string; no complete
  private key was found. Profiles, credentials, runtime logs
  and cache are excluded from application/source packaging.
- Matching source snapshots and SHA-256 checksums accompany each platform.
  Per-package VALIDATION.json records the source commit and package checks.

The AMD fix, rendering, poser, photography and motion-blur code was not changed.
Domain lists live in per-user settings, outside application payloads; ordinary
updates and default uninstall preserve them. Windows' explicit settings-removal
option also removes these lists. Application replacement with a disposable
profile was tested; a real public installer upgrade retaining lists is separate.

## Not tested or claimed

- An actual installed public 0.1.4-to-0.1.5 update/uninstall cycle retaining new
  personal domain lists, cross-user Windows elevation or a clean Windows VM.
- Native Mint, Fedora or Bazzite desktop/GPU/audio/voice/media behavior in 0.1.5,
  fresh distribution dependency installation or final-build in-world rendering.
- Every skin, language, UI scale or browser route; embedded page navigation,
  redirects and parcel media are outside the link checks by design.
- Protection from every phishing/malware site or sudden power-loss recovery.
  Trusted domains and the Common sites catalogue are not safety guarantees.
- An independent legal/security audit or Linden Lab approval.

Release publication/feed integrity and download verification are recorded
separately after publication; this pre-publication record does not claim an
actual installation. Installed viewers and personal profiles were untouched.
