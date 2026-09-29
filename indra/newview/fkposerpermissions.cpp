// Fire Kitty poser prototype. LGPL-2.1-only.
#include "llviewerprecompiledheaders.h"
#include "fkposerpermissions.h"
#include "fsfloaterposer.h"
#include "fsposeranimator.h"
#include "llagent.h"
#include "llagentui.h"
#include "llfloaterreg.h"
#include "llinstantmessage.h"
#include "llmutelist.h"
#include "llnotificationsutil.h"
#include "llslurl.h"
#include "llviewerobjectlist.h"
#include "llviewerregion.h"
#include "llvoavatar.h"
#include "message.h"
#include "rlvactions.h"

FKPoserPermissions& FKPoserPermissions::instance()
{
    static FKPoserPermissions instance;
    return instance;
}

LLVOAvatar* FKPoserPermissions::findAvatar(const LLUUID& id)
{
    return dynamic_cast<LLVOAvatar*>(gObjectList.findObject(id));
}

bool FKPoserPermissions::eligible(LLVOAvatar* avatar)
{
    return avatar && !avatar->isDead() && !avatar->isSelf() && !avatar->isControlAvatar()
        && gAgent.getRegion() && avatar->getRegion() == gAgent.getRegion()
        && !LLMuteList::getInstance()->isMuted(avatar->getID())
        && RlvActions::canReceiveIM(avatar->getID()) && RlvActions::canSendIM(avatar->getID());
}

bool FKPoserPermissions::current(const Peer& peer, LLVOAvatar* avatar) const
{
    return eligible(avatar) && avatar == peer.avatar
        && peer.session == gAgent.getSessionID()
        && peer.region == gAgent.getRegion()->getRegionID();
}

FKPoserPermissions::Peer* FKPoserPermissions::ensurePeer(const LLUUID& id)
{
    LLVOAvatar* avatar = findAvatar(id);
    if (!eligible(avatar)) return nullptr;
    auto it = mPeers.find(id);
    if (it != mPeers.end() && !current(it->second, avatar))
    {
        changed(id, true);
        mPeers.erase(it);
    }
    auto& peer = mPeers[id];
    peer.avatar = avatar;
    peer.region = gAgent.getRegion()->getRegionID();
    peer.session = gAgent.getSessionID();
    return &peer;
}

bool FKPoserPermissions::canPose(LLVOAvatar* avatar) const
{
    if (!avatar) return false;
    auto it = mPeers.find(avatar->getID());
    return it != mPeers.end() && current(it->second, avatar) && it->second.consent.mayPose;
}

bool FKPoserPermissions::hasGranted(const LLUUID& id) const
{
    auto it = mPeers.find(id);
    return it != mPeers.end() && current(it->second, findAvatar(id)) && it->second.consent.peerMayPose;
}

bool FKPoserPermissions::isPending(const LLUUID& id) const
{
    auto it = mPeers.find(id);
    return it != mPeers.end() && current(it->second, findAvatar(id))
        && it->second.consent.pending(LLTimer::getTotalSeconds());
}

void FKPoserPermissions::send(const LLUUID& id, const std::string& message)
{
    if (!gAgent.getRegion() || !gMessageSystem || !RlvActions::canSendIM(id)) return;
    std::string name;
    LLAgentUI::buildFullname(name);
    pack_instant_message(gMessageSystem, gAgent.getID(), false, gAgent.getSessionID(),
                         id, name, message, IM_ONLINE, IM_NOTHING_SPECIAL);
    gAgent.sendReliableMessage();
}

void FKPoserPermissions::request(const LLUUID& id)
{
    Peer* peer = ensurePeer(id);
    if (!peer || !peer->consent.request(LLTimer::getTotalSeconds())) return;
    send(id, ";PoserRequest");
    changed(id, false);
}

void FKPoserPermissions::revoke(const LLUUID& id)
{
    auto it = mPeers.find(id);
    if (it == mPeers.end()) return;
    it->second.consent.revoke();
    send(id, ";PoserDeny");
    changed(id, false);
}

void FKPoserPermissions::answer(const LLUUID& id, const LLUUID& session, const LLUUID& region,
                              double token, bool allow)
{
    auto it = mPeers.find(id);
    if (it == mPeers.end() || !current(it->second, findAvatar(id))
        || it->second.session != session || it->second.region != region) return;
    if (!it->second.consent.answer(LLTimer::getTotalSeconds(), token, allow)) return;
    send(id, allow ? ";PoserAccept" : ";PoserDeny");
    changed(id, false);
}

bool FKPoserPermissions::process(const LLUUID& from, const std::string& message)
{
    if (message != ";PoserRequest" && message != ";PoserAccept" && message != ";PoserDeny") return false;
    // A denial is always allowed to stop our pose, even after mute/region changes.
    if (message == ";PoserDeny")
    {
        auto it = mPeers.find(from);
        if (it != mPeers.end()) it->second.consent.deny();
        changed(from, true);
        return true;
    }
    Peer* peer = ensurePeer(from);
    if (!peer) return true;
    const double now = LLTimer::getTotalSeconds();
    if (message == ";PoserAccept")
    {
        if (peer->consent.accept(now)) changed(from, false);
        return true;
    }
    if (!peer->consent.receiveRequest(now)) return true;
    const double token = peer->consent.incomingUntil;
    const LLUUID session = peer->session, region = peer->region;
    LLSD args;
    args["NAME_SLURL"] = LLSLURL("agent", from, "about").getSLURLString();
    LLNotificationsUtil::add("FKPoserPermissionRequest", args, LLSD(),
        [this, from, session, region, token](const LLSD& notification, const LLSD& response)
        {
            answer(from, session, region, token,
                   LLNotificationsUtil::getSelectedOption(notification, response) == 0);
            return false;
        });
    return true;
}

void FKPoserPermissions::changed(const LLUUID& id, bool stop)
{
    if (stop)
    {
        // stopPosingAvatar deliberately works even after consent/region is lost.
        FSPoserAnimator animator;
        animator.stopPosingAvatar(findAvatar(id));
    }
    if (auto* floater = LLFloaterReg::findTypedInstance<FSFloaterPoser>("fs_poser"))
        floater->refreshPosePermissions();
}

bool FKPoserPermissions::tick()
{
    for (auto it = mPeers.begin(); it != mPeers.end(); )
    {
        if (!current(it->second, findAvatar(it->first)))
        {
            const LLUUID id = it->first;
            const bool notify = it->second.consent.peerMayPose;
            it = mPeers.erase(it);
            if (notify) send(id, ";PoserDeny");
            changed(id, true);
        }
        else ++it;
    }
    if (auto* floater = LLFloaterReg::findTypedInstance<FSFloaterPoser>("fs_poser"))
        floater->refreshPosePermissions();
    return false;
}
