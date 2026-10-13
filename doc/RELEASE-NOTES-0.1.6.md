# Stellarys Viewer 0.1.6 (based on Firestorm 7.2.4.80712)

## What's new

- Correct version labels in the viewer title and translated About pages.
- Windows Second Life link setup now uses the simple application name Stellarys.
- Expanded official Second Life links, including Marketplace in every language.
- Trust NekoMisa's GitHub profile and projects without trusting all of GitHub.
- Existing saved lists stay unchanged; experimental link checks remain off by default.

## Version labels and browser links

The window title and About header now use the compiled Stellarys version on
Windows and Linux. The official Firestorm base stays 7.2.4.80712. Windows app
descriptions and link-registration display names use Stellarys, with stable
registration identifiers. Windows may retain a previously cached chooser label
until it refreshes. Linux desktop-entry names also use Stellarys.

## Expanded trusted sites (Experimental)

New profiles include 31 reviewed official Second Life service domains and aliases,
alongside the original social-site defaults and the scoped NekoMisa GitHub entry.
The Common sites picker contains 59 entries. Existing saved lists receive no
automatic additions: open Preferences > Privacy > Links > Manage trusted sites
and blocked domains > Common sites to select additions you want. Removed entries
stay removed. The main enable switch stays off by default; your saved mode is kept.

Marketplace's six language options all use marketplace.secondlife.com. Its
language parameters, listings and stores are covered by that exact-domain entry.
Other reviewed services include signup/accounts, profiles, land/auctions, search,
support, community, Wiki, creator documentation, feedback and grid status.
Official services can contain resident contributions; trusted does not mean safe.
Linden's dedicated second.life short-link domain is included, but redirects are
not inspected. No general shortener or blanket shared hosting domain is added.

github.com/nekomisa is an account-scoped trusted entry, covering the NekoMisa
profile and repositories, including Stellarys and Black Kitty Fix. It applies to
HTTPS on the normal GitHub port, with a path boundary. Other accounts, lookalikes,
ambiguous encoded/dot-segment paths and other GitHub hosts are not trusted by it.
An individual repository scope can be used instead. A github.com block wins;
remove it explicitly before trusting an account or repository. The warning's
Trust domain and open action still trusts a whole domain, as labelled.

Checks apply to clicked web links in viewer text, including chat/IM and their
browser context-menu choices. Embedded pages, redirects, parcel media and other
network traffic are outside these checks. Existing browser/media prompts apply.
No chat messages, clicked URLs or lists are sent to a checking service.

## Saved lists and older versions

Updates preserve per-user settings, cache and domain lists. Existing version-1
domain files remain readable and are not rewritten simply by reading them.
Explicitly adding a GitHub scope writes format 2 atomically while retaining other
entries. New profiles use format 2 because the scoped GitHub default is included.
Older 0.1.5 viewers cannot read format 2: they leave it intact and refuse checked
web links while the experimental feature is enabled. Avoid downgrading a profile
containing scoped entries without a backup. Domain-only lists continue to use
format 1. List edits save immediately and are not undone by cancelling Preferences.
Default uninstall keeps settings; explicit Windows settings removal deletes lists.

## Installation and validation

Use Help > Check for Updates in your existing viewer. Save your work and close
all Stellarys instances before installation. Windows Setup requires administrator
approval; select your existing marked Stellarys installation folder to update it.
The default is C:\Program Files\StellarysViewer. Another folder does not move
the old installation. Unrelated nonempty folders are refused.

Debian and portable Linux retain their separate preview feeds and package formats.
There is no AppImage or Flatpak release in this update. Sources, guides, checksums
and the performed checks/limits are attached to each release. Builds remain
unsigned; SHA-256 verifies integrity, not publisher identity.

Rendering, the AMD fix, poser, photography and motion blur are unchanged. Read
VALIDATION.md for actual build, package, policy, persistence and UI checks and
their limits. A native Linux hardware test or a real installed upgrade is separate
from headless and fixture validation. No personal profiles, accounts, credentials,
runtime logs or cache are packaged.

This software is not provided or supported by Linden Lab, the makers of Second
Life, or the Firestorm team. Read DISCLOSURES.md and PRIVACY.md. This is an
independent, non-commercial hobby project; support is available as time permits.
