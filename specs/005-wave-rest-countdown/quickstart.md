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

Expected result: existing movement, bureaucracy, fishing, stamina, game-over, and Restart tests remain passing together with the countdown tests.

## Deterministic countdown scenarios

1. Complete Wave 1 by serving its Civil Servant; verify the workflow enters completion feedback with 10.0 seconds remaining.
2. Advance 2.5 seconds; verify the remaining time is 7.5 seconds and the semicircular countdown is partially empty.
3. Verify the center label identifies the completed wave as `WAVE 1` while the countdown is active.
4. During the rest phase, stand empty-handed in the Fishing Pond and press `E`; verify a fishing phase starts and the rest timer continues to decrease.
5. During an active wave, stand in the Fishing Pond and press `E`; verify no fishing phase starts.
6. Advance the rest phase to zero; verify the next wave is created, the countdown is hidden, and active-wave fishing remains blocked.
7. Complete a zero-time boundary update more than once; verify exactly one next wave is created and the timer never becomes negative.
8. Restart after game over; verify Wave 1 is active and no rest countdown is visible.

The renderer can be checked without a display using `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`; the countdown and fishing overlays should render without exceptions.

## Headless and manual checks

Run the existing dummy-SDL launch/quit smoke path and render a completed-wave state without a display. On a desktop display, verify:

- the upward-facing semicircular arc is readable without depending on color alone;
- the clock is horizontally centered near the bottom of the screen;
- the completed wave number is centered inside the overlay;
- remaining seconds are readable and decrease smoothly;
- the overlay disappears when the next wave begins;
- fishing input starts a fishing attempt during rest;
- fishing input is blocked after the next wave starts.

See [data-model.md](./data-model.md) for state derivation and [spec.md](./spec.md) for acceptance criteria.
