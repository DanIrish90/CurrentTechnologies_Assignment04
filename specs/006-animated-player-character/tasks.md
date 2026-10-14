---

description: "Task list for implementing the animated Main Character"
---

# Tasks: Animated Player Character

**Input**: Design documents from `/specs/006-animated-player-character/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md)

**Tests**: Included because the feature specification explicitly requires independent tests for frame selection, direction, idle behavior, timing, mirroring, and regression behavior.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the baseline and preserve the existing runtime contract before presentation changes.

- [X] T001 Run the existing test suite with `python -m pytest` and record the baseline in the implementation notes for `tests/smoke/test_launch_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the presentation-only animation foundation shared by all user stories.

**⚠️ CRITICAL**: Complete this phase before user-story implementation.

- [X] T002 [P] Add centralized character animation constants for the asset path, 4 × 3 sheet layout, 84 × 128 frame size, and 0.125-second frame duration in `src/game/config.py`
- [X] T003 Create the presentation animation types, direction-to-row mapping, and fixed-grid frame loader in `src/presentation/character_animation.py`; validate the expected 336 × 384 asset dimensions and keep loaded frames reusable
- [X] T004 [P] Add frame-sheet loading and dimension validation tests for all 12 frames in `tests/unit/test_character_animation.py`

**Checkpoint**: The tileset can be loaded once, split deterministically, and represented without changing `GameState` or `Player`.

---

## Phase 3: User Story 1 - Bewegungsrichtung visuell erkennen (Priority: P1) 🎯 MVP

**Goal**: Select the correct character row and horizontal orientation from actual player displacement.

**Independent Test**: Exercise up, down, right, left, diagonal, and zero-displacement inputs through pure animation-direction tests and verify the expected row/orientation without starting a display.

### Tests for User Story 1

- [X] T005 [P] [US1] Add direction-selection tests for up/down/right/left, dominant-axis diagonals, equal-axis tie-breaking, and zero-displacement preservation in `tests/unit/test_character_animation.py`

### Implementation for User Story 1

- [X] T006 [US1] Implement actual-displacement direction selection and last-direction preservation in `src/presentation/character_animation.py`; map up to row 0, down to row 1, left to the original row-2 view, and right to the mirrored row-2 view
- [X] T007 [US1] Add a presentation update entry point that receives the player position before and after simulation, treats unchanged position as idle, and does not use raw `InputState` intent in `src/presentation/character_animation.py`

**Checkpoint**: Direction and mirroring are independently testable and do not alter collision or movement rules.

---

## Phase 4: User Story 2 - Laufanimation wahrnehmen (Priority: P1)

**Goal**: Advance the four-frame walking loop at approximately 8 FPS using elapsed time and return frame 0 while idle.

**Independent Test**: Advance the presentation animator with different update-step sizes and verify identical frame results for equal elapsed time; verify idle resets to frame 0.

### Tests for User Story 2

- [X] T008 [P] [US2] Add animation timing tests for 0.125-second frame steps, complete four-frame cycles, large elapsed intervals, frame-rate independence, movement-to-idle reset, and valid frame bounds in `tests/unit/test_character_animation.py`

### Implementation for User Story 2

- [X] T009 [US2] Implement elapsed-time frame advancement, cyclic frame indexing, and idle reset in `src/presentation/character_animation.py` with a fixed 0.125-second frame duration
- [X] T010 [US2] Cache horizontally mirrored side-facing frames for right movement and expose the selected current frame without performing file I/O or repeated frame extraction in `src/presentation/character_animation.py`

**Checkpoint**: All 12 source frames and both side orientations animate deterministically independent of render FPS.

---

## Phase 5: User Story 3 - Sprite passend zur Spielfigur darstellen (Priority: P1)

**Goal**: Replace the player placeholder in the renderer while keeping the existing logical player, camera, interactions, and UI unchanged.

**Independent Test**: Render a game state onto a Pygame surface, verify the sprite appears without the `YOU` placeholder, and manually validate movement, collision, interaction, fishing, countdown, and restart behavior.

### Tests for User Story 3

- [X] T011 [P] [US3] Extend the Pygame render smoke test to verify the character sprite path renders successfully and existing overlays remain renderable in `tests/smoke/test_launch_contract.py`
- [X] T012 [P] [US3] Add sprite-anchor tests that verify the rendered frame is centered horizontally and aligned by its bottom edge to the screen-space player collision rectangle in `tests/unit/test_character_animation.py`

### Implementation for User Story 3

