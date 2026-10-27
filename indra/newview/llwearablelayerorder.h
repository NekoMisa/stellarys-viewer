// Stellarys Edit Outfit layer ordering. SPDX-License-Identifier: LGPL-2.1-only
#ifndef LL_WEARABLE_LAYER_ORDER_H
#define LL_WEARABLE_LAYER_ORDER_H
#include "llfloater.h"
#include "llwearabletype.h"
#include <string>
#include <vector>

namespace LLWearableLayerOrder
{
struct Snapshot
{
    LLUUID agent, session, cof, selected;
    LLWearableType::EType type = LLWearableType::WT_INVALID;
    std::vector<LLUUID> items, links; // bottom to top
    std::vector<std::string> descriptions;
    int source = -1;
};
bool capture(const LLUUID& item, Snapshot& snapshot, std::string& error);
bool apply(const Snapshot& snapshot, int destination, std::string& error);
void enqueue(const Snapshot& snapshot, int destination);
void prompt(const LLUUID& item);
}

class LLFloaterWearableLayerOrder : public LLFloater
{
public:
    explicit LLFloaterWearableLayerOrder(const LLSD& key) : LLFloater(key) {}
    bool postBuild() override;
    void onOpen(const LLSD& key) override;
private:
    LLWearableLayerOrder::Snapshot mSnapshot;
};
#endif
