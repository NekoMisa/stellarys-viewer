# Stellarys Viewer 0.1.5 (based on Firestorm 7.2.4.80712)

## What's new

- Optional link warnings and blocking (Experimental), off by default.
- Warn on unlisted web links, or turn warnings off and keep your blocked list active.
- Open once, trust a domain, or block it directly from the warning.
- Manage saved trusted/blocked domains and optionally select familiar services from Common sites.
- Domain lists and your chosen mode stay saved between sessions and updates.

## Using the experimental link controls

Open Preferences > Privacy > Links and enable Link warnings and blocking.
Keep Warn before opening unlisted web links checked to see the choice prompt.
Clear it for blocked-list-only mode: unlisted links follow the normal browser
flow, while blocked domains still stop and show a brief notice. Turning the main
switch off restores the existing link behavior without deleting your lists.

Checks apply to web links clicked in viewer text, including chat/IM and internal
or external browser context-menu choices. Exact domains only: subdomains and
www names need separate entries. Trusted means skip this warning, not guaranteed
safe. Common sites is an optional local catalogue with no preselection or automatic
import. Blocks take priority. No chat messages or links are sent to a checking
service. Embedded pages, redirects and parcel media are outside these checks.
Unsupported/ambiguous web address formats are refused while checks are enabled.
Existing browser/media prompts still apply.

List edits save immediately for the current OS-user profile and are not undone
by cancelling Preferences. Updates preserve that profile, including removed
defaults. Explicitly removing settings during Windows uninstall also removes
the domain lists. Do not include personal lists in public support reports.

## Installation and updates

Choose the package for your platform. Windows uses the unsigned x64 installer
and requires administrator approval. Linux Debian and portable builds remain
experimental previews with separate update feeds; they do not install Windows
updates. Use Help > Check for Updates to download and verify the appropriate
package. Save your work and close all Stellarys instances before installation.
Settings and cache are preserved during normal updates.

Windows Setup defaults to C:\Program Files\StellarysViewer. When updating,
choose your existing marked Stellarys installation folder to update that copy.
Choosing another folder does not move the old installation or its shortcuts.
Setup refuses unrelated nonempty folders. See the bundled installation guide.

The Firestorm base version, AMD flicker fix, poser, photography tools, motion
blur and rendering behavior are unchanged. These link controls do not add a
malware database or guarantee protection from phishing. Releases remain unsigned;
SHA-256 verifies integrity, not publisher identity.

## Validation

Windows and Linux compiled tests and disposable-profile UI checks passed for
link decisions, blocking, selected-domain imports and saved choices. The user
reported that the updated Windows private build works. See VALIDATION.md for
the final package checks and their limits. No account data, profiles, runtime
logs or cache are packaged. Native Linux distributions/GPU behavior and a real
public version-to-version update are separate from headless validation.

This software is not provided or supported by Linden Lab, the makers of Second
Life, or by the Firestorm team. Read DISCLOSURES.md and PRIVACY.md. This is an
independent, non-commercial hobby project; support is available as time permits.
