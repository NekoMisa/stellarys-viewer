// SPDX-License-Identifier: LGPL-2.1-only
#ifndef LL_FLOATER_LINK_DOMAINS_H
#define LL_FLOATER_LINK_DOMAINS_H
#include "llfloater.h"
#include <functional>

namespace StellarysLinkSafety
{
// Entry point for clicked viewer-text links, including context-menu browser
// choices. The continuation preserves the existing internal/external routing.
void open(const std::string& url, std::function<void()> continuation);
}

class LLFloaterLinkDomains : public LLFloater
{
public:
    explicit LLFloaterLinkDomains(const LLSD& key) : LLFloater(key) {}
    bool postBuild() override;
    void onOpen(const LLSD& key) override;
private:
    void refresh();
    void edit(bool blocked, bool remove);
    void status(const std::string& text);
};

class LLFloaterCommonLinkDomains : public LLFloater
{
public:
    explicit LLFloaterCommonLinkDomains(const LLSD& key) : LLFloater(key) {}
    bool postBuild() override;
    void onOpen(const LLSD& key) override;
private:
    void refresh();
    void trustSelected();
};
#endif
