// Fire Kitty poser prototype. LGPL-2.1-only.
#pragma once

// Per-peer state, deliberately independent of viewer globals for executable tests.
// Wire compatibility: Black Dragon ;PoserRequest / ;PoserAccept / ;PoserDeny.
// The legacy protocol has no nonce, so accept only during an explicit short request.
struct FKPoserConsent
{
    double pendingUntil = 0;
    double incomingUntil = 0;
    double requestAgainAt = 0;
    double incomingAgainAt = 0;
    bool mayPose = false;
    bool peerMayPose = false;

    bool request(double now)
    {
        if (mayPose || now < requestAgainAt || now < pendingUntil) return false;
        pendingUntil = now + 120;
        requestAgainAt = now + 30;
        return true;
    }
    bool accept(double now)
    {
        if (pendingUntil == 0 || now >= pendingUntil) return false;
        pendingUntil = 0;
        mayPose = true;
        return true;
    }
    bool receiveRequest(double now)
    {
        if (now < incomingAgainAt || now < incomingUntil) return false;
        incomingUntil = now + 120;
        incomingAgainAt = now + 30;
        return true;
    }
    bool answer(double now, double token, bool allow)
    {
        if (incomingUntil == 0 || token != incomingUntil || now >= incomingUntil) return false;
        incomingUntil = 0;
        peerMayPose = allow;
        return true;
    }
    void deny() { mayPose = false; pendingUntil = 0; }
    void revoke() { peerMayPose = false; incomingUntil = 0; }
    bool pending(double now) const { return pendingUntil != 0 && now < pendingUntil; }
};
