# Link warnings (Experimental) — Stellarys 0.1.5

Enable **Preferences > Privacy > Links > Enable link warnings and blocking**.
It is **off by default**. Manage the trusted and blocked domains from the same tab.

The separate **Warn before opening unlisted web links** checkbox starts checked.
Clear it for blocked-list-only mode: ordinary unlisted web links continue through
the existing browser flow without this warning, while saved blocks still stop
links. A blocked link still shows a brief blocked notice. Existing browser/media
prompts and refusal of unsupported address formats remain. Both choices persist;
turning the main switch off disables these checks without clearing your lists.

Web links clicked in chat/IM and other viewer text are checked before the existing
browser-opening flow. This also covers the text-link context menu's internal and
external browser choices. Second Life/Hop actions retain their existing handling.
The feature does not scan embedded web pages, redirects, parcel media or every
network request. Existing browser/media permission prompts still apply.

- Trusted domain: skip this experimental warning, not a guarantee of safety.
- Unlisted domain: **Open once**, **Trust domain and open**, **Block domain**, or **Cancel**.
- **Block domain** saves the block immediately without opening the link.
- Blocked domain: do not open; manage the list to remove the block if desired.

**Manage domains > Common sites...** opens an optional picker with 36 exact
domains for familiar services and documentation. Nothing is preselected or
automatically imported. Choose rows, then **Trust selected** to save those
choices immediately. Existing trusted/blocked entries are omitted; a block added
after opening the picker also wins when saving. Other personal entries and
unselected removals are untouched. Choosing a previously removed domain here
explicitly adds it back. Future catalogue changes do not alter saved lists.

The catalogue identifies common services, not guaranteed safe destinations or
security-scanned content. Social sites can host user content; redirects are not
checked. URL shorteners and blanket shared download/hosting domains are excluded.
It is bundled locally: opening the picker does not contact the suggested sites.

Checks use the actual URL destination, not its display label. Exact domain
matches only: `www.example.com` and `sub.example.com` are separate entries.
Lookalikes such as `secondlife.com.evil.example` are not trusted automatically.
HTTP/HTTPS ports use the same domain rule. Ordinary ASCII/punycode domains and
canonical IPv4 addresses are supported. IPv6, encoded hostnames, credentials in
addresses, control bytes, backslashes and ambiguous numeric hosts are refused
while enabled; they are not silently trusted. This is intentionally experimental.

Initial trusted entries include explicit Primfeed, Second Life, Flickr and
Facebook domains. Shared hosts such as all of GitHub are not automatically
trusted. You can add/remove entries. No malicious-site database is bundled and
no chat messages or URLs are sent to a checking service.

## Saved data and updates

The enable/disable preference is a normal persistent viewer preference.
Domain choices save immediately in the per-user settings directory:

- Windows: normally `%APPDATA%\Stellarys_x64\user_settings\stellarys_link_domains.txt`
- Linux: normally `~/.stellarys_x64/user_settings/stellarys_link_domains.txt`

The adjacent `.lock` file coordinates simultaneous viewer instances. It can stay
on disk after exit; the OS releases its lock when the process exits. The rule
file stores only domains and trust/block decisions, not clicked URLs or queries.
Do not include this personal file in source or release application payloads.

Updates replace application files and retain this settings directory. Existing
lists, including removed defaults and empty lists, are read as saved; future
bundled defaults never silently overwrite them. Normal uninstall preserves the
profile; explicitly choosing to remove settings also removes personal domain lists.
Other avatars using this same OS-user viewer profile share these choices.

Editor changes save immediately and are not undone by cancelling Preferences.
Adding a domain to one list removes it from the other. An already-open warning
cannot use “Trust and open” to undo a newer block from another instance.
Unreadable/corrupt/unknown-version files are preserved and reported. While the
feature is enabled, a failed list read/save does not open the requested web link.
File changes use a same-directory temporary file and replacement under a lock.
Normal failed saves preserve previous data; sudden power-loss recovery is not
guaranteed. This feature does not replace browser security or careful judgment.

## Developer checks

The test compiles the actual policy and persistent store, using disposable folders.
Windows, from a Visual Studio C++ developer prompt:

```text
cl /nologo /std:c++17 /EHsc /W4 tools\stellarys-links\link_tests.cpp /Fe:link-tests.exe
link-tests.exe
```

Linux:

```sh
g++ -std=c++17 -Wall -Wextra -pedantic tools/stellarys-links/link_tests.cpp -o /tmp/stellarys-link-tests
/tmp/stellarys-link-tests
```

Tests cover disabled behavior, exact matches/lookalikes, misleading/unsupported
addresses, block precedence, saved-state round trips, new instances after update,
removed defaults, empty lists, stale views, locking, failed saves, corrupt/future
schemas and oversized files. Linux also checks private file permissions/symlinks.
Picker tests cover normalized/unique suggestions, explicit selections only,
preserving existing entries/removals, newer block precedence and atomic rejection
of invalid selections.
Compiled-viewer UI and a real in-world chat click are separate validation steps.
