# Stellarys Viewer 0.1.3 validation

Official base: Firestorm 7.2.4.80712. Separate Stellarys version: 0.1.3.
This release adds browser location-link setup, a Photo menu visibility preference,
and optional installation immediately after a verified update download.
Rendering, the AMD fix, posing, photography and shot presets are unchanged.

## Checks performed

- Windows incremental viewer build completed successfully with the existing
  v143 toolchain. The packaged viewer matches the compiled executable.
- Native installer link helper compiled with /W4 /WX. A harmless executable
  confirmed Explorer launches it as the interactive desktop user, unelevated,
  with exactly --link-settings. No actual Windows defaults were changed.
- 25 updater parsing, URL policy, release-summary and hash/size checks passed.
- 29 link registration/update/uninstall checks passed in a disposable registry
  subtree. Existing handler commands, UserChoice and other viewer registrations
  were preserved by the fixtures. Real association keys were untouched.
- Graceful shutdown IPC contract and missing-window checks passed. The final
  compiled viewer also accepted the shutdown request at its empty login screen
  and exited normally. The installed, logged-in viewer stayed open.
- 27 installation-folder/process guard tests passed with disposable folders.
  Optional profile removal tests checked exact-profile scope, older viewer
  preservation, missing profiles and refusal of nested junctions.
- Computer Use inspection confirmed an empty-account login screen, the link
  setup entry under Preferences > Network & Files > Stellarys, its opening of
  the bundled compact dialog, and the checked-by-default Show Photo menu setting
  under User Interface > Top Bars. The compact dialog and updater checkbox
  were readable at the current display scale. The updater preview's download
  and installation actions were disabled.
- Changed XUI/settings XML parsed; source/payload resources and compiler source
  matched. Unrelated rendering, shader, poser, camera/photo/shot-preset source,
  and existing Photo menu actions were unchanged from 0.1.2.
- NSIS compilation, requireAdministrator manifest, asInvoker link-helper
  manifest, embedded approved icons, unsigned binaries, application-file hashes,
  exact uninstall list and clean staging contents were checked.
- Source archive CRC and every member's match to the reviewed source were checked.
  Private marker/credential scans found no matches. Runtime profiles, accounts,
  credentials, caches and build logs are excluded. Previous release artifacts
  remain unchanged. SHA256SUMS.txt records installer and source archive hashes.

## Not tested

No complete elevated 0.1.3 install/update/uninstall cycle or alternate-credential
UAC installation was performed. The installer finish checkbox was checked in
source and its desktop handoff tested separately, rather than through a full
installer run. Actual Windows default-app selection and browser-to-viewer
teleport delivery remain manual checks. Live hiding/showing Photo after login,
unsaved-edit cancellation, multi-session shutdown, high-DPI/multi-monitor layouts
and a clean Windows VM were not tested for this release. The real compiled
shutdown check occurred before login, so it does not confirm server logout.

The combined download/install option is available once 0.1.3 is installed;
updating from 0.1.2 uses the existing 0.1.2 updater and confirmation prompts.
Windows administrator approval still applies. No viewer is forcibly killed.
Existing installed viewers and their profiles were left untouched.
