---

description: "Task list for implementing animated Bureaucrat sprites"
---

# Tasks: Animated Bureaucrats

**Input**: Design documents from `/specs/007-animated-bureaucrat/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md)

**Tests**: Included because the specification explicitly requires tests for frame selection, looping, state changes, independent servant state, placement, and regression behavior.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the baseline and verify the existing game contract before replacing the Civil Servant placeholder.

- [X] T001 Run the existing suite with `python -m pytest` and record baseline results for `tests/smoke/test_launch_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the reusable asset and per-servant presentation foundation.

**⚠️ CRITICAL**: Complete this phase before user-story implementation.

- [X] T002 [P] Add centralized Bureaucrat animation constants for `assets/NPC/Bureaucrat/Bureaucrat-Sheet.png`, 2 × 2 sheet layout, 84 × 128 frame size, and 1/3-second frame duration in `src/game/config.py`
- [X] T003 Create the Bureaucrat frame-set loader in `src/presentation/bureaucrat_animation.py`; validate the exact 168 × 256 source size, extract four reusable frames, map row 0 to Idle and row 1 to Permit, and wrap frame indexes to 0–1
- [X] T004 [P] Add frame extraction and dimension-validation tests for all four Bureaucrat frames in `tests/unit/test_bureaucrat_animation.py`
- [X] T005 Create the per-servant animation manager in `src/presentation/bureaucrat_animation.py`; store independent state by `CivilServant.id`, prune IDs absent from the active wave, and keep all state outside `GameState`

**Checkpoint**: The sheet loads once and the presentation layer can maintain independent animation state for active servant IDs.

---

## Phase 3: User Story 1 - Bureaucrats sichtbar animieren (Priority: P1) 🎯 MVP

**Goal**: Display every unserved Civil Servant as a continuously looping two-frame Idle animation.

**Independent Test**: Create one or more unserved servants, advance controlled elapsed time, and verify that only row-0 frames 0 and 1 are selected in a repeating cycle.

### Tests for User Story 1

- [X] T006 [P] [US1] Add Idle-state tests for `served=False`, repeated 0/1 frame looping, 3 FPS timing, large elapsed intervals, and frame-rate-independent advancement in `tests/unit/test_bureaucrat_animation.py`

### Implementation for User Story 1

- [X] T007 [US1] Implement `served=False` state selection and continuous Idle looping in `src/presentation/bureaucrat_animation.py`; ensure a new unserved servant starts at Idle frame 0
- [X] T008 [US1] Add a presentation update method that advances every active servant independently using elapsed time without mutating `src/game/bureaucracy.py` or `src/game/state.py`

**Checkpoint**: At this point an unserved Civil Servant can be demonstrated with a deterministic, continuously looping Idle animation without renderer integration.

---

## Phase 4: User Story 2 - Erhaltenes Permit visuell darstellen (Priority: P1)

**Goal**: Switch each servant between Idle and Permit loops according to its current `served` state.

**Independent Test**: Advance a servant from `served=False` to `served=True`, verify the Permit row starts at frame 0 and loops, then switch back and verify Idle frame 0 resumes; run the same scenario for multiple servant IDs.

### Tests for User Story 2

- [X] T009 [P] [US2] Add Permit-state tests for row-1 frame selection, continuous 0/1 looping, already-served initialization, and return to Idle after `served=True` becomes false in `tests/unit/test_bureaucrat_animation.py`
- [X] T010 [P] [US2] Add multi-servant isolation tests proving that at least three servant IDs can have independent kinds, frame indexes, and elapsed times in `tests/unit/test_bureaucrat_animation.py`

### Implementation for User Story 2

- [X] T011 [US2] Implement state-kind synchronization in `src/presentation/bureaucrat_animation.py`; reset only the changed servant to frame 0, preserve unrelated servant progress, and initialize already-served servants directly in Permit mode
- [X] T012 [US2] Implement continuous Permit looping and safe frame wrapping at the configured 3 FPS in `src/presentation/bureaucrat_animation.py`

**Checkpoint**: Idle and Permit animations are selected exclusively by each servant’s current `served` value and loop independently.

---

## Phase 5: User Story 3 - Spielinformationen und Interaktion erhalten (Priority: P1)

**Goal**: Replace the Civil Servant rectangles in the running renderer while preserving labels, overlays, target positions, and interaction behavior.

**Independent Test**: Render a wave with multiple servants, including both served states, and verify sprites, labels, overlays, and existing interaction behavior on a Pygame surface.

