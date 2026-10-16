---

description: "Implementation tasks for Tiled World Integration"
---

# Tasks: Tiled World Integration

**Input**: Design documents from `/specs/008-tiled-world-integration/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and `quickstart.md`

**Organization**: Tasks are grouped by user story. Tests are included because the specification requires deterministic geometry, map validation, gameplay regression, and launch validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the map-backed integration boundary without changing gameplay behavior yet.

- [ ] T001 Add the authored world asset paths and 1920×1088 map dimensions to `src/game/config.py`, preserving existing asset and gameplay constants.
- [ ] T002 [P] Add a focused map-loader module skeleton with typed loading/validation error types in `src/game/map_loader.py`.
- [ ] T003 [P] Add map-loader and geometry test module skeletons in `tests/unit/test_map_loader.py` and `tests/unit/test_geometry.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the pure data and geometry foundations required by every story.

**⚠️ CRITICAL**: User-story work depends on this phase.

- [ ] T004 Define map-backed world entities for collision shapes, spawnpoints, interaction zones, draw-order anchors, and render layers in `src/game/map_loader.py` and `src/game/world.py`, including the data-model constraints from `specs/008-tiled-world-integration/data-model.md`.
- [ ] T005 Implement exact polygon primitives and helpers for translated vertices, point-in-polygon checks, segment intersection, rectangle-edge intersection, and polygon-vs-player-rectangle overlap in `src/game/geometry.py`.
- [ ] T006 [P] Add unit tests for convex, concave, negative-local-coordinate, edge-touching, and non-overlapping polygon cases in `tests/unit/test_geometry.py`.
- [ ] T007 [P] Add unit tests for rectangle/polygon shape classification, including valid zero-size polygon objects and ignored empty non-polygon objects, in `tests/unit/test_map_loader.py`.
- [ ] T008 Implement TMJ JSON loading, Tiled layer lookup, local-to-world polygon translation, rectangle extraction, and typed validation errors in `src/game/map_loader.py`.
- [ ] T009 Implement map validation for required layers, 60×34/32×32 dimensions, 1920×1088 bounds, unique integer `servant_id` mappings, valid player spawn, and in-bounds interaction/collision geometry in `src/game/map_loader.py`.
- [ ] T010 Add foundational map validation tests against `assets/World/World.tmj` and malformed in-memory map fixtures in `tests/unit/test_map_loader.py`.
- [ ] T011 Extend the domain `World` representation and world factory in `src/game/world.py` to consume validated map data without creating duplicate hard-coded obstacles, spawns, or zones.

**Checkpoint**: The map can be loaded and validated headlessly; exact polygon overlap helpers pass their unit tests.

---

## Phase 3: User Story 1 - Navigate the Tiled World (Priority: P1) 🎯 MVP

**Goal**: Render the authored world and prevent movement through rectangle and polygon collision geometry.

**Independent Test**: Load the map, render it at 1920×1088 world coordinates, and move a 32×32 player against representative rectangles and all four polygons without tunneling or leaving the map.

### Tests for User Story 1

- [ ] T012 [P] [US1] Add collision tests for rectangle blocking, exact polygon contour blocking, edge touching, axis sliding, large displacement, and no-overlap invariants in `tests/unit/test_collision.py`.
- [ ] T013 [P] [US1] Add a map-backed world test asserting the loaded bounds are 1920×1088 and all four authored polygons plus all positive-size rectangles are active in `tests/unit/test_world.py`.

### Implementation for User Story 1

- [ ] T014 [US1] Implement bounded movement subdivision and axis-independent collision resolution against rectangles and exact polygons in `src/game/movement.py`, preserving the existing player movement contract.
- [ ] T015 [US1] Update `src/game/world.py` and `src/game/state.py` to construct the initial player from the validated `PlayerSpawn` and enforce map bounds from the loaded world.
- [ ] T016 [US1] Implement map tile/object rendering in authored layer order using `World.tmj`, `WorldTileSet.tsx`, and `MasterTileset.png` in `src/presentation/renderer.py`.
- [ ] T017 [US1] Remove the abstract grid/placeholder world drawing and hard-coded initial-world obstacle/location usage from `src/presentation/renderer.py`, `src/game/world.py`, and `src/game/config.py` while preserving unrelated UI rendering.
- [ ] T018 [US1] Integrate map loading during application initialization in `main.py` and surface clear validation errors when required map data is malformed.
- [ ] T019 [US1] Update the launch smoke contract in `tests/smoke/test_launch_contract.py` to verify valid map-backed startup, authored world bounds, and valid player spawn.

