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
    auto authority = url.substr(start, url.find_first_of("/?#", start) - start);
    // Ambiguous/browser-specific authority forms are never trusted or opened by
    // this experimental path. No percent decoding, userinfo or IPv6 guessing.
    if (authority.find_first_of("%@[]") != std::string::npos) return result;
    const auto port = authority.find(':');
    if (port != std::string::npos)
    {
        const auto text = authority.substr(port + 1);
        if (text.empty() || text.size() > 5 || text.find_first_not_of("0123456789") != std::string::npos) return result;
        if (std::stoul(text) > 65535) return result;
        authority.resize(port);
    }
    result.host = domain(authority);
    return result;
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
    return warn_unlisted ? Decision::Ask : Decision::Bypass;
}

inline Rules defaults()
{
    return {{"primfeed.com", "www.primfeed.com", "secondlife.com", "www.secondlife.com",
             "my.secondlife.com", "marketplace.secondlife.com", "support.secondlife.com",
             "wiki.secondlife.com", "maps.secondlife.com", "flickr.com", "www.flickr.com",
             "facebook.com", "www.facebook.com"}, {}};
}

// Optional convenience suggestions, never automatically merged into saved rules.
// These service names identify common destinations, not a security endorsement.
inline std::vector<std::pair<std::string, std::string>> commonSites()
{
    return {
        {"secondlife.com", "Second Life"}, {"www.secondlife.com", "Second Life"},
        {"my.secondlife.com", "Second Life"}, {"marketplace.secondlife.com", "Second Life Marketplace"},
        {"support.secondlife.com", "Second Life support"}, {"wiki.secondlife.com", "Second Life Wiki"},
        {"maps.secondlife.com", "Second Life maps"}, {"community.secondlife.com", "Second Life community"},
        {"feedback.secondlife.com", "Second Life feedback"},
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
}
}
#endif
