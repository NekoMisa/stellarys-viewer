// SPDX-License-Identifier: LGPL-2.1-only
#ifndef STELLARYS_CAMERA_PATH_H
#define STELLARYS_CAMERA_PATH_H
#include "stellarysshotvalidation.h"
#include <algorithm>
#include <vector>

namespace StellarysCameraPath
{
using Vec = std::array<double, 3>;
constexpr double PI = 3.14159265358979323846;
constexpr std::size_t MAX_FRAMES = 100;
enum class Motion { Curve, Ease, Linear };
enum class Repeat { Once, Closed, Reverse };
struct Frame
{
    Vec position{}, focus{};
    double roll = 0., fov = 1., seconds = 3.; // seconds from this frame to the next
    bool cut = false; // Instant jump to the next frame; keeps seconds for switching back to Move.
};
inline double legDuration(const Frame& frame) { return frame.cut?0.:frame.seconds; }
inline Vec add(const Vec& a, const Vec& b) { return {{a[0]+b[0],a[1]+b[1],a[2]+b[2]}}; }
inline Vec scale(const Vec& a, double n) { return {{a[0]*n,a[1]*n,a[2]*n}}; }
inline Vec sub(const Vec& a, const Vec& b) { return add(a,scale(b,-1)); }
inline double dot(const Vec& a, const Vec& b) { return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
inline double length(const Vec& a) { return std::sqrt(dot(a,a)); }
inline Vec unit(const Vec& a) { return scale(a,1./length(a)); }
inline Vec mix(const Vec& a, const Vec& b, double t) { return add(scale(a,1-t),scale(b,t)); }
inline bool valid(const Frame& f)
{
    return StellarysShot::validCamera(f.position,f.focus,f.roll) &&
        StellarysShot::inRange(f.fov,.01,3.1) && StellarysShot::inRange(f.seconds,.1,600.);
}
inline bool valid(const std::vector<Frame>& frames)
{
    if (frames.empty() || frames.size()>MAX_FRAMES) return false;
    double total=0;
    for (const auto& f:frames) { if (!valid(f)) return false; total+=legDuration(f); }
    return total<=3600.;
}
inline double duration(const std::vector<Frame>& frames, bool loop)
{
    if (frames.size()<2 || !valid(frames)) return 0.;
    double total=0;
    for (std::size_t i=0;i<frames.size()-(loop?0:1);++i) total+=legDuration(frames[i]);
    return total;
}
inline Vec direction(const Vec& a, const Vec& b, double t)
{
    if(t<=0)return a;
    if(t>=1)return b;
    const double cosine=std::clamp(dot(a,b),-1.,1.);
    if (cosine>.9995) return unit(mix(a,b,t));
    if (cosine<-.999999999)
    {
        // A deterministic perpendicular avoids a zero look vector in a 180-degree turn.
        Vec axis=std::abs(a[2])<.9?Vec{{0,0,1}}:Vec{{0,1,0}};
        axis=unit(sub(axis,scale(a,dot(axis,a))));
        return add(scale(a,std::cos(PI*t)),scale(axis,std::sin(PI*t)));
    }
    const double angle=std::acos(cosine), sine=std::sin(angle);
    return add(scale(a,std::sin((1-t)*angle)/sine),scale(b,std::sin(t*angle)/sine));
}
inline Vec curve(const std::vector<Frame>& f, std::size_t i, double t, bool loop, bool focus)
{
    const auto n=f.size(), j=(i+1)%n, before=(i+n-1)%n, after=(j+1)%n;
    auto value=[&](std::size_t k)->const Vec& {return focus?f[k].focus:f[k].position;};
    const Vec v0=(!loop && i==0)||f[before].cut?Vec{}:scale(sub(value(j),value(before)),1./(f[before].seconds+f[i].seconds));
    const Vec v1=(!loop && j==n-1)||f[j].cut?Vec{}:scale(sub(value(after),value(i)),1./(f[i].seconds+f[j].seconds));
    const double t2=t*t,t3=t2*t,dt=f[i].seconds;
    return add(add(scale(value(i),2*t3-3*t2+1),scale(value(j),-2*t3+3*t2)),
        add(scale(v0,(t3-2*t2+t)*dt),scale(v1,(t3-t2)*dt)));
}
inline bool sample(const std::vector<Frame>& frames, double seconds, bool loop, Motion motion, Frame& out)
{
    const double total=duration(frames,loop);
    if (total<=0 || !std::isfinite(seconds)) return false;
    seconds=std::max(0.,seconds);
    if (!loop && seconds>=total) { out=frames.back(); return true; }
    if (loop) seconds=std::fmod(seconds,total);
    std::size_t i=0;
    while (i+1<frames.size() && seconds>=legDuration(frames[i])) { seconds-=legDuration(frames[i]); ++i; }
    const auto& a=frames[i]; const auto& b=frames[(i+1)%frames.size()];
    const double t=std::clamp(seconds/a.seconds,0.,1.), eased=t*t*(3-2*t);
    const double u=motion==Motion::Linear?t:eased;
    out=a;
    out.position=motion==Motion::Curve?curve(frames,i,t,loop,false):mix(a.position,b.position,u);
    out.focus=motion==Motion::Curve?curve(frames,i,t,loop,true):mix(a.focus,b.focus,u);
    // When the look directions oppose, interpolate the direction instead of crossing the camera.
    const Vec da=sub(a.focus,a.position),db=sub(b.focus,b.position);
    if (dot(unit(da),unit(db))<-.9)
        out.focus=add(out.position,scale(direction(unit(da),unit(db),u),length(da)*(1-u)+length(db)*u));
    out.roll=std::remainder(a.roll+std::remainder(b.roll-a.roll,2*PI)*u,2*PI);
    out.fov=a.fov*(1-u)+b.fov*u;
    return valid(out);
}

inline double repeatDuration(const std::vector<Frame>& frames, Repeat repeat)
{
    const double leg=duration(frames,repeat==Repeat::Closed);
    return repeat==Repeat::Reverse?2*leg:leg;
}
inline bool sampleRepeated(const std::vector<Frame>& frames, double seconds, Repeat repeat, Motion motion, Frame& out)
{
    if(!std::isfinite(seconds))return false;
    if(repeat==Repeat::Reverse)
    {
        const double leg=duration(frames,false);
        if(leg<=0)return false;
        seconds=std::fmod(std::max(0.,seconds),2*leg);
        if(seconds>leg)seconds=2*leg-seconds;
    }
    return sample(frames,seconds,repeat==Repeat::Closed,motion,out);
}

// Shared transport logic: countdown time never advances the path itself.
class Clock
{
public:
    enum class State { Stopped, Countdown, Playing, Paused, Finished };
    State state=State::Stopped;
    double elapsed=0, remaining=0, total=0;
    bool loop=false;
    bool start(double duration, double delay, bool repeat)
    {
        if (!StellarysShot::inRange(duration,.1,7200.) || !StellarysShot::inRange(delay,0,60)) return false;
        elapsed=0; remaining=delay; total=duration; loop=repeat;
        state=remaining>0?State::Countdown:State::Playing; return true;
    }
    void pause() { if (state==State::Playing || state==State::Countdown) state=State::Paused; }
    void resume() { if (state==State::Paused) state=remaining>0?State::Countdown:State::Playing; }
    void stop() { *this=Clock(); }
    bool advance(double dt)
    {
        if (!StellarysShot::inRange(dt,0,3600.)) return false;
        if (state==State::Countdown)
        {
            const double used=std::min(remaining,dt); remaining-=used; dt-=used;
            if (remaining>0) return true;
            state=State::Playing;
        }
        if (state==State::Playing)
        {
            elapsed+=dt;
            if (loop) elapsed=std::fmod(elapsed,total);
            else if (elapsed>=total) { elapsed=total; state=State::Finished; }
        }
        return true;
    }
};
}
#endif
