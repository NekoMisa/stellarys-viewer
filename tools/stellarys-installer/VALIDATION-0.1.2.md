# Stellarys 0.1.2 â€” UI test build

Official base: Firestorm 7.2.4.80712. Separate Stellarys version: 0.1.2.
The user approved publication after testing the new UI and shot presets in-world.
The source archive records the reviewed release files without Git history.

Changes: readable updater version heading, up to five short release highlights
and a trusted full-notes link; a Photo menu for existing snapshot, camera,
lighting and moved poser/self-reset actions; clearer tool labels. Complete
local shot presets save camera position/focus/roll, lens/blur, visible sky/water,
exposure/tone mapping/glow and local snapshot dimensions. Toolbar customization
remains at its original access points.

Performed: successful Windows incremental viewer build and NSIS packaging;
25 updater parsing/summary/integrity checks; 77 shared shot geometry/range/name
checks; 27 installer guard fixture checks;
scoped optional profile-removal fixture tests. XUI parsed successfully, all
Photo actions resolve to original callbacks, with the added shot-preset floater;
moved self-reset/poser entries preserve their shortcuts and callbacks. Unrelated
menus and toolbar command IDs/defaults are unchanged. New C++ implements shot
storage/restoration and adds a camera restore method; existing camera behavior,
the rendering pipeline, AMD fix and poser implementation remain unchanged.
Installer behavior is unchanged apart from version labels and line endings.
Administrator manifest, unsigned certificate tables, embedded icon frames,
all 23,796 application-file hashes, exact uninstall file list, matching compiler
source and clean staging contents were checked. Previous release artifacts
remain unchanged. The source archive contains the current tracked working-tree
files and this report, without Git history, build logs or runtime profiles.
SHA256SUMS.txt records installer/source hashes; ZIP CRC is verified separately.

The user visually approved the local updater preview. Its download/installation
were disabled; this is not an end-to-end update test. Computer Use inspection
of that preview was rejected by automatic approval, so no agent visual check
is claimed. The user reported that shot presets seem to work in-world and approved release.
This is a general user confirmation, not a recorded check of each individual
setting or edge case. Actual new-version download/install, full installation/
uninstallation, restart persistence, wrong-region rejection, individual roll/
lens/lighting/dimension restoration and saved-toolbar persistence,
high-DPI/multi-monitor layouts, clean Windows VM and cross-user elevation/session
behavior have not yet been tested for 0.1.2. Runtime test results will be recorded
separately. Existing installed viewers and real user profiles are untouched.
