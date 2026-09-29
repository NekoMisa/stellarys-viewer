# Fire Kitty Poser Prototype 0.1 — revision 2

Base Firestorm 7.2.4 (80712); Fire Kitty Fix 0.1.0 retained.

Revision 1 accidentally retained a self/animesh-only filter in
getNearbyAvatarsAndAnimeshes(), before avatar rows were created. Revision 2
removes that filter and checks avatar validity and region before discovery.
The existing 50-metre range and mute checks remain. Listing an avatar does
not grant permission to pose it; the consent checks are unchanged.

## Checks performed for revision 2

- A regression harness compiles the actual discovery function extracted from
  the viewer source, using controlled avatar fixtures. It failed against the
  old implementation (returned self/animesh only), then passed after the fix.
  It checks inclusion of another nearby avatar, self and animesh, exclusion
  of muted, distant, dead, other-region and non-avatar entries, and an empty
  character list. This is not an in-world integration test.
- Incremental Windows Release build and link completed with exit code 0.
- Source audit and XML checks were rerun. Rendering and AMD shader sources
  remain unchanged from Fire Kitty Fix; consent implementation is unchanged
  from prototype revision 1, whose 26 consent-state tests passed.
- Application files are packaged separately in an r2 directory, without
  modifying existing viewer installations or the earlier portable package.
  The revision is recorded in fire-kitty-poser-version.json and the README.
  Official executable version remains 7.2.4.80712.
- Release archiving checks ZIP integrity, records application file hashes and
  writes SHA-256 checksums. Private settings, profiles, backups, logs and
  runtime caches are excluded from the portable application and source ZIPs.

## Manual testing still required

Revision 2 has not been launched or tested in-world by the assistant. The
earlier revision reached login wait on the RX 7900 XTX without logging in;
that startup result is not a live test of this revision's avatar discovery.

Run the r2 executable from a newly extracted folder. Put both avatars in the
same region, within 50 metres, and refresh Avatar > Poser > Model. Both
should appear. Then test requesting permission, acceptance/decline, posing,
stop/reset, revocation and region/relog behaviour. The other person needs
Black Dragon or this prototype for the permission protocol. Pose changes
remain local; pose synchronisation is not implemented.

Build and regression logs are retained under work/fire-kitty-poser in the
original workspace. See README.txt for the full manual test sequence.
