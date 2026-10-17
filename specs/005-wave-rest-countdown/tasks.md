---

description: "Implementation tasks for the WormTimer wave-rest countdown"
---

# Tasks: Wave Rest Countdown

**Input**: Design documents from `/specs/005-wave-rest-countdown/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently after the foundational work.

## Phase 1: Setup

**Purpose**: Confirm the existing project structure and asset contract before implementation.

- [X] T001 Verify the feature asset and existing UI rendering entry points in `assets/UserInterface/WormTimer.png`, `src/presentation/ui_assets.py`, and `src/presentation/renderer.py`
- [X] T002 [P] Record the feature validation commands and expected outcomes in `specs/005-wave-rest-countdown/quickstart.md`

---

## Phase 2: Foundational

**Purpose**: Establish shared configuration and validated sprite data that all user stories depend on.

**⚠️ CRITICAL**: Complete this phase before user-story implementation.

- [X] T003 Replace `DOCUMENT_TRANSITION_SECONDS` with positive `WAVE_REST_DURATION = 10.0` and add positive `WORM_TIMER_FPS = 8.0` plus `WORM_TIMER_ASSET_PATH`, `WORM_TIMER_FRAME_WIDTH = 64`, `WORM_TIMER_FRAME_HEIGHT = 32`, and `WORM_TIMER_FRAME_COUNT = 7` in `src/game/config.py`
- [X] T004 [P] Add `split_worm_timer_frames(surface)` and extend `UiAssets` with seven validated 64×32 frames from the 448×32 sheet in `src/presentation/ui_assets.py`
- [X] T005 [P] Add asset-dimension and seven-frame ordering tests for `WormTimer.png` in `tests/unit/test_ui_assets.py`
- [X] T006 Update existing workflow duration references and transition assertions to use `config.WAVE_REST_DURATION` in `src/game/bureaucracy.py`, `src/game/state.py`, `tests/unit/test_state.py`, and `tests/unit/test_wave_transition.py`

**Checkpoint**: Configuration and asset loading are validated; user stories can now be implemented.

---

## Phase 3: User Story 1 - Ruhephase und WormTimer verstehen (Priority: P1) 🎯 MVP

**Goal**: After wave completion, show the animated WormTimer below the stamina bar and make its movement represent the configured rest duration.

**Independent Test**: Complete a wave, verify the WormTimer is visible under the stamina bar, advance simulation time, verify monotonic left-to-right movement, and confirm it reaches the right endpoint at rest expiry for both default and alternate positive durations.

### Tests for User Story 1

- [X] T007 [P] [US1] Add snapshot tests for rest visibility, clamped remaining time, normalized elapsed progress, and WormTimer frame index in `tests/unit/test_ui_snapshot.py`
- [X] T008 [P] [US1] Add deterministic tests for configurable rest duration, zero clamping, and one-time next-wave transition in `tests/unit/test_wave_transition.py`
- [X] T009 [P] [US1] Add layout tests proving the WormTimer track is below `stamina_bar_rect`, moves from its left edge to right edge, and remains fully visible at endpoints in `tests/unit/test_ui_layout.py`

### Implementation for User Story 1

- [X] T010 [US1] Replace hard-coded duration references with `config.WAVE_REST_DURATION` in `src/game/bureaucracy.py` and preserve elapsed-time, clamping, and one-time transition behavior
- [X] T011 [US1] Extend `UiSnapshot` and `ui_snapshot` with `rest_elapsed_progress` and deterministic `worm_timer_frame_index` derived from `WAVE_REST_DURATION` and `WORM_TIMER_FPS` in `src/game/state.py`
- [X] T012 [US1] Add a pure WormTimer placement helper anchored to the rendered stamina-bar rectangle below the bar with a clamped left-to-right progress track in `src/presentation/ui_assets.py`
- [X] T013 [US1] Replace the semicircular `_draw_rest_countdown` implementation with WormTimer frame rendering below the stamina bar, using the snapshot frame index and elapsed progress in `src/presentation/renderer.py`
- [X] T014 [US1] Update the rest rendering smoke test to assert WormTimer rendering succeeds and the obsolete semicircular countdown path is absent in `tests/smoke/test_launch_contract.py`

**Checkpoint**: User Story 1 is independently functional: configurable rest timing, animated frames, time-proportional worm movement, and hidden-on-transition behavior work together.

---

## Phase 4: User Story 2 - Angeln während der Ruhephase (Priority: P1)

**Goal**: Preserve fishing as the exclusive rest-phase interaction while the WormTimer continues independently.

**Independent Test**: Start fishing during rest, advance time while fishing, verify the WormTimer continues progressing, then verify fishing remains blocked during an active wave.

### Tests for User Story 2

- [X] T015 [P] [US2] Extend state tests to verify fishing input does not pause rest progress or WormTimer progress in `tests/unit/test_state.py`
- [X] T016 [P] [US2] Extend smoke coverage to verify rest-phase fishing still starts and active-wave fishing remains blocked in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 2

- [X] T017 [US2] Preserve and, where needed, adjust rest-phase fishing eligibility while using the configurable transition timer in `src/game/state.py`
- [X] T018 [US2] Ensure the renderer draws WormTimer independently of fishing overlays and keeps WormTimer visibility tied only to the rest workflow phase in `src/presentation/renderer.py`

**Checkpoint**: User Story 2 is independently functional: fishing remains available only during rest and cannot alter the WormTimer or timer progression.

---

## Phase 5: User Story 3 - Automatischer Übergang zur nächsten Wave (Priority: P1)

**Goal**: At rest expiry, finish the WormTimer at the right endpoint, start exactly one next wave, hide the timer, and cancel active fishing without reward.

**Independent Test**: Advance a rest phase to zero with and without an active fishing attempt; verify one next wave, no negative timer, no reward at the boundary, and no visible WormTimer afterward.

### Tests for User Story 3

- [X] T019 [P] [US3] Add boundary tests for right-end WormTimer progress, timer hiding, one-time wave creation, and restart reset in `tests/unit/test_state.py`
- [X] T020 [P] [US3] Add regression coverage for cancellation without stamina reward when rest expires during fishing in `tests/unit/test_state.py`

### Implementation for User Story 3

- [X] T021 [US3] Preserve transition-before-fishing-reward ordering and reset active fishing at the configured rest boundary in `src/game/state.py`
- [X] T022 [US3] Ensure restart returns to Wave 1 with no visible WormTimer and no stale animation frame in `src/game/state.py` and `src/presentation/renderer.py`

**Checkpoint**: User Story 3 is independently functional: wave transition, timer visibility, fishing cancellation, and restart behavior satisfy the deadline rules.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature, remove obsolete implementation details, and preserve launchability.

- [X] T023 [P] Update countdown-related names, comments, and docstrings to describe WormTimer rather than the removed semicircular countdown in `src/game/state.py`, `src/presentation/renderer.py`, and `tests/`
- [X] T024 [P] Add validation that non-positive `WAVE_REST_DURATION` and `WORM_TIMER_FPS` fail clearly in `src/game/config.py` or the consuming pure helpers, with coverage in `tests/unit/`
- [X] T025 Run the complete automated suite and compile check from `specs/005-wave-rest-countdown/quickstart.md`
- [X] T026 Run the headless smoke validation and manually verify the WormTimer at reference window sizes 960×640, 800×600, and 1280×720 using `specs/005-wave-rest-countdown/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; confirm paths and validation commands.
- **Phase 2 Foundational**: Depends on Setup; blocks all user stories.
- **Phase 3 US1**: Depends on Foundational; delivers the MVP visual and timing slice.
- **Phase 4 US2**: Depends on Foundational and integrates with the US1 timer presentation; fishing behavior must remain independently testable.
- **Phase 5 US3**: Depends on Foundational and the transition behavior exercised by US1/US2; validates the expiry boundary.
- **Phase 6 Polish**: Depends on all required user stories.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2; MVP.
- **US2 (P1)**: Can start after Phase 2, but renderer integration should follow the shared snapshot shape from US1.
- **US3 (P1)**: Can start after Phase 2; boundary tests depend on the shared configurable timer and snapshot semantics.

