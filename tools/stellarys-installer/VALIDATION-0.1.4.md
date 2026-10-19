# Stellarys 0.1.4 — prepared Windows build

Official base: Firestorm 7.2.4.80712. Channel: Stellarys Viewer 0.1.4.
Checks recorded before release publication. Installed viewers were not updated.

Performed: successful MSVC v143 build and NSIS packaging; 8 real CMake release
identity/invalid-input cases; 25 compiled updater checks; 27 installer guard
fixtures; disposable optional-data-removal fixtures. Changed XML parsed.
The compiled Linux build of the shared startup code was tested separately.
The Windows first-run disclosure was visually reviewed and approved by the
maintainer, who then continued and signed in manually using the isolated test
profile. This does not constitute an agent-run in-world feature test.

The administrator manifest, approved PE icons/unsigned resources, compiled vs
packaged viewer, complete payload hashes/file inventory, bundled policy/source
documents and explicit uninstall list were verified. Known private markers and
credential-like material were scanned without printing private values. Source
ZIP CRC and member bytes match the prepared source. Previous 0.1.3 artifacts
still match their published checksums. Rendering/AMD/poser/shot code unchanged.

Not performed: full elevated installer/update/
uninstall cycle, real default-app selection, live ToS update/login, native GPU,
in-world posing/photography, or a complete dependency/security/legal audit.
The guard fixtures mock process/registry adapters and use real disposable files.
No TPV directory application or claim of Linden Lab approval is made.

Documentation and new identifiers become effective for downloads only after
publication of the documents and rebuilt release. Old binaries are unchanged.
