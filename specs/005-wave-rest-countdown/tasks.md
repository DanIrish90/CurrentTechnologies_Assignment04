---

description: "Implementation task list for the Wave Rest Countdown feature"
---

# Tasks: Wave Rest Countdown

**Input**: Design documents from `/specs/005-wave-rest-countdown/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Test tasks are included because the feature changes deterministic workflow timing, fishing eligibility, UI geometry, and reward handling.

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Add centralized ten-second rest duration, bottom-center clock geometry, and arc-orientation constants in `src/game/config.py`.
- [X] T002 [P] Add completed-rest, transitioning-rest, and active-wave fixtures/helpers in `tests/conftest.py`.
- [X] T003 [P] Verify the updated rest-fishing, active-wave blocking, orientation, and positioning scenarios in `specs/005-wave-rest-countdown/quickstart.md`.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preserve deterministic wave progression before changing fishing availability.

- [X] T004 [P] Add workflow tests for ten-second completion feedback, elapsed countdown, exact zero, and one-time next-wave creation in `tests/unit/test_wave_transition.py`.
- [X] T005 [P] Add boundary tests proving non-negative transition time and initial active Wave 1 behavior in `tests/unit/test_bureaucracy.py`.
- [X] T006 Confirm `advance_progress` remains the single authoritative transition path and handles large elapsed steps without duplicate waves in `src/game/bureaucracy.py`.

## Phase 3: User Story 1 - Understand the Wave Rest Countdown (Priority: P1) MVP

**Goal**: Show the completed wave, readable remaining time, and an upward-facing semicircle centered at the bottom of the screen.

**Independent Test**: Complete a wave, inspect the snapshot and render a rest state; verify the clock is visible, bottom-centered, upward-facing, and counts down from ten to zero.

- [X] T007 [P] [US1] Add `UiSnapshot` tests for rest visibility, completed wave number, clamped seconds, normalized progress, and hidden active-wave state in `tests/unit/test_ui_snapshot.py`.
- [X] T008 [P] [US1] Add state integration tests proving completion feedback starts the rest countdown without changing document or servant state in `tests/unit/test_state.py`.
- [X] T009 [P] [US1] Add a headless renderer smoke test for the visible rest clock and its completed-wave label in `tests/smoke/test_launch_contract.py`.
- [X] T010 [US1] Add derived rest countdown fields to `UiSnapshot`, clamped to `0.0–10.0` seconds and `0.0–1.0` progress, in `src/game/state.py`.
- [X] T011 [US1] Render the semicircle with its open side downward, completed wave number, and readable seconds in `src/presentation/renderer.py`.
- [X] T012 [US1] Position the rest clock horizontally centered in the lower viewport and use centralized dimensions/colors from `src/game/config.py` in `src/presentation/renderer.py`.

## Phase 4: User Story 2 - Fishing During the Rest Phase (Priority: P1)

**Goal**: Make the rest countdown the exclusive fishing window while the countdown continues independently.

**Independent Test**: During rest, cast in the Fishing Pond and verify fishing starts and can reward stamina; during an active wave, the same input remains idle.

- [X] T013 [P] [US2] Add state tests proving an empty-handed player can start fishing during `COMPLETION_FEEDBACK` and `TRANSITIONING` in `tests/unit/test_state.py`.
- [X] T014 [P] [US2] Add state tests proving fishing input is blocked during an `ACTIVE` wave, including inside the Fishing Pond, in `tests/unit/test_state.py`.
- [X] T015 [P] [US2] Add integration tests proving rest time decreases during an active fishing attempt and is not reset by fishing input in `tests/unit/test_state.py`.
- [X] T016 [P] [US2] Add UI snapshot tests for visible fishing feedback during rest and blocked fishing feedback during active waves in `tests/unit/test_ui_snapshot.py`.
- [X] T017 [US2] Gate fishing eligibility on non-`ACTIVE` rest phases while preserving empty-handed Fishing Pond checks in `src/game/state.py`.
- [X] T018 [US2] Keep fishing state progression and stamina rewards enabled during rest while preventing document interaction conflicts in `src/game/state.py`.
- [X] T019 [US2] Render clear fishing availability/unavailability feedback alongside the countdown and existing fishing overlay in `src/presentation/renderer.py`.

## Phase 5: User Story 3 - Automatic Next-Wave Transition (Priority: P1)

**Goal**: Start exactly one next wave at zero, hide the clock, and end fishing without reward at the deadline.

**Independent Test**: Advance a rest state to and beyond zero, verify Wave 2 is active exactly once, the clock is hidden, fishing is idle, and active-wave casting remains blocked.

- [X] T020 [P] [US3] Add exact-boundary and overlong-step tests for one-time next-wave creation and hidden countdown data in `tests/unit/test_state.py`.
- [X] T021 [P] [US3] Add deadline cancellation tests for `WAITING_FOR_BITE`, `BITE_WINDOW`, and `CATCHING` with no fish or stamina reward in `tests/unit/test_state.py`.
- [X] T022 [P] [US3] Add workflow preservation tests for next-wave servant count, document sequence, and active-wave fishing blocking in `tests/unit/test_state.py` and `tests/unit/test_bureaucracy.py`.
- [X] T023 [P] [US3] Add restart regression coverage proving Restart returns to active Wave 1 with no countdown in `tests/unit/test_state.py` and `tests/smoke/test_launch_contract.py`.
- [X] T024 [US3] Detect creation of a new active wave after `advance_progress`, reset fishing before same-update rewards, and preserve the deadline priority in `src/game/state.py`.
- [X] T025 [US3] Hide the rest snapshot after transition and preserve the active-wave fishing block while retaining stamina/game-over rules in `src/game/state.py`.

## Phase 6: Polish & Cross-Cutting Validation

- [X] T026 [P] Update `README.md` with exclusive rest-phase fishing and the bottom-center upward-facing clock.
- [X] T027 [P] Synchronize `specs/005-wave-rest-countdown/data-model.md`, `specs/005-wave-rest-countdown/quickstart.md`, and `specs/005-wave-rest-countdown/research.md` with the exclusive fishing window.
- [X] T028 Run `pytest`, `compileall`, and dummy-SDL renderer checks from `specs/005-wave-rest-countdown/quickstart.md`; fix regressions in `src/` and `tests/`.
- [X] T029 Manually verify fishing during rest, fishing blocked during active waves, deadline cancellation, clock orientation, bottom-center placement, and resumed Wave 2 gameplay in `src/game/state.py` and `src/presentation/renderer.py`.

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **US1 (P1)**: Depends on Phase 2 and delivers the MVP countdown UI.
- **US2 (P1)**: Depends on US1 workflow phase/snapshot data and defines the exclusive fishing window.
- **US3 (P1)**: Depends on US2 fishing eligibility and validates deadline cancellation.
- **Polish (Phase 6)**: Depends on all three user stories.

### Parallel Opportunities

- T004 and T005 can run in parallel.
- T007–T009 can run in parallel before US1 implementation.
- T013–T016 can run in parallel before US2 implementation.
- T020–T023 can run in parallel before US3 implementation.
- T026–T027 can run in parallel with final validation.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Implement US1 snapshot and bottom-center clock rendering.
3. Validate the ten-second rest display independently.

### Incremental Delivery

1. Add US2 and verify fishing is available only during rest.
2. Add US3 and verify exact transition, deadline cancellation, and active-wave fishing blocking.
3. Complete documentation and full validation.

## Notes

- Every task uses the checkbox format with a sequential `T###` ID, optional `[P]`/`[US#]` labels, and a file path.
- `[P]` is used only where tasks can proceed independently without conflicting edits.
- Tests should be written before implementation and must fail for missing behavior first.
