// Tests use the actual policy/store headers and disposable profiles only.
// SPDX-License-Identifier: LGPL-2.1-only
#include "../../indra/newview/stellaryslinkstore.h"
#include <iostream>

using namespace StellarysLinks;
void expect(bool condition, const char* message)
{ if (!condition) throw std::runtime_error(message); }
template<typename F> void refuses(F function, const char* message)
{
    bool failed = false;
    try { function(); } catch (const std::exception&) { failed = true; }
    expect(failed, message);
}
std::string readBytes(const std::filesystem::path& p)
{ std::ifstream s(p, std::ios::binary); return {std::istreambuf_iterator<char>(s), {}}; }
void put(const std::filesystem::path& p, const std::string& text)
{ std::ofstream s(p, std::ios::binary); s << text; }

int main()
{
    auto root = std::filesystem::temp_directory_path() / ("stellarys-links-test-" + std::to_string(std::random_device{}()));
    std::filesystem::create_directory(root);
    try
    {
        auto rules = defaults();
        std::set<std::string> suggestions;
        for (const auto& site : commonSites())
        {
            expect(!site.second.empty() && trustedRule(site.first) == site.first, "Invalid common-site suggestion");
            expect(suggestions.insert(site.first).second, "Duplicate common-site suggestion");
        }
        expect(suggestions.size() > rules.trusted.size(), "Common sites were not expanded");
        std::cout << "Catalogue: " << officialSecondLifeSites().size() << " official Second Life domains; "
                  << suggestions.size() << " suggestions; " << rules.trusted.size() << " new-profile trusted entries\n";
        expect(!suggestions.count("github.com") && !suggestions.count("t.co") && !suggestions.count("bit.ly"), "Shared download/shortener hosts suggested");
        for (const auto& site : officialSecondLifeSites())
            expect(rules.trusted.count(site.first) && suggestions.count(site.first), "Official site missing from new-profile defaults or catalogue");
        for (const auto& lang : {"en-US", "de-DE", "es-ES", "fr-FR", "ja-JP", "pt-BR"})
            expect(decide(std::string("https://marketplace.secondlife.com/?lang=") + lang, true, rules) == Decision::Trusted, "Marketplace language unexpectedly warns");
        expect(decide("https://wiki.secondlife.com/wiki/LSL_Portal/fr", true, rules) == Decision::Trusted, "Localized Wiki path unexpectedly warns");
        for (const auto& url : {"https://github.com/NekoMisa", "https://github.com/NekoMisa?tab=repositories",
            "https://github.com/NekoMisa/stellarys-viewer/releases", "https://github.com/NekoMisa/Black-Dragon---Black-Kitty-Fix",
            "https://github.com:443/nekomisa/stellarys-viewer/"})
            expect(decide(url, true, rules) == Decision::Trusted, "NekoMisa GitHub scope did not match");
        for (const auto& url : {"https://github.com/other-owner/project", "https://github.com/NekoMisa-lookalike/project",
            "https://github.com/NekoMisa/../other-owner/project", "https://github.com/NekoMisa/%2e%2e/other-owner",
            "https://github.com/NekoMisa//../other-owner", "https://github.com/NekoMisa/./project", "https://github.com/%4eekoMisa/project",
            "https://github.com/?next=/NekoMisa/project", "http://github.com/NekoMisa/project", "https://github.com:444/NekoMisa/project",
            "https://github.com.evil.example/NekoMisa/project", "https://raw.githubusercontent.com/NekoMisa/project/main/file"})
            expect(decide(url, true, rules) == Decision::Ask, "GitHub scoped trust escaped its HTTPS account boundary");
        Rules repo_only{{"github.com/nekomisa/stellarys-viewer"},{}};
        expect(decide("https://github.com/NekoMisa/Stellarys-Viewer/releases", true, repo_only) == Decision::Trusted, "Repository scope did not match");
        expect(decide("https://github.com/NekoMisa/stellarys-viewer-other", true, repo_only) == Decision::Ask, "Repository scope matched a prefix lookalike");
        repo_only.blocked.insert("github.com");
        expect(decide("https://github.com/NekoMisa/stellarys-viewer", true, repo_only) == Decision::Blocked, "GitHub path bypassed a domain block");
        expect(decide("https://secondlife.com/path", false, rules) == Decision::Bypass, "Disabled changes legacy behavior");
        expect(decide("https://evil.example/", false, rules) == Decision::Bypass, "Disabled warns on unknown");
        for (const auto& url : {"https://secondlife.com", "HTTP://SECONDlife.COM:80/path?x=a#b", "https://secondlife.com./"})
            expect(decide(url, true, rules) == Decision::Trusted, "Normal trusted URL not recognised");
        for (const auto& url : {"https://secondlife.com.evil.example/", "https://fake-secondlife.com/", "https://evil.example/?to=secondlife.com", "https://sub.secondlife.com/", "https://notsecondlife.com/"})
            expect(decide(url, true, rules) == Decision::Ask, "Lookalike/subdomain/query silently trusted");
        for (const auto& url : {"secondlife://Region/1/2/3", "hop://grid/Region/1/2/3", "mailto:hello@example.com", "file:///local/welcome.html"})
            expect(decide(url, true, rules) == Decision::Bypass, "Non-web behavior changed");
        for (const auto& url : {"https://secondlife.com@evil.example/", "https://evil.example@secondlife.com/",
             "https://%73econdlife.com/", "https://secondlife.com\\@evil.example/", "https:///secondlife.com/",
             "https://secondlife.com:bad/", "https://secondlife.com:65536/", "https://secondlife.com:/",
             "https://secondlife..com/", "https://secondlife.com../", "https://127.1/", "http://2130706433/",
             "http://0177.0.0.1/", "http://0x7f.0.0.1/", "http://0x7f000001/", "http://[::1]/",
             "\thttps://secondlife.com/", "ht\ttp://secondlife.com/", "https://second\nlife.com/",
             "https://secondlife.com%00.evil.example/", "https://secondlife.com /"})
            expect(decide(url, true, rules) == Decision::Unsupported, "Ambiguous authority accepted");
        expect(destination("https://example.com/\xc3\xa6").host == "example.com", "Unicode path rejected");
        expect(destination("https://\xc3\xa6.example/").host.empty(), "Unicode host silently trusted");
        expect(domain("XN--BCHER-KVA.example.") == "xn--bcher-kva.example", "ASCII IDN normalization failed");
        expect(destination("http://127.0.0.1:8080/").host == "127.0.0.1", "Canonical IPv4 failed");
        for (const auto& value : {"*.example.com", "https://example.com", "example.com/path", "example.com:443", "user@example.com", "example.com\n", "-example.com", "example-.com", "example.com.."})
            expect(domain(value).empty(), "Invalid editor entry accepted");
        rules.blocked.insert("secondlife.com");
        expect(decide("https://secondlife.com", true, rules) == Decision::Blocked, "Block loses to trust");
        expect(decide("https://secondlife.com", false, rules) == Decision::Bypass, "Disabled unexpectedly blocks");
        expect(decide("https://secondlife.com", true, rules, false) == Decision::Blocked, "Block-only mode ignored block/trust precedence");
        expect(decide("https://unlisted.example/path", true, rules, false) == Decision::Bypass, "Block-only mode prompted on unlisted domain");
        expect(decide("https://primfeed.com", true, rules, false) == Decision::Trusted, "Block-only mode changed trusted handling");
        expect(decide("https://secondlife.com", false, rules, false) == Decision::Bypass, "Master switch did not disable block-only mode");
        expect(decide("https://%73econdlife.com", true, rules, false) == Decision::Unsupported, "Block-only mode bypassed ambiguous authority rejection");
        expect(decide("secondlife://Region/1/2/3", true, rules, false) == Decision::Bypass, "Block-only mode changed SLURL handling");

        auto file = root / "profile" / "stellarys_link_domains.txt";
        std::filesystem::create_directory(file.parent_path());
        Store first(file);
        expect(first.read().trusted.count("primfeed.com") == 1, "First-run defaults missing");
        expect(std::filesystem::is_regular_file(file), "Defaults not persisted");
        auto legacy_file = root / "profile" / "legacy.txt";
        const std::string legacy_bytes = std::string(FILE_HEADER) + "\nT secondlife.com\nT personal.example\nB github.com\n";
        put(legacy_file, legacy_bytes);
        Store legacy(legacy_file);
        auto legacy_rules = legacy.read();
        expect(legacy_rules.trusted.count("personal.example") && !legacy_rules.trusted.count("community.secondlife.com") &&
            !legacy_rules.trusted.count("github.com/nekomisa") && legacy_rules.blocked.count("github.com"), "Expanded defaults changed an older saved list");
        expect(readBytes(legacy_file) == legacy_bytes, "Reading a legacy list rewrote it");
        legacy.trustSelected({"github.com/nekomisa", "community.secondlife.com"});
        expect(!legacy.read().trusted.count("github.com/nekomisa") && legacy.read().blocked.count("github.com"), "GitHub import removed a saved domain block");
        legacy.edit("github.com", true, true);
        legacy.trustSelected({"github.com/nekomisa"});
        expect(readBytes(legacy_file).find(SCOPED_FILE_HEADER) == 0, "GitHub scopes did not use the scoped file format");
        expect(legacy.read().trusted.count("personal.example") && legacy.read().trusted.count("github.com/nekomisa"), "Scoped format lost personal entries");
        legacy.edit("github.com", true);
        expect(!legacy.read().trusted.count("github.com/nekomisa"), "Domain block did not remove its scoped trust");
        legacy.edit("github.com", true, true);
        expect(!legacy.read().trusted.count("github.com/nekomisa"), "Removing a block resurrected scoped trust");
        for (const auto& bad : {"github.com/nekomisa/..", "github.com/nekomisa/../other", "github.com/nekomisa%2fother", "github.com/-owner", "example.com/path"})
            expect(trustedRule(bad).empty(), "Ambiguous trusted site accepted");
        first.edit("primfeed.com", false, true);
        first.edit("my.example", false);
        first.edit("bad.example", true);
        Store after_update(file);
        auto restored = after_update.read();
        expect(!restored.trusted.count("primfeed.com"), "Update restored a removed default");
        expect(restored.trusted.count("my.example") && restored.blocked.count("bad.example"), "New instance lost personal rules");
        first.edit("my.example", true);
        expect(!after_update.read().trusted.count("my.example"), "Block did not remove trust");
        expect(after_update.edit("my.example", false, false, true).blocked.count("my.example"), "Old trust prompt undid newer block");
        after_update.edit("other.example", false);
        expect(first.read().blocked.count("my.example") && first.read().trusted.count("other.example"), "Stale instance lost newer changes");
        after_update.edit("my.example", false);
        expect(!first.read().blocked.count("my.example"), "Explicit editor trust did not remove block");

        first.edit("discord.com", true);
        after_update.trustSelected({"discord.com", "youtube.com"});
        auto imported = first.read();
        expect(imported.blocked.count("discord.com") && !imported.trusted.count("discord.com"), "Picker import overrode a newer block");
        expect(imported.trusted.count("youtube.com") && imported.trusted.count("other.example"), "Picker import replaced personal entries");
        expect(!imported.trusted.count("primfeed.com"), "Picker import restored an unselected removed default");
        const auto before_invalid_import = readBytes(file);
        refuses([&] { first.trustSelected({"vimeo.com", "https://invalid.example"}); }, "Invalid picker selection saved");
        expect(readBytes(file) == before_invalid_import, "Invalid import partially saved");

        const auto before = readBytes(file);
        {
            FileLock held(first.lockPath());
            refuses([&] { after_update.edit("locked.example", false); }, "Concurrent writer was allowed");
            refuses([&] { after_update.trustSelected({"vimeo.com"}); }, "Picker import bypassed exclusive lock");
            refuses([&] { after_update.read(); }, "Concurrent read bypassed exclusive lock");
        }
        expect(readBytes(file) == before, "Locked operation changed saved lists");
        refuses([&] { first.edit("https://invalid.example", false); }, "Invalid entry saved");
        expect(readBytes(file) == before, "Invalid entry changed saved lists");
        for (const auto& bytes : {std::string("Stellarys link domains 3\nT example.com\n"), std::string("broken"),
             std::string(FILE_HEADER) + "\nT https://invalid.example\n", std::string(MAX_BYTES + 1, 'x')})
        {
            put(file, bytes);
            refuses([&] { first.read(); }, "Malformed/future/oversized file accepted");
            refuses([&] { first.edit("new.example", false); }, "Malformed file overwritten");
            expect(readBytes(file) == bytes, "Unreadable saved file reset");
        }
        put(file, std::string(FILE_HEADER) + "\n");
        expect(first.read().trusted.empty() && first.read().blocked.empty(), "Empty saved lists reset to defaults");
        expect(parse(std::string(FILE_HEADER) + "\nT example.com\nB example.com\n").trusted.empty(), "Conflicting saved block loses");
        refuses([&] { parse(std::string(FILE_HEADER) + "\nT github.com/nekomisa\n"); }, "Version-1 file silently accepted scoped syntax");
        auto scoped_conflict = parse(std::string(SCOPED_FILE_HEADER) + "\nT github.com/nekomisa\nT github.com/nekomisa/stellarys-viewer\nB github.com\n");
        expect(scoped_conflict.trusted.empty() && scoped_conflict.blocked.count("github.com"), "Hand-edited scoped trusts bypassed a domain block");
        expect(serialize(parse(before)) == before, "Saved rules do not round-trip");
#if !defined(_WIN32)
        expect((std::filesystem::status(file).permissions() & std::filesystem::perms::all) ==
            (std::filesystem::perms::owner_read | std::filesystem::perms::owner_write), "Saved lists are not private to this user");
        expect((std::filesystem::status(first.lockPath()).permissions() & std::filesystem::perms::all) ==
            (std::filesystem::perms::owner_read | std::filesystem::perms::owner_write), "Rule lock is not private to this user");
        put(file, before);
        std::filesystem::permissions(file.parent_path(), std::filesystem::perms::owner_read | std::filesystem::perms::owner_exec);
        if (::getuid() != 0) refuses([&] { first.edit("full.example", false); }, "Write failure not reported");
        std::filesystem::permissions(file.parent_path(), std::filesystem::perms::owner_all);
        expect(readBytes(file) == before, "Failed save damaged old rules");
        auto other = root / "other.txt"; put(other, before);
        std::filesystem::remove(file); std::filesystem::create_symlink(other, file);
        refuses([&] { first.edit("symlink.example", false); }, "Symlink file overwritten");
        expect(readBytes(other) == before, "Symlink target changed");
#endif
        std::filesystem::remove_all(root);
        std::cout << "PASS: destination, exact-domain/disabled decisions, persistence, removed defaults, blocked precedence, stale views, lock, corrupt/future/oversized files and failed saves\n";
        return 0;
    }
    catch (const std::exception& e)
    {
        std::cerr << "FAIL: " << e.what() << '\n';
        std::filesystem::permissions(root / "profile", std::filesystem::perms::owner_all);
        std::filesystem::remove_all(root);
        return 1;
    }
}
