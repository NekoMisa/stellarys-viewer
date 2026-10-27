# Stellarys 0.1.9 Beta 1 validation

This Windows experimental release is based on Firestorm 7.2.5.81788
(`4ac201fdc56127de27de34567286885f4e75d194`). Windows is identified as
0.1.9 Beta 1 on the experimental branch. Linux artifacts remain private.

## Checks performed

- The user tested the private Windows Beta 1 in-world and reported that the
  affected AMD mesh renders correctly and media/sound works. This is a visual
  confirmation for that tested mesh, not all AMD hardware or content.
  The user subsequently confirmed voice works as well, gave positive general
  feature-test feedback and approved the beta release. That feedback did not
  itemize every poser/photography case, so no exhaustive test claim is made.
- Private Windows startup reached the first-run disclosure with the correct
  version title and isolated AppData/cache folders. The user handled login.
- Native MSVC v143 Windows and GCC 11 Linux builds completed successfully.
  Windows was reconfigured and incrementally rebuilt with the exact channel
  `Stellarys Viewer 0.1.9 Windows Beta 1`. Its executable FileVersion and
  ProductVersion remain the official Firestorm base `7.2.5.81788`.
- The clean Windows application stage contains 24,523 files. Its generated
  SHA-256 inventory passed verification for every file. Packaging's forbidden
  data/path checks passed, and scanning the application against the maintainer's
  private marker values found no matches. No marker values were printed or sent
  to a third party. This is a scoped privacy check, not a malware certification.
- All 28,133 selected source files were checked against the same private marker
  values before committing; no matches or forbidden runtime/profile paths were
  found. Only aggregate results were reported.
- Merged the official upstream source while retaining Stellarys features.
  All 1,685 changed XML files parsed in the initial source validation.
- Existing camera path, shot validation, poser consent and link policy fixture
  suites passed on Windows and Linux. Nearby poser discovery passed controlled
  avatar fixtures. These are not tests of real user consent or live animation.
- The existing 32 Windows updater validations passed after the channel changes.
  All 52 new experimental channel/version/feed/profile checks passed after
  recompiling the test executable following the restart.
- The updater compiled with the new channel code. Its Windows UI was tested
  with disposable AppData directories: experimental updates initially off,
  opt-in persisted across closing/reopening, opt-out returned to stable checks.
  Both channel modes contacted the public GitHub feed and declined to downgrade
  the unpublished beta to the older public release. No installer was launched.
- Nine CMake release identity fixtures passed, including Windows Beta 1.
- Updated the offline first-run disclosure to the new upstream base and beta
  status; the regenerated XML parses.
- The private Windows beta installer compiled successfully. Windows SDK
  manifest extraction verified `requireAdministrator`; version resources say
  `0.1.9 Beta 1 (based on Firestorm 7.2.5.81788)`. Its unsigned status was checked
  and a SHA-256 checksum recorded. NSIS compiled the seven installation pages
  and three uninstall pages. This was not an interactive installation test.
- Ownership/process guards, file comparison, data removal and link registration
  implementation files are byte-unchanged from 0.1.8. Destination selection and
  per-user data protections remain in the compiled installer source.
- Actual Radeon RX 7900 XTX OpenGL shader compilation and linking passed four
  avatar shader variants (AMD safeguards on/off and precision qualifier on/off).
  This does not establish an in-world flicker fix for the new upstream renderer.
- Linux updater, portable launcher, desktop entry and GUI fixture suites passed
  in disposable environments. They do not establish native Linux compatibility.
- After antivirus restoration, all 2,511 integrated source files existed.
  Of 2,430 files copied directly from upstream, 2,427 exactly matched official
  Git blob hashes. The three differences were reviewed build/platform fixes.
  All 81 merged files matched the independent Linux source snapshot.

## Pending checks and limitations

- Linux Debian and portable packages were built privately. Debian identity,
  feed SHA-256/size and all 21 bundled 64-bit ELF runtime dependencies passed
  checks in Ubuntu 22.04 WSL. No non-64-bit ELF or unresolved libraries were
  found. The portable archive passed its updater's archive inspection. These
  Linux packages are not part of this Windows release and need runtime testing.
- Interactive beta installer destination selection, installation/update and
  uninstall have not been tested. No actual installation has been modified.
- Review clean payload inventories, licences, source archives and checksums.
- Complete user tests of posing, saved shots/camera paths and settings
  persistence. Windows startup, the affected mesh, media/sound and voice passed.
- Native Linux hardware tests are separate from compilation/WSL checks.
- No complete beta download/install/promotion cycle has been tested against a
  published beta, because no beta has been published. Fixtures cover ordering,
  metadata verification and channel selection.

## Antivirus incident

Chili Security reported suspicious behavior during build/testing. The user
restored the affected files. Windows initially denied overwriting two restored
files despite normal permissions. After a user-operated restart, ordinary edits
and recompilation to the same paths worked again. All 52 updater channel tests
then passed, and the build helper's channel default was updated successfully.
The cause has not been confirmed. No antivirus exclusions or protection changes
were made.
These checks do not certify an antivirus false positive.

Installed viewers, real profiles and real protocol defaults have not been
changed for these development checks. Private test profiles and logs remain
outside application staging. Do not publish runtime data or unredacted logs.