- [X] T013 [US3] Own one character animation instance in the presentation loop and update it from the previous and current `GameState.player` positions in `src/presentation/window.py`, without adding animation fields to `src/game/state.py`
- [X] T014 [US3] Update the renderer interface and player drawing in `src/presentation/renderer.py` to use the selected animation frame, mirror left-facing sprites, anchor the sprite at the player rectangle’s center-bottom, and remove only the rectangle and `YOU` label
- [X] T015 [US3] Preserve a deterministic renderer-test path by allowing `tests/smoke/test_launch_contract.py` and other direct callers to provide an explicit animation context or a stable initial presentation state in `src/presentation/renderer.py`

**Checkpoint**: The character is visible and animated in the running game while the 32 × 32 logical collision box and all existing gameplay systems remain unchanged.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete feature, regressions, and documented manual behavior.

- [X] T016 [P] Run focused animation tests from `tests/unit/test_character_animation.py` and resolve any direction, timing, frame-bound, or anchor regressions
- [X] T017 [P] Run the complete regression suite covering movement, collision, state, bureaucracy, stamina, fishing, wave transition, UI, and smoke behavior from `tests/`
- [X] T018 Manually execute the validation scenarios in `specs/006-animated-player-character/quickstart.md`, including blocked movement, left/right mirroring, idle frame, and all existing gameplay overlays
- [X] T019 Review `src/presentation/character_animation.py`, `src/presentation/renderer.py`, and `src/presentation/window.py` for type hints, no per-frame asset loading, no global mutable state, and no changes to authoritative gameplay state

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No implementation dependency; establishes the regression baseline.
- **Phase 2 (Foundational)**: Depends on T001; blocks all user-story work.
- **Phase 3 (US1)**: Depends on T002–T004; provides direction selection used by later animation behavior.
- **Phase 4 (US2)**: Depends on T003 and can run alongside US1 after the shared loader exists, but its final animator integration should use the direction contract from US1.
- **Phase 5 (US3)**: Depends on T006–T010 because rendering needs direction, timing, and selected-frame behavior.
- **Phase 6 (Polish)**: Depends on the desired user-story implementation, especially T014–T015.

### User Story Dependencies

- **US1 (P1)**: Depends only on the foundational loader and test fixture.
- **US2 (P1)**: Depends on the foundational loader; shares the animation module with US1 but remains independently testable.
- **US3 (P1)**: Depends on US1 and US2’s selected-frame contract for final renderer integration.

### Parallel Opportunities

- T002 and T004 can be worked on in parallel after the baseline.
- T005 can be written in parallel with T004; both are test-only work in the same test module and should be merged carefully.
- After T003, the US1 direction tests/implementation and US2 timing tests/implementation can be developed in parallel if one owner coordinates changes to `character_animation.py`.
- T011 and T012 can be developed in parallel because they cover smoke integration and pure anchor behavior separately.
- T016 and T017 are independent validation runs after implementation.

## Parallel Example: User Story 1

```text
Task: "Add direction-selection tests in tests/unit/test_character_animation.py"
Task: "Implement actual-displacement direction selection in src/presentation/character_animation.py"
```

## Parallel Example: User Story 3

```text
Task: "Extend the render smoke test in tests/smoke/test_launch_contract.py"
Task: "Add sprite-anchor tests in tests/unit/test_character_animation.py"
```

## Implementation Strategy

### MVP First (User Story 1 + minimum shared foundation)

1. Complete T001–T004.
2. Complete T005–T007.
3. Validate direction and mirroring independently.
4. Continue through US2 and US3 before considering the feature complete, because direction-only behavior does not yet replace the placeholder in the running game.

### Incremental Delivery

1. Establish the loader and tests.
2. Deliver deterministic direction and mirroring.
3. Add elapsed-time walking animation and idle behavior.
4. Integrate the sprite into the live renderer and presentation loop.
5. Run focused tests, full regression tests, and the quickstart manual checks.

### Completion Criteria

The feature is ready when T001–T019 are checked, all tests pass, the game launches, the sprite is visibly animated, and no authoritative movement/collision/interactions regress.

## Validation Notes

- Focused character and render tests pass: 22 passed.
- Full suite result: 113 passed, 4 pre-existing failures in `tests/unit/test_state.py`, `tests/unit/test_ui_snapshot.py`, and `tests/unit/test_wave_transition.py`. Those failures expect a 10-second wave transition while the current project configuration uses 30 seconds; this feature did not change that configuration or wave logic.
- Headless launch completed without an exception under `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy`; the process was stopped after the validation timeout because the game loop is intentionally continuous.
