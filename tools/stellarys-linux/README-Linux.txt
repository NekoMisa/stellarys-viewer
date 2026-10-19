Stellarys Viewer 0.1.8 - Linux x86_64 experimental preview 1
Based on Firestorm 7.2.4.80712.

Stellarys is an independent hobby viewer with permission-based posing of other
avatars, photography tools, shot presets and the existing AMD flicker changes.
Firestorm or Black Dragon does not need to be installed. Their profiles are not
used. This preview retains the AMD code; it does not claim a Linux flicker fix.

GETTING STARTED
Extract the entire archive to a normal folder you own. Open a terminal in the
StellarysViewer folder and run ./stellarys. Do not run it as root, with sudo, or
by opening bin/stellarys-bin directly. Keep the complete application together.
Ubuntu 22.04 x86_64 is the build target; other distributions need testing.
Working OpenGL drivers and the normal Linux desktop/audio libraries are needed.
This build uses OpenAL audio, rather than the Windows build's FMOD backend.

DESKTOP SHORTCUT AND BROWSER MAP LINKS (OPTIONAL)
Run ./install-desktop.py to add a Stellarys application-menu entry for your Linux
user. This does not move the viewer or choose a different default link handler.
Run ./install-desktop.py --register-links only if you want Stellarys to become
your default for secondlife and hop links. This option requires xdg-utils.
The Linux package does not register handlers automatically when launched.
Moving the extracted folder requires rerunning install-desktop.py so the
shortcut points to the new location. The Windows link-settings button is disabled
on Linux. Stellarys uses its own desktop entry and message-service identity.

SETTINGS, CACHE AND UPDATES
Per-user data is stored separately under ~/.stellarys_x64. Shot presets and poser
data remain local. Posing another avatar requires their explicit permission.
Updates are manual for this initial Linux preview. Help > Check for Updates opens
the project's GitHub releases in your browser. Download a matching Linux archive,
close Stellarys, extract it into a new folder and test it before deleting the old
application folder. Do not copy runtime settings, logs or caches into application
folders. Back up your profile before changing builds.

To remove the application, close it and remove only its extracted folder. This
preserves your profile. Remove its org.stellarys.Viewer.desktop entry from
~/.local/share/applications if wanted, and select another link handler in your
desktop settings if you had chosen Stellarys. Profile deletion is separate and
manual; no automatic cleanup of Firestorm or Black Dragon data occurs.

TEST STATUS
See VALIDATION.md beside the archive for checks actually performed. This is an
experimental Linux build, not a claim of native Linux hardware or in-world
validation. Voice, media, graphics drivers and the added features need volunteer
testing. Report your distribution, GPU/driver and exact symptoms, excluding
saved sign-ins, credentials and private chat logs.

Source and releases: https://github.com/NekoMisa/stellarys-viewer
Keep upstream copyright, LGPL and third-party notices supplied in this package.

Voice runtime on Ubuntu 22.04
----------------------------
The viewer is 64-bit; its inherited Vivox voice helper is 32-bit. Enable the
32-bit runtime if voice is unavailable:
  sudo dpkg --add-architecture i386
  sudo apt update
  sudo apt install libc6:i386 libstdc++6:i386 zlib1g:i386 libuuid1:i386 libasound2:i386 libpulse0:i386
The older libidn.so.11 required by this helper is included from the upstream
runtime bundle. These are dependency instructions, not confirmation of working
in-world voice; native Linux volunteer testing is still required.
PROJECT DISCLOSURES AND PRIVACY
This software is not provided or supported by Linden Lab, the makers of Second Life.
Stellarys is also not provided or supported by the Firestorm team.
Read the bundled DISCLOSURES.md and PRIVACY.md before installing/using it.
Privacy: https://github.com/NekoMisa/stellarys-viewer/blob/stellarys-linux/PRIVACY.md
Support: https://github.com/NekoMisa/stellarys-viewer/issues (as time permits).
Never post credentials, private conversations or unredacted logs in public issues.
The first-run screen includes the policy offline before sign-in or automatic login.
