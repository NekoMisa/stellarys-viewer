# Stellarys Viewer 0.2.0 for Windows

## What's new

- New **Stellarys Midnight** skin: dark navy panels, subtle stars and softer blue unread-IM highlights.
- Prefer **Firestorm** or **StarLight**? Choose it in **Preferences > Skins**, then restart. Please leave feedback on the new skin through the Stellarys Discord server.
- Rotating Stellarys feature tips during login and teleporting.
- Stellarys additions: clothing-layer drag-and-drop, numeric layer positioning and the tested mirror sampling fix.

**Firestorm base:** 7.2.5.81788.

Join the [Stellarys Discord](https://discord.gg/MEHr9xgnXG) from the login page or **Help > Stellarys Discord** for community discussion and feedback.

## Stellarys Midnight

Midnight is the default for the Stellarys login mode. Saved explicit skin choices
take precedence. Existing Firestorm, StarLight and other included skins remain
selectable under **Preferences > Skins**. Skin changes require a restart.
Leave the toolbar-reset option unchecked to retain customised toolbar placement.

The skin keeps familiar controls, fonts and toolbar customisation. Folder categories
retain their distinct icons, Received Items matches the navy palette, and unread
tabs use muted blue with a slightly lighter blue for mentions. Existing flashing
settings remain in effect.

Feedback on readability, contrast, stars and artwork is welcome at
[Stellarys Discord](https://discord.gg/MEHr9xgnXG). When reporting
a visual problem, include the skin, UI scale and relevant cropped screenshot;
hide private conversations and account details.

Login/teleport tips are bundled locally and avoid an immediate repeat. This does
not add paid advertisements, tracking pixels or a new content service.

## Firestorm base

This stable release brings the work previously offered in the Windows 0.1.9 betas
to stable users. The official numeric base is **7.2.5.81788**, with upstream AO
tracks/groups, custom inventory tabs, camera roll and WebRTC voice retained.

## Stellarys clothing layers and mirror fix

In **Appearance > Edit Outfit Parts > Clothing**, drag within one clothing type
or right-click **Move to position…**. Position **1 is topmost within that type**.
Use the normal outfit Save action afterwards. Wearing, attachments, body parts
and RLV commands are unchanged.

Mirror sampling now skips zero-weight reads and avoids mip levels that mirror
generation has not filled. The maintainer reported that this fixed the reproduced
coloured patches in the test scene on an RX 7900 XTX. It is not a claim to fix every
reflection issue on every GPU or driver.

The upstream Inter font and wider script dialogs remain. For the older font/text
sizes, choose **Preferences > User Interface > Font > Font Scheme > Deja vu**, then
restart. Dialog width is a separate upstream layout change.

## Updating

Open **Help > Check for Updates**. This is a stable release, so the experimental
checkbox is not required. Version 0.2.0 supersedes the Windows 0.1.9 betas.
Alternatively, download the Windows installer attached to this release.

Close Stellarys and install into its existing marked installation folder; no
uninstall is needed. Normal updates keep identical application files, while
optional full reinstall/repair replaces all packaged application files. Both
preserve settings, cache, poses, saved shots/paths and trusted/blocked lists.
Choosing another folder creates a separate installation; it does not move the old one.

The installer remains unsigned and requires Windows administrator approval.
This release contains Windows x64/AVX2 files. Linux remains on its separate
published 0.1.8 packages until the Linux update is built and checked.

See [VALIDATION-0.2.0.md](VALIDATION-0.2.0.md) for checks actually performed and
remaining limits. Stellarys is an independent non-commercial hobby project,
not provided or supported by Linden Lab or the Firestorm team. Read
DISCLOSURES.md and PRIVACY.md before use.
