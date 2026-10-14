# Tasks: Fishing Mini-Game

**Input**: Design documents from `/specs/004-fishing-mini-game/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Organization**: Tasks are grouped by the three P1 user stories and follow the deterministic fishing state-machine design.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add centralized fishing balance and presentation values without introducing dependencies.

- [X] T001 Add fishing timing, meter, progress, fish-motion, reward, and UI constants to `src/game/config.py`: bite delay `2.0s`, bite window `1.0s`, catch-bar rise `12`, centralized catch-bar fall balance, aligned progress `25/s`, misaligned progress `35/s`, and stamina reward `25`.
- [X] T002 [P] Add fishing fixtures/helpers for idle, waiting, bite-window, and catching states in `tests/conftest.py`.
- [X] T003 [P] Update `README.md` scope text to describe the Fishing Pond and active fishing recovery instead of passive stamina regeneration.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the pure fishing model and rename the world entity before integrating player state or rendering.

**⚠️ CRITICAL**: User-story implementation depends on this phase.

- [X] T004 Create `FishingPhase`, `FishingState`, `FishingOutcome`, and initial-state factories in `src/game/fishing.py`, including phase elapsed time, catch-bar position/height, fish position, progress, reward flag, and feedback.
- [X] T005 [P] Add pure-model construction and invariant tests to `tests/unit/test_fishing.py`, covering non-negative elapsed time, 0–100 progress bounds, catch-bar bounds, and one-time reward state.
- [X] T006 Rename `StaminaRegenZone` to `FishingPond` and `stamina_regen_zone` to `fishing_pond` in `src/game/world.py`, preserving world containment and unique-id validation.
- [X] T007 [P] Update `tests/unit/test_world.py` for `FishingPond`, its `FISHING POND` label, initial placement, and world-bound validation.
- [X] T008 Remove passive regeneration-zone semantics from `src/game/state.py` and keep the pond as the only world location eligible for active fishing.
- [X] T009 [P] Add initial launch assertions for the renamed pond and no passive regeneration in `tests/smoke/test_launch_contract.py`.

**Checkpoint**: Pure fishing state and renamed pond geometry are testable without Pygame rendering.

---

## Phase 3: User Story 1 - Cast and react to a fish bite (Priority: P1) 🎯 MVP

**Goal**: Let an empty-handed player in the Fishing Pond cast with `E`, wait exactly 2 seconds, and enter the catch game only when reacting before the one-second boundary.

**Independent Test**: Place the player in the pond, press `E`, advance 2 seconds, press within 0.5 seconds, and verify the catching phase; verify a press at 1.0 seconds misses.

### Tests for User Story 1

- [X] T010 [P] [US1] Add fishing transition tests to `tests/unit/test_fishing.py` for `IDLE -> WAITING_FOR_BITE -> BITE_WINDOW`, fixed 2-second bite delay, valid `E` reaction, strict `<1.0s` boundary, and missed-bite reset.
- [X] T011 [P] [US1] Add state integration tests to `tests/unit/test_state.py` for casting only inside `FishingPond`, only empty-handed, and only during an active run.
- [X] T012 [P] [US1] Add fishing status snapshot tests to `tests/unit/test_ui_snapshot.py` for idle, waiting, bite prompt, missed bite, and catching feedback.

### Implementation for User Story 1

- [X] T013 [US1] Implement `start_cast`, bite-delay advancement, and strict reaction-window transitions in `src/game/fishing.py` using elapsed time and `E` edge actions.
- [X] T014 [US1] Add `fishing: FishingState` to `GameState` and initialize it to `IDLE` in `src/game/state.py`.
- [X] T015 [US1] Integrate pond overlap, empty-handed workflow checks, active-run checks, and fishing input dispatch into `update_game_state` in `src/game/state.py`.
- [X] T016 [US1] Pause player movement while fishing is in `WAITING_FOR_BITE`, `BITE_WINDOW`, or `CATCHING` in `src/game/state.py`.
- [X] T017 [US1] Extend `UiSnapshot` and `ui_snapshot` in `src/game/state.py` with fishing phase, status text, bite prompt state, and cancellation/missed-bite feedback.
- [X] T018 [US1] Render the renamed `FISHING POND` label and casting/waiting/bite feedback in `src/presentation/renderer.py` without color-only communication.

**Checkpoint**: User Story 1 is playable: cast, fixed bite timing, valid reaction, missed reaction, and movement pause all work.

---

## Phase 4: User Story 2 - Play the catch game (Priority: P1)

**Goal**: Display and update the fish symbol, catch bar, and fishing progress so timing and repeated `E` presses determine success.

**Independent Test**: Start catching, press `E` and verify an upward impulse and a 0.15-second grace period, then verify smooth gravity-driven fall and compare aligned and misaligned fish progress updates.

### Tests for User Story 2

- [X] T019 [P] [US2] Add catch-bar movement tests to `tests/unit/test_fishing.py`, asserting +12 per `E` press, bounded fall behavior, and clamping at both bounds.
- [X] T020 [P] [US2] Add deterministic fish-motion tests to `tests/unit/test_fishing.py`, asserting the fish symbol stays inside the play range across elapsed updates.
- [X] T021 [P] [US2] Add aligned/misaligned progress tests to `tests/unit/test_fishing.py`, asserting +25/s when the fish touches or overlaps the catch bar and −35/s otherwise, with 0–100 clamping.
- [X] T022 [P] [US2] Add movement-pause and catch-overlay state tests to `tests/unit/test_state.py` and `tests/unit/test_ui_snapshot.py`.

### Implementation for User Story 2

- [X] T023 [US2] Implement deterministic fish-position updates and catch-bar movement in `src/game/fishing.py` with `E` press input and elapsed-time decay.
- [X] T024 [US2] Implement fish/catch-bar overlap detection and fishing-progress gain/loss in `src/game/fishing.py`, treating touching bounds as aligned.
- [X] T025 [US2] Integrate catch-game updates and one-frame interaction consumption into `update_game_state` in `src/game/state.py` without changing document workflow state.
- [X] T026 [US2] Extend `UiSnapshot` in `src/game/state.py` with normalized fish position, catch-bar position/height, fishing progress, and catch-game visibility.
- [X] T027 [US2] Render the vertical catch play bar, fish symbol, catch bar, fishing-progress bar, and readable active-catch instructions in `src/presentation/renderer.py`.
- [X] T028 [US2] Add cancellation paths in `src/game/state.py` for game over and conflicting document interaction, resetting fishing without a reward.

**Checkpoint**: User Stories 1 and 2 work together; the catch game is deterministic, readable, bounded, and movement remains paused.

---

## Phase 5: User Story 3 - Catch a fish and recover stamina (Priority: P1)

**Goal**: Award exactly one fish and restore 25 stamina on full progress, while failed or canceled attempts award nothing.

**Independent Test**: Drive progress to 100, verify one catch and +25 stamina capped at maximum; drive progress to 0 or miss the bite and verify no reward.

### Tests for User Story 3

- [X] T029 [P] [US3] Add escape, success, one-time reward, full-stamina clamp, and failed-attempt tests to `tests/unit/test_fishing.py`.
- [X] T030 [P] [US3] Add stamina reward integration tests to `tests/unit/test_state.py`, asserting +25 only on success and no revival after game over.
- [X] T031 [P] [US3] Add post-catch reset and resumed-document-workflow tests to `tests/unit/test_state.py`.

### Implementation for User Story 3

- [X] T032 [US3] Implement `CAUGHT`, `ESCAPED`, `MISSED_BITE`, and `CANCELED` outcomes in `src/game/fishing.py`, ensuring reward emission can occur only once.
- [X] T033 [US3] Apply `FishingOutcome.stamina_reward` through bounded stamina updates in `src/game/state.py`, adding exactly 25 on success and never reviving game over.
- [X] T034 [US3] Reset fishing to `IDLE` after success, escape, missed bite, cancellation, or Restart in `src/game/state.py` while preserving wave/document state.
- [X] T035 [US3] Add success, escape, miss, cancellation, and restart feedback to `UiSnapshot` in `src/game/state.py`.
- [X] T036 [US3] Render result feedback and successful stamina restoration messaging in `src/presentation/renderer.py`.

**Checkpoint**: All three user stories are complete; skilled fishing restores stamina exactly once and failed attempts remain safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate compatibility with existing gameplay and document the completed vertical slice.

- [X] T037 [P] Add Fishing Pond, fishing-state, and successful-reward launch assertions to `tests/smoke/test_launch_contract.py`.
- [X] T038 [P] Add fishing controls, phases, timing, reward, and cancellation behavior to `README.md`.
- [X] T039 Run the complete pytest and compile checks from `specs/004-fishing-mini-game/quickstart.md`, fixing regressions in `src/` and `tests/`.
- [X] T040 Run the headless Pygame render/quit check against `main.py` and manually verify pond labels, catch meters, feedback, paused movement, success reward, and resumed bureaucracy in `src/presentation/renderer.py` and `src/presentation/window.py`.

---

## Phase 7: User Story 2 Follow-up - Velocity-Based Catch-Bar Motion (Priority: P1)

**Goal**: Replace direct catch-bar fall distance with frame-rate-independent velocity, upward impulses, gravity, and bounded speed while preserving the existing grace period.

**Independent Test**: Start the catch game, press `E`, verify an upward impulse and no gravity change for 0.15 seconds, then verify downward velocity increases smoothly and position/speed remain bounded.

### Tests for User Story 2 Follow-up

- [X] T041 [P] [US2] Add tests in `tests/unit/test_fishing.py` for catch-bar velocity initialization, the 0.15-second grace period, and grace reset after every valid `E` press.
- [X] T042 [P] [US2] Add deterministic velocity-model tests in `tests/unit/test_fishing.py` proving upward impulses, continuous gravity acceleration, bounded speed, and equivalent results for different update chunk sizes.
- [X] T043 [P] [US2] Add state/UI regression coverage in `tests/unit/test_state.py` and `tests/unit/test_ui_snapshot.py` proving velocity-based motion does not alter movement pause, fish alignment, progress, or reward behavior.

### Implementation for User Story 2 Follow-up

- [X] T044 [US2] Replace the prior direct-fall constants with centralized `FISH_CATCH_BAR_UPWARD_IMPULSE`, `FISH_CATCH_BAR_GRAVITY`, `FISH_CATCH_BAR_MAX_SPEED`, and `FISH_CATCH_BAR_GRACE_SECONDS = 0.15` in `src/game/config.py`.
- [X] T045 [US2] Extend the immutable fishing state in `src/game/fishing.py` with `catch_bar_velocity`, validate its speed bound, and retain `time_since_last_press` for the grace-period state.
- [X] T046 [US2] Integrate upward impulses, grace-period gravity suppression, gravity-based velocity updates, velocity clamping, and elapsed-time position integration into `advance_fishing` in `src/game/fishing.py`, preserving fish movement, progress rates, cancellation, and one-time rewards.

**Checkpoint**: User Story 2 remains playable with visible upward impulses, smooth gravity-driven fall, bounded velocity, frame-rate-independent behavior, and unchanged success/failure rules.

---

## Phase 8: Polish & Cross-Cutting Validation

**Purpose**: Synchronize documentation and validate the updated balance behavior.

- [X] T047 [P] Update `specs/004-fishing-mini-game/quickstart.md`, `specs/004-fishing-mini-game/data-model.md`, and `README.md` with velocity, impulse, gravity, bounds, and grace-period controls.
- [X] T048 Run the complete pytest, compile, and headless Pygame checks from `specs/004-fishing-mini-game/quickstart.md` and fix regressions in `src/` and `tests/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on the pure fishing model and Fishing Pond rename.
- **User Story 2 (Phase 4)**: Depends on User Story 1's active fishing integration and movement pause.
- **User Story 3 (Phase 5)**: Depends on User Story 2's progress transitions and overlay data.
- **User Story 2 Follow-up (Phase 7)**: Depends on the existing User Story 2 catch-game implementation and replaces direct fall distance with velocity-based motion without changing the other stories.
- **Polish (Phases 6 and 8)**: Depends on the relevant user story and follow-up tasks.

