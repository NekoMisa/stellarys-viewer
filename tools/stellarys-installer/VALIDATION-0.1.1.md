# Stellarys 0.1.1 — icon update

Official base: Firestorm 7.2.4.80712. Stellarys version: 0.1.1.

Changes since 0.1.0: approved cat-ear/silver-star artwork for the Windows viewer,
updater, installer/uninstaller and login logo; corresponding Stellarys version
labels; version-specific clean packaging folders. Existing viewer code that
renders the world, the AMD shader changes, poser implementation, profile/cache
identity and installer guard/data-removal scripts are unchanged.

The Windows viewer compiled successfully. Its three embedded application-icon
groups match all ten ICO frames, from 16 through 256 pixels. The viewer's numeric
base FileVersion/ProductVersion remains 7.2.4.80712 and its Stellarys description
is 0.1.1. The 17 updater core validation checks passed against the new version.
An isolated startup test reached the login screen without signing in. The new
icon was visually confirmed in the splash screen, title bar and login area;
0.1.1 and the unchanged Firestorm base appeared in the title/login page. Separate
Stellarys_x64 profile/cache folders appeared, and the test viewer closed normally.

The artifact-specific report beside the installer records final packaging,
administrator manifest, embedded-icon, application-file hash, source archive
and public-release checks. Tests from 0.1.0 remain historical evidence for the
unchanged guard/data-removal code; they are not a claim of a new full installation
or a completed 0.1.0-to-0.1.1 update cycle.

Existing installations and real profile data are not changed by building or
publishing this release. Settings/cache are retained during updates. Optional
uninstall removal remains unchecked by default. Installer/updater are unsigned.
In-world rendering/posing, a clean Windows VM, alternate-account elevation and
cross-user sessions are not newly validated by this icon update.
