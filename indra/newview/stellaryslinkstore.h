// Persistent per-user rules, shared by the viewer and standalone tests.
// SPDX-License-Identifier: LGPL-2.1-only
#ifndef STELLARYS_LINK_STORE_H
#define STELLARYS_LINK_STORE_H
#include "stellaryslinkpolicy.h"
#include <filesystem>
#include <fstream>
#include <random>
#include <sstream>
#include <stdexcept>
#if defined(_WIN32)
#include <windows.h>
#else
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace StellarysLinks
{
inline constexpr size_t MAX_RULES = 2000;
inline constexpr size_t MAX_BYTES = 1024 * 1024;
inline constexpr const char* FILE_HEADER = "Stellarys link domains 1";
inline constexpr const char* SCOPED_FILE_HEADER = "Stellarys link domains 2";

class FileLock
{
public:
    explicit FileLock(const std::filesystem::path& path)
    {
#if defined(_WIN32)
        mHandle = CreateFileW(path.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr,
            OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
        BY_HANDLE_FILE_INFORMATION info{};
        if (mHandle == INVALID_HANDLE_VALUE || !GetFileInformationByHandle(mHandle, &info) ||
            (info.dwFileAttributes & (FILE_ATTRIBUTE_REPARSE_POINT | FILE_ATTRIBUTE_DIRECTORY)))
        {
            if (mHandle != INVALID_HANDLE_VALUE) CloseHandle(mHandle);
            throw std::runtime_error("The domain lists are busy or cannot be locked. Try again.");
        }
#else
        mFd = ::open(path.c_str(), O_CREAT | O_RDWR | O_NOFOLLOW | O_CLOEXEC, 0600);
        struct stat info{};
        if (mFd < 0 || ::fstat(mFd, &info) || !S_ISREG(info.st_mode) ||
            info.st_uid != ::getuid() || info.st_nlink != 1 || ::flock(mFd, LOCK_EX | LOCK_NB))
        {
            if (mFd >= 0) ::close(mFd);
            throw std::runtime_error("The domain lists are busy or cannot be locked. Try again.");
        }
#endif
    }
    ~FileLock()
    {
#if defined(_WIN32)
        CloseHandle(mHandle);
#else
        ::close(mFd);
#endif
    }
    FileLock(const FileLock&) = delete;
    FileLock& operator=(const FileLock&) = delete;
private:
#if defined(_WIN32)
    HANDLE mHandle = INVALID_HANDLE_VALUE;
#else
    int mFd = -1;
#endif
};

inline Rules parse(const std::string& bytes)
{
    if (bytes.size() > MAX_BYTES) throw std::runtime_error("The saved domain lists are too large. They were left unchanged.");
    std::istringstream input(bytes);
    std::string line;
    if (!std::getline(input, line) || (line != FILE_HEADER && line != SCOPED_FILE_HEADER))
        throw std::runtime_error("The saved domain lists could not be read. They were left unchanged.");
    const bool scoped = line == SCOPED_FILE_HEADER;
    Rules result;
    size_t count = 0;
    while (std::getline(input, line))
    {
        if (++count > MAX_RULES || line.size() < 3 || line[1] != ' ' || (line[0] != 'T' && line[0] != 'B'))
            throw std::runtime_error("The saved domain lists are invalid. They were left unchanged.");
        const auto host = line[0] == 'T' && scoped ? trustedRule(line.substr(2)) : domain(line.substr(2));
        if (host.empty() || host != line.substr(2))
            throw std::runtime_error("The saved domain lists are invalid. They were left unchanged.");
        (line[0] == 'T' ? result.trusted : result.blocked).insert(host);
    }
    // An explicit block always wins, including a hand-edited conflicting file.
    for (auto it = result.trusted.begin(); it != result.trusted.end();)
        if (result.blocked.count(ruleHost(*it))) it = result.trusted.erase(it); else ++it;
    return result;
}

inline std::string serialize(const Rules& rules)
{
    if (rules.trusted.size() + rules.blocked.size() > MAX_RULES)
        throw std::runtime_error("The domain lists are full. Remove an unused entry first.");
    const bool scoped = std::any_of(rules.trusted.begin(), rules.trusted.end(),
        [](const std::string& item) { return item.find('/') != std::string::npos; });
    std::string bytes = std::string(scoped ? SCOPED_FILE_HEADER : FILE_HEADER) + '\n';
    for (const auto& item : rules.trusted)
    {
        if (item.empty() || trustedRule(item) != item || rules.blocked.count(ruleHost(item)))
            throw std::runtime_error("Invalid trusted domain.");
        bytes += "T " + item + '\n';
    }
    for (const auto& item : rules.blocked)
    {
        if (item.empty() || domain(item) != item) throw std::runtime_error("Invalid blocked domain.");
        bytes += "B " + item + '\n';
    }
    return bytes;
}

class Store
{
public:
    explicit Store(std::filesystem::path file) : mFile(std::move(file)) {}
    Rules read()
    {
        FileLock lock(lockPath());
        return readUnlocked();
    }
    // Each edit re-reads the current file under the interprocess lock; an older
    // open settings window never writes a stale copy over another viewer's edits.
    Rules edit(const std::string& value, bool blocked, bool remove = false, bool refuse_blocked = false)
    {
        const auto host = blocked ? domain(value) : trustedRule(value);
        if (host.empty()) throw std::runtime_error("Enter an exact domain or a trusted GitHub account/repository path, without https://, a port or wildcard.");
        FileLock lock(lockPath());
        auto rules = readUnlocked();
        if (refuse_blocked && rules.blocked.count(ruleHost(host))) return rules;
        if (remove) (blocked ? rules.blocked : rules.trusted).erase(host);
        else
        {
            if (!blocked && host.find('/') != std::string::npos && rules.blocked.count(ruleHost(host)))
                throw std::runtime_error("Remove the blocked GitHub domain before trusting a specific account or repository.");
            if (blocked)
            {
                for (auto it = rules.trusted.begin(); it != rules.trusted.end();)
                    if (ruleHost(*it) == host) it = rules.trusted.erase(it); else ++it;
            }
            (blocked ? rules.trusted : rules.blocked).erase(host);
            (blocked ? rules.blocked : rules.trusted).insert(host);
        }
        writeUnlocked(rules);
        return rules;
    }
    std::filesystem::path lockPath() const { auto p = mFile; p += ".lock"; return p; }
    Rules trustSelected(const std::set<std::string>& selected)
    {
        for (const auto& value : selected)
            if (value.empty() || trustedRule(value) != value) throw std::runtime_error("Invalid selected trusted site.");
        FileLock lock(lockPath());
        auto rules = readUnlocked();
        // Re-read under the lock: a new block always wins over an older picker.
        for (const auto& host : selected)
            if (!rules.blocked.count(ruleHost(host))) rules.trusted.insert(host);
        if (!selected.empty()) writeUnlocked(rules);
        return rules;
    }
private:
    Rules readUnlocked()
    {
        if (std::filesystem::is_symlink(mFile)) throw std::runtime_error("The saved domain file is a link. It was left unchanged.");
        if (!std::filesystem::exists(mFile))
        {
            auto rules = defaults();
            writeUnlocked(rules);
            return rules;
        }
        if (!std::filesystem::is_regular_file(mFile) || std::filesystem::file_size(mFile) > MAX_BYTES)
            throw std::runtime_error("The saved domain lists are invalid or too large. They were left unchanged.");
        std::ifstream input(mFile, std::ios::binary);
        if (!input) throw std::runtime_error("The saved domain lists could not be read. They were left unchanged.");
        std::string bytes(MAX_BYTES + 1, '\0');
        input.read(&bytes[0], bytes.size());
        const auto size = input.gcount();
        if (input.bad() || size > static_cast<std::streamsize>(MAX_BYTES)) throw std::runtime_error("The saved domain lists could not be read. They were left unchanged.");
        bytes.resize(size);
        return parse(bytes);
    }
    void writeUnlocked(const Rules& rules)
    {
        const auto bytes = serialize(rules);
        auto temporary = mFile;
        temporary += ".tmp." + std::to_string(std::random_device{}());
        if (std::filesystem::exists(temporary) || std::filesystem::is_symlink(temporary))
            throw std::runtime_error("Could not create a temporary domain file. Your lists are unchanged.");
        try
        {
            std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
#if !defined(_WIN32)
            std::filesystem::permissions(temporary, std::filesystem::perms::owner_read | std::filesystem::perms::owner_write);
#endif
            output.write(bytes.data(), bytes.size()); output.flush();
            const bool ok = output.good(); output.close();
            if (!ok || output.fail()) throw std::runtime_error("Could not save the domain lists. Your previous lists are unchanged.");
#if defined(_WIN32)
            if (!MoveFileExW(temporary.c_str(), mFile.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH))
                throw std::runtime_error("Could not replace the domain file. Your previous lists are unchanged.");
#else
            std::filesystem::rename(temporary, mFile);
#endif
        }
        catch (...)
        {
            std::error_code unused; std::filesystem::remove(temporary, unused);
            throw;
        }
    }
    std::filesystem::path mFile;
};
}
#endif
