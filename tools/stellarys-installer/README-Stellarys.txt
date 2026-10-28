Stellarys Viewer 0.2.1
Firestorm base: 7.2.5.81788

A hobby viewer with the AMD flicker fix and permission-based local posing.
The viewer includes clearer update highlights with a full release-notes link, plus
a Photo menu for snapshots, camera controls, Camera Tools, Photo Tools and the
poser and self reset actions. Shot Presets saves camera position, lens/blur,
local lighting and image dimensions together; restore shots in their original
region. Toolbar customization stays at its existing access points.
Your saved toolbar layout and existing shortcuts are retained. Stellarys posing,
photography and AMD safeguards are retained alongside the rendering and UI
updates from Firestorm 7.2.5.

STELLARYS MIDNIGHT
The new navy/starry skin is the default for the Stellarys login mode; saved
explicit skin choices take precedence. Prefer the familiar look? Select Firestorm
or StarLight in Preferences > Skins, then restart. Leave toolbar reset unchecked
to retain custom toolbar placement. Please leave feedback about the skin's
readability, contrast and artwork at https://discord.gg/MEHr9xgnXG.
Unread IM highlights use muted blue, with a lighter blue for mentions. Folder
icons remain distinct and Received Items matches the navy controls.
Login and teleport screens now show bundled rotating Stellarys feature tips.

EDIT OUTFIT LAYER ORDER
Appearance > Edit Outfit Parts > Clothing: drag a layer above or below another
of the same clothing type, or right-click > Move to position. Position 1 is the
topmost within that type. Drag near the list edge to scroll; Esc or dropping
outside a valid target cancels. Use the normal outfit Save action afterwards.
The Wearing list, attachments, body parts and RLV commands are unchanged.

MIRROR RENDERING
The mirror shader now avoids reading texture mip levels that mirror generation
has not filled. This addresses the coloured surface corruption reproduced in
the maintainer's RX 7900 XTX test scene with Mirrors enabled. It does not claim
to fix every reflection issue on every GPU. The existing AMD mesh fix is retained.

CAMERA PATHS
Photo > Camera Paths saves camera keyframes with timing, zoom and roll. Choose
Move or Cut for each transition: A as Move and B as Cut moves from A to B, then
jumps directly to C. Choose a start countdown, Play once, Back and forth or a
Closed loop. Stop / return or Esc restores the starting view where allowed.
Paths save locally with your settings and play in their original region/grid.

UPDATES AND REPAIR
Normal Setup keeps identical application files and replaces changed, missing
or damaged files. The complete installer is still downloaded. Full reinstall /
repair replaces every packaged application file instead. It is available in
Setup and in the new updater, including repair of the current published version.
Both modes preserve settings, saved shots/camera paths, poses, trusted/blocked
lists and cache. Repair does not reset your profile or remove unrelated extra
files. Settings import from Firestorm is not included in this version.

This software is not provided or supported by Linden Lab, the makers of Second Life.
It is also not provided or supported by the Firestorm team.
Read the bundled DISCLOSURES.md and PRIVACY.md before installing/using it.
Privacy: https://github.com/NekoMisa/stellarys-viewer/blob/main/PRIVACY.md
Support: https://discord.gg/MEHr9xgnXG (as time permits).
Never post credentials or private/unredacted logs in public support requests.

EXPERIMENTAL WEB LINK CONTROLS
Preferences > Privacy > Links: enable Link warnings and blocking (off by default).
Keep Warn before opening unlisted web links checked for Open once / Trust and
open / Block domain / Cancel. Clear it to keep blocking without unlisted prompts.
Blocked links show a brief notice. Main OFF bypasses these checks but keeps lists.
Manage sites saves immediately; Common sites imports only selected entries.
New profiles include 31 official Second Life domains and github.com/nekomisa.
Existing saved lists do not receive new defaults automatically. Select additions
in Common sites. GitHub account/repo scopes apply only to their HTTPS pages;
a whole-domain block wins. Adding a scope writes list format 2, which older
0.1.5 viewers cannot read. Back up settings before any downgrade.
Trusted does not mean guaranteed safe. Subdomains need separate entries. Checks
are local and apply to viewer text links, not embedded pages, redirects or media.
The mode and personal lists survive updates. Default uninstall keeps them;
explicit settings removal deletes them. Existing browser prompts still apply.
When updating, choose the existing marked Stellarys installation folder. Another
folder does not move the old installation.

SECOND LIFE LINKS AND PHOTO MENU
The final Setup page has an unchecked "Set up Second Life links with Stellarys"
option. Select it to make Stellarys available for secondlife and hop browser
location links and open the compact link dialog after installation.
This does not replace your existing viewer default. To select Stellarys, choose
Preferences > Network & Files > Stellarys > Open Second Life links with Stellarys, then
Set up SL links. In Windows Default apps, select Stellarys for SECOND LIFE and HOP.
Windows may open the general Default apps page instead of Stellarys's page.
Use the file/link-type search at the top: search secondlife, choose Stellarys,
then repeat for hop. Do not use the general Settings search box.
This update declares missing URL protocols and repairs older Stellarys aliases;
it does not write Windows UserChoice or select a different viewer for you.
Setup registers availability for all users; the Preferences button registers
this installation for the current Windows user without administrator approval.
The dialog shows which application currently opens each link type.

