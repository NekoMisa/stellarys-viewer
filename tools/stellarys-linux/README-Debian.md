# Stellarys Viewer — Linux installer preview 1

Stellarys 0.1.4, based on Firestorm 7.2.4.80712. Native Linux x86_64.
This experimental installer targets Ubuntu 22.04 and compatible amd64 systems.
Other distributions have not been validated. No Firestorm or Black Dragon
installation is required. No Wine is required for the viewer itself.

## Install

Download the `.deb` to your Downloads folder. Open a terminal there and run:

```bash
sudo apt install ./Stellarys-Viewer-0.1.4-Linux-amd64-preview1.deb
```

Approve the Linux administrator prompt. APT installs the declared dependencies.
Open **Stellarys Viewer** from your application menu. Application files are
installed in `/opt/stellarys-viewer`; this is a system package with a fixed path.
Close every installed Stellarys window before installing, updating or removing it.
An unrelated nonempty folder at that path will not be overwritten.

To use Stellarys for Second Life browser links, run as your normal user:

```bash
stellarys --register-links
```

This chooses Stellarys for this user's `secondlife:` and `hop:` links. Installing
the package alone preserves existing link defaults. A marked desktop entry from
the older tar preview is backed up when registering links; its application folder
is kept. An unrelated entry or symlink is refused.

## Moving from the tar preview

Close the tar preview. Remove its per-user menu entry:

```bash
rm -f ~/.local/share/applications/org.stellarys.Viewer.desktop
```

If you used a custom `XDG_DATA_HOME`, remove that same desktop entry from its
`applications` folder instead. Delete only the extracted `StellarysViewer`
application folder when you no longer need it. Keep `~/.stellarys_x64` for your
settings. Then install the `.deb`. Previously selected Stellarys link defaults use
the same desktop ID and can resolve to the new system entry after the old per-user
entry is removed. Register links again if your desktop needs it.

## Updates

**Help → Check for Updates** checks the Stellarys GitHub repository for a newer
Linux installer, shows short changes and links to full release notes. Windows-only
releases are ignored. Linux preview releases are included while Linux is experimental.
Startup checks can be disabled in the updater window. There is no background daemon.

The installer is downloaded to your per-user cache and checked against the release's
SHA-256, size, package name, architecture and version. These checks detect corruption;
the package is unsigned and they are not an independent publisher signature.

Select **Close Stellarys and install after download** for normal logout followed by
installation, or download first and click **Install update** afterwards. Save your
work first. The viewer is never forcibly killed. Linux still requires administrator
approval. Other open installed Stellarys instances must also be closed. After a
successful update, click **Open Stellarys** or use the application menu.

The updater starts working when a newer release includes both its `.deb` and
`Stellarys-Linux-Update.json`. This preview's local checks are documented separately;
a future public Linux update and your desktop's authentication prompt still need
end-to-end testing. Windows update behavior is unchanged.

## Remove

Close Stellarys and run:

```bash
sudo apt remove stellarys-viewer
```

This removes the application, system menu entry and updater integration. Settings,
accounts, logs, downloaded updates and cache in your home folder are preserved,
including with `apt purge`. The package never deletes files from users' home folders.
Choose another viewer for browser links before removal if desired. Old tar folders,
old per-user shortcuts and any desktop shortcuts you created manually are separate.

Stellarys uses `~/.stellarys_x64`, separate from Firestorm and Black Dragon. The
installer contains clean application files only; it includes no user's settings,
accounts, credentials, logs or cache.

## Limitations

The viewer retains the AMD changes, poser and photography features. The AMD issue
was reported on Windows; its fix is not claimed to be necessary on Linux. GPU,
voice, media and desktop integration can vary by distribution. Legacy Vivox audio
may require additional 32-bit ALSA/PulseAudio packages; these are not automatically
enabled through foreign-architecture setup. The optional Wine voice proxy is not
required to run Stellarys. See VALIDATION.md for actual test coverage.

PROJECT DISCLOSURES AND PRIVACY
This software is not provided or supported by Linden Lab, the makers of Second Life.
Stellarys is also not provided or supported by the Firestorm team.
Read the bundled DISCLOSURES.md and PRIVACY.md before installing/using it.
Privacy: https://github.com/NekoMisa/stellarys-viewer/blob/stellarys-linux/PRIVACY.md
Support: https://github.com/NekoMisa/stellarys-viewer/issues (as time permits).
Never post credentials, private conversations or unredacted logs in public issues.
The first-run screen includes the policy offline before sign-in or automatic login.
