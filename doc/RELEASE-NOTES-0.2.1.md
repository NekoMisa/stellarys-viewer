# Stellarys Viewer 0.2.1 for Windows

## What's new

- Midnight minimap avatar colours match Firestorm: green for other people, yellow for friends. Radar avatar colours also match Firestorm.
- Group profiles use Firestorm’s familiar layout with Midnight’s colours and controls.
- Your own chat messages use white, matching Firestorm.
- Updates allow ReShade’s extra root `opengl32.dll` file link and leave it untouched. Directory junctions and links replacing packaged application files remain blocked.
- Discord is the preferred place for feedback and bug reports, linked from the login page and **Help > Stellarys Discord**.

**Firestorm base:** 7.2.5.81788.

Join the [Stellarys Discord](https://discord.gg/MEHr9xgnXG) for feedback and bug reports. Redact private account details and conversations from screenshots or logs.

## Updating

Use **Help > Check for Updates** or the attached Windows installer. Update the existing marked installation folder with Stellarys closed; uninstalling first is unnecessary. ReShade’s additional DLL is not packaged, replaced or deleted by Stellarys. Existing user/contact-set colour customisations still take precedence.

Other reparse points remain refused, now with their exact path and attributes in the error. This is a narrow compatibility exception, not a general bypass of installer protections. Settings and cache remain separate per user.

Prefer the familiar skin? Choose **Firestorm** or **StarLight** in **Preferences > Skins**, then restart. Please share Midnight feedback on Discord.

This is a stable Windows release. Linux packages are unchanged and will be updated separately. The Windows installer remains unsigned and requires administrator approval. Source and SHA-256 checksums are attached.

See [validation](VALIDATION-0.2.1.md) for completed checks and their limits.
