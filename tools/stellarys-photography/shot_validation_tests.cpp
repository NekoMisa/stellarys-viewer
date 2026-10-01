// SPDX-License-Identifier: LGPL-2.1-only
#include "../../indra/newview/stellarysshotvalidation.h"
#include <iostream>
#include <limits>
#include <stdexcept>
static unsigned checks=0;
void check(bool value) { ++checks; if (!value) throw std::runtime_error("Shot validation check failed"); }
int main()
{
    using namespace StellarysShot;
    check(validName("Portrait 1")); check(validName("A/B: portrait")); // names are map keys, never file paths
    check(!validName("")); check(!validName(std::string(81,'x'))); check(!validName("name\nnext line"));
    check(validName(std::string(80,'x'))); check(!validName("bad\tname"));
    check(validDimensions(32,32)); check(validDimensions(6016,6016));
    check(!validDimensions(0,1080)); check(!validDimensions(1920,-1));
    check(!validDimensions(6017,6016)); check(!validDimensions(1920,6017));
    std::array<double,3> position={{256000,256000,30}},focus={{256010,256000,31}};
    check(validCamera(position,focus,0)); check(validCamera(position,focus,3.14159265));
    check(validCamera(position,focus,-3.14159265)); check(!validCamera(position,focus,4));
    check(!validCamera(position,position,0));
    auto invalid=position; invalid[0]=std::numeric_limits<double>::quiet_NaN(); check(!validCamera(invalid,focus,0));
    invalid=focus; invalid[2]=std::numeric_limits<double>::infinity(); check(!validCamera(position,invalid,0));
    invalid=position; invalid[0]=-1; check(!validCamera(invalid,focus,0));
    invalid=focus; invalid[0]+=100000; check(!validCamera(position,invalid,0));
    check(!validCamera(position,focus,std::numeric_limits<double>::infinity()));
    check(samePlace("grid-a","region-a","grid-a","region-a"));
    check(!samePlace("grid-a","region-a","grid-b","region-a"));
    check(!samePlace("grid-a","region-a","grid-a","region-b"));
    check(!samePlace("","","",""));
    for (const auto& rule:lensRanges)
    {
        check(inRange(rule.minimum,rule.minimum,rule.maximum));
        check(inRange(rule.maximum,rule.minimum,rule.maximum));
        check(!inRange(rule.minimum-1,rule.minimum,rule.maximum));
        check(!inRange(rule.maximum+1,rule.minimum,rule.maximum));
        check(!inRange(std::numeric_limits<double>::quiet_NaN(),rule.minimum,rule.maximum));
    }
    std::cout<<checks<<" shared shot validation checks passed.\n";
}
