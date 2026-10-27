// Stellarys clothing layer ordering. SPDX-License-Identifier: LGPL-2.1-only
#ifndef STELLARYS_LAYER_ORDER_H
#define STELLARYS_LAYER_ORDER_H
#include <algorithm>
#include <vector>

namespace StellarysLayerOrder
{
// Wearables are stored bottom first; Edit Outfit displays top first.
inline int indexForPosition(int count, int position)
{
    return count > 0 && position >= 1 && position <= count ? count - position : -1;
}

inline int dropIndex(int count, int source, int target, bool above)
{
    if (count < 1 || source < 0 || source >= count || target < 0 || target >= count) return -1;
    int slot = target + (above ? 1 : 0);
    return slot - (source < slot ? 1 : 0);
}

// A permutation of original indices. Every unaffected layer keeps its relative order.
inline std::vector<int> plan(int count, int source, int destination)
{
    if (count < 1 || source < 0 || source >= count || destination < 0 || destination >= count) return {};
    std::vector<int> order;
    for (int i = 0; i < count; ++i) if (i != source) order.push_back(i);
    order.insert(order.begin() + destination, source);
    return order;
}
}
#endif
