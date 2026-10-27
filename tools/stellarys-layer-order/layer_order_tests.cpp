// SPDX-License-Identifier: LGPL-2.1-only
#include "../../indra/newview/stellaryslayerorder.h"
#include <cassert>
#include <iostream>
#include <numeric>
#include <set>

int main()
{
    int moves = 0, drops = 0;
    for (int count = 1; count <= 60; ++count)
    {
        for (int source = 0; source < count; ++source)
        {
            for (int target = 0; target < count; ++target)
            {
                auto result = StellarysLayerOrder::plan(count, source, target);
                assert(static_cast<int>(result.size()) == count && result[target] == source);
                assert(std::set<int>(result.begin(), result.end()).size() == result.size());
                auto others = result;
                others.erase(others.begin() + target);
                std::vector<int> expected;
                for (int i = 0; i < count; ++i) if (i != source) expected.push_back(i);
                assert(others == expected);
                const int position = count - target;
                assert(StellarysLayerOrder::indexForPosition(count, position) == target);
                ++moves;

                for (bool above : {false, true})
                {
                    // Independent model in visual (top-first) order: insert before/after the target.
                    std::vector<int> visual;
                    for (int i = count - 1; i >= 0; --i) visual.push_back(i);
                    if (source != target)
                    {
                        visual.erase(std::find(visual.begin(), visual.end(), source));
                        auto spot = std::find(visual.begin(), visual.end(), target);
                        visual.insert(spot + (above ? 0 : 1), source);
                    }
                    const int destination = StellarysLayerOrder::dropIndex(count, source, target, above);
                    auto actual = StellarysLayerOrder::plan(count, source, destination);
                    std::reverse(actual.begin(), actual.end());
                    assert(actual == visual);
                    ++drops;
                }
            }
        }
        for (int bad : {-10, -1, count, count + 1, 1000})
        {
            assert(StellarysLayerOrder::plan(count, bad, 0).empty());
            assert(StellarysLayerOrder::plan(count, 0, bad).empty());
            assert(StellarysLayerOrder::dropIndex(count, bad, 0, true) == -1);
            assert(StellarysLayerOrder::dropIndex(count, 0, bad, false) == -1);
        }
        for (int bad_position : {-1, 0, count + 1})
            assert(StellarysLayerOrder::indexForPosition(count, bad_position) == -1);
    }
    assert(StellarysLayerOrder::plan(0, 0, 0).empty());
    assert(StellarysLayerOrder::plan(-1, 0, 0).empty());
    assert(StellarysLayerOrder::dropIndex(0, 0, 0, true) == -1);
    assert(StellarysLayerOrder::indexForPosition(0, 1) == -1);
    std::cout << moves << " numeric moves, " << drops << " drag placements and invalid-input cases passed.\n";
}
