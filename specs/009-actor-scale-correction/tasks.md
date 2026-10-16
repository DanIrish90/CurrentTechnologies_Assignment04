---

description: "Task list for correcting player and civil-servant actor scale"
---

# Tasks: Actor Scale Correction

**Input**: Design documents from `/specs/009-actor-scale-correction/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and `quickstart.md`

**Tests**: Required by FR-011. New and updated tests must cover scaled frames, foot anchors, logical collision dimensions, servant non-solid behavior, and gameplay regressions.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently after the shared scale foundation is complete.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish centralized actor-scale constants and preserve the existing asset-loading boundary.

- [X] T001 Add centralized actor render scale, player body size `8x10`, servant presentation size `12x15`, and expected scaled frame dimensions `21x32` to `src/game/config.py`.
- [X] T002 [P] Add a focused actor-scale test fixture/helper for initializing headless Pygame surfaces in `tests/conftest.py` or the relevant animation test modules.
- [X] T003 [P] Document the actor scale profile and asset assumptions in `specs/009-actor-scale-correction/data-model.md` and `specs/009-actor-scale-correction/quickstart.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared scaling and anchoring behavior before story-specific integration.

**⚠️ CRITICAL**: User-story implementation depends on these deterministic scale and asset rules.

- [X] T004 Implement one nearest-neighbor frame-scaling helper that converts validated `84x128` source frames to `21x32` without smoothing in `src/presentation/character_animation.py` or a shared presentation helper module.
- [X] T005 [P] Add equivalent scaled-frame loading for bureaucrat animations while preserving the existing `2x2` sheet validation in `src/presentation/bureaucrat_animation.py`.
- [X] T006 Add tests proving character and bureaucrat output frames are exactly `21x32` and retain pixel-sharp, unblended source colors in `tests/unit/test_character_animation.py` and `tests/unit/test_bureaucrat_animation.py`.
- [X] T007 Define and test a shared bottom-center foot-anchor contract for scaled player and servant frames in `src/presentation/character_animation.py`, `src/presentation/bureaucrat_animation.py`, and `tests/unit/test_character_animation.py`.
- [X] T008 Update asset validation errors to identify the actor type, expected source dimensions, and received dimensions when a sheet is malformed in `src/presentation/character_animation.py` and `src/presentation/bureaucrat_animation.py`.

**Checkpoint**: Both animation systems return cached `21x32` pixel-sharp frames and preserve their bottom-center world anchors.

---

## Phase 3: User Story 1 - See Actors at World Scale (Priority: P1) 🎯 MVP

**Goal**: Render the player and civil servants at quarter-scale relative to the original source frames against the unchanged 32x32 world.

**Independent Test**: Run the focused animation and renderer tests, then launch headlessly and verify actor surfaces are `21x32`, pixel-sharp, and foot-anchored.

### Tests for User Story 1

- [X] T009 [P] [US1] Add player rendering assertions for `21x32` frames, bottom-center anchoring, and unchanged world position across direction changes in `tests/unit/test_character_animation.py`.
- [X] T010 [P] [US1] Add civil-servant rendering assertions for `21x32` frames, `12x15` presentation target anchoring, and unchanged world position across animation states in `tests/unit/test_bureaucrat_animation.py`.
- [X] T011 [P] [US1] Add a headless renderer regression asserting actor scale is not altered by the 32x32 map tile rendering path in `tests/smoke/test_launch_contract.py` or `tests/unit/test_render_order.py`.

### Implementation for User Story 1

- [X] T012 [US1] Scale and cache player animation frames before rendering while retaining direction and animation-state behavior in `src/presentation/character_animation.py`.
- [X] T013 [US1] Scale and cache civil-servant animation frames before rendering while retaining idle/permit animation-state behavior in `src/presentation/bureaucrat_animation.py`.
- [X] T014 [US1] Render the player using the scaled frame and its bottom-center anchor without changing player world coordinates in `src/presentation/renderer.py`.
- [X] T015 [US1] Render civil servants using the scaled frame and centralized `12x15` presentation target while preserving authored spawn coordinates in `src/presentation/renderer.py`.

**Checkpoint**: The player and servants visibly fit the authored world scale, remain pixel-sharp, and do not shift their feet when animated.

---

## Phase 4: User Story 2 - Use Correct Actor Collision Size (Priority: P1)

**Goal**: Use the exact `8x10` player body for movement while keeping servants non-solid.

**Independent Test**: Move an `8x10` player through open space and against rectangle/polygon collision; verify stopping, sliding, no tunneling, and passage through servants.

### Tests for User Story 2

- [X] T016 [P] [US2] Update player/world tests to assert new players are exactly `8x10` and remain valid at the authored `PlayerSpawn` in `tests/unit/test_world.py`.
- [X] T017 [P] [US2] Extend rectangle and polygon movement tests for the `8x10` body, including boundary stopping, axis sliding, large displacement, and edge-touching behavior in `tests/unit/test_collision.py`.
- [X] T018 [P] [US2] Add a non-solid servant traversal regression asserting servant positions are never included in collision geometry in `tests/unit/test_world.py` and `tests/unit/test_collision.py`.

### Implementation for User Story 2

