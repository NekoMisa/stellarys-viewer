# Stellarys 0.1.8 validation

Status: unpublished release candidate. A real Windows 0.1.7-to-0.1.8 upgrade
passed on the maintainer's PC on 20 October 2026. The Firestorm numeric base
remains 7.2.4.80712.

## Windows viewer and camera

- MSVC v143 / Visual Studio 2026 release build completed successfully.
- Standalone tests passed: 7,293 camera interpolation/countdown checks and
  77 existing shot validation checks.
- The maintainer reported successful in-world playback and saved-path
  persistence after restarting the private Windows preview.
- Disposable logged-out UI tests checked invalid-file preservation, valid
  collection loading, cut fields, repeat/countdown persistence and refusal to
  overwrite a collection changed by another process.
- Eight release-channel generation/refusal cases passed. The final packager
  requires the compiled channel to match Stellarys Viewer 0.1.8.

The maintainer's playback report is distinct from automated tests. Every camera
mode, region/restriction edge case and rendering/poser scenario has not been
independently exercised in-world.

## Windows installation and repair

- 36 file-helper checks passed, including content comparison, same-size changed
  files, missing files, repair, protected paths, duplicate entries, locked files
  and hard-link refusal.
- An actual user-level NSIS fixture reused the production file-copy functions
  and macros. Normal mode replaced two changed/missing files and kept one
  identical file with its old timestamp. Repeating normal mode replaced zero;
  repair replaced all three. Fresh installation also passed.
- The fixture refused a bad destination before copying, detected deliberately
  corrupted post-copy content, and retained four synthetic profile sentinels.
- All 27 installer ownership/process/registry guard fixture checks passed.
  Process/registry adapters were mocked; filesystem checks used real fixtures.
- Optional-data-removal tests passed against disposable profiles, including
  unrelated-profile and junction protection. No real user data was removed.
- The final full application manifest contains 23,806 files. A read-only plan
  against both a clean 0.1.7 payload and the installed 0.1.7 application kept
  23,784 identical files and selected 22 for installation. About 660 MB of
  identical application data can remain in place. All candidate payload hashes
  were verified. This does not measure a full production upgrade's duration.
- The updater passed 32 core checks, including same-version repair, downgrade
  refusal and the ordering of /REPAIR before the final /D argument.
- The updater's repair option and the reused installation-options page were
  visually checked in non-installing previews. Downloads and installation were
  disabled in the updater preview. The Setup preview confirmed /REPAIR selected
  the checkbox. Those UI previews did not perform installation.

The complete installer is still downloaded. Normal mode hashes files before
choosing which to copy and verifies the completed application. Repair replaces
all packaged application files. Neither mode removes unrelated extra files or
resets the profile. Failed verification requires retry/repair; transactional
rollback is not implemented.

The final 225,915,278-byte unsigned installer passed administrator-manifest
extraction and full payload verification. Unchanged public 0.1.7 updater code
accepted synthetic 0.1.8 release metadata, its five highlights, and the actual
installer's size/SHA-256 offline. This did not test a public download.

On 20 October 2026 the maintainer completed an administrator upgrade of the
existing marked installation in normal mode, after a private settings backup.
All 23,806 installed files matched the candidate manifest; the 23,784 previously
identical files retained their pre-upgrade timestamps. Windows' machine-wide
uninstall entry records 0.1.8. All 141 backed-up profile files were byte-identical
after installation while the viewer remained closed; no private names or content
are included in the reports. Cache contents were not independently compared.

A real full-repair run, production uninstall, clean Windows VM, alternate
administrator, cross-user elevation and public-feed Windows upgrade remain
untested for this candidate. Repair/repeat-update behavior passed the actual
small NSIS fixtures described above.

## Linux

The Debian and portable channels are native Linux x86_64 builds, prepared in a
D-backed Ubuntu 22.04 WSL environment. The camera/shot standalone tests passed
under GCC 11. The Linux updater/desktop/GUI suite passed 37 tests plus 11 launcher
checks using disposable fixtures. The combined test discovery was corrected to
avoid rerunning imported fixture classes against shared temporary data.

The Debian package's full file inventory, hashes, modes, metadata and update-feed
hash/size passed verification. Its packaged viewer started under Xvfb/software
OpenGL with a disposable home/profile, retained the compiled channel despite a
legacy override, displayed the first-run disclosure and exited normally without
logging in.

The portable archive passed its full inventory/hash and normalized archive
metadata checks (23,759 files). A local-transport GTK update fixture used the
compiled viewer with a synthetic older metadata label, downloaded and verified
the full archive, requested normal D-Bus shutdown, replaced the application,
retained its previous folder and synthetic settings/cache, then restarted and
exited the updated viewer normally. This was not a public-feed or real older
binary upgrade.

Native Linux hardware, real Second Life login, camera playback on Linux and a
public-feed Linux upgrade are separate tests and have not been performed for
this candidate. Windows file-preserving installation does not change Linux's
existing package-manager and portable updater mechanisms.

## Data and distribution

Source and application staging exclude profiles, credentials, logs, cache and
private test paths. Local account-name and credential-pattern scans report
counts only; their search strings are never included in source or releases.
See the accompanying candidate verification reports for final artifact hashes,
manifest extraction, legacy-updater compatibility and package checks.

No public release has been published from these preparation steps. The
Firestorm settings import, smaller downloads and the proposed renderer port
are not included.
