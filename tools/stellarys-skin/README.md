# Stellarys Midnight

Optional deep midnight-blue/violet skin with original flat controls and fixed stars in
window-frame corners. Select **Stellarys Midnight / Midnight** under
**Preferences > Skins**, then restart. All existing skins remain available.
No rendering settings, fonts, control sizes, menus or toolbar commands change.
The login page uses the same darker navy/violet palette with a sparse blue-white
starfield around the edges and retains project, privacy,
source, support and upstream documentation links. No external art, tracking or
scripts are loaded. Version numbers remain in the viewer title and About.
Its outer edges stay flat navy to blend with the native login panel even when
the embedded browser leaves margins on large windows or unusual aspect ratios.
The photography concept illustrates appearance only; it does not add or replace
the viewer's existing photography windows.

Midnight is the default for the Stellarys login mode. Saved explicit skin choices
continue to take precedence. Switching skins follows the existing restart workflow. Leave **Reset toolbars to the skin's
preferred layout** unchecked to retain custom toolbar placement.

Original assets and colour roles are reproducible with Python 3 and Pillow:

```
python tools/stellarys-skin/generate_midnight.py
```

The generator writes `skins/stellarys_midnight` plus its colour-sample thumbnail
under `default/textures/skinspreview`. The shared texture list registers only
that new preview name; existing artwork and definitions are unchanged.
Most layouts and remaining icons use the viewer's fallback skin. The generator
copies complete current default widget definitions and both login panels before
applying style-only changes. Rerun it after upstream changes to those files.
Control names, callbacks, fonts, dimensions and toolbar commands are retained.

Inventory folder categories reuse the familiar bundled legacy artwork through
the same 58 folder aliases as the Firestorm skin. No icon files are changed or
duplicated. Received Items has matching navy/violet textures for collapsed and
expanded states, with its original 40x35 dimensions and arrow preserved.

Prefer the familiar look? Select **Firestorm** or **StarLight** under
**Preferences > Skins**, then restart. Feedback on Midnight's readability,
contrast and artwork is welcome through
[GitHub Issues](https://github.com/NekoMisa/stellarys-viewer/issues).

Unread tab/button highlights use muted steel blue (#355574), with a slightly
lighter blue for mentions (#466583). The selected tab remains lavender. The
existing notification flash timing, count and user settings are unchanged.
