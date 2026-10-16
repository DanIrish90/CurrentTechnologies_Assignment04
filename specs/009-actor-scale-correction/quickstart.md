# Quickstart: Actor Scale Correction

## Prerequisites

- Python 3.12+
- Project dependencies installed from `pyproject.toml`
- Repository root as working directory
- Player and bureaucrat sprite sheets present at their configured asset paths
- `assets/World/World.tmj` and `assets/World/MasterTileset.png` present

## Focused automated validation

Run the actor and collision tests:

```bash
SDL_VIDEODRIVER=dummy pytest -q \
  tests/unit/test_character_animation.py \
  tests/unit/test_bureaucrat_animation.py \
  tests/unit/test_collision.py \
  tests/unit/test_world.py \
  tests/unit/test_render_order.py
```

Expected results:

- Source sheets still validate at 84x128 per frame.
- Scaled presentation frames are 21x32 and pixel-sharp.
- Player body is 8x10.
- Servant target is 12x15 and non-solid.
- Foot anchors remain stable.
- Rectangle and polygon collision still blocks movement.

## Full regression validation

```bash
SDL_VIDEODRIVER=dummy pytest -q
```

Expected result: all existing movement, map, document, fishing, stamina, wave, camera, UI, renderer, and smoke tests pass.

## Manual validation

```bash
python main.py
```

Verify:

1. The player and servants fit naturally against the 32x32 tiles and are visibly smaller than before.
2. Pixel edges remain crisp with no smoothing artifacts.
3. Changing direction or animation frame does not move an actor's feet.
4. The player can traverse narrow open paths using the 8x10 body.
5. Rectangle and polygon collision still prevents passage without tunneling.
6. The player can walk through servants; servants do not block movement.
7. Player and servant spawn points, document zones, fishing zone, camera bounds, and draw ordering are unchanged.
8. Document workflow, fishing, stamina recovery, wave progression, and restart remain usable.

## Failure validation

Asset-loading tests should produce clear errors for missing or incorrectly dimensioned sprite sheets. No map coordinates should be edited to compensate for actor scale.
