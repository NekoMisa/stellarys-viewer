# Windows updates and application repair

The updater downloads the complete verified installer. Normal installation
compares packaged files by length and SHA-256 and replaces only missing or
different application files. Identical files keep their contents and timestamps.
This works when the existing 0.1.7 updater starts the 0.1.8 installer too.

**Full reinstall / repair** in Setup replaces every packaged application file.
The updater can request it with `/REPAIR` (before the final `/D=...` argument).
It can repair the same published version; older releases remain disallowed.
Installer bookkeeping, shortcuts and uninstall registration are refreshed in
both modes. Repair neither purges unrelated extra files nor resets the profile.

Settings, saved sign-ins, shots, camera paths, poses, trusted/blocked lists and
cache stay outside the application. No update or repair action removes them.
Optional data removal remains a separate unchecked uninstaller choice.

Setup retains destination/marker, reparse-point, running-process and registry
ownership checks. An embedded manifest drives file selection; setup checks the
completed application against it before reporting success. File planning also
rejects hard-linked application files. A failed verification requires retry or
repair; this is not a transactional rollback implementation.

Downloads are not smaller. Linux keeps its existing package/portable updater
mechanisms. Installer file logic is documented in
`../stellarys-installer/BUILDING.md`; report actual installed-upgrade testing
separately from fixture, manifest and verification tests.
