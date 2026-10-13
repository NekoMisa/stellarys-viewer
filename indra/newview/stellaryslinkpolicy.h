// Local, exact-domain link decisions. SPDX-License-Identifier: LGPL-2.1-only
#ifndef STELLARYS_LINK_POLICY_H
#define STELLARYS_LINK_POLICY_H
#include <algorithm>
#include <set>
#include <string>
#include <vector>
#include <utility>

namespace StellarysLinks
{
inline std::string lower(std::string value)
{
    for (auto& c : value) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
    return value;
}

// Conservative ASCII host syntax shared by the editor and URL decisions.
// Internationalised domains can be entered using their ASCII (xn--) spelling.
inline std::string domain(std::string value)
{
    value = lower(value);
    if (!value.empty() && value.back() == '.') value.pop_back();
    if (value.empty() || value.size() > 253) return {};
    size_t start = 0;
    bool numeric_last = false;
    unsigned labels = 0;
    bool ipv4 = true;
    while (start < value.size())
    {
        const auto end = value.find('.', start);
        const auto label = value.substr(start, end == std::string::npos ? end : end - start);
        if (label.empty() || label.size() > 63 || label.front() == '-' || label.back() == '-') return {};
        bool digits = true;
        unsigned number = 0;
        for (const unsigned char c : label)
        {
            if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '-')) return {};
            digits = digits && c >= '0' && c <= '9';
            if (digits && number < 1000) number = number * 10 + c - '0';
        }
        // Browsers interpret numeric final labels as IPv4, including abbreviated,
        // octal and hexadecimal addresses. Only canonical dotted decimal is listable.
        numeric_last = digits || (label.size() > 2 && label.substr(0, 2) == "0x" &&
            label.find_first_not_of("0123456789abcdef", 2) == std::string::npos);
        ipv4 = ipv4 && digits && number <= 255 && (label.size() == 1 || label.front() != '0');
        ++labels;
        if (end == std::string::npos) break;
        start = end + 1;
        if (start == value.size()) return {};
    }
    if (numeric_last && !(ipv4 && labels == 4)) return {};
    return value;
}

struct Destination
{
    bool web = false;
    std::string host;
    std::string path;
    bool standard_https = false;
};

inline Destination destination(const std::string& url)
{
    const auto colon = url.find(':');
    auto scheme = lower(url.substr(0, colon));
    // Recognise then refuse schemes disguised by whitespace/control bytes that
    // browsers may strip. They must not fall through the non-web bypass.
    scheme.erase(std::remove_if(scheme.begin(), scheme.end(),
        [](unsigned char c) { return c <= 0x20 || c == 0x7f; }), scheme.end());
    if (scheme != "http" && scheme != "https") return {};
    Destination result;
    result.web = true;
    if (url.size() > 8192 || colon == std::string::npos || url.substr(colon, 3) != "://") return result;
    for (const unsigned char c : url) if (c <= 0x20 || c == 0x7f || c == '\\') return result;
    const auto start = colon + 3;
    const auto end = url.find_first_of("/?#", start);
    auto authority = url.substr(start, end - start);
    result.standard_https = scheme == "https";
    // Ambiguous/browser-specific authority forms are never trusted or opened by
    // this experimental path. No percent decoding, userinfo or IPv6 guessing.
    if (authority.find_first_of("%@[]") != std::string::npos) return result;
    const auto port = authority.find(':');
    if (port != std::string::npos)
    {
        const auto text = authority.substr(port + 1);
        if (text.empty() || text.size() > 5 || text.find_first_not_of("0123456789") != std::string::npos) return result;
        if (std::stoul(text) > 65535) return result;
        result.standard_https = result.standard_https && text == "443";
        authority.resize(port);
    }
    result.host = domain(authority);
    if (end != std::string::npos && url[end] == '/')
        result.path = url.substr(end, url.find_first_of("?#", end) - end);
    else result.path = "/";
    return result;
}