### Tests for User Story 3

- [X] T013 [P] [US3] Add sprite-placement tests verifying each 84 × 128 frame uses the existing servant target rectangle’s center-bottom anchor without changing logical position or interaction range in `tests/unit/test_bureaucrat_animation.py`
- [X] T014 [P] [US3] Extend the render smoke test to verify multiple Bureaucrat sprites, Servant labels/status text, and existing document/fishing/countdown/Game-Over overlays render successfully in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 3

- [X] T015 [US3] Own one Bureaucrat animation manager in the presentation loop and update it from the current active `CivilServant` collection and elapsed time in `src/presentation/window.py`, without adding animation fields to `src/game/state.py`
- [X] T016 [US3] Update `src/presentation/renderer.py` to draw the selected Bureaucrat frame at each servant’s center-bottom anchor and remove the old Civil Servant rectangle while preserving servant number/status labels
- [X] T017 [US3] Pass an explicit Bureaucrat presentation context through the renderer and adapt direct render callers in `tests/smoke/test_launch_contract.py` so asset loading never occurs inside the render function

**Checkpoint**: The live game displays independent animated Bureaucrats and all existing gameplay/UI behavior remains unchanged.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature and preserve project quality gates.

- [X] T018 [P] Run focused Bureaucrat animation tests from `tests/unit/test_bureaucrat_animation.py` and resolve frame, state, timing, isolation, or placement regressions
- [X] T019 [P] Run the complete regression suite across `tests/` and confirm any failures are unrelated to the Bureaucrat presentation feature
- [X] T020 Run the manual scenarios in `specs/007-animated-bureaucrat/quickstart.md`, including a multi-servant wave and both served states
- [X] T021 Review `src/presentation/bureaucrat_animation.py`, `src/presentation/renderer.py`, and `src/presentation/window.py` for type hints, no global mutable state, no per-frame asset loading, and no mutation of authoritative gameplay state

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No implementation dependency; establishes the regression baseline.
- **Phase 2 (Foundational)**: Depends on T001 and blocks all user stories.
- **Phase 3 (US1)**: Depends on T002–T005 and delivers the MVP idle presentation.
- **Phase 4 (US2)**: Depends on the shared frame set and manager from Phase 2; extends the same presentation module.
- **Phase 5 (US3)**: Depends on the complete state/loop behavior from US1 and US2 before renderer integration.
- **Phase 6 (Polish)**: Depends on the desired implementation tasks from Phases 2–5.

### User Story Dependencies

- **US1 (P1)**: Can start after foundational frame loading and manager setup.
- **US2 (P1)**: Depends on the manager from Phase 2 but remains independently testable before renderer integration.
- **US3 (P1)**: Depends on US1 and US2 so the renderer consumes a complete selected-frame contract.

### Parallel Opportunities

- T002 and T004 can run in parallel after the baseline because they affect configuration and tests.
- T006 can be authored in parallel with T007 if test and implementation ownership is separated; both touch the same behavior and should be merged sequentially.
- T009 and T010 can run in parallel because they add separate test cases in the same test module and should be coordinated before implementation.
- T013 and T014 can run in parallel because one covers pure placement and the other covers rendering integration.
- T018 and T019 are independent validation runs after implementation.

## Parallel Example: User Story 1

```text
Task: "Add Idle-loop tests in tests/unit/test_bureaucrat_animation.py"
Task: "Implement served=False selection and looping in src/presentation/bureaucrat_animation.py"
```

## Parallel Example: User Story 2

```text
Task: "Add Permit-loop tests in tests/unit/test_bureaucrat_animation.py"
Task: "Add multi-servant isolation tests in tests/unit/test_bureaucrat_animation.py"
```

## Parallel Example: User Story 3

```text
Task: "Add sprite-placement tests in tests/unit/test_bureaucrat_animation.py"
Task: "Extend render smoke coverage in tests/smoke/test_launch_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T005.
2. Complete T006–T008.
3. Validate the unserved Idle loop independently.
4. Continue with Permit state and renderer integration before calling the feature complete.

### Incremental Delivery

1. Load and split the sheet once.
2. Add independent Idle loops for all active servant IDs.
3. Add state-driven Permit loops and reset behavior.
4. Integrate sprites and labels into the live renderer.
5. Run focused tests, full regression tests, and manual quickstart validation.

### Completion Criteria

The feature is ready when T001–T021 are checked, both animations loop at the configured rate, multiple servants remain independent, the game launches, and no authoritative workflow or interaction behavior regresses.
