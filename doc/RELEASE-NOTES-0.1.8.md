# Stellarys Viewer 0.1.8 (based on Firestorm 7.2.4.80712)

## What's new

- Cinematic camera paths with keyframes, adjustable timing, camera zoom and roll.
- Instant cuts: move from A to B, then jump directly to C.
- Optional start countdowns, pause/resume, back-and-forth loops and closed loops.
- Faster Windows updates keep identical application files in place.
- Full reinstall / repair replaces every packaged application file while keeping settings and cache.

## Camera paths

Open Photo > Camera Paths. Add two or more keyframes and set each transition
to Move or Cut. Moves use the travel time and motion style; cuts take no travel
time. For A-to-B movement followed by a cut to C, set A to Move and B to Cut.
Snap to view lets you inspect any selected keyframe, including a single-frame
path. Replace view updates that keyframe from the current camera.

Choose no countdown, 5 seconds, 10 seconds or a custom 0–60 seconds. Pause also
pauses the countdown. It runs only before the first pass. Back and forth retraces
the path; a closed loop connects the last frame to the first. Use several views
around a subject for a circle. Stop / return or Esc cancels and restores the
starting view where the current region and camera restrictions allow it.

Paths save locally with motion, cuts, timing, repeat mode and countdown. They
play in their original region and grid with normal third-person camera, Flycam
and snapshot Freeze Frame off. Existing camera limits and RLVa restrictions
remain active. This moves the camera for filming; it does not encode video.
The scene, moving objects and avatar positions are not rewound.

## Windows updates and repair

The complete installer is still downloaded and verified. During installation,
normal mode compares packaged application files by size and SHA-256, keeping
identical files and replacing changed, damaged or missing files. This also works
when an older Stellarys updater launches this installer. Installer bookkeeping,
shortcuts and uninstall registration are refreshed normally.

Choose Full reinstall / repair in Setup to replace every packaged application
file. The new updater also offers this option, including repair of the current
published version. Repair does not reset preferences or clear cache. Neither
mode removes unrelated extra files from the application folder.

Choose the existing marked Stellarys folder to update it. Another folder does
not move an installation. The default remains C:\Program Files\StellarysViewer;
administrator approval is required, and Stellarys must be closed. Official
Firestorm/Black Dragon folders and unrelated nonempty folders are refused.
Windows browser-link registration and its documented Default apps fallback are
retained. Installers remain unsigned; SHA-256 checks file integrity rather than
publisher identity.

## Preserved data and platforms

Settings, cache, saved shots/camera paths, posing data and trusted/blocked lists
remain per-user and survive normal updates and repair. Windows uninstall keeps
them unless explicit removal is selected. Linux packages and portable previews
keep their existing native update mechanisms and separate update feeds; the
Windows file-copy optimization does not change Linux package-manager behavior.

The Firestorm base remains 7.2.4.80712. The AMD fix, posing, rendering algorithms
and existing photography tools are retained. Firestorm settings import and
smaller update downloads are not included.

## Validation

See the matching VALIDATION files for performed tests and remaining limitations.
The maintainer confirmed Windows path playback and saved-path persistence in
the private preview. Native Linux hardware validation is separate from a WSL
build or software-rendered UI check. This independent, non-commercial hobby
viewer is not provided or supported by Linden Lab or the Firestorm team.
