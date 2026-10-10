# Stellarys Viewer 0.1.4 (based on Firestorm 7.2.4.80712)

Windows release and experimental Linux preview 1.

## What's new

- Read the project's privacy policy and support information before first sign-in.
- The policy is bundled offline and available from the welcome page and About.
- Each release now reports its own Stellarys identifier to Second Life.
- Clearer independent-project information in Setup and download documentation.

## Before installing

This software is not provided or supported by Linden Lab, the makers of Second Life.
It is also not provided or supported by the Firestorm team.
Read [project disclosures](https://github.com/NekoMisa/stellarys-viewer/blob/main/DISCLOSURES.md)
and the [privacy policy](https://github.com/NekoMisa/stellarys-viewer/blob/main/PRIVACY.md).
Support is available through [GitHub Issues](https://github.com/NekoMisa/stellarys-viewer/issues)
as time permits; there is no guaranteed response time. Never post credentials,
private chat or unredacted logs. The disclosures describe local-only posing,
other feature limitations and optional maturity/RLVa functionality.

## Installation and updates

Windows Setup defaults to C:\Program Files\StellarysViewer. Update the same
marked installation folder, with every instance closed. Choosing a different
folder does not move your existing installation. Setup refuses a different
registered machine installation and unrelated nonempty folders. Administrator
approval is required; existing viewers and their profiles are left intact.

Linux remains an experimental native x86_64 preview. Install the matching .deb
on a compatible Ubuntu 22.04-based system such as Linux Mint. The Linux updater
uses the existing repository's Linux feed and ignores Windows packages.
Its package/preview version is separate from the official Firestorm base.

Updates preserve Stellarys settings/cache. Windows uninstall offers explicit
optional data removal; default uninstall preserves it. Linux package removal
and purge preserve home-directory data. Binaries/installers remain unsigned;
SHA-256 verifies integrity rather than publisher identity. Download and install
actions require your approval.

Rendering, the AMD flicker fix, poser consent and photography/shot-preset
behavior are unchanged. No Black Dragon renderer transplant is included.

## Validation and source

See the matching VALIDATION.md and source archive for performed checks and
remaining manual tests. The project does not claim TPV directory listing or
Linden Lab approval. Existing installed releases keep their old identifiers
until updated; released installers are not silently replaced.
