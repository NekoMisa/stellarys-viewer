# Stellarys shot presets

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
