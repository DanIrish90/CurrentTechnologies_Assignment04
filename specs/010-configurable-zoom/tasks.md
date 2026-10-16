---

description: "Task list for configurable start zoom"
---

# Tasks: Configurable Start Zoom

**Input**: Design documents from `/specs/010-configurable-zoom/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Included because the project constitution requires pytest coverage for critical behavior and the plan explicitly calls for pure viewport and headless rendering regression tests.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated as an incremental slice.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature's test and documentation touchpoints without changing gameplay behavior.

- [X] T001 [P] Add zoom feature test module placeholders and shared test constants in `tests/unit/test_zoom.py`
- [X] T002 [P] Add the zoom validation scenarios and representative values to `tests/smoke/test_launch_contract.py`
- [X] T003 [P] Record the configurable zoom setting, supported range, and startup-only behavior in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide validated zoom configuration and deterministic logical viewport calculations before presentation integration.

**⚠️ CRITICAL**: User story implementation depends on these rules and helpers.

- [X] T004 [P] Add centralized `ZOOM_MULTIPLIER`, `ZOOM_MINIMUM`, and `ZOOM_MAXIMUM` values to `src/game/config.py`, using default `2.0` and inclusive bounds `0.5`–`4.0` from `data-model.md`
- [X] T005 [P] Implement finite, positive, range-checked zoom validation in `src/game/zoom.py`, with controlled handling for non-numeric, non-finite, and out-of-range values
- [X] T006 [P] Implement logical viewport derivation from display dimensions and validated zoom in `src/game/zoom.py`, guaranteeing positive dimensions for valid supported values
- [X] T007 [P] Add unit coverage for zoom validation, boundary values, fractional values, invalid values, and logical viewport dimensions in `tests/unit/test_zoom.py`
- [X] T008 Run the focused zoom unit tests and confirm the foundational helpers do not require Pygame display initialization in `tests/unit/test_zoom.py`

**Checkpoint**: Zoom configuration and viewport arithmetic are deterministic, documented, and independently testable.

---

## Phase 3: User Story 1 - Startansicht fein abstimmen (Priority: P1) 🎯 MVP

**Goal**: Make one centralized decimal multiplier control the initial visible world area and scale the complete game frame.

**Independent Test**: Run the game with `1.0`, `1.25`, `1.5`, and `2.0`; confirm that each value changes only the visible presentation, keeps the player visible at startup, and requires no map or gameplay-data edits.

### Tests for User Story 1

- [X] T009 [P] [US1] Add a headless render regression for `1.0`, `1.5`, and `2.0` in `tests/smoke/test_launch_contract.py`, asserting successful frame creation and complete display-surface coverage
- [X] T010 [P] [US1] Add camera viewport assertions showing that the zoom-adjusted logical viewport is passed to the initial game state in `tests/unit/test_state.py`

### Implementation for User Story 1

- [X] T011 [US1] Derive the initial logical viewport from the current display size and validated configuration in `src/presentation/window.py`
- [X] T012 [US1] Create and maintain a logical render surface sized to the zoom-adjusted viewport while preserving the actual display surface in `src/presentation/window.py`
- [X] T013 [US1] Render world, actors, HUD, fishing overlay, rest countdown, and game-over presentation to the logical surface and scale the complete frame to the display in `src/presentation/window.py` and `src/presentation/renderer.py`
- [X] T014 [US1] Ensure the initial `GameState` camera receives the logical world viewport while the authoritative player/world coordinates remain unchanged in `src/game/state.py`
- [X] T015 [US1] Preserve pixel-sharp non-smoothed final scaling and document the presentation choice in `src/presentation/window.py`

**Checkpoint**: User Story 1 is playable independently; changing one config value changes the startup zoom and the whole frame remains aligned.

---

## Phase 4: User Story 2 - Spielbarkeit bei jeder gültigen Zoomstufe erhalten (Priority: P1)

**Goal**: Prove that zoom affects presentation only and leaves movement, camera clamping, collisions, interactions, stamina, fishing, waves, game-over, and restart unchanged.

**Independent Test**: Execute the existing gameplay smoke and unit scenarios with representative zoom-adjusted viewports and confirm identical world-coordinate outcomes.

### Tests for User Story 2

- [X] T016 [P] [US2] Add camera clamp tests for zoom-derived viewports, including a viewport smaller than the world and a viewport larger than the world, in `tests/unit/test_camera.py`
- [X] T017 [P] [US2] Add state regression tests proving movement, interaction ranges, wave transitions, stamina, fishing, and restart use unchanged world coordinates at zoom-derived viewports in `tests/unit/test_state.py`
- [X] T018 [P] [US2] Add a renderer regression that confirms actor anchors and draw order are unchanged when the logical viewport changes in `tests/unit/test_render_order.py`

### Implementation for User Story 2

- [X] T019 [US2] Route the zoom-derived logical viewport through existing update and restart paths without changing movement or interaction calculations in `src/presentation/window.py` and `src/game/state.py`
- [X] T020 [US2] Verify and adjust camera clamping only where needed so every zoom-derived camera bounds rectangle remains within the world in `src/game/camera.py`
- [X] T021 [US2] Keep renderer world-to-logical-screen conversion and actor foot anchors consistent for all zoom values without changing actor dimensions or map coordinates in `src/presentation/renderer.py`

**Checkpoint**: User Stories 1 and 2 both work; the zoomed game is mechanically equivalent to the unzoomed game.

---

## Phase 5: User Story 3 - Robuste und lesbare Darstellung erhalten (Priority: P2)

**Goal**: Handle fractional values, window resizing, invalid configuration, and all overlays without empty regions, crashes, or misalignment.

**Independent Test**: Start with fractional, boundary, and invalid values; resize the window during active play and overlays; confirm controlled behavior, full-frame rendering, and readable aligned presentation.

### Tests for User Story 3

- [X] T022 [P] [US3] Add fractional and boundary viewport tests for `0.5`, `1.25`, `1.75`, and `4.0` in `tests/unit/test_zoom.py`
- [X] T023 [P] [US3] Add invalid-value startup tests for zero, negative, non-numeric, non-finite, and out-of-range values in `tests/smoke/test_launch_contract.py`
- [X] T024 [P] [US3] Add headless resize/render tests covering normal play, fishing, rest countdown, and game-over overlays in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 3

- [X] T025 [US3] Recalculate the logical viewport and recreate or reuse the render surface safely whenever the resizable display dimensions change in `src/presentation/window.py`
- [X] T026 [US3] Add clear startup error or documented safe fallback handling for invalid zoom configuration before the main loop begins in `src/presentation/window.py`
- [X] T027 [US3] Ensure UI and temporary overlays use the logical surface dimensions consistently and remain aligned after final frame scaling in `src/presentation/renderer.py`
- [X] T028 [US3] Update runtime and developer-facing documentation with valid values, invalid-value behavior, and resize expectations in `README.md` and `specs/010-configurable-zoom/quickstart.md`

**Checkpoint**: All three user stories are independently demonstrable across supported zoom values and window sizes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature against project quality gates and the quickstart guide.

- [X] T029 [P] Run `git diff --check` and resolve whitespace or formatting issues in all changed feature files
- [X] T030 [P] Run the complete automated suite with `python -m pytest` and resolve zoom-related regressions in `tests/`
- [X] T031 Run the automated/headless validation scenarios from `specs/010-configurable-zoom/quickstart.md`, covering valid values, invalid values, resize, gameplay interactions, overlays, and restart
- [X] T032 Confirm the zoom startup path and render integration compile and pass the launch-contract tests at the configured default, matching `specs/010-configurable-zoom/spec.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No implementation dependencies; documentation and test touchpoints can be prepared in parallel.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user story work.
- **Phase 3 (US1)**: Depends on Phase 2 and delivers the MVP startup zoom.
- **Phase 4 (US2)**: Depends on Phase 2 and should follow US1 integration so gameplay regressions are tested against the real presentation path.
- **Phase 5 (US3)**: Depends on US1 and US2 because it hardens the integrated render loop and all overlays.
- **Phase 6 (Polish)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Depends only on the foundational zoom helpers; independently delivers configurable startup presentation.
- **US2 (P1)**: Depends on the foundational zoom helpers and shares the US1 presentation boundary, but its gameplay tests can run independently against state and camera modules.
- **US3 (P2)**: Depends on the integrated US1/US2 render path to validate resizing, overlays, and invalid startup behavior end to end.

