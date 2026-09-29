#include "fkposerconsent.h"
#include <iostream>
#include <stdexcept>

static int checks = 0;
static void check(bool value, const char* label)
{
    ++checks;
    if (!value) throw std::runtime_error(label);
}
int main()
{
    FKPoserConsent a, b;
    check(!a.mayPose && !a.peerMayPose, "default denied");
    check(!a.accept(10), "unsolicited accept rejected");
    check(a.request(10), "explicit request");
    check(!a.request(11), "duplicate request suppressed");
    check(a.pending(129), "request valid before deadline");
    check(!a.accept(130), "accept rejected exactly at expiry");
    check(!a.mayPose, "expired accept grants nothing");
    check(a.request(131), "retry after expiry");
    check(!b.accept(132), "different peer cannot consume request");
    check(a.accept(132) && a.mayPose, "pending request accepts");
    check(!a.accept(133), "replayed accept rejected");
    check(!a.peerMayPose, "grant direction remains independent");
    a.deny();
    check(!a.mayPose && !a.pending(134), "revoke cancels grant and pending");
    check(!a.accept(134), "late accept after deny rejected");
    check(a.receiveRequest(140), "incoming consent prompt");
    const double token = a.incomingUntil;
    check(!a.receiveRequest(141), "duplicate prompt suppressed");
    check(!a.answer(142, token + 1, true), "wrong prompt token rejected");
    check(a.answer(142, token, true) && a.peerMayPose, "explicit affirmative grants");
    check(!a.mayPose, "incoming grant does not grant reverse direction");
    check(!a.answer(143, token, true), "replayed prompt answer rejected");
    a.revoke();
    check(!a.peerMayPose, "local revoke clears grant");
    check(a.receiveRequest(180), "new prompt after cooldown");
    check(a.answer(181, a.incomingUntil, false) && !a.peerMayPose, "decline grants nothing");
    check(a.receiveRequest(220), "another request");
    check(!a.answer(340, a.incomingUntil, true), "expired prompt grants nothing");
    a = FKPoserConsent{};
    check(!a.accept(341) && !a.mayPose && !a.peerMayPose, "lifecycle reset invalidates consent");
    std::cout << "PASS: " << checks << " consent state checks\n";
}
