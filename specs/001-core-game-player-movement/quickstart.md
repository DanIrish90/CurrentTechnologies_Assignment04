# Quickstart Validation: Core Game Window and Player Movement

**Feature**: `001-core-game-player-movement`

This guide validates the first playable slice end to end. It assumes Python 3.12+, a working virtual environment, Pygame-ce, and pytest are available or can be installed according to the project's environment setup.

## 1. Automated validation

From the repository root:

```bash
python -m pytest
```

Expected result: all unit tests for input translation, frame-rate-independent movement, collision resolution, world bounds, camera clamping, and initial configuration pass.

The authoritative entities and invariants are documented in [data-model.md](./data-model.md).

## 2. Launch smoke test

From the repository root:

```bash
python main.py
```

Expected result within 5 seconds:

- A desktop game window opens.
- A clearly visible player character appears in a bounded top-down world.
- At least one solid obstacle is visible.
- A title or current-context label, movement hint, and initial player-state indicator are visible.

## 3. Movement validation

1. Hold each documented cardinal movement key separately.
2. Confirm the player moves in the matching direction and stops after release.
3. Hold two compatible movement keys together.
4. Confirm diagonal movement is possible and is not faster than cardinal movement.
5. Hold opposing keys together.
6. Confirm movement on that axis cancels or resolves deterministically without a speed increase.
7. Press an unsupported key.
8. Confirm the player position does not change because of that key.

## 4. Collision and boundary validation

1. Move directly into every visible obstacle.
2. Confirm the player stops at the obstacle boundary and never overlaps it.
3. Move along an obstacle after contacting it.
4. Confirm movement remains possible along a free axis.
5. Move toward each world edge.
6. Confirm the player remains inside the world and the game stays responsive.

## 5. Camera validation

1. Move far enough from the starting position that the player would otherwise leave the viewport.
2. Confirm the camera follows and keeps the player visible.
3. Move to each world edge.
4. Confirm the camera stops at the world edge and never shows invalid space outside the world.

## 6. Stability and UI validation

1. Resize the window if supported and verify the game remains stable and the UI remains usable.
2. Remove window focus and restore it; verify no invalid movement or crash occurs.
3. Close the window through the supported close action.
4. Confirm the game exits cleanly without forced termination.
5. At the target display size, verify that player, obstacles, world bounds, labels, and indicators are distinguishable without relying on color alone.

## 7. Acceptance evidence

Record:

- pytest output and test count;
- launch time across at least 20 launches, with at least 19 reaching the main view within 5 seconds;
- results of obstacle, boundary, camera-edge, unsupported-input, focus, resize, and close checks;
- any control or readability issue found during first-time tester review.

The feature is ready for implementation completion only when the scenarios in [spec.md](./spec.md) and the constitution quality gates are satisfied.
