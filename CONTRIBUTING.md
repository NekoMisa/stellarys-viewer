# Contributing to Stellarys Viewer

Thank you for helping improve Stellarys Viewer. Bug reports, documentation,
translations and code contributions are welcome.

Stellarys is an independent project based on Firestorm and Linden Lab viewer
code. Please use this repository for Stellarys issues and pull requests.
The upstream teams do not provide support for Stellarys builds.
Review and support are best effort; a submission does not guarantee a merge
or a response time.

## Reporting bugs and suggesting features

Search the [existing issues](https://github.com/NekoMisa/stellarys-viewer/issues)
before opening a new one. For a bug report, include:

- Your Stellarys version and the separate Firestorm base version from About.
- Your Windows version and, for graphics problems, GPU and driver version.
- Steps to reproduce the problem, expected behaviour and what actually happened.
- Relevant screenshots or a short, redacted log excerpt if useful.

Remove account identifiers, private conversations, personal file paths and other
personal information before posting screenshots or logs. Never upload passwords,
login credentials, account settings or your complete settings/cache folders.

For a feature request, explain what you want to do and how the change would help.
Discuss substantial rendering, posing, UI or installer changes in an issue before
starting a large implementation.

## Submitting a pull request

1. Create a branch from `main` and keep the change focused on one problem.
2. Use a descriptive title and link related Stellarys GitHub issues, such as
   `Fixes #123`. Firestorm JIRA references are only needed when citing an
   actual upstream issue; they are not required for Stellarys contributions.
3. Describe the problem, resulting behaviour and any relevant tradeoffs.
4. Follow the surrounding code style. Preserve upstream copyright, licence
   notices, credits and existing Firestorm/Linden Lab change annotations.
   Mark new Stellarys-specific changes where it helps future upstream merges;
   do not relabel existing upstream work as Stellarys work.
5. Explain how you verified the change. State your build/test environment,
   results and anything that remains untested. Distinguish a successful build
   from a visually confirmed rendering fix or an in-world posing test.
6. Update the relevant Stellarys documentation when user behaviour, build steps
   or installation instructions change.

For build information, start with the [README](README.md#building-and-testing).
Use a separate test installation and disposable settings for tests that modify
user data. Contributions should preserve posing permissions and the separation
of Stellarys settings/cache from other viewers. Installer and updater changes
must retain installation guards and user approval for downloading/installing.

Do not include generated installers, dependency bundles, personal settings,
credentials, logs or cache in a source pull request. Keep the Stellarys release
version distinct from the Firestorm base version; a version bump should be
coordinated with the release.

## Credits and licensing

Contributions must be compatible with the applicable licences. Keep existing
notices and identify the origin and licence of any imported code or artwork.
See [LICENSE](LICENSE), the [README credits](README.md#credits-and-licensing)
and [source provenance](SOURCE-PROVENANCE.md).

Changes intended for official Firestorm should be submitted separately to that
project under its own contribution guidelines. A Stellarys pull request does
not submit anything upstream.
