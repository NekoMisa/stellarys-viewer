# Private label and trusted-site checks before 0.1.6

Checked 13 October 2026. These checks preceded final 0.1.6 packaging. The private
builds carried the 0.1.5 identity; published 0.1.5 assets remain unchanged.

- Windows v143 and native Linux GCC 11 rebuilds completed successfully.
  The Linux binary tested here is the portable preview channel. The Debian
  variant shares the corrected code but was not separately rebuilt this time.
- The window title now comes from the compiled channel/version. The Linux
  runtime window property was exactly `Stellarys Viewer 0.1.5 Linux Portable
  Preview 1 (based on Firestorm 7.2.4.80712)`, using a disposable blank profile.
- Windows executable description/product name are `Stellarys`, with numeric
  Firestorm base version 7.2.4.80712 retained. Registration keeps its stable
  identifiers and exposes `Stellarys` as its display name. All 30 real disposable
  registry fixture checks passed, including legacy-label replacement and
  preservation of other defaults, registrations and ownership protections.
  The actual installed Windows chooser was not changed or visually retested.
- Translated About headers use the runtime channel instead of old version
  literals. XML parsing and the existing About argument path were checked;
  every translated UI was not individually rendered.
- The 31 official Second Life domains and aliases were reviewed against official
  navigation/documentation and direct alias redirects. Marketplace's six
  language choices share one host. See OFFICIAL-SECOND-LIFE-SITES.md.
- Production policy/store C++17 tests passed on both Windows and Linux, including
  all language parameters, GitHub account/repository boundaries, HTTPS/port
  limits, lookalikes, dot/encoded-path refusal, domain-block precedence, legacy
  list preservation, explicit scoped imports and format-2 persistence.
- An older version-1 list was read without any byte changes or new defaults.
  Its personal trust and GitHub block survived catalogue changes. Importing a
  scope did not remove the block. After explicit block removal, importing the
  scope preserved personal entries and wrote format 2; blocking the domain
  removed the scope, and removing that block did not resurrect trust.
- The compiled Linux list editor and picker were visually inspected with
  Xvfb/software OpenGL and no audio/account. New-profile defaults displayed
  correctly. Removing the NekoMisa scope made it available in Common sites;
  selecting/importing it saved it again. No external test link was opened.
  The viewer exited normally with status 0. This is not a native Linux GPU test.
- Master enable remains off by default. Old saved lists and removed entries are
  not automatically merged with expanded defaults. Rendering, AMD fix, poser,
  photography and motion-blur code were not changed.

During these private checks, no installer packaging, publication, real installed upgrade/downgrade, actual
Windows chooser refresh, or native Mint/Fedora/Bazzite test was performed for
this private test stage. Final 0.1.6 package checks are recorded separately in
doc/VALIDATION-0.1.6.md. Older 0.1.5 readers cannot read scoped format-2 files;
they preserve them and refuse checked links instead of resetting the lists.
