# Testing the experimental link controls

Introduced in Stellarys 0.1.5. Earlier private test builds used a 0.1.4 label.
No rendering, poser or photography changes are included.

1. Open Preferences > Privacy > Links, including before login. Check that the
   heading, explanation and Manage button are visible. The warning option starts
   unchecked in a new profile and is labelled Experimental. The separate warning
   checkbox starts checked but disabled until the main switch is enabled.
2. Enable warnings and click OK in Preferences. Open Manage trusted and blocked
   domains and confirm both lists are visible.
3. Send yourself a plain `https://example.com/` link in chat or IM, then click it.
   If example.com is already listed, remove it from both lists first. The warning
   should offer Open once, Trust domain and open, Block domain and Cancel.
4. Press Enter: Cancel is the default and the browser should not open. Click
   again and choose Open once. Existing external-browser prompts may also appear.
   Clicking the link again should still warn.
5. Choose Trust domain and open. The domain is saved and subsequent clicks skip
   this warning. Trusted does not mean the site is guaranteed safe.
6. Remove example.com from the trusted list, click the link again and choose
   Block domain. The link must not open. The blocked notice offers Manage domains
   and Cancel, with no Open once bypass.
7. Use the list editor to add another trusted domain and remove one default
   entry. Close and restart the test viewer. Confirm both personal additions,
   the block and the removed default are retained. List edits save immediately;
   cancelling Preferences does not undo list edits.
8. Optionally test the text link's Open in internal browser / external browser
   context-menu choices. Both should apply the same domain rules.
9. Turn the main Enable link warnings and blocking switch off. This restores the existing link-opening behavior,
   including for domains on the saved blocked list. The saved lists remain.
10. In Manage domains, open Common sites. Nothing should be selected and Trust
    selected should be disabled. Select one domain, then Trust selected: only that
    domain is added. Your other entries remain. Blocked domains should be absent
    from suggestions; a newer block must also win if the picker was already open.
    Removing an imported entry should stay removed after restart, without the
    catalogue silently adding it again.
11. Enable the main switch but clear Warn before opening unlisted web links.
    Unlisted ordinary web links should open without the domain-choice prompt;
    saved blocked links must still show the blocked notice and never open.
    Restart and verify this mode is retained. Turning the main switch off restores
    the original handling, even for saved blocked domains, without deleting lists.

Use ordinary web links for testing. SLURL/Hop actions keep their existing behavior.
Embedded browser pages/redirects are outside this feature's scope. No malicious
site needs to be visited for these checks.

For the pending expanded catalogue, check a new disposable profile separately
from an existing saved one. New profiles include the reviewed Second Life
services and `github.com/nekomisa`. Existing lists do not receive new defaults
automatically; select additions in Common sites. Marketplace's different
`?lang=...` links all share its trusted domain. NekoMisa profile/repository links
match only the HTTPS account scope; other GitHub accounts should still warn.
Blocking `github.com` must override scoped trust and remove that host's scopes.
Removing the block must not resurrect trust. Do not use a downgraded 0.1.5 viewer
to edit a profile after scoped entries have written format 2; keep a backup.

Automated policy/store tests, compiled-viewer fixture checks and this real chat/IM
test are separate checks. A future actual installer/updater upgrade retaining the
lists is also a separate test; a simulated application replacement is not a
published version-to-version upgrade.
