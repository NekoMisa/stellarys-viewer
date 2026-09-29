# Rebuilding this prototype

The source/ tree already contains the existing Fire Kitty Fix 0.1.0 AMD changes
and the experimental poser implementation. It is based on Firestorm commit
10bd3c9f930c76e1427ddd4ecece6cdf36b4406d, base version 7.2.4 (80712).
The poser patch is relative to the previously prepared Fire Kitty Fix source,
not pristine upstream Firestorm.

The build helper reuses the established local Windows build environment:
Visual Studio 2026 with v143 14.44, Windows SDK 10.0.26100.0, Python 3.11,
autobuild, CMake, the Firestorm build variables and its dependencies.
The FMOD installable in autobuild.xml references the locally built 2.03.14
package from the earlier Fire Kitty Fix build. That package and the external
toolchain are dependencies, not bundled viewer source. Set up those packages
and satisfy their licenses before rebuilding on another PC.

Place the extracted source/ directory under C:\FK-Poser-Test, or set
FK_PROTOTYPE_ROOT to its parent directory. FK_TOOLS_ROOT can override the
default Python tools directory C:\FS-AMD-Test\python-tools, and
FK_BUILD_VARIABLES can override C:\FS-AMD-Test\variables\variables.
Keep paths short for Windows compiler tools.

Run prototype/build_prototype.py using the configured Python. It configures
and builds Release; --configure-only and --build-only are also supported.
Use --test-consent to compile/run the standalone consent-state tests.
Run prototype/package_prototype.py after a successful build to assemble the
portable viewer from the upstream packaging manifest. It does not include
profiles or create/install an installer. No settings should be copied into
the release directory.

For revision 2 packaging, set FK_RELEASE_REVISION=r2 before running the
packaging helper. Run test_discovery.py to exercise the actual discovery
function against controlled avatar fixtures (it requires the source at the
default C:\FK-Poser-Test location and the original toolchain helper layout).

prepare_prototype.py and audit_source.py are development provenance helpers;
they expect the earlier unmodified Fire Kitty Fix checkout at
C:\FS-AMD-Test\source. They are not needed to build the already patched tree.
