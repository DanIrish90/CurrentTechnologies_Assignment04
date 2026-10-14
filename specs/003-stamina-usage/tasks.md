# Tasks: Stamina Usage and Recovery

**Input**: Design documents from `/specs/003-stamina-usage/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Organization**: Tasks are grouped by user story. All tasks use the existing modular Pygame application and pytest suite.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature's centralized balance values and preserve the existing dependency/runtime setup.

- [X] T001 Add `STAMINA_MAXIMUM`, `STAMINA_DRAIN_RATE`, `STAMINA_REGEN_RATE`, recovery-zone colors, and stamina UI dimensions to `src/game/config.py` without adding dependencies.
- [X] T002 [P] Add feature-level test fixtures/helpers for full stamina, carrying workflow, recovery-zone placement, and game-over setup in `tests/conftest.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the pure rules and shared world/input primitives required by every user story.

**⚠️ CRITICAL**: User-story work depends on this phase.

- [X] T003 Create immutable `StaminaState` and elapsed-time update functions in `src/game/stamina.py` with `current` clamped to `[0, maximum]`, `maximum=100.0`, `drain_rate=5.0`, and `regen_rate=10.0`.
- [X] T004 [P] Add unit tests for `src/game/stamina.py` in `tests/unit/test_stamina.py`, covering construction validation, fractional elapsed time, clamping, carrying precedence, and negative elapsed-time rejection.
- [X] T005 Add immutable `StaminaRegenZone` and optional zone field/containment validation to `src/game/world.py`; ensure the zone is contained by world bounds and has a unique id.
- [X] T006 [P] Add recovery-zone geometry and initial-world validity tests in `tests/unit/test_world.py`, including player overlap and world containment cases.
- [X] T007 Extend `InputState` and `input_from_events` in `src/game/input_state.py` with a one-frame mouse restart action and pointer position while preserving movement, interaction, focus-loss, and quit behavior.
- [X] T008 [P] Add mouse restart input tests in `tests/unit/test_input_state.py`, including click detection data and unchanged keyboard interaction behavior.

**Checkpoint**: Pure stamina rules, recovery-zone data, and restart input are independently testable.

---

## Phase 3: User Story 1 - Track stamina while carrying documents (Priority: P1) 🎯 MVP

**Goal**: Show full stamina at session start and drain exactly 5 points per elapsed second while the existing workflow carries a document.

**Independent Test**: Create a game state, collect the initial document, advance simulation by 2 seconds, and verify stamina changes from 100 to 90; verify empty-handed movement outside the zone does not drain it.

### Tests for User Story 1

- [X] T009 [P] [US1] Add initial-stamina and document-carrying drain tests to `tests/unit/test_state.py`, asserting 100 at session start and 90 after 2.0 elapsed seconds with a carried document.
- [X] T010 [P] [US1] Add frame-rate-independent drain tests to `tests/unit/test_stamina.py`, comparing equivalent elapsed-time updates split into different step sizes.

### Implementation for User Story 1

- [X] T011 [US1] Add authoritative `stamina` state to `GameState` and initialize it at maximum in `create_game_state` in `src/game/state.py`.
- [X] T012 [US1] Integrate carried-document detection from `workflow.carried_document` into `update_game_state` in `src/game/state.py`, applying the 5-per-second drain before returning the updated state.
- [X] T013 [US1] Extend `UiSnapshot` and `ui_snapshot` in `src/game/state.py` with current/max stamina text and a carrying/drain status that does not depend on color.
- [X] T014 [US1] Render the stamina bar, numeric value, and carrying status in `_draw_ui` in `src/presentation/renderer.py` using centralized configuration and readable labels.
- [X] T015 [US1] Add stamina UI snapshot assertions to `tests/unit/test_ui_snapshot.py`, covering full, carrying, and empty-handed status text.

**Checkpoint**: User Story 1 is playable and independently demonstrates stamina visibility plus document-carrying drain.

---

## Phase 4: User Story 2 - Recover stamina at a regeneration zone (Priority: P1)

**Goal**: Provide one clearly labeled world recovery zone that restores 10 points per second only while the player is inside and empty-handed.

**Independent Test**: Place the player inside the initial zone without a document, advance 2 seconds, and verify +20 capped at 100; verify outside-zone and carrying-in-zone cases do not regenerate.

### Tests for User Story 2

- [X] T016 [P] [US2] Add recovery, outside-zone, maximum-clamp, and carrying-precedence tests to `tests/unit/test_state.py` using deterministic elapsed times.
- [X] T017 [P] [US2] Add recovery-zone eligibility/status tests to `tests/unit/test_ui_snapshot.py`, covering entering the zone and losing recovery while carrying.

### Implementation for User Story 2

