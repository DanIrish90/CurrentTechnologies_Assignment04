# Quickstart: Configurable Start Zoom

This guide validates that the zoom multiplier is centrally editable, supports fine tuning, preserves gameplay, and renders the complete frame consistently.

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed: `python -m pip install -e ".[test]"`
- World assets present under `assets/World/`

## Automated validation

Run the complete test suite:

```bash
python -m pytest
```

Expected result: all existing gameplay tests pass, plus the zoom configuration, viewport, camera, and headless rendering checks.

Run focused checks while iterating:

```bash
SDL_VIDEODRIVER=dummy python -m pytest tests/unit/test_camera.py tests/smoke/test_launch_contract.py
```

## Manual validation

For each value below, edit the centralized zoom setting, launch the game with `python main.py`, and close it normally:

1. `1.0`: confirm the view matches the pre-feature layout.
2. `1.25`: confirm a fractional intermediate view works and the full UI remains aligned.
3. `1.5`: confirm the player and world are visibly larger than at `1.0`.
4. `2.0`: confirm the default enlarged start view keeps the player visible.
5. `0.5`: confirm the wider view remains clamped to the world.

For each valid value, verify:

- WASD/arrow movement speed and collision behavior are unchanged.
- The camera follows the player and never shows outside-world space.
- Document handover, rest countdown, fishing, stamina, wave progression, game over, and restart still work.
- The window can be resized without black or unrendered regions and without resetting gameplay.
- World, actors, HUD, and overlays scale as one aligned presentation.

## Invalid-value validation

Temporarily test `0`, `-1`, a non-numeric value, and a non-finite value if the configuration format permits it. Expected behavior is a controlled startup fallback or a clear startup error; an uncaught exception or partially initialized game is a failure.

See [data-model.md](./data-model.md) for validation rules and logical viewport semantics.