- [X] T019 [US2] Change initial player construction to use centralized `PLAYER_WIDTH=8` and `PLAYER_HEIGHT=10` while preserving map spawn coordinates in `src/game/world.py` and `src/game/config.py`.
- [X] T020 [US2] Verify movement subdivision and rectangle/polygon collision continue to operate from the reduced body without introducing actor-specific collision exceptions in `src/game/movement.py` and `src/game/world.py`.
- [X] T021 [US2] Keep civil servants outside authoritative collision shapes and use only the `12x15` visual target for rendering in `src/game/world.py`, `src/game/map_loader.py`, and `src/presentation/renderer.py`.

**Checkpoint**: The player uses the `8x10` body, solid geometry remains authoritative, and servants remain pass-through actors.

---

## Phase 5: User Story 3 - Preserve Gameplay Anchors (Priority: P2)

**Goal**: Prove that rescaling does not move map-driven interactions, camera limits, or draw ordering.

**Independent Test**: Start a new session, use document pickup/drop-off and fishing, move near world bounds, and compare actor ordering by world foot position.

### Tests for User Story 3

- [X] T022 [P] [US3] Add regression assertions that player and servant spawn coordinates, world bounds, and camera clamping are unchanged after actor resizing in `tests/unit/test_world.py` and `tests/unit/test_camera.py`.
- [X] T023 [P] [US3] Add document pickup, matching drop-off, mismatched drop-off, and fishing-zone regression coverage using the resized player body in `tests/unit/test_interaction.py`, `tests/unit/test_state.py`, and `tests/unit/test_fishing.py`.
- [X] T024 [P] [US3] Add draw-order assertions proving actor sorting still uses world foot Y positions after scaled rendering in `tests/unit/test_render_order.py`.

### Implementation for User Story 3

- [X] T025 [US3] Preserve actor world positions, camera bounds, and map-derived interaction coordinates while routing only visual/body dimensions through the actor scale profile in `src/game/state.py`, `src/game/camera.py`, and `src/game/world.py`.
- [X] T026 [US3] Ensure document and fishing interaction checks continue to use the resized player bounds without changing authored zone geometry or interaction timing in `src/game/state.py` and `src/game/bureaucracy.py`.
- [X] T027 [US3] Keep dynamic NPC/player foot-position sorting and foreground masking unchanged while consuming the scaled presentation rectangles in `src/presentation/renderer.py`.

**Checkpoint**: All existing map-driven interactions, camera behavior, and readable actor layering remain functional with the corrected scale.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Run the complete validation guide, update documentation, and remove scale regressions.

- [X] T028 [P] Add or update README guidance describing the actor scale profile and pixel-sharp asset behavior in `README.md`.
- [X] T029 [P] Add explicit assertions that map dimensions, tile dimensions, spawn coordinates, and interaction-zone coordinates are unchanged in `tests/unit/test_world.py`.
- [X] T030 Run the focused commands from `specs/009-actor-scale-correction/quickstart.md` with `SDL_VIDEODRIVER=dummy` and resolve any actor-scale regressions in the affected source/tests.
- [X] T031 Run the complete test suite and the documented launch/manual validation from `specs/009-actor-scale-correction/quickstart.md`; record results in the implementation handoff.
- [X] T032 Run `git diff --check` and verify all task requirements, checklist criteria, and generated artifacts are complete in `specs/009-actor-scale-correction/tasks.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; establishes centralized values and documentation.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories because both stories need the same scaled-frame and anchor behavior.
- **User Story 1 (Phase 3)**: Depends on Phase 2; delivers the visual-scale MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 1 for dimensions and can proceed alongside US1 after Phase 2, but its renderer-facing validation benefits from US1's scaled frames.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and integrates the resized body/presentation with existing map-driven gameplay.
- **Polish (Phase 6)**: Depends on all selected stories.

### User Story Dependencies

- **US1 (P1)**: Foundational dependency only; recommended MVP.
- **US2 (P1)**: Foundational dependency only; independent collision slice, with shared configuration from Setup.
- **US3 (P2)**: Depends on the corrected actor body/presentation from US1 and US2 to validate gameplay regressions.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001's intended values are agreed.
- T005, T006, and T008 can run in parallel after the shared scaling contract in T004 is settled.
- T009, T010, and T011 can run in parallel within US1.
- T016, T017, and T018 can run in parallel within US2.
- T022, T023, and T024 can run in parallel within US3.
- T028 and T029 can run in parallel during polish.

## Parallel Example: User Story 1

```text
Task: T009 player scaled-frame and foot-anchor tests in tests/unit/test_character_animation.py
Task: T010 servant scaled-frame and target-anchor tests in tests/unit/test_bureaucrat_animation.py
Task: T011 headless actor-scale renderer regression in tests/smoke/test_launch_contract.py
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup and Phase 2 Foundational.
2. Complete Phase 3 User Story 1.
3. Run the focused animation and renderer tests from `quickstart.md`.
4. Stop and visually validate that actors fit the 32x32 map without changing world coordinates.

### Incremental Delivery

1. Add US1 for corrected visual scale and pixel-sharp foot anchoring.
2. Add US2 for the exact `8x10` player collision body and servant pass-through behavior.
3. Add US3 for full map-driven gameplay regression coverage.
4. Complete polish, full-suite validation, and manual launch checks.

## Notes

- Every task has a checkbox, sequential ID, required story label for story tasks, and at least one concrete repository path.
- No external contracts are generated because this is an internal desktop-game change.
- Do not change Tiled map coordinates to compensate for actor scale; the map remains authoritative.
