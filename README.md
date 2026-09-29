# Stellarys Viewer

An independent Firestorm-based viewer project with local posing and photography
enhancements. This repository starts from the tested **Fire Kitty Poser
Prototype 0.1, revision 2**, including the existing **Fire Kitty Fix 0.1.0 AMD
rendering changes**.

This software is not provided or supported by Linden Lab, the makers of Second
Life. It is also not an official Firestorm or Black Dragon release. Support is
best effort through this repository's Issues; no support response is guaranteed.

## Included in this source snapshot

- Firestorm **7.2.4 (80712)** as the official upstream base version.
- The Fire Kitty Fix AMD changes carried forward from the working build.
- Permission-based local posing of other avatars in Firestorm's existing poser.
- The revision 2 fix that includes other nearby avatars in the Model list.
- Separate prototype settings/cache identity from the official viewers.

The pose changes are local to the photographer's viewer. The other person must
explicitly grant permission using a compatible viewer. Pose synchronisation is
not implemented. The maintainer has confirmed that revision 2 posing works in
their live test; this is not a claim of comprehensive compatibility testing.

**The compiled application still identifies itself as Fire Kitty Poser.**
Stellarys application/installer branding and the updater are planned follow-up
changes. No Black Dragon renderer transplant is included. There is no
updater-enabled Stellarys release yet, and no official release binary is
published by this initial source import.

## Versions and provenance

The Stellarys release version will remain distinct from the upstream Firestorm
version and the Kitty Fix version. See [SOURCE-PROVENANCE.md](SOURCE-PROVENANCE.md)
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
