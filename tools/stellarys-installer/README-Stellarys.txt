Stellarys Viewer 0.1.3 (based on Firestorm 7.2.4.80712)

A hobby viewer with the AMD flicker fix and permission-based local posing.
The viewer includes clearer update highlights with a full release-notes link, plus
a Photo menu for snapshots, camera controls, Camera Tools, Photo Tools and the
poser and self reset actions. Shot Presets saves camera position, lens/blur,
local lighting and image dimensions together; restore shots in their original
region. Toolbar customization stays at its existing access points.
Your saved toolbar layout and existing shortcuts are retained. Rendering,
posing, the AMD fix and existing skins are unchanged.
This independent viewer is not supported by Firestorm or Linden Lab.

SECOND LIFE LINKS AND PHOTO MENU
The final Setup page has an unchecked "Set up Second Life links with Stellarys"
option. Select it to make Stellarys available for secondlife and hop browser
location links and open the compact link dialog after installation.
This does not replace your existing viewer default. To select Stellarys, choose
Preferences > Network & Files > Stellarys > Open Second Life links with Stellarys, then
Set up SL links. In Windows Default apps, select Stellarys for SECOND LIFE and HOP.
On older Windows versions, search for those link types in Default apps manually.
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
disabled there. It checks the latest stable GitHub Release at:
https://github.com/NekoMisa/stellarys-viewer
Updates require an exact versioned Windows installer asset with GitHub's SHA-256
digest. No digest, unexpected URL, wrong size or wrong hash means no install.
The digest is obtained over HTTPS from GitHub; it is not a publisher signature
and does not protect against compromise of the repository/account itself.
Downloads need approval. From version 0.1.3, the unchecked "Install when the
download finishes (closes Stellarys)" option combines download and install approval.
The installer starts only after SHA-256/size verification and normal viewer
shutdown. Without it, a separate install confirmation is shown. Save your work
first. The ordinary quit confirmation is skipped; settings are saved and logout
completes normally. Unsaved editing can still prompt. If shutdown is cancelled
or times out, installation is postponed. Updating from 0.1.2 still uses its
existing two-step updater; the new option is available for subsequent updates.
The updater never force-kills the viewer, never asks for credentials and never
bypasses Windows administrator approval. An offline or failed check does not
mean that this version is up to date. Until a stable release is published, the
manual check reports that no public releases are available.

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
