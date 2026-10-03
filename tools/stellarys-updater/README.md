# Stellarys Windows updater

The viewer starts the bundled `StellarysUpdater.exe` on startup and from
Help â†’ Check for Updates. This separate process survives viewer shutdown;
it is part of the installed viewer, not a browser download workflow.

It uses Windows .NET Framework 4.8 and normal user privileges. Only the final
installer launch requests elevation. Startup checks are optional. A manual
check reports errors; a startup check stays quiet when there is no actionable
update. Downloads and installation require explicit user action. The viewer is
never forcibly terminated. The unchecked install-after-download option treats clicking Download as
approval to install once verification succeeds. Otherwise installation has a
separate confirmation. On installation approval it requests normal logout via
a local WM_COPYDATA message and waits up to 90 seconds. Only the ordinary quit
confirmation is skipped; unsaved editing may still prompt. A cancelled
or timed-out shutdown postpones installation. Other installations/sessions must
be closed by their user. The installer independently rechecks running processes.

## Release contract

The update window shows the release version, installed version and up to five
short bullet highlights. Write release notes with a `## What's new` heading
followed by concise bullets, then a separate heading for installation notes,
validation or other details. Long highlights are shortened in the dialog;
the full notes remain available through the GitHub link. The link is derived
from the validated version tag and fixed Stellarys repository.

- Repository: `NekoMisa/stellarys-viewer`.
- Stable tags: `vMAJOR.MINOR.PATCH`; no drafts or prereleases.
- Asset: `Stellarys-Viewer-MAJOR.MINOR.PATCH-Windows-x64-Setup.exe`.
- Exactly one matching asset, in uploaded state, with a `sha256:` digest and size.
- Obtain metadata from GitHub's HTTPS API, with certificate validation enabled.
- Accept download URLs only for this repository/tag/asset and HTTPS redirects
  only to GitHub's release asset hosts.
- Reject missing digests, malformed versions, oversized metadata/downloads,
  hash/size mismatches, unknown hosts, and same/older versions.

GitHub documents the [release asset digest](https://docs.github.com/en/rest/releases/assets).
This is transport and file-integrity verification, **not publisher signing**.
Repository/account compromise remains within the trust boundary. No tokens are
stored or requested by the updater. Do not publish a stable release until the
matching installer and source are ready. Publishing/updating assets is a
maintainer action; this helper does not do it.

## Build and tests

Compile `Updater.cs`, `LinkRegistration.cs` and `ViewerShutdown.cs` using .NET Framework's `csc.exe`, target `winexe`, referencing
`System.Windows.Forms.dll`, `System.Drawing.dll`, `System.Net.Http.dll`, and
`System.Web.Extensions.dll`. Install it beside `StellarysViewer.exe`.

For tests, compile those three `.cs` files plus `UpdaterTests.cs` with target `exe` and `/main:UpdaterTests`.
The tests exercise real release parsing, version comparison, URL policy,
release-summary formatting and SHA-256/size verification with harmless
temporary files.

`Test-RemoveUserData.ps1 -FixtureRoot <new empty directory>` validates optional
profile removal only against generated fixtures. Never run the production
removal script against a real user's data as part of a build test.

When changing the release version, update `Release.Current`, the installer,
version metadata and visible About/window-title version together. The upstream
`indra/VIEWER_VERSION` stays at the official Firestorm base version.


## Windows location links
`--link-settings` opens the user-operated link setup/status dialog. Registering
from there writes only the current user's Stellarys capabilities and ProgIDs,
then opens Windows Default apps. `--register-links-machine` is used by the
installer's optional final-page action; `--refresh-links-machine` refreshes
registration only if this folder already owns it. `--remove-links` is called
before uninstall removes the helper and unregisters only matching paths/commands.
No mode writes a protocol default or Windows UserChoice, chooses another viewer,
or removes another viewer's registration. Only secondlife/hop are claimed.
The standard viewer `--url` option is last-option bounded and retains its existing
location handling, login behavior and running-instance dispatch.

`LinkRegistrationTests.cs` uses a disposable subtree under the current user's
registry, plus dummy files, to test registration/update/cleanup without modifying
actual association keys. Compile it with LinkRegistration.cs, main
LinkRegistrationTests, references System.Windows.Forms/System.Drawing.

`ViewerShutdownTests.cs` checks the local message contract against a disposable
message-only window. No running viewer is closed. The native finish-page helper
asks the interactive Explorer shell to open link setup. Failure directs the user to
Preferences rather than opening the dialog as the elevated administrator.
