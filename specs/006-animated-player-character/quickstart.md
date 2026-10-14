# Quickstart: Animated Player Character

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed with `python -m pip install -e ".[test]"`
- Repository root as the current directory

## Automated validation

Run the complete test suite:

```bash
python -m pytest
```

Expected result: all existing tests and the new character-animation tests pass.

Run only the focused animation tests:

```bash
python -m pytest tests/unit/test_character_animation.py
```

The focused tests must cover:

1. all twelve frames are extracted from the 4 × 3 tileset;
2. up, down, right, and left select the expected row/orientation;
3. dominant-axis selection is deterministic for diagonal displacement;
4. zero displacement returns the first frame of the last direction;
5. 0.125-second frame timing is independent of update-call frequency;
6. large elapsed intervals wrap safely through frames 0–3;
7. blocked movement produces zero displacement and therefore no walking animation;
8. sprite placement uses the player rectangle’s center-bottom anchor.

## Manual validation

Start the game:

```bash
python main.py
```

Verify:

1. The yellow `YOU` rectangle is replaced by the Main Character sprite.
2. Hold each movement direction and observe the correct row and four-frame loop.
3. Move left and right and confirm the side-facing character is original when moving left and mirrored when moving right.
4. Release the movement keys and confirm the character stops on frame 0 of its last direction.
5. Press movement into an obstacle and confirm the player does not walk in place visually when position does not change.
6. Visit the document source, Civil Servant, Fishing Pond, and rest countdown to confirm existing UI and interactions still render normally.
7. Confirm the character’s feet remain anchored to the same logical player position while the sprite extends above the collision box.

## Regression expectations

The feature must not change player speed, collision bounds, interaction range, camera following, document workflow, stamina, fishing, wave transitions, game-over behavior, or restart behavior.
