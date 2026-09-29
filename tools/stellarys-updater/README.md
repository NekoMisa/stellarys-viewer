# Stellarys Windows updater

The viewer starts the bundled `StellarysUpdater.exe` on startup and from
Help → Check for Updates. This separate process survives viewer shutdown;
it is part of the installed viewer, not a browser download workflow.

It uses Windows .NET Framework 4.8 and normal user privileges. Only the final
installer launch requests elevation. Startup checks are optional. A manual
check reports errors; a startup check stays quiet when there is no actionable
update. Downloads and installation require explicit user action. The viewer is
never forcibly terminated. On installation approval it requests normal window
closure and waits up to 90 seconds, allowing viewer shutdown prompts. A cancelled
or timed-out shutdown postpones installation. Other installations/sessions must
be closed by their user. The installer independently rechecks running processes.

## Release contract

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

Compile `Updater.cs` using .NET Framework's `csc.exe`, target `winexe`, referencing
`System.Windows.Forms.dll`, `System.Drawing.dll`, `System.Net.Http.dll`, and
`System.Web.Extensions.dll`. Install it beside `StellarysViewer.exe`.

For tests, compile both `.cs` files with target `exe` and `/main:UpdaterTests`.
The tests exercise real release parsing, version comparison, URL policy, and
SHA-256/size verification with harmless temporary files.

`Test-RemoveUserData.ps1 -FixtureRoot <new empty directory>` validates optional
profile removal only against generated fixtures. Never run the production
removal script against a real user's data as part of a build test.

When changing the release version, update `Release.Current`, the installer,
version metadata and visible About/window-title version together. The upstream
`indra/VIEWER_VERSION` stays at the official Firestorm base version.
