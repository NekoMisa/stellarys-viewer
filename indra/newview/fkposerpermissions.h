// Fire Kitty poser prototype. LGPL-2.1-only.
#pragma once
#include "lleventtimer.h"
#include "lluuid.h"
#include "fkposerconsent.h"
#include <map>
#include <string>

class LLVOAvatar;
class FKPoserPermissions : public LLEventTimer
{
public:
    static FKPoserPermissions& instance();
    bool canPose(LLVOAvatar* avatar) const;
    bool hasGranted(const LLUUID& id) const;
    bool isPending(const LLUUID& id) const;
    void request(const LLUUID& id);
    void revoke(const LLUUID& id);
    bool process(const LLUUID& from, const std::string& message);
    bool tick() override;
private:
    FKPoserPermissions() : LLEventTimer(0.5f) {}
    struct Peer
    {
        LLVOAvatar* avatar = nullptr; // identity comparison only; never dereferenced
        LLUUID region;
        LLUUID session;
        FKPoserConsent consent;
    };
    std::map<LLUUID, Peer> mPeers;
    static LLVOAvatar* findAvatar(const LLUUID& id);
    static bool eligible(LLVOAvatar* avatar);
    bool current(const Peer& peer, LLVOAvatar* avatar) const;
    Peer* ensurePeer(const LLUUID& id);
    void answer(const LLUUID& id, const LLUUID& session, const LLUUID& region,
                double token, bool allow);
    static void send(const LLUUID& id, const std::string& message);
    static void changed(const LLUUID& id, bool stop);
};