### User Story Dependencies

```text
Foundation: FishingState + FishingPond
    |
    v
US1: Cast + bite reaction
    |
    v
US2: Catch game
    |
    v
US3: Catch reward + stamina recovery
    |
    v
Polish and regression validation
```

### Parallel Opportunities

- T002, T003, T005, T007, and T009 can run in parallel after the model boundaries are agreed.
- US1 tests T010–T012 can be written in parallel before state/render integration.
- US2 tests T019–T022 can be written in parallel before fishing arithmetic integration.
- US3 tests T029–T031 can be written in parallel before reward integration.
- T037 and T038 can run in parallel after the feature behavior is complete.
- US2 follow-up tests T041–T043 can run in parallel.
- Documentation task T047 can run in parallel with implementation after the behavior is agreed.

## Parallel Example: User Story 2

```text
T019: Catch-bar movement tests in tests/unit/test_fishing.py
T020: Fish-motion tests in tests/unit/test_fishing.py
T021: Fishing-progress tests in tests/unit/test_fishing.py
T022: State/UI catch-overlay tests in tests/unit/test_state.py and tests/unit/test_ui_snapshot.py
```

## Implementation Strategy

### MVP First (Existing Feature + Catch-Bar Follow-up)

1. Complete the unchecked User Story 2 follow-up tasks T041–T046.
2. Run the independent velocity/impulse tests and existing regression tests.
3. Complete T047–T048 and manually verify the playable catch game.

### Incremental Delivery

1. Add User Story 2 and validate all catch-bar/fish/progress rules.
2. Add User Story 3 and validate the one-time stamina reward and reset behavior.
3. Run the full quickstart and manual visual validation.

## Notes

- Every task follows `- [ ] T### [P?] [US?] description with file path`.
- `[P]` is used only where tasks touch independent files or test concerns.
- No `contracts/` directory is needed because this is an internal offline desktop game.