Uninstall removes only link registrations still owned by that installation.
It does not change Windows' saved choice to another viewer. Other users' per-user
registrations are left alone; they may need to select another viewer in Windows
if their chosen Stellarys installation is removed.

Hide/show Photo through Preferences > User Interface > Top Bars > Show Photo menu.
Photo is visible by default. Hiding it keeps tools and existing shortcuts usable.

INSTALLATION
Shot Presets: choose Photo > Shot Presets, name your current setup, set the
image width/height and click Save shot. Choose a saved shot and click Restore
shot in its original region. This applies camera, lens/blur, local lighting and
snapshot dimensions; it does not save or upload a photo. Open Snapshot to review
and save to disk. Flycam and snapshot Freeze Frame must be off. Saved lighting
is a fixed local sky/water setup; use Photo Tools to return to Shared Environment.
Poses are saved separately in the poser. Your shot presets are stored with your
per-user settings and are preserved by updates and default uninstall.

Windows x64; administrator approval required. Default:
C:\Program Files\StellarysViewer
Setup accepts an empty folder or an existing marked Stellarys installation.
It refuses unrelated nonempty folders. Close Stellarys before updating/removing.
The installer and updater are unsigned; Windows may show an unknown publisher.

For an older per-user Stellarys installation, updating its marked folder in
place changes registration to all users and removes matching loaded per-user
uninstall entries only after installation succeeds. It does not move files.
To migrate to Program Files, close Stellarys, back up its per-user data, uninstall
the old application with both data-removal boxes unchecked, then install in the
default folder. Keep your data backup until the new installation works. Setup
never moves or deletes an installation in another folder automatically.

UPDATES
Help > Check for Updates opens the bundled updater. Startup checks can be
disabled there. By default it checks the latest stable GitHub Release at:
https://github.com/NekoMisa/stellarys-viewer
"Include experimental updates (beta)" is off by default. Enable it to also
receive Windows betas. The choice is saved with your Stellarys settings and
survives normal updates. Beta 2 replaces Beta 1; final 0.2.1 replaces its betas.
Turning it off stops beta offers without automatically downgrading your viewer.
Version 0.1.8 needs one manual beta installation to get this checkbox.
Updates require an exact versioned Windows installer asset with GitHub's SHA-256
digest. No digest, unexpected URL, wrong size or wrong hash means no install.
The digest is obtained over HTTPS from GitHub; it is not a publisher signature
and does not protect against compromise of the repository/account itself.
Downloads need approval. From version 0.1.4, the unchecked "Install when the
download finishes (closes Stellarys)" option combines download and install approval.
The installer starts only after SHA-256/size verification and normal viewer
shutdown. Without it, a separate install confirmation is shown. Save your work
first. The ordinary quit confirmation is skipped; settings are saved and logout
completes normally. Unsaved editing can still prompt. If shutdown is cancelled
or times out, installation is postponed. Updating from 0.1.2 still uses its
existing two-step updater; the new option is available for subsequent updates.
The updater never force-kills the viewer, never asks for credentials and never
bypasses Windows administrator approval. An offline or failed check does not
mean that this version is up to date. A failed check is shown as an error; it does not mean you are up to date.

PROFILES AND MIGRATION
Stellarys uses its own folders, per Windows user:
  %APPDATA%\Stellarys_x64
  %LOCALAPPDATA%\Stellarys_x64
Existing Firestorm, Black Dragon and older prototype profiles are untouched.
Start with the fresh profile, then use the viewer's preferences backup/restore
features to transfer selected preferences from your old viewer if desired.
Back up first, close both viewers during any manual copying, and do not copy
saved credentials or old cache paths into the new profile. Migration has not
been automated. Keep your old viewer until you have checked the new one.

UNINSTALLATION
Uninstall preserves settings/cache by default. Two unchecked options allow
removing Stellarys settings/saved sign-ins/logs and its default cache/downloads.
The page shows the Windows account and exact folders. If elevation used another
administrator account, only that administrator's folders are targeted. Other
users' profiles and custom cache locations are never automatically deleted.
No Firestorm, Black Dragon or older prototype data is deleted by these options.

LICENSING
See LICENSE.txt and ThirdPartyLicenses. Credits and upstream notices retained.
Source, issues and release information:
https://github.com/NekoMisa/stellarys-viewer

0.2.1 hotfix: Midnight minimap/radar colours match Firestorm, own chat is white, and group profiles use Firestorm’s layout with Midnight colours. The installer preserves ReShade’s additional root opengl32.dll file link. Other directory/owned-file links remain refused with an exact path in the error.
