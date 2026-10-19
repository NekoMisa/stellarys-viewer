// SPDX-License-Identifier: LGPL-2.1-only
#include "../../indra/newview/stellaryscamerapath.h"
#include <iostream>
#include <limits>
#include <stdexcept>
using namespace StellarysCameraPath;
static unsigned checks=0;
void check(bool value) {++checks;if(!value)throw std::runtime_error("Camera path check failed: "+std::to_string(checks));}
bool near(double a,double b) {return std::abs(a-b)<1e-6;}
int main()
{
    Frame a{{{1000,1000,30}},{{1005,1000,30}},3.1,1.,2.};
    Frame b{{{1010,1000,30}},{{1005,1000,30}},-3.1,.5,3.};
    Frame c{{{1010,1010,35}},{{1005,1000,30}},0,1.2,4.};
    std::vector<Frame> path{a,b,c}; Frame out;
    check(valid(path));check(near(duration(path,false),5));check(near(duration(path,true),9));
    check(!sample({},0,false,Motion::Linear,out));check(!sample({a},0,false,Motion::Curve,out));
    for(auto motion:{Motion::Curve,Motion::Ease,Motion::Linear})
    {
        check(sample(path,0,false,motion,out)&&out.position==a.position&&out.focus==a.focus);
        check(sample(path,2,false,motion,out)&&out.position==b.position&&near(out.fov,b.fov));
        check(sample(path,5,false,motion,out)&&out.position==c.position);
        check(sample(path,100,false,motion,out)&&out.position==c.position);
        check(sample(path,9,true,motion,out)&&out.position==a.position);
        for(unsigned n=0;n<900;++n)check(sample(path,n*.01,true,motion,out)&&valid(out));
        check(sample(path,1,false,motion,out)&&std::abs(out.roll)>3.1); // short route over pi
    }
    auto invalid=path;invalid[1].seconds=0;check(!valid(invalid));
    check(near(repeatDuration(path,Repeat::Reverse),10));
    check(near(repeatDuration(path,Repeat::Closed),9));
    // Unequal segment times must still give a continuous velocity at curve joins.
    Frame left,at,right;const double h=.0001;
    check(sample(path,2-h,false,Motion::Curve,left)&&sample(path,2,false,Motion::Curve,at)&&sample(path,2+h,false,Motion::Curve,right));
    check(length(sub(scale(sub(at.position,left.position),1/h),scale(sub(right.position,at.position),1/h)))<.01);
    check(sample(path,9-h,true,Motion::Curve,left)&&sample(path,0,true,Motion::Curve,at)&&sample(path,h,true,Motion::Curve,right));
    check(length(sub(scale(sub(at.position,left.position),1/h),scale(sub(right.position,at.position),1/h)))<.01);
    const Vec almostOpposite=unit(Vec{{-1,.01,0}});
    check(length(sub(direction(Vec{{1,0,0}},almostOpposite,.99999),almostOpposite))<.0001);
    for(auto motion:{Motion::Curve,Motion::Ease,Motion::Linear})
    {
        Frame forward,backward;
        for(unsigned n=0;n<=500;++n)
        {
            const double t=n*.01;
            check(sampleRepeated(path,t,Repeat::Reverse,motion,forward));
            check(sampleRepeated(path,10-t,Repeat::Reverse,motion,backward));
            check(length(sub(forward.position,backward.position))<1e-6&&length(sub(forward.focus,backward.focus))<1e-6&&near(forward.fov,backward.fov));
        }
        check(sampleRepeated(path,5,Repeat::Reverse,motion,out)&&out.position==c.position);
        check(sampleRepeated(path,10,Repeat::Reverse,motion,out)&&out.position==a.position);
    }
    invalid=path;invalid[0].fov=std::numeric_limits<double>::quiet_NaN();check(!valid(invalid));
    invalid=path;invalid[0].focus=invalid[0].position;check(!valid(invalid));
    check(!sample(path,std::numeric_limits<double>::infinity(),false,Motion::Ease,out));
    check(!valid(std::vector<Frame>(MAX_FRAMES+1,a)));
    auto cutPath=path;cutPath[1].cut=true;
    check(near(duration(cutPath,false),2)&&near(duration(cutPath,true),6));
    for(auto mode:{Motion::Curve,Motion::Ease,Motion::Linear})
    {
        check(sample(cutPath,1.999999,false,mode,out)&&length(sub(out.position,b.position))<.0001);
        check(sample(cutPath,2,false,mode,out)&&out.position==c.position); // A -> B, then cut directly to C
        check(sample(cutPath,2,true,mode,out)&&out.position==c.position);
        check(sampleRepeated(cutPath,2.000001,Repeat::Reverse,mode,out)&&length(sub(out.position,b.position))<.0001);
        auto leading=cutPath;leading[0].cut=true;leading[1].cut=false;
        check(sample(leading,0,false,mode,out)&&out.position==b.position);
        auto chained=path;chained[0].cut=true;chained[1].cut=true;
        check(near(duration(chained,false),0)&&!sample(chained,0,false,mode,out));
        check(sample(chained,0,true,mode,out)&&out.position==c.position); // leading cut chain, timed closing leg
    }
    invalid=std::vector<Frame>(10,a);for(auto& f:invalid)f.seconds=600;check(!valid(invalid));
    // Two stationary camera keyframes looking in opposite directions must not look at themselves.
    b.position=a.position;b.focus={{995,1000,30}};
    check(sample({a,b},1,false,Motion::Linear,out)&&near(length(sub(out.focus,out.position)),5));
    Clock clock;
    check(clock.start(5,5,false));check(clock.state==Clock::State::Countdown);
    check(clock.advance(4)&&near(clock.elapsed,0)&&near(clock.remaining,1));
    clock.pause();check(clock.advance(10)&&near(clock.remaining,1));
    clock.resume();check(clock.advance(1)&&near(clock.elapsed,0)&&clock.state==Clock::State::Playing);
    check(clock.advance(2)&&near(clock.elapsed,2));
    clock.pause();check(clock.advance(10)&&near(clock.elapsed,2));clock.resume();
    check(clock.advance(4)&&clock.state==Clock::State::Finished&&near(clock.elapsed,5));
    check(clock.start(5,10,true));check(clock.advance(11)&&near(clock.elapsed,1));
    check(clock.advance(11)&&near(clock.elapsed,2));
    check(!clock.advance(-1));check(!clock.advance(std::numeric_limits<double>::quiet_NaN()));
    check(!clock.start(0,5,false));check(!clock.start(5,61,false));
    check(clock.start(10,7,true));check(clock.advance(7)&&near(clock.elapsed,0)&&near(clock.remaining,0));
    check(clock.advance(21)&&near(clock.elapsed,1)&&near(clock.remaining,0)); // no countdown on later loops
    clock.stop();check(clock.state==Clock::State::Stopped&&near(clock.elapsed,0)&&near(clock.remaining,0));
    std::cout<<checks<<" camera interpolation/countdown/transport checks passed.\n";
}