- [X] T018 [US2] Place exactly one `StaminaRegenZone` in `create_initial_world` in `src/game/world.py`, with a valid labeled rectangle that is distinct from obstacles and document sources.
- [X] T019 [US2] Integrate player-zone overlap and empty-handed eligibility into `update_game_state` in `src/game/state.py`, applying 10-per-second recovery only when no document is carried and giving drain precedence.
- [X] T020 [US2] Extend `UiSnapshot` status derivation in `src/game/state.py` with recovering, stable, and carrying-in-zone feedback.
- [X] T021 [US2] Render the recovery-zone rectangle and label in `src/presentation/renderer.py`, ensuring it is distinguishable without color alone.
- [X] T022 [US2] Add initial-world recovery-zone assertions to `tests/smoke/test_launch_contract.py` and preserve existing document-source/wave assertions.

**Checkpoint**: User Stories 1 and 2 work together: carrying drains, empty-handed zone presence recovers, and all precedence/clamp rules hold.

---

## Phase 5: User Story 3 - Understand and respond to game over (Priority: P1)

**Goal**: Enter a stable exhaustion game-over state at zero and let the player restart via a clickable “Restart” button.

**Independent Test**: Drain a carried-document run across zero, verify exhaustion feedback and frozen state, then click Restart and verify a fresh wave-one state with 100 stamina.

### Tests for User Story 3

- [X] T023 [P] [US3] Add zero-crossing, one-time transition, non-negative clamp, and post-game-over freeze tests to `tests/unit/test_state.py`.
- [X] T024 [P] [US3] Add Restart-button visibility/state-text assertions to `tests/unit/test_ui_snapshot.py`.
- [X] T025 [P] [US3] Add restart click event tests to `tests/unit/test_input_state.py`, including clicks outside the button bounds.

### Implementation for User Story 3

- [X] T026 [US3] Add explicit game-over state handling to `GameState` and `update_game_state` in `src/game/state.py`, freezing stamina, movement, and workflow mutations after exhaustion while preserving the quit flag separately.
- [X] T027 [US3] Add restart hitbox/action handling in `src/game/input_state.py` and route an accepted restart action through `create_game_state` in `src/game/state.py`.
- [X] T028 [US3] Extend `UiSnapshot` and `ui_snapshot` in `src/game/state.py` with clear `GAME OVER: EXHAUSTED` feedback and Restart-button bounds/state.
- [X] T029 [US3] Render the game-over overlay and clickable “Restart” button in `src/presentation/renderer.py`, including readable text and non-color-only exhaustion feedback.
- [X] T030 [US3] Process mouse events and one-frame restart actions in `src/presentation/window.py`, ensuring a successful restart replaces the active state and normal play resumes.

**Checkpoint**: All three user stories are playable, testable, and preserve the existing document workflow during active play.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the vertical slice, documentation, regressions, and launchability.

- [X] T031 [P] Add feature smoke assertions for stamina initialization, zone availability, and game-over/restart launch behavior in `tests/smoke/test_launch_contract.py`.
- [X] T032 [P] Update `README.md` with stamina rules, recovery-zone behavior, exhaustion feedback, and the clickable Restart control.
- [X] T033 Run the complete pytest suite and compilation checks from `specs/003-stamina-usage/quickstart.md`, fixing regressions in `src/` and `tests/` as needed.
- [X] T034 Run the headless Pygame quit/event smoke check against `main.py` and manually verify `src/presentation/renderer.py` output: readable stamina UI, recovery-zone labeling, document workflow, exhaustion overlay, and Restart button on a desktop display.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on T003, T004, and the shared state/input/world foundation.
- **User Story 2 (Phase 4)**: Depends on User Story 1's stamina integration, especially T011–T014.
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 so game over freezes the complete active simulation.
- **Polish (Phase 6)**: Depends on all desired user stories.

### User Story Dependencies

```text
Foundational
    |
    v
US1: visible stamina + document drain
    |
    v
US2: recovery zone + regeneration
    |
    v
US3: exhaustion + Restart
    |
    v
Polish and validation
```

### Parallel Opportunities

- T002, T004, T006, and T008 can run in parallel after their referenced files are understood.
- Within US1, T009, T010, and T015 can be prepared in parallel before the corresponding implementation tasks.
- Within US2, T016 and T017 can be prepared in parallel; rendering and smoke assertions can proceed separately once the world/state interfaces are agreed.
- Within US3, T023–T025 can be prepared in parallel before the state, input, and presentation integration tasks.
- T031 and T032 can run in parallel after the feature behavior is complete.

## Parallel Example: User Story 1

```text
T009: State tests for initial stamina and carrying drain in tests/unit/test_state.py
T010: Frame-rate independence tests in tests/unit/test_stamina.py
T015: UI snapshot tests in tests/unit/test_ui_snapshot.py
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Implement User Story 1: visible `100/100` stamina and 5/s document drain.
3. Run the independent US1 tests and existing regression suite.
4. Stop for a playable MVP checkpoint before adding recovery and game over.

### Incremental Delivery

1. Add User Story 2 and validate zone recovery, clamping, and carrying precedence.
2. Add User Story 3 and validate exhaustion freeze plus clickable Restart.
3. Run the complete quickstart and manual display validation.

## Notes

- Every task follows the required `- [ ] T### [P?] [US?] description with file path` checklist format.
- `[P]` marks only tasks that can work on different files without waiting on incomplete dependencies.
- No `contracts/` directory is required because this is an internal offline desktop game without external interfaces.
