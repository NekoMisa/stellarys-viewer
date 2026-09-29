Stellarys Viewer 0.1.1 (based on Firestorm 7.2.4.80712)

Includes the AMD flicker changes and permission-based local posing, including
the nearby-avatar discovery correction. Version 0.1.1 adds the Stellarys cat-ear
and silver-star application/installer icon. Existing skins remain unchanged.
This independent viewer is not supported by Firestorm or Linden Lab.

INSTALLATION
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
Downloads need approval. After approval to install, the updater asks Stellarys
to close normally and waits for it. Save your work and respond to any shutdown
prompts. If shutdown is cancelled or times out, installation is postponed.
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
