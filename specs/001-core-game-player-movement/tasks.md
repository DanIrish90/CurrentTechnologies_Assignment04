---

description: "Actionable implementation tasks for the core game window and player movement feature"
---

# Tasks: Core Game Window and Player Movement

**Input**: Design documents from `/specs/001-core-game-player-movement/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Included because the feature specification requires automated gameplay checks and the project constitution requires pytest for deterministic game rules.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated as an independent vertical slice.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the minimal Python project, dependencies, and test entry points.

- [X] T001 Create `pyproject.toml` with Python 3.12+ metadata, Pygame-ce runtime dependency, pytest test dependency, and pytest discovery configuration.
- [X] T002 [P] Create package markers in `src/game/__init__.py`, `src/presentation/__init__.py`, `tests/__init__.py`, `tests/unit/__init__.py`, and `tests/smoke/__init__.py`.
- [X] T003 [P] Create the planned source and test directories at `src/game/`, `src/presentation/`, `tests/unit/`, and `tests/smoke/` without adding unrelated framework structure.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared configuration and deterministic test conventions required by every user story.

**⚠️ CRITICAL**: Complete this phase before starting user-story implementation.

- [X] T004 Create `src/game/config.py` with named constants for window size, viewport size, world size, player size, movement speed, target frame rate, and placeholder UI colors; keep balancing and presentation values centralized.
- [X] T005 [P] Create `tests/conftest.py` with reusable factories for valid player, world, viewport, and input-state fixtures that do not initialize a Pygame display.
- [X] T006 [P] Document local dependency installation and the supported launch/test commands in `README.md`, including `python -m pytest` and `python main.py`.

**Checkpoint**: The project has a minimal dependency setup, importable package layout, deterministic test fixtures, and documented commands.

---

## Phase 3: User Story 1 - Start and Control the Player (Priority: P1) 🎯 MVP

**Goal**: Launch a desktop window and move a visible player responsively in four directions and diagonally.

**Independent Test**: Run the unit tests for input and frame-rate-independent movement, launch `python main.py`, move in each cardinal direction and diagonally, release input, and confirm the player stops.

### Tests for User Story 1

- [X] T007 [P] [US1] Add `tests/unit/test_geometry.py` covering positive dimensions, rectangle translation, center calculation, containment, and exclusive-edge overlap rules from `data-model.md`.
- [X] T008 [P] [US1] Add `tests/unit/test_input_state.py` covering cardinal input mapping, compatible diagonal input, opposing-input cancellation, unsupported-key ignoring, and clean quit-request mapping.
- [X] T009 [P] [US1] Add `tests/unit/test_movement.py` covering zero-input stopping, cardinal movement, normalized diagonal speed, elapsed-time scaling, and deterministic behavior for opposing input.
- [X] T010 [P] [US1] Add `tests/smoke/test_launch_contract.py` covering valid initial configuration, player spawn inside the world, and the application entry point's construction contract without opening an interactive window.

### Implementation for User Story 1

- [X] T011 [P] [US1] Implement typed `Vector2` and `Rect` value objects with positive-size validation, exclusive-edge overlap, containment, center, and translation operations in `src/game/geometry.py`.
- [X] T012 [P] [US1] Implement `InputState` and supported keyboard/event translation in `src/game/input_state.py`; opposing directions must cancel per axis and unsupported keys must not alter state.
- [X] T013 [US1] Implement frame-rate-independent player displacement in `src/game/movement.py` using elapsed seconds, configured speed, normalized nonzero input, and immediate zero-input stopping.
- [X] T014 [US1] Implement the initial `Player` and `World` data structures plus a valid fixed spawn configuration in `src/game/world.py`; enforce positive dimensions and a spawn position inside the world.
- [X] T015 [US1] Implement explicit runtime state creation and one-update orchestration in `src/game/state.py`, keeping authoritative player state independent of Pygame rendering.
- [X] T016 [US1] Implement the Pygame-ce window lifecycle and event loop in `src/presentation/window.py`, including elapsed-time clock updates, clean close handling, and delegation to game state updates.
- [X] T017 [US1] Implement the initial player/world placeholder rendering path in `src/presentation/renderer.py` and expose the launchable application through `main.py`.

**Checkpoint**: User Story 1 is independently playable: the window launches, the player moves at consistent speed, diagonal movement is normalized, and releasing input stops the player.

---

## Phase 4: User Story 2 - Navigate Around Obstacles (Priority: P1)

**Goal**: Add visible solid obstacles and collision-aware movement that preserves free-axis movement and keeps the player inside the world.

**Independent Test**: Run collision and boundary unit tests, launch the game, move directly into every obstacle and world edge, and confirm no overlap/out-of-bounds state while movement along an open axis remains possible.

### Tests for User Story 2

- [X] T018 [P] [US2] Add `tests/unit/test_collision.py` covering obstacle blocking, axis-aligned sliding, large-displacement safety, edge-touching behavior, and no-overlap invariants after every movement update.
- [X] T019 [P] [US2] Add `tests/unit/test_world.py` covering obstacle containment, positive dimensions, unique obstacle identifiers, valid spawn placement, and rejection of invalid world definitions.
- [X] T020 [P] [US2] Extend `tests/smoke/test_launch_contract.py` to assert that the initial world contains at least one visible solid obstacle and that the player starts without overlap.

### Implementation for User Story 2

- [X] T021 [P] [US2] Add structured obstacle definitions and world validation to `src/game/world.py`; every obstacle must be fully contained by the world and the spawn must be outside every obstacle.
- [X] T022 [US2] Implement collision-aware movement in `src/game/movement.py` by resolving horizontal and vertical displacement independently, preventing obstacle overlap, preserving an unblocked axis, and safely handling large requested displacement.
- [X] T023 [US2] Integrate world-bound clamping and obstacle collision into `src/game/state.py` so every completed update preserves player-in-world and player-not-overlapping-obstacle invariants.
- [X] T024 [US2] Render solid obstacles and a visible world boundary in `src/presentation/renderer.py` with shapes and labels/position cues that remain understandable without color alone.

**Checkpoint**: User Stories 1 and 2 are both playable: the player moves, collides with obstacles, slides along free space, and cannot leave the world.

---

## Phase 5: User Story 3 - Understand the Current Game State (Priority: P2)

**Goal**: Keep the player readable through a bounded following camera and communicate context, controls, and initial player state through a basic UI.

**Independent Test**: Run camera tests, launch the game, travel beyond the viewport center, reach each world edge, and confirm camera clamping plus readable labels and indicators.

### Tests for User Story 3

- [X] T025 [P] [US3] Add `tests/unit/test_camera.py` covering player-centered camera positioning, world-edge clamping, smaller-world anchoring, and the invariant that the viewport never displays outside the world.
- [X] T026 [P] [US3] Add `tests/unit/test_ui_snapshot.py` covering nonempty title/context, player-state placeholder, documented control hint, and text/shape state information that is not color-only.
- [X] T027 [P] [US3] Extend `tests/smoke/test_launch_contract.py` with a display-independent check that the runtime can create a camera and UI snapshot from the initial game state.

### Implementation for User Story 3

- [X] T028 [P] [US3] Implement pure camera positioning and world-bound clamping in `src/game/camera.py`; anchor any axis where the world is smaller than the viewport to the world start.
- [X] T029 [US3] Add camera state updates and `UiSnapshot` creation to `src/game/state.py`, targeting the player's center and exposing title, context/state label, and control hint values.
- [X] T030 [US3] Update `src/presentation/renderer.py` to draw world content through the camera transform plus a readable UI panel containing game context, movement controls, and an initial player-state placeholder.
- [X] T031 [US3] Update `src/presentation/window.py` to handle supported focus/resize behavior without corrupting input or game state and to preserve clean close transitions.

**Checkpoint**: All three user stories are independently demonstrable: movement works, obstacles constrain navigation, and camera/UI feedback remains readable across the world.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete slice, preserve maintainability, and align documentation with the implemented behavior.

- [X] T032 [P] Add public-interface type hints and concise module docstrings across `src/game/` and `src/presentation/` without introducing new abstractions.
- [X] T033 [P] Add readable placeholder labels and non-color visual distinctions in `src/presentation/renderer.py` for player, obstacles, world boundary, controls, and player-state indicator.
- [X] T034 Run the full automated suite with `python -m pytest` and resolve any regressions in `tests/unit/` and `tests/smoke/`.
- [X] T035 Run every manual scenario in `specs/001-core-game-player-movement/quickstart.md` against `main.py` and record launch, movement, collision, camera, UI, focus, resize, and close results in the implementation handoff.
- [X] T036 Update `README.md` with the final supported movement keys, launch instructions, test command, and known first-slice scope boundaries.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; starts immediately.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user-story work.
- **Phase 3 User Story 1**: Depends on Phase 2; delivers the MVP.
- **Phase 4 User Story 2**: Depends on Phase 3's geometry, player, world, and update seams; it extends the MVP with collisions.
- **Phase 5 User Story 3**: Depends on the runtime state and world from Phases 3–4; it adds camera and UI presentation.
- **Phase 6 Polish**: Depends on all selected user stories being implemented.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on another user story.
- **US2 (P1)**: Uses US1's player/world update seam and extends it with obstacles and collision; it is independently testable after the US1 foundation exists.
- **US3 (P2)**: Uses the stable runtime state from US1/US2 for camera and UI; it does not change movement or collision rules.

### Dependency Graph

```text
Setup (T001-T003)
        |