### Parallel Opportunities

- T004 and T005 can run in parallel with T003 only if the constants are agreed; otherwise T005 follows T004.
- T007, T008, and T009 can run in parallel because they target separate test concerns/files.
- T015 and T016 can run in parallel.
- T019 and T020 can run in parallel before the transition-order implementation is finalized.
- T023 and T024 can run in parallel after core implementation.

## Parallel Execution Examples

### User Story 1

```text
Task group A: T007 snapshot tests in tests/unit/test_ui_snapshot.py
Task group B: T008 transition tests in tests/unit/test_wave_transition.py
Task group C: T009 layout tests in tests/unit/test_ui_layout.py
Then: T011 snapshot implementation, T012 placement helper, T013 renderer integration
```

### User Story 2

```text
Task group A: T015 state/fishing regression tests in tests/unit/test_state.py
Task group B: T016 smoke fishing regression tests in tests/smoke/test_launch_contract.py
Then: T017 state preservation and T018 renderer integration
```

### User Story 3

```text
Task group A: T019 transition visibility/restart tests in tests/unit/test_state.py
Task group B: T020 fishing-boundary reward test in tests/unit/test_state.py
Then: T021 transition ordering and T022 restart cleanup
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup and Phase 2 Foundational.
2. Complete Phase 3 User Story 1.
3. Run the US1 tests and headless renderer check.
4. Stop for validation/demo: the configurable WormTimer is already visible and time-synchronized.

### Incremental Delivery

1. Add US1 for the WormTimer visual and configurable duration.
2. Add US2 regression protection for fishing during rest.
3. Add US3 boundary and restart behavior.
4. Finish cross-cutting validation and manual window-size checks.

## Notes

- Every task uses the required checklist format: checkbox, sequential ID, optional `[P]`, story label where applicable, and an exact file path.
- No external contracts are needed for this internal offline Pygame application.
- Existing Fishing, Stamina, document workflow, Game Over, and restart rules remain in scope and must not regress.
