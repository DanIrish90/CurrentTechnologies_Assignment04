# Quickstart: Animated Bureaucrats

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed with `python -m pip install -e ".[test]"`
- Repository root as the current directory

## Automated validation

Run focused animation tests:

```bash
python -m pytest tests/unit/test_bureaucrat_animation.py
```

The focused tests must cover:

1. extraction of all four 84 × 128 frames from the 168 × 256 sheet;
2. selection of row 0 for `served=False`;
3. selection of row 1 for `served=True`;
4. repeated two-frame loops for both states;
5. independent frame progress for at least three servant IDs;
6. reset to frame 0 when a servant changes state;
7. direct Permit initialization for an already served servant;
8. frame-rate independence and safe wrapping for large elapsed intervals;
9. stable center-bottom sprite placement.

Run the complete suite:

```bash
python -m pytest
```

Expected result: the new Bureaucrat animation tests pass and existing bureaucracy, interaction, wave, UI, fishing, stamina, camera, and smoke tests do not regress because the logical game state is unchanged.

## Manual validation

Start the game:

```bash
python main.py
```

Verify:

1. Civil Servants appear as Bureaucrat sprites instead of colored rectangles.
2. Unserved Civil Servants continuously loop the two idle frames.
3. Successfully hand a document to a Civil Servant and confirm that only that servant switches to the Permit animation.
4. Confirm the Permit animation continues looping while the servant remains served.
5. Confirm other servants retain their own frame progress when one servant changes state.
6. Confirm Servant numbers, status labels, document UI, fishing UI, countdown, and Game Over UI remain readable.
7. Confirm the sprite’s larger visual size does not change the interaction position or range.
8. Start a new wave and confirm each new servant starts in the animation matching its current `served` value.

## Regression expectations

The feature must not change document validation, servant ordering, wave transitions, movement, collision, stamina, fishing, camera following, game-over behavior, restart behavior, or interaction range.
