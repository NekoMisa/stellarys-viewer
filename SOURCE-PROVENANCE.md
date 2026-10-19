# Source provenance

This is a source snapshot import into the independently named Stellarys Viewer
project, not a rewrite of the original authors' contribution history.

| Component | Identity |
| --- | --- |
| Official Firestorm base | 7.2.4 (80712) |
| Firestorm base commit | `10bd3c9f930c76e1427ddd4ecece6cdf36b4406d` |
| Kitty AMD fix version | Fire Kitty Fix 0.1.0 |
| AMD reference commit | `0c132c2eb3d15afc56d7fe42589dc8f2eb778197` |
| Poser snapshot | Fire Kitty Poser Prototype 0.1, revision 2 |
| Public project name | Stellarys Viewer |
| Stellarys Windows package version | 0.1.8 |
| Current release source | Stellarys 0.1.8 |

Upstream repository: https://github.com/FirestormViewer/phoenix-firestorm

The source retains the existing AMD patch adaptation and build/dependency
adjustments used for the working Windows build. It also includes the independent
poser permission implementation and the revision 2 nearby-avatar discovery fix.
No rendering changes were made during this repository import. The proposed
Black Dragon renderer port has not been implemented. Subsequent Stellarys
releases added approved GitHub update downloads/installation, photography shot
presets, optional browser-link registration and project disclosures. The Linux
branch adds native Linux packaging and an administrator-approved update helper.

Original tracked source files were selected from the upstream Git inventory,
then taken from the tested patched source tree. The three new poser permission
files were included explicitly. Private ignored API-key headers, local profiles,
settings backups, build trees and compiled application packages were not imported.

The upstream README was moved to doc/README-firestorm-upstream.md. Upstream
.github automation/configuration was omitted to avoid running workflows intended
for the Firestorm/Linden Lab infrastructure. The original .gitignore was retained
and extended for local builds, profiles and signing material.

The root licence and original source notices remain intact. The prototype
verification notes report exactly what was tested and what still needs live
verification; the maintainer subsequently reported that the poser works.

The official Firestorm base remains 7.2.4.80712. From 0.1.4 onward the compiled
channel contains the Stellarys release number, with a separate variant for
different preview sources. Its channel/base-version pair is the viewer
identifier used for login and statistics. Historical 0.1.1-0.1.3 identifiers
were not distinct; new packages do not retroactively change installed binaries.

Public Windows builds include the FMOD runtime, its licence and upstream
attribution, subject to FMOD's terms. The maintainer confirmed the project is
entirely non-commercial. Linux uses OpenAL instead. Proprietary Havok/KDU and
automatic crash upload are disabled in these build configurations. Dependency
notices are retained; a complete independent legal audit is not claimed.
