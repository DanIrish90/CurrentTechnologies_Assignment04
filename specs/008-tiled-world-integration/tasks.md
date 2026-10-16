---

description: "Actionable task list for Tiled World Integration"
---

# Tasks: Tiled World Integration

**Input**: Design documents from `/specs/008-tiled-world-integration/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md)

**Organization**: Tasks are grouped by user story. All tasks are intentionally unchecked so the implementation pass can execute the regenerated plan from a clean task state.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the authored map assets and the existing Python/Pygame test entry points before changing runtime behavior.

- [X] T001 Verify `assets/World/World.tmj`, `assets/World/WorldTileSet.tsx`, and `assets/World/MasterTileset.png` are present and referenced consistently by the runtime configuration in `src/game/config.py`.
- [X] T002 Verify the existing pytest and Pygame-ce commands documented in `pyproject.toml` and `specs/008-tiled-world-integration/quickstart.md` run from the repository root.
- [X] T003 Capture the pre-implementation regression baseline with `tests/smoke/test_launch_contract.py` and the existing unit-test suite before changing map integration.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared data and geometry boundaries that all user stories use.

**Checkpoint**: The foundational types and fixtures are available without changing gameplay rules.

- [X] T004 Add or verify the map-backed world path and authored 1920×1088 world constants in `src/game/config.py` without duplicating gameplay locations.
- [X] T005 Define immutable map render references, world bounds, collision collections, and authored location relationships in `src/game/world.py` according to `specs/008-tiled-world-integration/data-model.md`.
- [X] T006 Add deterministic rectangle/polygon primitives and exact player-box overlap helpers in `src/game/geometry.py`, preserving the 32×32 logical collision contract.
- [X] T007 Add reusable map-test fixtures and headless Pygame initialization in `tests/conftest.py` for map loading and transformed-surface assertions.
- [X] T008 Document the map-loader, transform-rendering, and regression-test boundaries in `README.md` without adding a new runtime dependency.

---

## Phase 3: User Story 1 - Navigate the Tiled World (Priority: P1) 🎯 MVP

**Goal**: Load and render the authored 60×34 Tiled map, preserve its geometry and tile orientation, and keep movement inside valid walkable space.

**Independent Test**: Load the map headlessly, render asymmetric tiles for every H/V/D flag combination plus representative authored GIDs, start at `PlayerSpawn`, and test movement against all authored rectangles and polygons.

### Tests for User Story 1

- [X] T009 [P] [US1] Add map-loader tests for 60×34 dimensions, 32×32 tiles, 1920×1088 bounds, required layers, authored rectangles, and four polygon objects in `tests/unit/test_map_loader.py`.
- [X] T010 [P] [US1] Add table-driven asymmetric-pixel tests for all eight orthogonal H/V/D combinations using the official diagonal-axis-swap-first order in `tests/unit/test_tile_transforms.py`.
- [X] T011 [P] [US1] Add geometry and movement regressions for exact polygon overlap, rectangle blocking, bounded movement, and unchanged world coordinates in `tests/unit/test_geometry.py` and `tests/unit/test_collision.py`.
- [X] T012 [P] [US1] Add a headless launch/render smoke test covering transformed tile layers, transformed tile objects, base-GID extraction, and no dropped high-bit flags in `tests/smoke/test_launch_contract.py`.

### Implementation for User Story 1

- [X] T013 [US1] Implement Tiled GID decoding in `src/presentation/renderer.py` by reading horizontal, vertical, diagonal, and reserved high-bit flags and clearing all four high bits before tileset lookup.
- [X] T014 [US1] Implement the official orthogonal transform in `src/presentation/renderer.py` with a direct pixel-coordinate mapping: diagonal X/Y axis swap first, horizontal flip second, vertical flip third; cache transformed surfaces by tileset, tile ID, and flags.
- [X] T015 [US1] Extend `src/game/map_loader.py` and `src/game/world.py` so visible tile layers and tile objects retain raw GIDs, decoded flags, source tile IDs, and authored positions without changing collision or gameplay coordinates.
- [X] T016 [US1] Render visible tile layers in authored order in `src/presentation/renderer.py`, excluding empty `NPCDrawOrder` and `PlayerDrawOrder` marker layers from visible map content.
- [X] T017 [US1] Render Tiled tile objects with the same official transforms and bottom-left object alignment in `src/presentation/renderer.py` without shifting their authored world positions.
- [X] T018 [US1] Implement map-backed bounds, positive-size rectangle collisions, four polygon collisions, player spawn validation, and no-tunneling movement integration in `src/game/map_loader.py`, `src/game/world.py`, `src/game/movement.py`, and `src/game/state.py`.
- [X] T019 [US1] Validate malformed required map data with actionable errors and preserve all existing movement/camera behavior in `src/game/map_loader.py`, `src/game/state.py`, and `tests/unit/test_world.py`.

**Checkpoint**: User Story 1 is independently playable; the map, collision, spawn, and official Tiled transforms pass their focused tests.

---

## Phase 4: User Story 2 - Process Documents at Authored Locations (Priority: P1)

**Goal**: Use authored pickup and matching drop-off rectangles while preserving the existing document workflow.

**Independent Test**: Collect a document, deliver it in the matching zone, and verify a mismatched zone rejects it without corrupting progress.

### Tests for User Story 2

- [X] T020 [P] [US2] Add tests for both authored pickup zones, matching drop-off delivery, mismatched-zone rejection, and unchanged workflow state in `tests/unit/test_interaction.py`.
- [X] T021 [P] [US2] Add map-loader assertions for non-solid pickup/drop-off rectangles, unique positive `servant_id` values, and exact spawn/drop-off ID matching in `tests/unit/test_map_loader.py`.

### Implementation for User Story 2

- [X] T022 [US2] Load `DocumentPickupZones` and `DocumentDropOffZones` with their authored properties and bounds in `src/game/map_loader.py`.
- [X] T023 [US2] Integrate all authored pickup sources and servant-ID keyed drop-off zones into document acquisition and delivery in `src/game/state.py`.
- [X] T024 [US2] Preserve rejection behavior, document ownership, and wave progression for invalid drop-off zones in `src/game/state.py` and `src/game/bureaucracy.py`.

**Checkpoint**: User Story 2 works independently with both pickup zones and all matching/mismatching delivery cases.

---

## Phase 5: User Story 3 - Spawn Actors and Preserve Readable Layering (Priority: P2)

**Goal**: Spawn the player and civil servants at authored points and preserve readable actor/world layering without making servants solid.

**Independent Test**: Start a wave, verify all requested actors use their authored positions, walk through a servant, and verify Y-sorted actor rendering around the authored anchors.

### Tests for User Story 3

- [X] T025 [P] [US3] Add tests for authored servant spawn IDs, player spawn validity, non-solid servant movement, and actor foot-position ordering in `tests/unit/test_world.py`, `tests/unit/test_collision.py`, and `tests/unit/test_render_order.py`.
- [X] T026 [P] [US3] Add a smoke assertion that foreground map layers retain masking order around actors in `tests/smoke/test_launch_contract.py`.

### Implementation for User Story 3

- [X] T027 [US3] Load and validate unique positive `servant_id` spawn points and the `PlayerSpawn` point in `src/game/map_loader.py` and `src/game/world.py`.
- [X] T028 [US3] Integrate map-backed servant positions and player spawn initialization into `src/game/state.py` without adding servant sprites to collision geometry.
- [X] T029 [US3] Implement stable foot-position actor sorting between `NPCDrawOrder` and `PlayerDrawOrder` anchors in `src/presentation/renderer.py`.
- [X] T030 [US3] Preserve foreground/background layer masking and non-solid actor behavior in `src/presentation/renderer.py` and `src/game/movement.py`.

**Checkpoint**: User Story 3 is independently testable with authored actor positions, readable ordering, and pass-through servants.

---

## Phase 6: User Story 4 - Use the Fishing Zone as a Gameplay Trigger (Priority: P3)

**Goal**: Keep the existing fishing mini-game and restore stamina only after successfully catching a fish inside the authored fishing zone.

**Independent Test**: Enter `FishingZone`, complete the fishing interaction and catch a fish, verify stamina recovers without exceeding its maximum, then verify fishing is unavailable outside the zone.

### Tests for User Story 4

- [X] T031 [P] [US4] Add tests for fishing-zone entry/exit, fishing availability, successful catch recovery, failed attempts, and stamina maximum handling in `tests/unit/test_state.py`, `tests/unit/test_stamina.py`, and `tests/unit/test_interaction.py`.

### Implementation for User Story 4

- [X] T032 [US4] Load `FishingZone` as a non-solid rectangle with `kind=fishing_zone` and `stamina_regeneration=true` in `src/game/map_loader.py`.
- [X] T033 [US4] Preserve the existing fishing mini-game state transitions and controls while binding fishing availability to the authored zone in `src/game/state.py`.
- [X] T034 [US4] Restore stamina only on a successful fish catch and clamp it to the configured maximum in `src/game/state.py` and `src/game/stamina.py`.

**Checkpoint**: User Story 4 retains the fishing mini-game and catch-only stamina recovery.

---

## Phase 7: Polish & Cross-Cutting Validation

**Purpose**: Validate the complete feature, documentation, performance, and launch contract.

- [X] T035 [P] Run the focused map, geometry, transform, world, interaction, and render-order tests from `specs/008-tiled-world-integration/quickstart.md`.
- [X] T036 [P] Run the complete pytest suite and launch smoke test from `specs/008-tiled-world-integration/quickstart.md`.
- [X] T037 [P] Verify transformed tile surfaces are cached and map parsing/assets are not repeated per frame in `src/presentation/renderer.py` and `src/game/map_loader.py`.
- [X] T038 Update the map integration and official Tiled transform behavior in `README.md` and `specs/008-tiled-world-integration/quickstart.md` after manual traversal and screenshot comparison.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; verify assets and baseline first.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP and prerequisite for the authored world used by later stories.
- **User Story 2 (Phase 4)**: Depends on the map-loader boundary from US1; document workflow remains independently testable.
- **User Story 3 (Phase 5)**: Depends on map-backed world data from US1 and servant IDs from US2.
- **User Story 4 (Phase 6)**: Depends on the map-loader boundary from US1; preserves existing stamina/fishing logic.
- **Polish (Phase 7)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; no dependency on other user stories.
- **US2 (P1)**: Uses the map-loader/world boundary from US1.
- **US3 (P2)**: Uses map-backed spawn data from US1 and servant-ID relationships from US2.
- **US4 (P3)**: Uses the map-loader/world boundary from US1 and existing stamina/fishing systems.

### Parallel Opportunities

- T009–T012 can run in parallel after the foundational fixtures exist.
- T020 and T021 can run in parallel within US2.
- T025 and T026 can run in parallel within US3.
- T031 can be prepared in parallel with US3 after the shared map loader is stable.
- T035–T037 can run in parallel after the story checkpoints; T038 follows the manual validation results.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Complete US1 map loading, official Tiled transform rendering, collision, spawn, and focused tests.
3. Stop and validate the playable authored map with `specs/008-tiled-world-integration/quickstart.md`.

### Incremental Delivery

1. Add US2 document pickup/drop-off behavior and validate matching/mismatching delivery.
2. Add US3 authored actor placement and draw ordering without changing collision ownership.
3. Add US4 authored fishing-zone integration while retaining the existing mini-game and catch-only stamina recovery.
4. Run the complete polish and regression phase.

## Notes

- Every task uses the required unchecked checkbox, sequential ID, optional `[P]` marker, story label for user-story tasks, and at least one exact file path.
- Tiled transform semantics follow the [official Global Tile IDs documentation](https://doc.mapeditor.org/en/stable/reference/global-tile-ids/): diagonal axis swap first, then horizontal and vertical flips; all four high flag bits are cleared before base tile lookup.
- Transform flags affect presentation only. They must never change collision geometry, object coordinates, layer order, or gameplay state.
- No external interface contracts are required because this is an internal offline Pygame application.
