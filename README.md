# Stellarys Viewer

**Stellarys Viewer 0.1.1 (based on Firestorm 7.2.4.80712)** is an independent
viewer with an AMD flicker fix and permission-based local posing. The earlier
prototype names are retained only in historical provenance and build notes.

This software is not provided or supported by Linden Lab, the makers of Second
Life. It is also not an official Firestorm or Black Dragon release. Support is
best effort through this repository's Issues; no support response is guaranteed.

## Included in this source snapshot

- Firestorm **7.2.4 (80712)** as the official upstream base version.
- The AMD changes carried forward from the working build.
- Permission-based local posing of other avatars in Firestorm's existing poser.
- The revision 2 fix that includes other nearby avatars in the Model list.
- Separate Stellarys settings/cache identity from official viewers and prototypes.
- Built-in Windows update checks and a bundled download/verification helper.
- All-users Windows installer with optional profile/cache removal on uninstall.

The pose changes are local to the photographer's viewer. The other person must
explicitly grant permission using a compatible viewer. Pose synchronisation is
not implemented. The maintainer has confirmed that revision 2 posing works in
their live test; this is not a claim of comprehensive compatibility testing.

The source now uses **Stellarys Viewer 0.1.1 (based on Firestorm 7.2.4.80712)**
in About and its copied diagnostics. Help links point to this project, with
upstream documentation explicitly labelled. The Windows application, installer,
updater and login logo use the Stellarys cat-ear/star icon. Existing skins and
upstream credits are retained. The Second Life login page is local Stellarys information; it does
not display Firestorm release news. Stellarys uses its own per-user `Stellarys_x64` settings and cache
folders. Existing viewer profiles are not migrated or deleted. Updated branding strings
use English where new translations are not yet available.

Use Help → Check for Updates to open the updater and change startup checking.
Downloads and installation require approval. The unsigned installer requests
Windows administrator permission; updates preserve settings and cache.
Uninstall also preserves both by default, with explicit optional removal for
the Windows account shown on its data-removal page. Other users, older viewer
profiles and custom cache folders are excluded.

See the [installation notes](tools/stellarys-installer/README-Stellarys.txt) and
[updater release contract](tools/stellarys-updater/README.md). Until a stable
GitHub Release is published, the updater reports that no public release exists.
No Black Dragon renderer transplant or new visual skin is included.

## Versions and provenance

The Stellarys release version remains distinct from the upstream Firestorm
version. Earlier fix/prototype versions appear only in historical provenance.
See [SOURCE-PROVENANCE.md](SOURCE-PROVENANCE.md)
and [stellarys-source.json](stellarys-source.json) for this snapshot's identities.

## Building and testing

The imported source is already patched. Start with the
[prototype build notes](tools/kitty-prototype/BUILDING.md) and the
[upstream Windows instructions](doc/building_windows.md). The prototype helpers
describe the established local Windows environment; they are not a turnkey
clean-machine setup. External build dependencies are not included.

The default helper paths refer to `C:\FK-Poser-Test` and `C:\FS-AMD-Test`.
Use an isolated source/build directory rather than building over an installed
viewer. In particular, `autobuild.xml` retains the local FMOD dependency location
used by the tested build. Supply that dependency under its applicable licence
before reproducing that configuration on another machine.

See the [manual test guide](tools/kitty-prototype/TESTING-r2.txt) and
[revision 2 validation notes](tools/kitty-prototype/VALIDATION-r2.md).
The consent tests and actual-function avatar discovery harness are included.

## Credits and licensing

Stellarys is derived from the Firestorm viewer and the Linden Lab viewer code.
The local poser permission protocol was implemented with reference to Black
Dragon. Original copyright, licence notices and contributor credits are retained.

The upstream root licence is [LGPL 2.1](LICENSE). Individual components, assets
and external dependencies may have their own terms; the root licence does not
replace those notices or grant rights to upstream project branding.

The [original Firestorm README](doc/README-firestorm-upstream.md) is retained for
reference. Upstream GitHub build/deployment workflows were intentionally omitted
from this initial import; they target upstream infrastructure rather than this
project.