**Checkpoint**: The game is playable in the authored world; rectangle and polygon collision, map bounds, and camera behavior work with the existing movement tests.

---

## Phase 4: User Story 2 - Process Documents at Authored Locations (Priority: P1)

**Goal**: Use pickup and servant-ID-matched drop-off zones for document workflow.

**Independent Test**: Acquire a document, deliver it inside the matching drop-off zone, and verify mismatched zones reject delivery without mutating valid workflow progress.

### Tests for User Story 2

- [ ] T020 [P] [US2] Add map-loader tests for the two `DocumentPickupZones` and four `DocumentDropOffZones`, including `kind`, `interaction_radius`, and matching `servant_id` properties, in `tests/unit/test_map_loader.py`.
- [ ] T021 [P] [US2] Add workflow interaction tests for matching-zone success, mismatched-zone rejection, zone-boundary behavior, and unchanged invalid-handover state in `tests/unit/test_interaction.py` and `tests/unit/test_bureaucracy.py`.

### Implementation for User Story 2

- [ ] T022 [US2] Update the loaded world interaction data in `src/game/world.py` to expose pickup rectangles and drop-off rectangles keyed by integer `servant_id`.
- [ ] T023 [US2] Update document interaction dispatch in `src/game/state.py` and `src/game/bureaucracy.py` so delivery requires player intersection with the matching `DocumentDropOffZones` rectangle rather than servant-sprite proximity.
- [ ] T024 [US2] Preserve pickup behavior and authored properties while replacing the hard-coded document source location in `src/game/state.py` and `src/game/world.py`.
- [ ] T025 [US2] Add clear accepted/rejected interaction feedback for matching and mismatched drop-off zones in `src/game/state.py` and `src/presentation/renderer.py` without moving workflow rules into rendering.
- [ ] T026 [US2] Add a runtime reachability validation for every required drop-off rectangle against loaded solid geometry in `src/game/map_loader.py` or `src/game/world.py`.

**Checkpoint**: Document acquisition and delivery use authored zones, servant IDs are unambiguous, and invalid deliveries do not corrupt progression.

---

## Phase 5: User Story 3 - Spawn Actors and Preserve Readable Layering (Priority: P2)

**Goal**: Spawn the player and civil servants from authored points and apply dynamic actor draw ordering.

**Independent Test**: Start a new game, verify the player and each active servant use matching authored points, walk through a servant without collision, and verify actor ordering by foot position.

### Tests for User Story 3

- [ ] T027 [P] [US3] Add tests for unique `servant_id` spawn mappings, missing/duplicate ID errors, valid `PlayerSpawn`, and non-solid servant behavior in `tests/unit/test_world.py`.
- [ ] T028 [P] [US3] Add renderer tests for `NPCDrawOrder`/`PlayerDrawOrder` anchors and dynamic foot-position sorting in `tests/unit/test_camera.py` or a new `tests/unit/test_render_order.py`.

### Implementation for User Story 3

- [ ] T029 [US3] Replace hard-coded civil-servant positions with `CivilServantSpawnPoints` lookup by `servant_id` in `src/game/world.py` and `src/game/state.py`.
- [ ] T030 [US3] Mark civil servants as non-solid in the runtime world model and ensure they are never appended to collision shapes in `src/game/world.py` and `src/game/map_loader.py`.
- [ ] T031 [US3] Load `NPCDrawOrder` and `PlayerDrawOrder` as non-visible ordering anchors and dynamically sort runtime actors by foot position in `src/presentation/renderer.py`.
- [ ] T032 [US3] Render foreground layers around the sorted actors according to authored layer placement in `src/presentation/renderer.py`, preserving readable masking without changing gameplay collision.

**Checkpoint**: Player and NPC placement is map-driven, NPCs do not block movement, and actor layering follows the authored anchors plus foot-position sorting.

---

## Phase 6: User Story 4 - Use the Fishing Zone as a Gameplay Trigger (Priority: P3)

