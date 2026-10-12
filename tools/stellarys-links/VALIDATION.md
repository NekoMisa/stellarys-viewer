# Experimental link checks — private validation

12 October 2026. These private checks preceded 0.1.5 release packaging and used
the 0.1.4 version label. Final release package checks are recorded separately
with the 0.1.5 downloads. Installed viewers and personal profiles were not used
for these private checks.

## Checks performed

- Actual shared policy/store tests passed on Windows with v143/C++17 and on
  Linux with GCC 11/C++17. Includes exact destination parsing, lookalikes,
  blocked precedence, disabled checks, removed defaults, empty lists, restart
  persistence, stale instances, locking, rejected edits, corrupt/future/oversized
  files, failed writes and Linux private permissions/symlink refusal.
- Common-site import tests passed: normalized unique suggestions, explicit
  selections only, preserving other entries/removals, keeping newer blocks and
  rejecting invalid selections without a partial save.
- Full Windows and Linux builds containing the Common sites picker passed.
  The initial compile errors were corrected; build logs were retained locally.
- Windows Computer Use visually checked the compiled private application with
  a blank profile, before login: full Privacy > Links tab, Experimental heading,
  main switch unchecked, list editor and readable Common sites picker with no
  automatic selection and Trust selected disabled. No Windows privacy option
  was changed through Computer Use.
- Compiled Linux UI fixtures used a disposable profile, Xvfb/software rendering
  and a localhost HTTP server. Actual text links exercised the production
  callbacks without an account or login. Unknown-link Enter/Cancel made no
  request; Open once opened the local browser destination without saving trust;
  repeated clicks warned; Trust and open saved the domain and subsequent clicks
  followed the trusted route. The direct Block domain button saved the block
  without opening the link. Blocked clicks showed the blocked notice.
- Final Common sites UI fixture: selecting community.secondlife.com imported
  only that domain. Existing photos.example, blocked 127.0.0.1 and a removed
  facebook.com default were preserved. The imported domain was omitted from
  suggestions after a normal viewer restart, with no selection imported
  automatically. Invalid editor input showed a readable error and left rules
  unchanged. The manager stayed a single instance when reopened from the blocked
  notice. Internal and external context-menu browser choices both showed the
  blocked notice, with zero localhost requests. Normal fixture exit was zero.
- Replacing the private application while reusing only the disposable profile
  preserved opt-in, trusted/blocked entries and removed defaults. This was a
  simulated application replacement, not an actual installer/updater upgrade.

## Blocked-list-only follow-up

The separate persisted Warn before opening unlisted web links preference was
added after the Common sites checks above. The shared policy tests passed on
both platforms: unlisted normal links bypass the choice dialog, blocks still
win over trust, the master switch still disables checks, unsupported authorities
remain refused and SLURL handling remains unchanged. Full Windows and Linux
rebuilds for this follow-up passed. The compiled Linux pre-login Links tab
displayed both checkboxes and the explanatory text correctly. Windows has a
separate compiled test copy with a new blank profile; the final checkbox was
not visually rechecked there while the user was using their active viewer.
With the warning checkbox cleared through the compiled Linux UI, a blocked
127.0.0.1 link showed the blocked notice and made zero HTTP requests. After
explicitly removing that test block, clicking the same now-unlisted destination
opened the existing internal browser directly, without the domain-choice prompt;
the local server received /link-test and no trust entry was saved. Preferences
saved the main switch enabled and the warning switch disabled.

The first follow-up restart attempt was interrupted by a non-atomic command-file
write in the private test harness, not a viewer failure. The harness was changed
to submit complete commands atomically and wait for each result before continuing.
The resumed fixture then exited/restarted normally with its existing profile.
The main preference remained enabled, the warning preference remained disabled,
and personal entries/removals persisted. The restored block again stopped the
actual text link, with zero local requests. Final viewer and harness exit were
zero. The unused localhost text in the fixture was not recognized as a clickable
link; the successful unlisted test used the canonical 127.0.0.1 address after
explicitly removing its temporary block.

## Not yet tested

- Real logged-in Second Life chat/IM clicks on Windows, including the user's
  existing browser preference and normal external-browser permission prompts.
- A published installer/updater upgrade carrying these new files and retaining
  actual user lists; uninstall with optional profile removal.
- Real Linux desktop/hardware behavior for this feature. Headless software
  rendering and the inherited CEF plugin emitted environment warnings; these
  fixtures do not establish GPU/rendering quality or general browser security.
- Every skin, language, UI scale or embedded-browser route. Embedded page
  navigation/redirects and parcel media are intentionally outside this feature.
- Sudden power-loss recovery. Normal failed writes preserve the previous file;
  this is not a power-loss durability guarantee.

See TESTING.md for the separate user test. Common-site suggestions are a local
convenience catalogue, not a guarantee that hosted content or redirects are safe.
