# Edit Outfit layer ordering

Only **Appearance → Edit Outfit Parts → Clothing** gains these controls.
Wearing, attachments, body parts and RLV commands are unchanged.

- Drag a clothing row above or below another layer of the **same clothing type**.
  A blue insertion line shows the destination. Hover near the list's edge to scroll.
  Escape or releasing outside a valid target cancels.
- Right-click a clothing row and choose **Move to position…**.
  Position **1 is topmost within that clothing type**, not position 1 of the whole outfit.
- Layers between the old and new positions shift together without changing their
  relative order. Changes use the normal outfit/save mechanism.

The new backend validates the worn-item IDs, COF links and order before moving.
An outfit change while the dialog/drag is open cancels the move. Items are identified
by inventory UUID, so separate copies sharing a wearable asset remain distinct.
Local swaps are batched before updating COF descriptions and notifying appearance
once. Reordering follows the existing arrow action's semantics; it does not detach,
replace or add wearables, or introduce new RLV behavior.

## Validation

Compile `layer_order_tests.cpp` as C++17 with assertions enabled and run it.
It exhaustively checks numeric moves and both sides of every drag target for
1–60 layers, plus bounds and stable order of unaffected layers.

In-world checks required before release:

1. Use several clearly distinguishable tattoos. Move the bottom one to position 1,
   then the top one to the last position. Check both appearance and row order.
2. Drag upward and downward, between adjacent rows, to the first/last row, and
   while scrolling a long stack. Check the insertion line matches the result.
3. Drop onto another clothing type or outside the list, or press Escape: no move.
4. Check ordinary selection, multi-selection, right-click and existing row buttons.
5. Open the position dialog, then add/remove/reorder a layer elsewhere. The old
   dialog must refuse its stale move. Refresh during a drag must cancel safely.
6. Test two inventory copies with the same wearable asset. The selected copy moves.
7. Save the outfit, relog and wear the saved outfit again. Layer order must persist.
8. Confirm Wearing has no new controls and attachment/body-part behavior is unchanged.

No in-world validation is claimed merely by passing the native algorithm tests.
