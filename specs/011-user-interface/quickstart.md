# Quickstart: User Interface Overlay Refresh

This guide validates the replacement of the debug HUD and world labels with the supplied UserInterface assets.

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed: `python -m pip install -e ".[test]"`
- `assets/UserInterface/InteractionButton.png`, `StaminaBar.png`, `GameOver.png`, and `FishingMeter.png` present
- World assets present under `assets/World/`

## Automated validation

Run the full suite:

```bash
SDL_VIDEODRIVER=dummy python -m pytest
```

Expected result: existing gameplay tests remain green and new UI tests cover asset dimensions, FishingMeter state/icon composition, native-size centering, modal movement pause, two-second outcome feedback, state visibility, stamina thresholds, layout, overlays, GameOver, restart, and zoomed rendering.

Current workspace note: the full suite currently has three unrelated pre-existing WormTimer/rest-duration failures because the tests expect a 10-second rest while `src/game/config.py` currently defines `WAVE_REST_DURATION = 20.0`. The focused UI, Fishing, stamina, state, and zoom suite is green apart from the same existing rest-duration assertion.

Run focused UI checks while iterating:

```bash
SDL_VIDEODRIVER=dummy python -m pytest tests/unit/test_ui_snapshot.py tests/smoke/test_launch_contract.py
```

## Manual scenarios

1. Launch with the configured Feature 010 zoom. Confirm there is no large debug panel and no visible `FISHING POND` or `DOCUMENTS` label/rectangle overlay.
2. Move to the document source. Confirm the interaction button appears centered in the lower third only while collection is possible.
3. Collect a document and move to the relevant civil servant. Confirm the button appears for a valid handover and disappears after leaving the zone.
4. Complete a wave and enter rest. Move to the pond with empty hands. Confirm that merely entering or remaining in the pond does not restore stamina. Cast with `E` and verify the centered native-size FishingMeter shows the bait icon centered inside the left bar; wait for the bite and verify the bite icon is centered inside the same bar rather than shown on the right. Press `E` within the bite window and verify the fish icon follows the fish position while the catchbar overlay is active. Confirm movement and unrelated actions are paused. Complete the Catching mini-game and verify that only a successful catch increases stamina by the existing configured reward. Verify success and failure icons are centered for exactly 2 seconds, then disappear; a missed bite or escaped fish gives no reward and the Fishpond debug label/rectangle remains hidden.
5. Consume stamina through document carrying and inspect the bar at full, 50%, below 50%, 10%, below 10%, and zero. Confirm green/yellow/red states and left-anchored proportional shortening. Change the StaminaBar scale to `0.5` and `1.5` in the config and confirm only the bar size changes while its top-left placement and the rest of the UI remain stable.
6. Trigger GameOver. Confirm `GameOver.png` is centered, fully visible, and visually prioritized; confirm the existing Restart control still starts a fresh session.
7. Repeat the visual checks after resizing to 800×600 and 1280×720. Confirm the stamina bar remains top-left, the interaction button remains centered in the lower third, and GameOver remains centered without clipping.

## Expected asset checks

- `StaminaBar.png` is treated as two 320×32 rows.
- `InteractionButton.png` is displayed without changing its E-key meaning.
- `GameOver.png` preserves its aspect ratio and fits inside the visible logical surface.
- Ordinary HUD UI follows the configured zoom and remains aligned with the final display surface; FishingMeter remains exactly 128×448 pixels and centered at every tested zoom.
- `FishingMeter.png` is validated as a 128×448 sheet with a 64×448 left bar and six 64×64 right-side icon regions.
- During waiting and the bite window, the selected bait/bite icon is centered inside the left bar and the right icon column is not rendered as an active display.
- The existing Fishing mini-game, its bite/Catching feedback, and its successful-catch stamina recovery remain unchanged.
- Pond occupancy, missed bites, and escaped fish do not restore stamina.
- `UI_STAMINA_BAR_SCALE` defaults to `1.0` and affects only the StaminaBar's logical presentation size.
- Latest validation: `SDL_VIDEODRIVER=dummy python -m pytest -q` → 231 passed, 3 pre-existing rest-duration failures described above.
