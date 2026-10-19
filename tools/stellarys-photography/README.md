# Stellarys shot presets

## Camera paths (unreleased preview)

**Photo → Camera Paths** records camera position, focus, roll and lens zoom as
keyframes. Add at least two views, set the travel time to the next point, then
choose smooth curves, straight movement with easing, or constant-speed straight
movement. This moves the camera for recording; it does not encode video.

For each keyframe, **Transition to next** chooses **Move** or **Cut**. Move uses
the travel time and motion style. Cut jumps instantly to the next frame with no
travel time. For example, set A to Move and B to Cut to travel from A to B, then
jump straight to C. The camera stays at C after a non-looping path finishes.
Cuts also work in reverse and closed loops. Include at least one timed Move
transition to play a path. Consecutive cuts skip directly to the next timed view.

Choose **Play once**, **Closed loop (for circling)** or **Back and forth**.
A closed loop connects the last point to the first; back and forth retraces the
path in reverse. The last point's travel time is used only for a closed loop.
The summary and preview slider cover one full cycle, including both directions
when using Back and forth.

**Start after** offers no countdown, 5 seconds, 10 seconds or a custom 0–60
seconds. The camera remains unchanged during the countdown. Pause also pauses
the countdown; Resume continues it. The delay runs once, before the first pass.
Stop / return or Esc cancels and restores the pre-preview camera position,
focus, roll and lens. Mouse camera control, camera keys, Flycam, leaving the
region, logout or new camera restrictions also stop playback. Stop also restores
avatar focus, or focus on the previous object if it is still present. A moving
avatar/object can change the resulting view; the scene itself is not rewound.

The timeline and **Snap to view** let you inspect a point. Snap to view jumps
directly to the selected keyframe and also works with just one frame. Replace
view instead updates that keyframe from your current camera. Play starts a new run
from the first frame. After pausing playback, Resume continues that run.
For a circle, place several keyframes around the subject and use Closed loop.
Two points alone produce a trip out and back, rather than a circular orbit.

Name and save a path to keep its keyframes, travel times, motion, repeat mode
and countdown in `user_settings/stellarys_camera_paths.xml`. This is per-user
data outside the application, preserved during normal updates and uninstall.
Removing settings deliberately also removes saved paths. Collections are limited
to 20 paths and 100 keyframes per path. Do not package this file: it may contain
private scene locations. Unreadable, invalid or newer files are left intact.
If another viewer changed the file, saving is refused until you reload.

Playback requires the original region and grid, third-person camera, and Flycam,
pilot playback and snapshot Freeze Frame off. Normal camera limits and RLVa
restrictions remain active. Long frame stalls pause playback instead of skipping
ahead. Curves may overshoot between keyframes; use the preview slider to check
the trajectory and add points or choose straight movement when needed.

Standalone C++17 interpolation/countdown tests are in `camera_path_tests.cpp`.
Automated checks and a successful compile do not establish in-world camera
behavior; countdown, reverse/closed loops, constraints, persistence and the
return view must also be exercised in the private preview before release.

## Shot presets

**Photo → Shot Presets** saves a named photo setup in your own Stellarys profile.
It includes the camera's world position, focus and roll, lens/depth-of-field
controls, exposure/tone mapping/glow, visible sky and water, and local snapshot
width and height. Set the image size in the shot panel before saving.

Select a shot and click **Restore shot** to apply it. Return to the original
region and grid first. It sets Snapshot to save to disk with a custom image size;
it does not save, upload or publish an image. The snapshot preview may refresh.
Open Snapshot to review the
image and save when ready. The existing snapshot limits still apply, including
resolution limits for shots containing the UI or HUDs.

Lighting is local to your viewer. A shot stores the visible moment of a day cycle
as fixed lighting. Use Photo Tools to return to the shared environment later.
Poses are separate; save/load them in the poser. Avatars, objects, the region and
the aspect ratio of the live viewer window are not restored by a shot.

Use the normal third-person camera with Flycam and snapshot Freeze Frame off.
Existing camera limits and viewer restrictions remain in effect. A lens value
outside the supported range is rejected rather than silently changed.

Saved shots persist in `user_settings/stellarys_shot_presets.xml`, outside the
installed application. They can contain private scene locations; do not include
this file in application packages or source archives. Updates and the default
uninstall preserve them. Opting to remove Stellarys settings also removes shots.

The collection is bounded, validated and replaced atomically. Preset names are
map keys rather than filenames. Invalid/unreadable collections are left intact.
The shared geometry/range validator has standalone C++ tests in
`shot_validation_tests.cpp`, compiled with C++17. Runtime save/restart/restore,
snapshot dimensions, lighting, roll and wrong-region behavior still need testing
in-world before release.