**Goal**: Preserve fishing and stamina recovery using the authored `FishingZone`.

**Independent Test**: Fishing is available inside the loaded fishing rectangle and unavailable outside it; successful fishing preserves existing stamina limits.

### Tests for User Story 4

- [ ] T033 [P] [US4] Add map-backed fishing-zone tests for `kind=fishing_zone`, `stamina_regeneration=true`, inside/outside intersection, and non-solid behavior in `tests/unit/test_world.py` and `tests/unit/test_fishing.py`.

### Implementation for User Story 4

- [ ] T034 [US4] Replace the hard-coded fishing pond with the loaded `FishingZone` in `src/game/world.py` and `src/game/state.py`.
- [ ] T035 [US4] Preserve existing fishing interaction, stamina recovery, and maximum clamping while sourcing zone membership from the loaded rectangle in `src/game/fishing.py` and `src/game/state.py`.

**Checkpoint**: Fishing remains playable and map-driven without changing its existing timing or stamina rules.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete regression validation and documentation after all stories are integrated.

- [ ] T036 [P] Add focused error-message assertions for missing layers, invalid bounds, invalid spawn, malformed polygons, and servant-ID mismatches in `tests/unit/test_map_loader.py`.
- [ ] T037 [P] Add a regression test ensuring no duplicate hard-coded world locations are used after map loading in `tests/unit/test_world.py`.
- [ ] T038 Run the complete automated suite and fix regressions across `tests/`.
- [ ] T039 Run the manual scenarios from `specs/008-tiled-world-integration/quickstart.md` and record map rendering, collision, interaction, spawn, draw-order, fishing, and launch results in the feature handoff.
- [ ] T040 Update `README.md` with the map-backed launch/asset requirement and the feature validation command.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2 and is the MVP foundation for runtime map integration.
- **Phase 4 US2**: Depends on Phase 2 and the loaded world from US1 for runtime interaction integration.
- **Phase 5 US3**: Depends on Phase 2 and the loaded world from US1; servant workflow integration uses US2's ID mapping.
- **Phase 6 US4**: Depends on Phase 2 and the loaded world from US1; existing fishing rules remain reusable.
- **Phase 7 Polish**: Depends on all selected stories.

### User Story Dependencies

- **US1 (P1)**: Foundational dependency only; MVP.
- **US2 (P1)**: Requires map loading from US1 for runtime zones, but its workflow tests can begin after foundational data structures.
- **US3 (P2)**: Requires map loading from US1; uses servant-ID mapping established with US2.
- **US4 (P3)**: Requires map loading from US1; otherwise independent of document workflow.

### Parallel Opportunities

- T002, T003 can run in parallel during setup.
- T006 and T007 can run in parallel after geometry/map interfaces are defined.
- T012 and T013 can run in parallel during US1.
- T020 and T021 can run in parallel during US2.
- T027 and T028 can run in parallel during US3.
- T033 can run in parallel with US2/US3 after map loading is stable.
- T036 and T037 can run in parallel during polish.

## Parallel Example: User Story 1

```text
Task T012: collision behavior tests in tests/unit/test_collision.py
Task T013: map-backed world invariants in tests/unit/test_world.py
```

## Parallel Example: User Story 2

```text
Task T020: authored interaction-zone parsing tests in tests/unit/test_map_loader.py
Task T021: workflow handover tests in tests/unit/test_interaction.py and tests/unit/test_bureaucracy.py
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1: map loading, rendering, exact polygon/rectangle collision, bounds, and player spawn.
3. Run the focused US1 tests and full regression suite.
4. Stop for a playable map-backed movement demo before adding workflow integrations.

### Incremental Delivery

1. Add US2 for map-driven document pickup/drop-off.
2. Add US3 for servant spawns and actor layering.
3. Add US4 for the map-driven fishing zone.
4. Complete polish and manual quickstart validation.

### MVP Scope

The MVP is **User Story 1 only** after Phases 1–2: the authored map renders, the player spawns from Tiled, and rectangle/polygon collisions work without breaking existing movement and camera behavior.

## Notes

- Every task includes an exact repository path.
- `[P]` marks tasks that can proceed in parallel without modifying the same incomplete dependency.
- Polygon objects with zero width/height are valid when a `polygon` field exists; only empty non-polygon collision objects are ignored.
