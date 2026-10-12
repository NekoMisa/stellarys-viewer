// SPDX-License-Identifier: LGPL-2.1-only
#include "llviewerprecompiledheaders.h"
#include "llfloaterlinkdomains.h"
#include "stellaryslinkstore.h"
#include "llbutton.h"
#include "lldir.h"
#include "llfloaterreg.h"
#include "lllineeditor.h"
#include "llnotificationsutil.h"
#include "llscrolllistctrl.h"
#include "llscrolllistitem.h"
#include "lltextbox.h"
#include "llviewercontrol.h"

namespace
{
StellarysLinks::Store store()
{
    const auto name = gDirUtilp->getExpandedFilename(LL_PATH_USER_SETTINGS, "stellarys_link_domains.txt");
#if defined(__cpp_char8_t)
    return StellarysLinks::Store(std::filesystem::path(std::u8string(name.begin(), name.end())));
#else
    return StellarysLinks::Store(std::filesystem::u8path(name));
#endif
}
void unavailable()
{
    // Do not disclose the URL or local file path through logging or an exception.
    LLNotificationsUtil::add("StellarysLinkListsUnavailable");
}
void blocked(const std::string& host)
{
    LLSD args; args["DOMAIN"] = host;
    LLNotificationsUtil::add("StellarysLinkBlocked", args, LLSD(),
        [](const LLSD& notification, const LLSD& response)
        {
            if (LLNotificationsUtil::getSelectedOption(notification, response) == 0)
                LLFloaterReg::showInstance("stellarys_link_domains");
        });
}
}

void StellarysLinkSafety::open(const std::string& url, std::function<void()> continuation)
{
    if (!gSavedSettings.getBOOL("StellarysLinkWarningsEnabled") || !StellarysLinks::destination(url).web)
    {
        continuation();
        return;
    }
    StellarysLinks::Rules rules;
    try { rules = store().read(); }
    catch (const std::exception&) { unavailable(); return; }
    const auto decision = StellarysLinks::decide(url, true, rules, gSavedSettings.getBOOL("StellarysWarnUnlistedLinks"));
    const auto host = StellarysLinks::destination(url).host;
    if (decision == StellarysLinks::Decision::Trusted || decision == StellarysLinks::Decision::Bypass) { continuation(); return; }
    if (decision == StellarysLinks::Decision::Blocked) { blocked(host); return; }
    if (decision == StellarysLinks::Decision::Unsupported)
    {
        LLNotificationsUtil::add("StellarysLinkUnsupported");
        return;
    }
    LLSD args; args["DOMAIN"] = host; args["DESTINATION"] = url;
    LLNotificationsUtil::add("StellarysLinkUnknown", args, LLSD(),
        [host, continuation](const LLSD& notification, const LLSD& response)
        {
            const auto option = LLNotificationsUtil::getSelectedOption(notification, response);
            if (option != 0 && option != 1 && option != 2) return;
            try
            {
                if (option == 2)
                {
                    store().edit(host, true);
                    blocked(host);
                    return;
                }
                // Lists may have changed while the dialog was open. An explicit
                // block in another viewer must never be undone by an old prompt.
                auto current = store().read();
                if (current.blocked.count(host)) { blocked(host); return; }
                if (option == 1 && store().edit(host, false, false, true).blocked.count(host))
                { blocked(host); return; }
            }
            catch (const std::exception&) { unavailable(); return; }
            continuation();
        });
}

