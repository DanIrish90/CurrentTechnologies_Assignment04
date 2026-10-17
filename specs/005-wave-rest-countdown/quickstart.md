# Quickstart: Wave Rest Countdown

## Prerequisites

- Python 3.12 or newer
- Project virtual environment at `.venv`
- Pygame-ce and pytest installed as documented in `README.md`

## Automated validation

From the repository root:

```bash
./.venv/bin/python -m pytest -q
./.venv/bin/python -m compileall -q src main.py tests
```

Expected result: existing gameplay, fishing, UI, and smoke tests remain passing, including the WormTimer-specific tests.

## Deterministic feature checks

1. Complete Wave 1 and verify the rest phase starts with `WAVE_REST_DURATION` remaining; default configuration must report 10.0 seconds.
2. Change `WAVE_REST_DURATION` to another positive value and verify the next-wave transition occurs exactly at that duration.
3. During rest, verify `rest_countdown_visible` is true, the WormTimer is rendered below the stamina bar, and the worm position progresses monotonically from the bar's left edge toward its right edge.
4. Set at least two positive `WORM_TIMER_FPS` values and verify frame selection changes at the configured rate while rest duration and worm position remain unchanged.
5. Verify the 448×32 asset is loaded as seven 64×32 frames in left-to-right order and frames loop during rest.
6. Advance rest to zero and verify the worm reaches the right endpoint, the WormTimer disappears, the next wave starts once, and any active fishing attempt ends without reward.
7. During an active wave, including inside the Fishing Pond, verify fishing remains blocked and the WormTimer is hidden.
8. Restart after Game Over and verify Wave 1 is active with no rest countdown or WormTimer visible.

## Headless rendering

Use dummy SDL drivers for display-independent checks:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./.venv/bin/python -m pytest -q tests/smoke/test_launch_contract.py
```

Expected result: the rest UI renders without exceptions, the WormTimer is below the stamina bar, and the obsolete semicircular countdown is absent.

See [data-model.md](./data-model.md) for fields and invariants and [spec.md](./spec.md) for acceptance criteria.
