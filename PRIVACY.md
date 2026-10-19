# Stellarys Viewer privacy policy

Effective date: 12 October 2026. Maintainer: NekoMisa.

Stellarys Viewer is an independent hobby project based on Firestorm. This
software is not provided or supported by Linden Lab, the makers of Second Life.
This policy describes the Stellarys Windows and Linux builds; services reached
through the viewer have their own privacy policies.

## Information on your computer

The viewer stores preferences, account identifiers and optional saved sign-in
information, chat/diagnostic logs, cached world content, browser data, poses and
shot presets and camera paths on your computer. Saved sign-ins are optional. Chat logging and
other privacy options are available in Preferences. These files may contain
avatar names, conversations, locations and technical information. Protect your
Windows/Linux account and review files before sharing them.

Windows normally uses `%APPDATA%\Stellarys_x64` and
`%LOCALAPPDATA%\Stellarys_x64`. Linux normally uses `~/.stellarys_x64`.
Cache, chat logs and snapshots can use locations you select instead. Updates
preserve this data. Windows uninstall preserves it by default and offers explicit
removal options. Linux package removal/purge preserves home-directory data;
remove your Stellarys profile and any custom data locations yourself if wanted.
Neither installer requires a Second Life account or password.

## Second Life and network services

Connecting sends authentication information to Linden Lab's login service and
exchanges account, avatar, location, inventory, chat and world data with Second
Life as needed to operate the viewer. The inherited viewer statistics packet
sends session/performance information, viewer version, operating system, CPU,
GPU, memory, network and device identifiers to Linden Lab. This is separate
from any analytics operated by the Stellarys maintainer.

The inherited Firestorm functionality can request configuration, compatibility
and support data from Firestorm/Phoenix services, including at startup. Recipients
can see your IP address, request headers and viewer/browser identification.
Some inherited endpoints use HTTP rather than HTTPS. These services are operated
by their respective providers, not by Stellarys.

Optional voice, parcel media, web pages, search, translation and external links
contact the selected providers. They can receive your IP address and information
needed for the feature, such as requested URLs, voice traffic or text submitted
for translation. Embedded web content can store cookies/browser data locally.
Use Preferences to control media, voice and related privacy choices. A manually
selected alternative grid receives the information required to log into that
grid; do not reuse your Second Life password on an untrusted grid.

See [Linden Lab's privacy policy](https://lindenlab.com/privacy) and the policies
of the services you choose to use.

## Experimental link warnings

Link warnings are off by default and can be enabled in Preferences > Privacy >
Links. Checks compare clicked web links in viewer text with trusted and blocked
domain lists and explicit trusted GitHub account/repository scopes on your computer.
No chat messages, clicked URLs or domain lists
are sent to a checking service. Opening an approved link still contacts its
destination through your selected browser. A separate warning checkbox allows
blocked-list-only checks: unlisted links open without a domain-choice prompt,
while saved blocks remain enforced. Both preferences persist between sessions.

The lists store domains, selected GitHub account/repository scopes and trust/block choices in your per-user settings
directory, without recording clicked URLs or queries. They are shared by avatars
using that viewer profile and preserved during updates. List edits save
immediately, even if you later cancel Preferences. Explicitly removing your
settings also removes these lists. A trusted domain skips the warning; it is not
a guarantee of safety. Embedded pages and redirects are not checked.
The optional Common sites picker is a bundled local catalogue. It does not
contact the listed sites or add domains automatically. Only your selected entries
are added, while existing blocks are preserved.
New profiles start with reviewed official Second Life services and the scoped
NekoMisa GitHub account alongside the original social-site defaults. Existing
saved lists are not merged with new defaults. GitHub scopes cover only the named
account/repository over HTTPS, and a domain block takes priority. These entries
are local preferences, not verification of hosted content or redirect destinations.

## Update checks and downloads

The bundled updater requests release information and approved downloads from
GitHub over HTTPS. GitHub and its download infrastructure receive normal network
information, including your IP address and updater user agent. The updater does
not send your Second Life credentials, chat logs, settings or cache. Startup
checks can be disabled; manual checks remain available. Downloading and
installing an update require your approval. Downloads and updater preferences
are stored locally. See [GitHub's privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

## Posing, photographs and support

Posing another avatar uses explicit permission requests and acceptance/revocation
messages through Second Life IMs. Consent state is kept in memory for the current
session/region. Pose changes are local to the viewer applying them; they are not
broadcast as animations or synchronised with other viewers. Poses and shot
presets and camera paths can be saved locally. A snapshot is uploaded or shared only when you
choose a viewer action that does so.

The Stellarys additions do not operate a separate maintainer analytics or
automatic crash-upload service. Diagnostic files can still be created locally.
Support requests are voluntary. GitHub Issues, comments and attachments are
public; do not post passwords, saved sign-in files, private conversations or
unredacted logs. Technical information sent to another resident through the
inherited support feature requires your approval.

The maintainer can read and use information you deliberately submit to the
project to investigate issues and discuss development. Public submissions may
remain in GitHub history and copies held by others. Do not assume that deleting
a comment removes every copy. GitHub handles its own account and hosting data.

## Contact and changes

For privacy questions, contact the maintainer through
[Stellarys GitHub Issues](https://github.com/NekoMisa/stellarys-viewer/issues)
without including sensitive information. Ask for a private contact method before
sharing any private details. Support is provided as time permits, without a
guaranteed response time. Changes to these practices will be documented in this
policy and relevant release notes. This policy does not claim Linden Lab
approval or replace the policies of external services.
