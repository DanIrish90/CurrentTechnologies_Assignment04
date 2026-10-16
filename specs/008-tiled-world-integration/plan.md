# Implementation Plan: Tiled World Integration

**Branch**: `008-tiled-world-integration` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-tiled-world-integration/spec.md`

## Summary

Replace the current hard-coded abstract world with the authored `assets/World/World.tmj` map. A focused map-loading boundary will convert Tiled tile layers and object layers into render data, including each tile's authored rotation/mirroring transform, world bounds, collision shapes, spawn points, interaction zones, and draw-order anchors. The renderer will implement the official Tiled orthogonal global-tile-ID transform algorithm: clear the four high flag bits for tile lookup, apply the diagonal axis swap first, then horizontal and vertical flips, and cache the resulting tile surface. The existing pure movement system will be extended with exact player-rectangle versus polygon overlap checks and rectangle collision, while workflow, stamina, fishing, and wave rules remain in their existing modules.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce, Python standard library `json`, and pytest. No new third-party dependency.

**Storage**: Read-only repository assets: `assets/World/World.tmj`, `assets/World/WorldTileSet.tsx`, and `assets/World/MasterTileset.png`. Runtime state remains in Python data structures.

**Testing**: pytest, including pure geometry/map-loader unit tests, gameplay regression tests, and a launch smoke test.

**Target Platform**: Offline desktop on Windows and Linux.

**Project Type**: Single-player Pygame desktop application with separated game logic and presentation.

**Performance Goals**: Maintain the existing 60 FPS target. Collision and interaction checks must remain fast for the authored map's 37 active rectangles and 4 polygons; transform lookup must avoid per-frame map parsing or asset reloads.

**Constraints**: Preserve the current 32×32 player collision box, axis-independent movement, camera, document workflow, fishing, stamina, waves, and restart behavior. Polygon collision must be exact against polygon contours. Actors are non-solid. Visible tile layers and tile objects must preserve Tiled rotation, horizontal/vertical mirroring, and combined transform flags. Transform rendering must follow Tiled's documented operation order and direct pixel-coordinate mapping, not a guessed rotation table.

**Scale/Scope**: One finite 60×34 orthogonal map (1920×1088 pixels), four servant spawn/drop-off mappings, two pickup zones, one fishing zone, 37 rectangle collision objects, and four polygon collision objects.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gameplay First**: PASS. The map supports movement, document pickup/drop-off, servant progression, and fishing.
- **Simple, Modular Python Architecture**: PASS. The design adds focused map and geometry modules without an engine, ECS, or new dependency.
- **Deterministic and Testable Game Rules**: PASS. Map validation and collision are pure deterministic operations covered by pytest.
- **Data-Driven Bureaucratic Escalation**: PASS. Servant locations and destinations are read from `servant_id`-keyed map data.
- **Stamina and Fishing Form One Survival System**: PASS. `FishingZone` remains a non-solid trigger using existing stamina rules.
- **Vertical Slices and Continuous Playability**: PASS. Launch smoke and regression tests are included.
- **Visual Consistency and Satirical Identity**: PASS. Existing pixel-art assets, authored layer order, and authored tile orientations are reused.
- **Complexity Gate**: PASS. No violation requires an exception.

## Project Structure

### Documentation

```text
specs/008-tiled-world-integration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md                 # created by speckit-tasks
```

### Source Code

```text
src/game/
├── geometry.py              # Rect/Vector2 plus polygon primitives and exact overlap helpers
├── map_loader.py            # TMJ parsing, validation, and conversion to world data
├── movement.py              # axis-independent movement using rectangle/polygon collision
├── world.py                 # World/Player domain objects and map-backed world construction
└── state.py                 # integrates loaded world with existing gameplay state

src/presentation/
└── renderer.py              # transformed tile/object rendering and actor draw-order integration

tests/unit/
├── test_geometry.py         # polygon overlap and movement safety
├── test_map_loader.py       # TMJ parsing and validation
├── test_tile_transforms.py  # Tiled GID decoding and orientation composition
├── test_world.py            # map-backed spawn and zone invariants
└── test_collision.py        # regression and exact collision behavior

tests/smoke/
└── test_launch_contract.py   # valid startup and transformed-tile rendering contract
```

**Structure Decision**: Keep the existing modular monolith. `map_loader.py` owns Tiled parsing, `geometry.py` owns pure geometry, `movement.py` owns collision resolution, `world.py` owns domain validation, and `renderer.py` consumes read-only render data. No `contracts/` directory is required because this is an internal desktop application.

## Phase 0: Research Decisions

See [research.md](research.md). Research resolves polygon collision, Tiled coordinate semantics, rendering strategy, and compatibility.

## Phase 1: Design Outputs

- [data-model.md](data-model.md) defines entities, relationships, and validation.
- [quickstart.md](quickstart.md) defines automated and manual validation.
- No external interface contracts are required.

## Post-Design Constitution Check

- **Gameplay and interaction ownership**: PASS. Map data supplies locations; existing workflow owns document and wave decisions.
- **Geometry ownership**: PASS. Collision is pure game logic and independent of rendering.
- **Rendering ownership**: PASS. Tile layers, official Tiled transform decoding, and actors remain presentation concerns.
- **Regression safety**: PASS. Existing movement, state, camera, fishing, bureaucracy, and smoke tests remain required.
- **Complexity**: PASS. Exact polygons are required by the clarified specification; bounded movement subdivision avoids a physics dependency.
