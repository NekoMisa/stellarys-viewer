# Official Second Life links

Reviewed 13 October 2026. This list identifies official destinations; it does
not certify their content, resident contributions, downloads or redirects as safe.
It covers verified public websites and their known aliases, not every internal
API, asset server or future subdomain. Matching remains exact, without wildcards.

The following 31 domains are included in both new-profile trusted defaults and
the optional Common sites picker. Existing saved lists are read as saved: no
new defaults are merged into them and removed entries stay removed. Existing
users can explicitly select additions in Common sites. The feature remains off
by default, and a personal block always wins.

| Domains | Purpose / official reference |
| --- | --- |
| `secondlife.com`, `www.secondlife.com` | [Official homepage](https://secondlife.com/); main site, downloads, destinations, events, account/LindeX pages and localized paths |
| `join.secondlife.com`, `accounts.secondlife.com`, `id.secondlife.com` | Signup and account/sign-in links in the [official site navigation](https://secondlife.com/destinations) |
| `my.secondlife.com`, `world.secondlife.com` | Public profiles and place pages; [official search documentation](https://wiki.secondlife.com/wiki/FAQ_sur_la_recherche) describes world pages |
| `marketplace.secondlife.com` | [Marketplace](https://marketplace.secondlife.com/), linked by the official homepage and community navigation |
| `community.secondlife.com`, `blogs.secondlife.com` | [Community, blogs, forums, Answers and localized knowledge base](https://community.secondlife.com/); the old blog host redirects here |
| `support.secondlife.com`, `lindenlab.freshdesk.com` | Official support and ticket service, linked by [Community navigation](https://community.secondlife.com/) |
| `wiki.secondlife.com`, `create.secondlife.com` | [Wiki](https://wiki.secondlife.com/wiki/Main_Page) and [creator/scripting documentation](https://secondlife.com/create) |
| `feedback.secondlife.com`, `jira.secondlife.com` | Current [feedback portal](https://secondlife.com/) and [legacy JIRA endpoint](https://jira.secondlife.com/) |
| `status.secondlifegrid.net` | [Grid status](https://status.secondlifegrid.net/), linked by Community navigation |
| `maps.secondlife.com`, `slurl.com`, `www.slurl.com` | [Official map/SLurl documentation](https://wiki.secondlife.com/wiki/Linden_Lab_Official:Map_API_SLurl_Technical_Details); both legacy hostnames redirect to maps |
| `search.secondlife.com`, `land.secondlife.com`, `places.secondlife.com` | Search, land/Linden Homes, places and auctions in [official navigation](https://secondlife.com/destinations) |
| `go.secondlife.com` | Official [destination/landing pages](https://go.secondlife.com/destination/da-boom) and affiliate links from the support portal |
| `connect.secondlife.com`, `www.connect.secondlife.com` | Enterprise/education links from the homepage and grid status footer |
| `second.life` | Linden's dedicated short-link domain, used by the [official creator page](https://secondlife.com/create); redirects are not inspected |
| `lindenlab.com`, `www.lindenlab.com`, `dmca.lindenlab.com` | Linden Lab company, terms/privacy and [DMCA reporting](https://lindenlab.com/) |
| `forums-archive.secondlife.com` | Historical official forums, referenced from [Wiki discussions](https://wiki.secondlife.com/wiki/PRIM_CAST_SHADOWS) |

## Languages

Marketplace's own language menu was checked: English (`en-US`), German (`de-DE`),
Spanish (`es-ES`), French (`fr-FR`), Japanese (`ja-JP`) and Brazilian Portuguese
(`pt-BR`) all use `https://marketplace.secondlife.com/?lang=...`. One exact-domain
entry covers every language, listing, store and language parameter on that host.
The website, community knowledge base and Wiki also use paths, parameters or
cookies for their languages. No guessed country domains or language subdomains
are needed. A genuinely new hostname would need a separately reviewed entry.

## GitHub project links

`github.com/nekomisa` is also included as an explicitly scoped trusted entry in
new profiles and Common sites. It covers the NekoMisa profile and its repositories,
including [Stellarys](https://github.com/NekoMisa/stellarys-viewer) and
[Black Kitty Fix](https://github.com/NekoMisa/Black-Dragon---Black-Kitty-Fix).
It applies only to HTTPS on the normal GitHub port, with an account-path boundary.
Other accounts, lookalike names, encoded/dot-segment paths and other GitHub hosts
are not automatically trusted. A `github.com` block overrides this entry.
An explicit repository scope such as `github.com/nekomisa/stellarys-viewer` can
be used instead. Remove the account scope first if only one repository should
be trusted. GitHub discussions/files may contain user contributions and redirects.

General shorteners, shared hosting/CDNs and partner/social platforms are not
automatically trusted merely because an official page links to them. The
dedicated `second.life` entry is an explicit exception for official short links;
it does not add Bitly or another general shortener. No redirect destination is
checked, including official short links. These rules do not inspect embedded web
pages, parcel media, downloads or all viewer network traffic.

Some automated page requests were refused or required sign-in. Those services
were identified through official navigation/documentation instead; no account
was used. A hostname's inclusion does not promise that a retired service works.
