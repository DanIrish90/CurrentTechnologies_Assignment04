# Quickstart: User Interface Overlay Refresh

This guide validates the replacement of the debug HUD and world labels with the supplied UserInterface assets.

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed: `python -m pip install -e ".[test]"`
- `assets/UserInterface/InteractionButton.png`, `StaminaBar.png`, and `GameOver.png` present
- World assets present under `assets/World/`

## Automated validation

Run the full suite:

```bash
SDL_VIDEODRIVER=dummy python -m pytest
```

Expected result: existing gameplay tests remain green and new UI tests cover asset dimensions, state visibility, stamina thresholds, layout, overlays, GameOver, restart, and zoomed rendering.

Current workspace note: the full suite currently has one unrelated pre-existing Map Loader failure because `tests/unit/test_map_loader.py` expects 29 obstacles while the already modified `assets/World/World.tmj` loads 37. The focused UI, Fishing, stamina, state, and zoom suite remains green.

Run focused UI checks while iterating:

```bash
SDL_VIDEODRIVER=dummy python -m pytest tests/unit/test_ui_snapshot.py tests/smoke/test_launch_contract.py
```

## Manual scenarios

1. Launch with the configured Feature 010 zoom. Confirm there is no large debug panel and no visible `FISHING POND` or `DOCUMENTS` label/rectangle overlay.
2. Move to the document source. Confirm the interaction button appears centered in the lower third only while collection is possible.
3. Collect a document and move to the relevant civil servant. Confirm the button appears for a valid handover and disappears after leaving the zone.
4. Complete a wave and enter rest. Move to the pond with empty hands. Confirm that merely entering or remaining in the pond does not restore stamina. Cast with `E`, wait for the bite, press `E` within the bite window, complete the Catching mini-game, and verify that only a successful catch increases stamina by the existing configured reward. Verify that a missed bite or escaped fish gives no reward and that the Fishpond debug label/rectangle remains hidden.
5. Consume stamina through document carrying and inspect the bar at full, 50%, below 50%, 10%, below 10%, and zero. Confirm green/yellow/red states and left-anchored proportional shortening. Change the StaminaBar scale to `0.5` and `1.5` in the config and confirm only the bar size changes while its top-left placement and the rest of the UI remain stable.
6. Trigger GameOver. Confirm `GameOver.png` is centered, fully visible, and visually prioritized; confirm the existing Restart control still starts a fresh session.
7. Repeat the visual checks after resizing to 800×600 and 1280×720. Confirm the stamina bar remains top-left, the interaction button remains centered in the lower third, and GameOver remains centered without clipping.

## Expected asset checks

- `StaminaBar.png` is treated as two 320×32 rows.
- `InteractionButton.png` is displayed without changing its E-key meaning.
- `GameOver.png` preserves its aspect ratio and fits inside the visible logical surface.
- All UI follows the configured zoom and remains aligned with the final display surface.
- The existing Fishing mini-game, its bite/Catching feedback, and its successful-catch stamina recovery remain unchanged.
- Pond occupancy, missed bites, and escaped fish do not restore stamina.
- `UI_STAMINA_BAR_SCALE` defaults to `1.0` and affects only the StaminaBar's logical presentation size.