Foundation (T004-T006)
        |
        +--> US1: launch + movement (T007-T017)
                 |
                 +--> US2: obstacles + collision (T018-T024)
                          |
                          +--> US3: camera + UI (T025-T031)
                                   |
                                   +--> Polish (T032-T036)
```

### Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001's dependency decision is known; T006 can be prepared in parallel with package creation.
- **Foundation**: T005 and T006 can run in parallel with T004.
- **US1 tests**: T007–T010 can run in parallel because they target separate test files and pure seams; implementation T011 and T012 can run in parallel before T013–T017 integrate them.
- **US2 tests**: T018–T020 can run in parallel; T021 and T024 can run in parallel once the world shape is agreed, while T022 precedes T023.
- **US3 tests**: T025–T027 can run in parallel; T028 and the UI test scaffolding can proceed independently before T029–T031 integrate them.
- **Polish**: T032 and T033 can run in parallel; T034–T036 follow implementation completion.

## Parallel Example: User Story 1

```text
Track A: T007 tests/unit/test_geometry.py -> T011 src/game/geometry.py
Track B: T008 tests/unit/test_input_state.py -> T012 src/game/input_state.py
Track C: T009 tests/unit/test_movement.py -> T013 src/game/movement.py
Track D: T010 tests/smoke/test_launch_contract.py -> T014 src/game/world.py
Integration: T015 state.py -> T016 window.py -> T017 renderer.py + main.py
```

## Parallel Example: User Story 2

```text
Track A: T018 tests/unit/test_collision.py -> T022 src/game/movement.py
Track B: T019 tests/unit/test_world.py -> T021 src/game/world.py
Track C: T020 smoke extension -> T023 src/game/state.py
Presentation: T024 src/presentation/renderer.py after world shape is available
```

## Parallel Example: User Story 3

```text
Track A: T025 tests/unit/test_camera.py -> T028 src/game/camera.py
Track B: T026 tests/unit/test_ui_snapshot.py -> T029 src/game/state.py
Track C: T027 smoke extension -> T031 src/presentation/window.py
Presentation: T030 src/presentation/renderer.py after T028 and T029 contracts are stable
```

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phases 1–2.
2. Implement US1 with its pure tests and launchable window.
3. Stop and validate cardinal movement, diagonal normalization, prompt stopping, and clean closure.
4. Demo the first playable movement slice before adding obstacles.

### Incremental Delivery

1. Add US2 after US1 remains launchable; validate obstacle and world-bound invariants.
2. Add US3 after US2 remains playable; validate camera edges and readable UI.
3. Run the complete quickstart and pytest suite.
4. Keep later bureaucracy, stamina, fishing, and progression systems outside this feature until separately specified.

### Completion Evidence

- All 36 implementation tasks are checked off.
- `python -m pytest` passes.
- `python main.py` launches the playable slice.
- The manual quickstart scenarios pass, including frame-rate behavior, collision, camera edges, UI readability, focus/resize stability, and clean close.
