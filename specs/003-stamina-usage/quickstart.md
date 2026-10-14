# Quickstart: Stamina Usage and Recovery

## Prerequisites

- Python 3.12 or newer
- Project virtual environment at `.venv`
- Dependencies installed, including Pygame-ce and pytest

## Automated validation

From the repository root:

```bash
./.venv/bin/python -m pytest -q
python -m compileall -q src main.py tests
```

Expected result: all existing tests and the new stamina unit, state, UI, and smoke tests pass; compilation completes without errors.

## Deterministic gameplay checks

The implementation should have tests for these elapsed-time cases:

1. A fresh state starts at `100/100` and is not game over.
2. Carrying a document for `2.0` seconds reduces stamina from 100 to 90.
3. Empty-handed movement outside the zone leaves stamina unchanged.
4. Empty-handed presence in the zone for `2.0` seconds increases stamina by 20, capped at 100.
5. Carrying a document inside the zone drains at 5/s rather than regenerating.
6. A time step that crosses zero clamps stamina to zero and enters game over.
7. Updates and document interactions after game over do not change state.
8. Clicking the visible “Restart” button creates a fresh wave-one state with full stamina.

## Headless launch check

For environments without a display, run the existing Pygame smoke approach with the dummy SDL driver and post a short event sequence containing `QUIT`. Verify the process exits cleanly. A manual desktop run should additionally verify:

- the stamina bar/value and status text are readable;
- the recovery zone is visibly labeled and distinct from documents and servants;
- the Restart button is clickable after exhaustion;
- movement and the document workflow remain usable before game over.

See [data-model.md](./data-model.md) for state invariants and [spec.md](./spec.md) for acceptance scenarios.
