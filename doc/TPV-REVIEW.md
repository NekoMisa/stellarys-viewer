# Stellarys third-party viewer review

Review date: 10 October 2026. This records scoped engineering checks, not legal
certification, a complete security/licensing audit or Linden Lab approval.

Policy: https://secondlife.com/corporate/third-party-viewers
Identifier requirements: https://wiki.secondlife.com/wiki/Channel_and_Version_Requirements
Application: https://github.com/secondlife/third-party-viewers

## Changes prepared for 0.1.4

- PRIVACY.md describes local account/settings/log/cache/browser files, Linden Lab
  authentication/statistics, inherited Firestorm requests, optional network
  features, GitHub updates and voluntary public support submissions.
- DISCLOSURES.md supplies the exact Linden Lab disclaimer, support and privacy
  links, extra features/limitations and maturity/RLVa information. README and
  platform packages link/include it. Windows Setup shows the bundled disclosures
  and policy before installation. The first-run viewer screen includes both
  documents offline before credential widgets or automatic login.
- StellarysVersion.cmake derives the channel from stellarys-source.json. The
  official numeric Firestorm base stays 7.2.4.80712; for example a release uses
  `Stellarys Viewer 0.1.4 / 7.2.4.80712`, and a Linux preview uses
  `Stellarys Viewer 0.1.4 Linux Preview 1 / 7.2.4.80712`. A different source release
  must bump the Stellarys version or variant. Profiles and app IDs stay fixed.
  The inherited runtime `--channel`/CmdLineChannel override is ignored so old
  profile values cannot replace the compiled login/statistics identity.

## Source paths inspected

- lllogininstance.cpp sends the configured channel/version. Its initial
  `agree_to_tos=false`, server `tos` response and explicit acceptance callback
  remain intact. No ToS request is automatically accepted by these changes.
- llappviewer.cpp still schedules send_viewer_stats; llviewerstats.cpp posts the
  original statistics packet to the simulator's ViewerStats capability.
- fkposerpermissions.cpp, fkposerconsent.h, llimprocessing.cpp and
  fsposeranimator.cpp gate other-avatar posing on explicit, current consent.
  Requests expire; denial stops posing; region/session/avatar lifecycle changes
  invalidate consent. Commands use ordinary IMs: `;PoserRequest`, `;PoserAccept`,
  `;PoserDeny`. They add no simulator message type. The legacy compatible protocol
  has no nonce; it is not a cryptographic consent system. Poses are local.
- fsdata.cpp retains upstream Firestorm/Phoenix data requests. Its system-info
  response callback only sends technical information after approval. Inherited
  HTTP endpoints and optional media/voice/translation services are disclosed;
  this change is not a complete network-traffic audit.
- Updaters require user-directed downloads/installation; Windows UAC and Linux
  PolicyKit approval remain. Installers keep separate profiles and refuse an
  unrelated destination. No live user data is used for build/test packaging.

## Licensing and application items

Viewer source and licence notices remain public. Windows packaging copies
ThirdPartyLicenses; Linux includes the inherited component notices. FMOD's
bundled EULA permits non-commercial integration subject to its conditions. The
maintainer confirmed no sales/donations/sponsorship/paid promotion. This is not
a transfer of Firestorm's licences; reassess FMOD terms before monetisation.
Havok/KDU and crash upload are disabled in the configured builds. Full dependency
redistribution rights and trademark/asset history still require maintainer review.

The maintainer confirmed account standing and payment/age-verification eligibility.
No private identity documents are stored here. Confirm eligibility for every
additional developer with repository/web write access. The public application
needs a support email, Second Life contact and at least a 512px icon; never
publish private legal/address information in a public issue. Follow Linden Lab's
private process if it requests such information.

The changes are not effective for existing downloads until documentation is
published and new binaries are released. Update older release pages with the
disclosure/privacy links when publication is authorised. Do not silently replace
already released installer/source bytes or claim old binaries gained the new
identifier. Directory listing is optional; policy compliance is required.

Compiled/runtime/package checks and remaining manual checks belong in the
matching 0.1.4 validation record. No directory application has been submitted.
