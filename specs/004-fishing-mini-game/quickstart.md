# Quickstart: Fishing Mini-Game

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

Expected result: the existing movement, bureaucracy, stamina, game-over, and Restart tests remain passing together with fishing unit/state/UI/smoke tests.

## Deterministic fishing scenarios

1. Place an empty-handed player in the Fishing Pond and press `E`; verify `WAITING FOR BITE` and unchanged stamina.
2. Advance exactly 2.0 seconds; verify the bite prompt and a one-second reaction window.
3. Press `E` at 0.5 seconds; verify transition to the catch game. Pressing at 1.0 seconds must miss.
4. In the catch game, press `E` once and verify an upward movement impulse and the 0.15-second grace period; advance without pressing beyond the grace period and verify that downward velocity increases smoothly while position and velocity remain bounded.
5. Press `E` repeatedly during a catch game and verify that upward impulses alter the bar's velocity and that equal elapsed-time simulations produce equivalent positions regardless of update chunk size.
6. Set the fish inside the catch bar and advance 1 second; verify +25 progress. Set it outside and verify -35 progress.
7. Drive progress to 100; verify one caught fish and +25 stamina capped at the stamina maximum.
8. Drive progress to 0 or miss the bite; verify no stamina reward and a reset to idle fishing.
9. Try movement during each active fishing phase; verify the player does not move and the existing workflow remains unchanged.

## Headless and manual checks

Run the existing dummy-SDL launch/quit smoke path and render an active game state without a display. On a desktop display, verify:

- the world label says `FISHING POND`;
- casting, bite, catch, miss, escape, and success messages are readable;
- the vertical play bar, fish symbol, catch bar, and progress bar are distinguishable without color alone;
- movement is paused while fishing and resumes after the attempt;
- a successful catch restores 25 stamina and document processing still works.

See [data-model.md](./data-model.md) for state transitions and [spec.md](./spec.md) for acceptance criteria.
