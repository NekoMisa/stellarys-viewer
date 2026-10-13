# Optional common-site catalogue

This is a convenience catalogue, **not a certified-safe list or a malware scan**.
The current catalogue contains 59 entries: exact domains plus a scoped GitHub account. Entries
are bundled, reviewed as named service destinations, and never trusted merely
because the catalogue exists. Users explicitly select entries in Common sites.
The viewer does not fetch these pages when showing/importing the catalogue.

Service references reviewed on 12 October 2026; Second Life and NekoMisa GitHub
coverage expanded on 13 October 2026:

- [Second Life](https://www.secondlife.com/) and its
  [community](https://www.secondlife.com/community),
  [Marketplace](https://marketplace.secondlife.com/) and
  [feedback](https://feedback.secondlife.com/) services.
- The full 31-domain official-service review, language coverage and aliases are
  documented in [Official Second Life sites](OFFICIAL-SECOND-LIFE-SITES.md).
- [NekoMisa's GitHub profile and viewer projects](https://github.com/NekoMisa),
  scoped as `github.com/nekomisa`, rather than trusting the entire shared host.
- [Primfeed](https://primfeed.com/), [Flickr](https://www.flickr.com/) and
  [Facebook](https://www.facebook.com/). These retain the domains already in the
  initial default list; automated access to Primfeed was unavailable during review.
- [Bluesky](https://bsky.app/) and [Discord](https://discord.com/).
- [YouTube](https://www.youtube.com/), [Vimeo](https://vimeo.com/) and
  [Twitch](https://www.twitch.tv/).
- [Reddit](https://www.reddit.com/) and [Wikipedia](https://www.wikipedia.org/).
- [GIMP](https://www.gimp.org/), [Mozilla](https://www.mozilla.org/),
  [Microsoft Support](https://support.microsoft.com/) and
  [Microsoft Learn](https://learn.microsoft.com/).

The exact catalogue is defined by `commonSites()` in
`indra/newview/stellaryslinkpolicy.h`. Root and www names are separate entries;
only explicitly listed documentation/community subdomains are suggested. The
catalogue does not include general URL shorteners or blanket shared download/hosting
domains. Linden's dedicated `second.life` short-link domain is included explicitly;
its redirects are not inspected. Social services still host user-controlled content, and this feature
does not inspect redirects or embedded pages. A service's presence is not an
endorsement of its content, privacy practices or downloads.

Existing trusted and blocked domains are omitted from the picker. Saving rechecks
current lists under a lock, so a block created after opening the picker wins.
Only explicitly selected domains are added. Updating the viewer/catalogue never
merges it into personal rules. Unselected removed entries remain removed; choosing
a removed entry explicitly adds it back.

Even threat-detection providers do not promise complete or error-free safety
classification; see [Google Safe Browsing's usage guidance](https://developers.google.com/safe-browsing/reference/Appropriate.Usage).
