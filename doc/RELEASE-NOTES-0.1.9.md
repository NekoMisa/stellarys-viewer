# Stellarys Viewer 0.1.9 Beta 1 for Windows (based on Firestorm 7.2.5.81788)

## What's new

- Updated the Firestorm base to 7.2.5.81788, including AO tracks/groups,
  custom inventory tabs and camera roll.
- Added an off-by-default experimental updates checkbox, saved with your
  settings. Stable users continue to receive stable releases.
- Retained the AMD mesh fix, permission-based poser, Photo tools, shot presets,
  cinematic camera paths and saved trusted/blocked link lists.
- Includes the new default Inter font and wider script dialogs. The older
  Deja vu font scheme remains selectable in Preferences.
- Follows upstream's WebRTC voice path. Media/sound and voice passed the
  maintainer's Windows test.

Windows betas are ordered before the final release at the same version.
Turning experimental updates off never automatically downgrades a beta.
Existing 0.1.8 installations need one manual beta installation to get the
checkbox; later beta updates can then use the updater.

## Installing the beta from 0.1.8

Download the Windows beta Setup.exe from this prerelease, close Stellarys and
install into its existing marked installation folder. No uninstall is needed;
settings, saved shots, camera paths, trusted/blocked lists and cache are retained.
Then enable **Help > Check for Updates > Include experimental updates (beta)**
to receive later betas. The checkbox is off by default even after a manual beta
installation. The old 0.1.8 updater does not discover Windows prereleases.

The stable Windows release and Linux update feeds are unchanged. No Linux
0.1.9 application is included in this Windows prerelease.

## Font choice

The upstream default changed from DejaVu to Inter, with larger text and wider
script dialogs. Choose **Preferences > User Interface > Font > Font Scheme >
Deja vu** and restart to use the previous font and text sizes. The dialog's
wider layout is a separate upstream change.

## Preserved behavior

The Stellarys version remains separate from the official Firestorm base.
Rendering changes from the new upstream are incorporated together with our AMD
precision safeguards. The avatar skinning shader bounds both palette indices.
Other avatars still require explicit permission before local posing; existing
session/region permission restrictions remain. Poses are not synchronised.

The Photo menu, saved shot presets, cinematic keyframes/countdowns/cuts/loops,
optional trusted/blocked link lists and their off-by-default experimental
settings are retained. Existing per-user settings and cache remain separate
from official Firestorm and Black Dragon. This update does not import their
settings, move installations, or reset Stellarys profiles.

Windows keeps verified full-installer downloads, file-preserving normal updates,
and optional full reinstall/repair. Administrator approval, destination and
running-viewer protections remain. Linux Debian and portable packages keep
their separate verified update mechanisms and retained user data.

## Beta validation

Native Windows and Linux builds passed, along with the automated feature and
updater checks. The maintainer tested the Windows beta in-world, confirmed the
affected AMD mesh, media/sound and voice, gave positive feedback on the tested
features, and approved this beta release. Detailed test scope and outstanding
installer/platform checks are in [VALIDATION-0.1.9.md](VALIDATION-0.1.9.md).
Native Linux hardware testing remains distinct from WSL tests.

This update does not claim to fix the unresolved Windows restart/Bluetooth
report. No reporter has been asked to reproduce a crash loop.

Stellarys is an independent non-commercial hobby project, not provided or
supported by Linden Lab or the Firestorm team. Read DISCLOSURES.md and PRIVACY.md.