### Within Each User Story

- Write the story tests before implementation and verify they fail for the missing behavior where practical.
- Complete foundational helpers before presentation integration.
- Complete core frame integration before resize and overlay hardening.
- Run the story's independent test criteria at each checkpoint.

## Parallel Opportunities

- Phase 1: T001, T002, and T003 can run in parallel.
- Phase 2: T004, T005, and T006 can run in parallel; T007 depends on T005 and T006; T008 follows T007.
- US1: T009 and T010 can run in parallel; T011 and T012 touch the window integration and should be sequenced before T013.
- US2: T016, T017, and T018 can run in parallel; T019 and T020 can proceed in parallel after tests are defined, while T021 follows the render-path decision.
- US3: T022, T023, and T024 can run in parallel; T025 and T026 can run in parallel, followed by T027 and T028.
- Polish: T029 and T030 can run in parallel after implementation; T031 and T032 require the final integrated state.

## Parallel Example: User Story 1

```text
Task T009: Headless render regression in tests/smoke/test_launch_contract.py
Task T010: Initial logical viewport assertions in tests/unit/test_state.py

After both tests are defined:
Task T011: Derive logical viewport in src/presentation/window.py
Task T012: Manage logical render surface in src/presentation/window.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 zoom validation and logical viewport helpers.
3. Complete Phase 3 startup frame integration.
4. Stop and validate values `1.0`, `1.25`, `1.5`, and `2.0` independently.
5. Demo the configurable startup zoom before adding broader regression hardening.

### Incremental Delivery

1. Add US1 to deliver the configurable startup view.
2. Add US2 to prove all gameplay remains unchanged.
3. Add US3 to harden fractional values, invalid values, resizing, and overlays.
4. Run the final polish and manual validation phase.

### Task Format Validation

All implementation tasks use `- [ ]`, sequential `T###` IDs, `[P]` only for parallelizable work, `[US#]` labels in user-story phases, and explicit repository-relative file paths.
