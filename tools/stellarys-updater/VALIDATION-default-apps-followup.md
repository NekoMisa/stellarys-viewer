# Windows Default apps registration follow-up (0.1.7)

A report after 0.1.6 showed no selected secondlife/hop handler and Stellarys
missing from Windows Default apps. The screenshots alone do not establish
whether registration ran or which Windows version was used.

The 0.1.6 helper writes `ApplicationName=Stellarys` but uses `Stellarys Viewer`
as its RegisteredApplications name and Default apps deep-link target. This is
inconsistent with Microsoft's documented registration schema. The correction
uses `Stellarys` consistently and removes the previous alias only if it points
to Stellarys's capabilities path. Existing ProgIDs, viewer commands and
capabilities paths remain stable; no UserChoice or protocol default is written.

References:

- https://learn.microsoft.com/en-us/windows/win32/shell/default-programs
- https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-default-apps-settings

Checks performed on Windows, 2026-10-13:

- 45 real disposable-registry fixture checks passed: matching names and deep
  link, migration from the old alias, repeated registration, old-install cleanup,
  ownership checks, preservation of an unrelated alias, other handlers and
  synthetic UserChoice, missing-application rejection, preservation of an
  existing shared protocol marker, declaration of missing protocols without a
  default command, and version-free owned ProgID application names.
- All 25 updater parsing/download-integrity validation checks passed.
- Corrected production Windows helper compiled successfully.

After the user requested a local test, the installed updater helper was backed
up on D: and replaced with the corrected helper. The viewer executable hash was
verified unchanged; no viewer compilation or profile change was needed.
The first corrected helper still opened the general Default apps page. Inspection
found a missing shared Hop URL Protocol marker and an older machine-wide alias.
A second backed-up helper revision added missing protocol declarations and owned
ProgID application names. The installed machine registration was refreshed with
administrator approval; the dialog refreshed current-user registration.

On Windows 11 Pro build 26300, actual Windows Settings UI checks confirmed:

- Searching the app list finds Stellarys (duplicate entries remain).
- The selected Second Life entry's display label now reads Stellarys.
- Link-type search finds HOP, and its app chooser offers Stellarys by name.
- Both app-specific URI variants still open the general Default apps page,
  including after closing and reopening Settings. This shortcut limitation is
  unresolved; the source dialog now explains the link-type search fallback.

The installed second test helper predates the final explanatory-text change.
No final Windows default-selection button was clicked by the agent. An automated
browser test was stopped because Computer Use could not reliably identify the
browser URL. The user subsequently tested a browser link and confirmed that it
opened installed Stellarys 0.1.6 with the corrected helper. This is user-reported
dispatch confirmation, not an automated test of the final 0.1.7 application.
Clean-machine installation, other Windows builds and the original reporter's
confirmation remain untested.
No screenshots containing the Windows account sidebar are included in source
or release artifacts.
The published 0.1.6 installer and its source archives have not been replaced.
