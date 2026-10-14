# Implementation Plan: Core Game Window and Player Movement

**Branch**: `001-core-game-player-movement` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-core-game-player-movement/spec.md`

## Summary

Create the first playable desktop vertical slice: a launchable game window with a clearly visible player, frame-rate-independent top-down movement, bounded collision-aware navigation, a camera constrained to the world, and a readable starter UI. Gameplay rules will live in pure Python modules that can be tested without opening the rendering window; the application layer will connect input, simulation updates, and rendering through Pygame-ce.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce for the desktop window, input, timing, and rendering; pytest for automated tests

**Storage**: N/A; the first slice has no save data or persistence

**Testing**: pytest for pure game-logic unit tests; manual smoke testing for launch, controls, rendering, camera, and window lifecycle

**Target Platform**: Desktop on Windows and Linux; offline-first

**Project Type**: Single-player desktop game / modular monolith

**Performance Goals**: Target a stable 60 frames per second on ordinary desktop hardware; input response should remain within the specification's 100 ms target during normal play

**Constraints**: No server, account, database, or network connection; movement must use elapsed simulation time; rendering and input must not contain the authoritative collision rules; dependencies remain minimal

**Scale/Scope**: One fixed initial world, one player, a small set of static solid obstacles, one camera view, and foundational UI; no documents, bureaucrats, stamina, fishing, progression, audio, save system, controller support, or final art assets in this slice

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gameplay First**: PASS. The slice is directly playable, prioritizes responsive movement and readable feedback, and establishes navigation for later bureaucracy and fishing systems.
- **Simple, Modular Python Architecture**: PASS. The design separates pure simulation and collision rules from Pygame input/rendering and uses a small number of focused modules.
- **Deterministic and Testable Game Rules**: PASS. Movement, bounds, collision, and camera clamping use explicit state and elapsed time and are testable without a rendering loop.
- **Data-Driven Bureaucratic Escalation**: PASS. This slice does not implement waves or documents; its world entities are represented as structured data so later gameplay can extend the same boundaries without scattering rules.
- **Stamina and Fishing Survival System**: PASS. Out of scope for this vertical slice; the UI reserves a clear placeholder without pretending that stamina mechanics exist.
- **Vertical Slices and Continuous Playability**: PASS. The result is a launchable game slice with placeholder visuals, automated logic tests, and manual validation steps.
- **Visual Consistency and Satirical Identity**: PASS. Placeholder visuals distinguish player, obstacles, world, and UI; text and shape provide feedback beyond color and leave final pixel-art assets replaceable.
- **Technical constraints**: PASS. The plan uses Python 3.12+, Pygame-ce, pytest, desktop targets, offline operation, and a minimal dependency set.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-game-player-movement/
├── plan.md              # This implementation plan
├── research.md          # Phase 0 decisions and rationale
├── data-model.md        # Phase 1 simulation and rendering state model
├── quickstart.md        # Phase 1 run and validation guide
└── tasks.md             # Created later by $speckit-tasks
```

No `contracts/` directory is needed: this is an internal desktop application feature with no external API, CLI schema, or service integration.

### Source Code (repository root)

```text
main.py                         # Small application entry point
src/
├── game/
│   ├── __init__.py
│   ├── config.py               # Window, world, movement, and visual constants
│   ├── geometry.py             # Small typed rectangles/vectors and collision helpers
│   ├── input_state.py          # Translation from application events to input state
│   ├── world.py                # Initial world and structured obstacle definitions
│   ├── movement.py              # Pure player movement and collision resolution
│   ├── camera.py               # Pure camera positioning and world-bound clamping
│   └── state.py                 # Explicit runtime state and update orchestration
└── presentation/
    ├── __init__.py
    ├── renderer.py             # Pygame drawing for world, player, and UI
    └── window.py                # Pygame window lifecycle and main loop
tests/
├── unit/
│   ├── test_movement.py
│   ├── test_collision.py
│   ├── test_camera.py
│   └── test_input_state.py
└── smoke/
    └── test_launch_contract.py # Non-window checks for initial configuration
```

**Structure Decision**: Use a single Python project with an application entry point, pure `src/game` rules, and a thin `src/presentation` adapter around Pygame-ce. This is the smallest structure that satisfies the constitution's separation of logic, input, and rendering while remaining easy to extend with later vertical slices.

## Phase 0: Research Summary

Research decisions are recorded in [research.md](./research.md). The important decisions are:

1. Use a fixed-step-independent, elapsed-time movement update with a normalized input vector.
2. Represent player and obstacle bounds with simple axis-aligned rectangles and resolve movement per axis so sliding remains possible.
3. Keep camera calculations pure and clamp the camera rectangle to world bounds.
4. Keep Pygame-ce at the presentation boundary and test authoritative rules through plain Python values.

## Phase 1: Design Summary

The data model in [data-model.md](./data-model.md) defines the player, world, obstacles, camera, input state, and UI snapshot, including invariants and transitions. The validation workflow in [quickstart.md](./quickstart.md) covers automated tests, launch, movement, collision, camera edges, UI readability, and clean shutdown.

## Constitution Check: Post-Design Re-evaluation

- **Gameplay and playability**: PASS. The design produces a complete launchable slice and keeps later survival mechanics out of scope until they can be specified and tested independently.
- **Module boundaries**: PASS. Input translation and rendering depend on the game state; movement, collision, and camera calculations do not depend on Pygame-ce.
- **Determinism and tests**: PASS. The model defines explicit invariants, deterministic input resolution, elapsed-time movement, and headless test seams.
- **Visual clarity**: PASS. The UI contract includes text and control hints, while player and obstacles have distinct shapes/positions rather than color-only signaling.
- **Complexity and dependencies**: PASS. There are no unjustified services, persistence layers, frameworks, or contracts; the proposed modules are limited to the active feature's responsibilities.
- **Continuous playability**: PASS. The quickstart covers both automated rule checks and a manual launch/interaction path, and placeholder visuals keep implementation unblocked.

## Complexity Tracking

No constitution violations require justification. No additional architectural abstraction, service, persistence layer, or dependency is introduced.
