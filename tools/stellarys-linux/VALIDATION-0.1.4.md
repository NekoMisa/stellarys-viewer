# Stellarys 0.1.4 Linux preview 1 — prepared build

Base: Firestorm 7.2.4.80712. Debian: 0.1.4~linuxpreview1-1, amd64.
Channel: Stellarys Viewer 0.1.4 Linux Preview 1. Checks recorded before publication.

Successful native GCC build, clean staging and Debian packaging. Eight real
CMake version/variant/invalid-input cases and 12 Linux updater core tests passed.
The shared first-run gate rendered under Xvfb/Mesa software OpenGL: no credential
widgets appeared before Continue; Continue opened the blank sign-in screen;
normal per-PID D-Bus quit returned true and exited 0; the persisted acknowledgment
was 1 and the next startup showed sign-in without repeating the disclosure.
Screenshots were inspected. No account was entered and no in-world login occurred.
The final packaged binary also ignored a legacy --channel Firestorm override,
retained its Stellarys login/statistics identity, blocked sign-in at the disclosure
and exited normally with status 0 when Exit was clicked.

The first headless attempt stalled during audio initialization before the new
gate. The successful test used --noaudio and the null audio backend; native audio
and GPU behavior are not validated by this test. No audio/rendering code changed.

Extracted Debian payload paths, hashes, modes, symlinks, policy documents,
metadata and update-feed hash/size verified. Known private-marker scan ran against
all selected source and payload files with values withheld. Matching source
archive and checksums generated. Existing published preview 2 was not replaced.

Not retested: native Mint authentication, an actual public version-to-version
upgrade, fresh distribution dependency installation, dpkg running-viewer guards,
voice/media, in-world posing/photography or AMD hardware. Installer/updater guard
implementation is unchanged from preview 2; its prior checks remain recorded.
No full independent legal/security audit or Linden Lab approval is claimed.
Installed Windows viewers remain untouched. No TPV application was submitted.
