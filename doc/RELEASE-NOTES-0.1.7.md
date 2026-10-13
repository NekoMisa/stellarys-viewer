# Stellarys Viewer 0.1.7 (based on Firestorm 7.2.4.80712)

## What's new

- Corrected Windows registration for Second Life and Hop browser links.
- Consistent Stellarys names in Windows link setup and app selection.
- Clear setup instructions when Windows opens the general Default apps page.

## Windows link setup

Open Preferences > Network & Files > Stellarys > Open Second Life links with
Stellarys, then click Set up SL links. Setup also offers this as an unchecked
option on its final page.

Windows may open the general Default apps page instead of Stellarys's page.
Use the file/link-type search at the top: enter secondlife, choose Stellarys,
then repeat for hop. This is separate from the general Settings search box.
On the tested Windows 11 build, app-specific shortcuts still opened the general
page; the shortcut limitation is not claimed fixed. Duplicate application-list
entries may remain on existing profiles; link-type search avoids that ambiguity.

Registration now uses a matching version-free application name, safely removes
its older registration alias, and declares missing URL protocols without
overwriting existing protocol defaults or other viewers' commands. Existing
Stellarys ProgIDs and capabilities paths remain stable. The helper never writes
Windows UserChoice; you choose the default through Windows.

## Installation and preserved data

Use Help > Check for Updates, or download the Windows x64 Setup executable below.
Save your work and close Stellarys before installing. Administrator approval is
required. Choose your existing marked Stellarys folder to update it; the default
is C:\Program Files\StellarysViewer. Another folder does not move the installation.
Unrelated nonempty folders are refused. This release uses the existing full
installer; smaller/faster updates are a separate future change.

Settings, cache, shot presets, trusted/blocked lists and link-checking modes are
preserved. Uninstall keeps per-user data by default; removal remains optional.
Experimental link controls stay off by default. Existing format-2 link lists
remain supported; back up before downgrading to 0.1.5 or older.

The official Firestorm base remains 7.2.4.80712. Rendering, the AMD fix, posing,
photography and motion blur are unchanged. Linux Debian and portable previews
remain at 0.1.6; their separate update feeds ignore this Windows release.

## Validation and limits

See the attached VALIDATION.md and VALIDATION.json for performed checks and
limitations. Local Windows registration and chooser checks are separate from
clean-machine tests and from browser-to-viewer dispatch. The installer/updater
remain unsigned; SHA-256 verifies file integrity, not publisher identity.
Only application files and selected clean source are packaged; no personal
settings, accounts, credentials, runtime logs or cache are included.

This independent non-commercial hobby project is not provided or supported by
Linden Lab or the Firestorm team. Read DISCLOSURES.md and PRIVACY.md.
