// Stellarys Edit Outfit layer ordering. SPDX-License-Identifier: LGPL-2.1-only
#include "llviewerprecompiledheaders.h"
#include "llwearablelayerorder.h"
#include "stellaryslayerorder.h"
#include "llagent.h"
#include "llagentwearables.h"
#include "llappearancemgr.h"
#include "llbutton.h"
#include "llcallbacklist.h"
#include "llfloaterreg.h"
#include "llinventoryfunctions.h"
#include "llnotificationsutil.h"
#include "llspinctrl.h"
#include "lltextbox.h"
#include "llviewerinventory.h"
#include "llvoavatarself.h"
#include <cmath>
#include <set>

// Shared with LLAppearanceMgr's existing adjacent-layer action.
std::string build_order_string(LLWearableType::EType type, U32 index);

namespace LLWearableLayerOrder
{
bool capture(const LLUUID& item_id, Snapshot& out, std::string& error)
{
    out = Snapshot();
    auto& appearance = LLAppearanceMgr::instance();
    if (!isAgentAvatarValid() || !gAgentWearables.areWearablesLoaded() ||
        appearance.isOutfitLocked() || appearance.isInUpdateAppearanceFromCOF())
    {
        error = "Please wait for your outfit to finish loading or changing, then try again.";
        return false;
    }
    auto* selected = gInventory.getItem(item_id);
    if (!selected || selected->getType() != LLAssetType::AT_CLOTHING ||
        !selected->getIsLinkType() || selected->getIsBrokenLink() ||
        selected->getParentUUID() != appearance.getCOF())
    {
        error = "Choose a worn clothing layer in Edit Outfit.";
        return false;
    }
    out.agent = gAgent.getID();
    out.session = gAgent.getSessionID();
    out.cof = appearance.getCOF();
    out.selected = item_id;
    out.type = selected->getWearableType();
    const U32 count = gAgentWearables.getWearableCount(out.type);
    if (count < 2)
    {
        error = "There must be at least two worn layers of the same clothing type.";
        return false;
    }
    LLInventoryModel::cat_array_t cats;
    LLInventoryModel::item_array_t links;
    LLFindWearablesOfType filter(out.type);
    gInventory.collectDescendentsIf(out.cof, cats, links, true, filter);
    std::set<LLUUID> seen;
    for (U32 i = 0; i < count; ++i)
    {
        const LLUUID id = gAgentWearables.getWearableItemID(out.type, i);
        LLViewerInventoryItem* match = nullptr;
        for (auto& link : links)
        {
            if (link->getLinkedUUID() != id) continue;
            if (match) { error = "Your outfit is still synchronising. Please try again shortly."; return false; }
            match = link;
        }
        if (id.isNull() || !seen.insert(id).second || !match || !match->getIsLinkType() ||
            match->getIsBrokenLink() || match->getParentUUID() != out.cof)
        {
            error = "Your outfit is still synchronising. Please try again shortly.";
            return false;
        }
        out.items.push_back(id);
        out.links.push_back(match->getUUID());
        out.descriptions.push_back(match->getActualDescription());
        if (match->getUUID() == item_id) out.source = static_cast<int>(i);
    }
    if (links.size() != count || out.source < 0)
    {
        error = "Your outfit is still synchronising. Please try again shortly.";
        return false;
    }
    return true;
}

bool apply(const Snapshot& saved, int destination, std::string& error)
{
    Snapshot now;
    if (!capture(saved.selected, now, error)) return false;
    if (saved.agent != now.agent || saved.session != now.session || saved.cof != now.cof || saved.type != now.type ||
        saved.items != now.items || saved.links != now.links || saved.descriptions != now.descriptions ||
        saved.source != now.source)
    {
        error = "The layer order changed. Please choose the layer and try again.";
        return false;
    }
    const auto order = StellarysLayerOrder::plan(static_cast<int>(now.items.size()), now.source, destination);
    if (order.empty()) { error = "Choose a position within this clothing type."; return false; }
    if (destination == now.source) return true;
    auto* item = gInventory.getItem(now.selected);
    int current = now.source;
    // Only local pointer swaps here: no intermediate COF requests, appearance updates or bakes.
    while (current != destination)
    {
        const bool down = destination < current;
        if (!gAgentWearables.moveWearable(item, down))
        {
            while (current != now.source)
            {
                const bool undo_down = now.source < current;
                if (!gAgentWearables.moveWearable(item, undo_down)) break;
                current += undo_down ? -1 : 1;
            }
            error = "The layer could not be moved. Please reopen Edit Outfit and try again.";
            return false;
        }
        current += down ? -1 : 1;
    }
    for (int i = 0; i < static_cast<int>(order.size()); ++i)
    {
        auto* link = gInventory.getItem(now.links[order[i]]);
        const std::string description = build_order_string(now.type, i);
        if (link->getActualDescription() == description) continue;
        link->setDescription(description);
        link->setComplete(true);
        link->updateServer(false);
        gInventory.updateItem(link);
    }
    gAgentAvatarp->wearableUpdated(now.type, false);
    LLAppearanceMgr::instance().setOutfitDirty(true);
    gInventory.notifyObservers();
    return true;
}

void enqueue(const Snapshot& snapshot, int destination)
{
    // Observer callbacks may rebuild and destroy the row which received the mouse event.
    doOnIdleOneTime([snapshot, destination]() {
        std::string error;
        if (!apply(snapshot, destination, error))
            LLNotificationsUtil::add("GenericAlert", LLSD().with("MESSAGE", error));
    });
}

void prompt(const LLUUID& item)
{
    LLFloaterReg::showInstance("stellarys_layer_position", LLSD(item));
}
}

bool LLFloaterWearableLayerOrder::postBuild()
{
    getChild<LLButton>("cancel")->setCommitCallback([this](LLUICtrl*, const LLSD&) { closeFloater(); });
    getChild<LLButton>("move")->setCommitCallback([this](LLUICtrl*, const LLSD&) {
        const F32 value = getChild<LLSpinCtrl>("position")->getValueF32();
        if (!std::isfinite(value) || value != std::floor(value) || value < 1.f || value > mSnapshot.items.size()) return;
        const int destination = StellarysLayerOrder::indexForPosition(static_cast<int>(mSnapshot.items.size()), static_cast<int>(value));
        if (destination < 0) return;
        LLWearableLayerOrder::enqueue(mSnapshot, destination);
        closeFloater();
    });
    return true;
}

void LLFloaterWearableLayerOrder::onOpen(const LLSD& key)
{
    std::string error;
    const bool ready = LLWearableLayerOrder::capture(key.asUUID(), mSnapshot, error);
    getChild<LLButton>("move")->setEnabled(ready);
    getChild<LLSpinCtrl>("position")->setEnabled(ready);
    auto* item = gInventory.getItem(key.asUUID());
    getChild<LLTextBox>("item")->setText(item ? item->getName() : "Clothing layer");
    auto* position = getChild<LLSpinCtrl>("position");
    position->setMaxValue(static_cast<F32>(llmax(1, static_cast<int>(mSnapshot.items.size()))));
    position->setValue(static_cast<S32>(mSnapshot.items.size()) - mSnapshot.source);
    getChild<LLTextBox>("scope")->setText(ready ?
        llformat("1 = topmost of the %d worn layers of this clothing type. Other layers keep their order.", static_cast<int>(mSnapshot.items.size())) : error);
}