bool LLFloaterLinkDomains::postBuild()
{
    getChild<LLButton>("add_trusted")->setCommitCallback([this](LLUICtrl*, const LLSD&) { edit(false, false); });
    getChild<LLButton>("add_blocked")->setCommitCallback([this](LLUICtrl*, const LLSD&) { edit(true, false); });
    getChild<LLButton>("remove_trusted")->setCommitCallback([this](LLUICtrl*, const LLSD&) { edit(false, true); });
    getChild<LLButton>("remove_blocked")->setCommitCallback([this](LLUICtrl*, const LLSD&) { edit(true, true); });
    getChild<LLButton>("refresh")->setCommitCallback([this](LLUICtrl*, const LLSD&) { refresh(); });
    getChild<LLScrollListCtrl>("trusted")->setCommitCallback([this](LLUICtrl*, const LLSD&)
        { getChildView("remove_trusted")->setEnabled(getChild<LLScrollListCtrl>("trusted")->getFirstSelected() != nullptr); });
    getChild<LLScrollListCtrl>("blocked")->setCommitCallback([this](LLUICtrl*, const LLSD&)
        { getChildView("remove_blocked")->setEnabled(getChild<LLScrollListCtrl>("blocked")->getFirstSelected() != nullptr); });
    return true;
}
void LLFloaterLinkDomains::onOpen(const LLSD&) { refresh(); }
void LLFloaterLinkDomains::status(const std::string& text) { getChild<LLTextBox>("status")->setText(text); }
void LLFloaterLinkDomains::refresh()
{
    auto* trusted = getChild<LLScrollListCtrl>("trusted");
    auto* denied = getChild<LLScrollListCtrl>("blocked");
    trusted->deleteAllItems(); denied->deleteAllItems();
    getChildView("remove_trusted")->setEnabled(false); getChildView("remove_blocked")->setEnabled(false);
    try
    {
        const auto rules = store().read();
        for (const auto& host : rules.trusted) trusted->addSimpleElement(host, ADD_BOTTOM, host);
        for (const auto& host : rules.blocked) denied->addSimpleElement(host, ADD_BOTTOM, host);
        getChildView("add_trusted")->setEnabled(true); getChildView("add_blocked")->setEnabled(true);
        status("Changes save immediately for this computer user and survive viewer updates.");
    }
    catch (const std::exception&)
    {
        getChildView("add_trusted")->setEnabled(false); getChildView("add_blocked")->setEnabled(false);
        status("The lists are busy or unreadable. Existing files are unchanged. Try Refresh; no web link will open while enabled until the lists can be read.");
    }
}
void LLFloaterLinkDomains::edit(bool denied, bool remove)
{
    const auto host = remove ? getChild<LLScrollListCtrl>(denied ? "blocked" : "trusted")->getSelectedValue().asString()
                             : getChild<LLLineEditor>("domain")->getText();
    if (remove && host.empty()) return;
    try
    {
        store().edit(host, denied, remove);
        if (!remove) getChild<LLLineEditor>("domain")->setText(std::string());
        refresh();
    }
    catch (const std::exception&)
    {
        status("Could not save. Enter an exact ASCII domain without https://, a path, port or wildcard. If the lists are busy, try Refresh. Existing entries are unchanged.");
    }
}

bool LLFloaterCommonLinkDomains::postBuild()
{
    getChild<LLButton>("trust_selected")->setCommitCallback([this](LLUICtrl*, const LLSD&) { trustSelected(); });
    getChild<LLButton>("refresh")->setCommitCallback([this](LLUICtrl*, const LLSD&) { refresh(); });
    getChild<LLButton>("close")->setCommitCallback([this](LLUICtrl*, const LLSD&) { closeFloater(); });
    getChild<LLScrollListCtrl>("suggestions")->setCommitCallback([this](LLUICtrl*, const LLSD&)
        { getChildView("trust_selected")->setEnabled(getChild<LLScrollListCtrl>("suggestions")->getNumSelected() > 0); });
    return true;
}
void LLFloaterCommonLinkDomains::onOpen(const LLSD&) { refresh(); }
void LLFloaterCommonLinkDomains::refresh()
{
    auto* list = getChild<LLScrollListCtrl>("suggestions");
    list->deleteAllItems();
    getChildView("trust_selected")->setEnabled(false);
    try
    {
        const auto rules = store().read();
        for (const auto& site : StellarysLinks::commonSites())
        {
            if (rules.trusted.count(site.first) || rules.blocked.count(site.first)) continue;
            LLSD row;
            row["value"] = site.first;
            row["columns"][0]["column"] = "service";
            row["columns"][0]["value"] = site.second;
            row["columns"][1]["column"] = "domain";
            row["columns"][1]["value"] = site.first;
            list->addElement(row);
        }
        getChild<LLTextBox>("status")->setText(std::string("Nothing is selected automatically. Existing trusted and blocked domains are omitted."));
    }
    catch (const std::exception&)
    {
        getChild<LLTextBox>("status")->setText(std::string("The lists are busy or unreadable. Existing files are unchanged. Try Refresh."));
    }
}
void LLFloaterCommonLinkDomains::trustSelected()
{
    std::set<std::string> selected;
    for (const auto* item : getChild<LLScrollListCtrl>("suggestions")->getAllSelected()) selected.insert(item->getValue().asString());
    if (selected.empty()) return;
    try
    {
        store().trustSelected(selected);
        refresh();
        if (auto* manager = LLFloaterReg::findTypedInstance<LLFloaterLinkDomains>("stellarys_link_domains")) manager->onOpen(LLSD());
        getChild<LLTextBox>("status")->setText(std::string("Selected domains saved. Any newer blocks were kept. Other entries are unchanged."));
    }
    catch (const std::exception&)
    {
        getChild<LLTextBox>("status")->setText(std::string("Could not save the selection. Existing entries are unchanged. Try Refresh."));
    }
}