// Whole-domain trust remains exact. GitHub additionally supports HTTPS account
// or repository scopes, so one project need not trust the entire shared host.
inline std::string trustedRule(std::string value)
{
    if (value.find('/') == std::string::npos) return domain(value);
    value = lower(value);
    const std::string prefix = "github.com/";
    if (value.substr(0, prefix.size()) != prefix) return {};
    const auto parts = value.substr(prefix.size());
    const auto slash = parts.find('/');
    const auto owner = parts.substr(0, slash);
    if (owner.empty() || owner.size() > 39 || owner.front() == '-' || owner.back() == '-' ||
        owner.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789-") != std::string::npos) return {};
    if (slash != std::string::npos)
    {
        const auto repo = parts.substr(slash + 1);
        if (repo.empty() || repo.size() > 100 || repo == "." || repo == ".." ||
            repo.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789._-") != std::string::npos) return {};
    }
    return value;
}
inline std::string ruleHost(const std::string& value) { return value.substr(0, value.find('/')); }
inline bool githubScopeMatches(const std::string& rule, const Destination& target)
{
    if (target.host != "github.com" || !target.standard_https || rule.find('/') == std::string::npos) return false;
    // Browsers normalise dot segments and encoded paths. Do not guess whether an
    // ambiguous spelling still points into the selected GitHub account/repo.
    if (target.path.find('%') != std::string::npos) return false;
    size_t start = 1;
    while (start < target.path.size())
    {
        const auto end = target.path.find('/', start);
        const auto part = target.path.substr(start, end - start);
        if (part.empty() || part == "." || part == "..") return false;
        if (end == std::string::npos) break;
        start = end + 1;
    }
    const auto path = lower(target.path);
    const auto scope = rule.substr(rule.find('/'));
    return path == scope || (path.size() > scope.size() && path.substr(0, scope.size()) == scope && path[scope.size()] == '/');
}

struct Rules
{
    std::set<std::string> trusted;
    std::set<std::string> blocked;
};

enum class Decision { Bypass, Trusted, Ask, Blocked, Unsupported };
inline Decision decide(const std::string& url, bool enabled, const Rules& rules, bool warn_unlisted = true)
{
    if (!enabled) return Decision::Bypass;
    const auto target = destination(url);
    if (!target.web) return Decision::Bypass;
    if (target.host.empty()) return Decision::Unsupported;
    if (rules.blocked.count(target.host)) return Decision::Blocked;
    if (rules.trusted.count(target.host)) return Decision::Trusted;
    for (const auto& rule : rules.trusted)
        if (githubScopeMatches(rule, target)) return Decision::Trusted;
    return warn_unlisted ? Decision::Ask : Decision::Bypass;
}

// Reviewed first-party user-facing services; see OFFICIAL-SECOND-LIFE-SITES.md.
inline std::vector<std::pair<std::string, std::string>> officialSecondLifeSites()
{
    return {
        {"secondlife.com", "Second Life"}, {"www.secondlife.com", "Second Life"},
        {"join.secondlife.com", "Second Life signup"}, {"my.secondlife.com", "Second Life profiles"},
        {"accounts.secondlife.com", "Second Life accounts"}, {"id.secondlife.com", "Second Life sign-in"},
        {"marketplace.secondlife.com", "Second Life Marketplace (all languages)"},
        {"community.secondlife.com", "Second Life community and blogs"},
        {"blogs.secondlife.com", "Second Life legacy blog links"},
        {"support.secondlife.com", "Second Life support"}, {"lindenlab.freshdesk.com", "Linden Lab support tickets"},
        {"wiki.secondlife.com", "Second Life Wiki (all languages)"},
        {"create.secondlife.com", "Second Life creator documentation"},
        {"feedback.secondlife.com", "Second Life feedback"}, {"jira.secondlife.com", "Second Life legacy issue tracker"},
        {"status.secondlifegrid.net", "Second Life grid status"},
        {"maps.secondlife.com", "Second Life maps"}, {"slurl.com", "Second Life legacy map links"},
        {"www.slurl.com", "Second Life legacy map links"},
        {"search.secondlife.com", "Second Life search"}, {"world.secondlife.com", "Second Life public profile/place pages"},
        {"land.secondlife.com", "Second Life land and Linden Homes"}, {"places.secondlife.com", "Second Life places and auctions"},
        {"go.secondlife.com", "Second Life destinations and landing pages"},
        {"connect.secondlife.com", "Second Life enterprise and education"}, {"www.connect.secondlife.com", "Second Life enterprise and education"},
        {"second.life", "Second Life official short links (redirects)"},
        {"lindenlab.com", "Linden Lab"}, {"www.lindenlab.com", "Linden Lab"}, {"dmca.lindenlab.com", "Linden Lab DMCA reporting"},
        {"forums-archive.secondlife.com", "Second Life archived forums"}
    };
}
inline Rules defaults()
{
    Rules rules{{"primfeed.com", "www.primfeed.com", "flickr.com", "www.flickr.com",
                 "facebook.com", "www.facebook.com", "github.com/nekomisa"}, {}};
    for (const auto& site : officialSecondLifeSites()) rules.trusted.insert(site.first);
    return rules;
}

// Optional convenience suggestions, never automatically merged into saved rules.
// These service names identify common destinations, not a security endorsement.
inline std::vector<std::pair<std::string, std::string>> commonSites()
{
    auto sites = officialSecondLifeSites();
    const std::vector<std::pair<std::string, std::string>> additional = {
        {"github.com/nekomisa", "GitHub: NekoMisa's viewer projects"},
        {"primfeed.com", "Primfeed"}, {"www.primfeed.com", "Primfeed"},
        {"flickr.com", "Flickr"}, {"www.flickr.com", "Flickr"},
        {"facebook.com", "Facebook"}, {"www.facebook.com", "Facebook"},
        {"bsky.app", "Bluesky"}, {"discord.com", "Discord"},
        {"youtube.com", "YouTube"}, {"www.youtube.com", "YouTube"},
        {"vimeo.com", "Vimeo"}, {"www.vimeo.com", "Vimeo"},
        {"twitch.tv", "Twitch"}, {"www.twitch.tv", "Twitch"},
        {"reddit.com", "Reddit"}, {"www.reddit.com", "Reddit"},
        {"wikipedia.org", "Wikipedia"}, {"www.wikipedia.org", "Wikipedia"}, {"en.wikipedia.org", "Wikipedia (English)"},
        {"gimp.org", "GIMP"}, {"www.gimp.org", "GIMP"}, {"docs.gimp.org", "GIMP manual"},
        {"mozilla.org", "Mozilla"}, {"www.mozilla.org", "Mozilla"}, {"support.mozilla.org", "Mozilla support"},
        {"support.microsoft.com", "Microsoft support"}, {"learn.microsoft.com", "Microsoft Learn"}
    };
    sites.insert(sites.end(), additional.begin(), additional.end());
    return sites;
}
}
#endif
