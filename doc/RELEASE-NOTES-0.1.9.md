# Stellarys Viewer 0.1.9 Beta 2 for Windows (based on Firestorm 7.2.5.81788)

## What's new

- Drag clothing layers into order in **Appearance → Edit Outfit Parts → Clothing**.
  A blue insertion line shows the drop position; drag near the list edge to scroll.
- Right-click a clothing layer and choose **Move to position…**. Position **1 is
  topmost within the same clothing type**. Other layers keep their relative order.
- Fixed coloured surface artifacts associated with Mirrors in the maintainer's
  test scene by preventing reads from unwritten mirror texture mip levels.
- Beta 1 users can receive this update through **Include experimental updates
  (beta)** in the updater; the option remains off by default.
- Retains the Firestorm 7.2.5.81788 base, AMD mesh workaround, permission-based
  poser, Photo tools, shot presets and cinematic camera paths.

## Clothing layer controls

The new controls are only in **Edit Outfit Parts → Clothing**. The Wearing list,
attachments, body parts and RLV commands are unchanged. Drag within one clothing
type, such as tattoos. Press Escape or release outside a valid target to cancel.
Use the normal outfit **Save** action to retain your edited outfit.

If your outfit changes while a position dialog or drag is open, the move is
cancelled rather than applying an outdated order. Separate inventory copies
sharing the same wearable asset are identified by inventory item ID.

## Mirror rendering

The shader now skips zero-weight mirror reads and limits sampling to the mip
levels actually generated for mirrors. The maintainer reproduced the coloured
patches by enabling Mirrors, tested the isolated shader change on an RX 7900 XTX,
and reported that the issue appeared fixed. The GPU regression test also passed.
This does not claim to fix every mirror issue or cover every GPU/driver.

## Updating

**Beta 1:** open **Help → Check for Updates**, enable **Include experimental
updates (beta)**, and download/install Beta 2. The checkbox is off by default.

**0.1.8:** install this Windows beta manually once to get the experimental-update
checkbox. Close Stellarys and select its existing marked installation folder in
Setup. No uninstall is needed. Settings, cache, saved shots, camera paths and
trusted/blocked lists are preserved. Experimental updates do not downgrade a beta.

This is an unsigned Windows experimental prerelease. Stable Windows remains at
0.1.8, and Linux update feeds and downloads are unchanged. No Linux 0.1.9 package
is included. Keep experimental updates enabled to receive later Windows betas.

## Firestorm base and font choice

The base remains **7.2.5.81788**, including upstream AO tracks/groups, custom
inventory tabs, camera roll and WebRTC voice. Stellarys' version remains separate.
The upstream Inter font and wider script dialogs are retained. To restore the
older font/text sizes, choose **Preferences → User Interface → Font → Font Scheme
→ Deja vu**, then restart. Dialog width is a separate upstream layout change.

The poser still requires explicit permission for other avatars; poses are local
to the viewer applying them. Existing photography tools, motion blur, link controls
and separate per-user settings remain. Normal installer updates retain identical
application files; optional full reinstall/repair remains available.

See [VALIDATION-0.1.9.md](VALIDATION-0.1.9.md) for actual checks and their limits.
Stellarys is an independent non-commercial hobby project, not provided or
supported by Linden Lab or the Firestorm team. Read DISCLOSURES.md and PRIVACY.md.
