# Implementation Plan: Animated Player Character

**Branch**: `006-animated-player-character` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-animated-player-character/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Replace the current player rectangle and `YOU` label with the existing 4 × 3 walking tileset. A small presentation-only animation module will split the sheet into 12 frames, select one of the three directional rows from the player’s actual displacement, use the original side view for left movement and its mirrored version for right movement, and advance four-frame loops using elapsed time. The authoritative `GameState`, player collision box, movement, interaction, camera, and gameplay rules remain unchanged.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce 2.5.x; no new dependency

**Storage**: Existing PNG asset; no runtime persistence

**Testing**: pytest for pure animation and regression tests; a Pygame surface smoke test for rendering

**Target Platform**: Existing Windows/Linux desktop target

**Project Type**: Single-player desktop game

**Performance Goals**: Preserve the existing 60 FPS target; load the sheet once and avoid per-frame file I/O or repeated frame extraction

**Constraints**: Keep game rules deterministic and presentation separate; preserve the 32 × 32 logical player collision box; use 84 × 128 native frames; do not add a sprite framework

**Scale/Scope**: One player, one tileset, three directional rows, four frames per row; no NPC animation or new gameplay state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The design passes the constitution gates:

- Gameplay First: improves movement readability without changing the survival loop.
- Simple, Modular Python Architecture: keeps animation in presentation code and uses a focused module rather than a framework or ECS.
- Deterministic and Testable Game Rules: frame selection and elapsed-time advancement are independently testable; no gameplay state is changed.
- Vertical Slices and Continuous Playability: the existing placeholder is replaced incrementally and the launch path remains unchanged.
- Visual Consistency: reuses the supplied pixel-art asset and keeps the collision box separate from the visual sprite.

No constitution violation or complexity exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/006-animated-player-character/
├── plan.md              # This file ($speckit-plan command output)
├── research.md          # Phase 0 output ($speckit-plan command)
├── data-model.md        # Phase 1 output ($speckit-plan command)
├── quickstart.md        # Phase 1 output ($speckit-plan command)
└── tasks.md             # Phase 2 output ($speckit-tasks command - NOT created by $speckit-plan)
```

### Source Code (repository root)

```text
src/
├── game/
│   ├── movement.py
│   ├── state.py
│   └── world.py
└── presentation/
    ├── renderer.py
    ├── window.py
    └── character_animation.py   # new presentation-only animation module

tests/
├── unit/
│   └── test_character_animation.py  # new pure animation tests
└── smoke/
    └── test_launch_contract.py       # extend render smoke coverage
```

**Structure Decision**: Use the existing single Python project. Add only `src/presentation/character_animation.py` and focused tests. The animation object is owned by the presentation loop, while `GameState` and `Player` stay unchanged. The renderer receives the presentation animator (or an equivalent render-context object) so direct renderer tests can create an explicit, deterministic context without global state. No external contracts are needed because this is an internal desktop application.

## Complexity Tracking

No violations. The feature adds one focused presentation module and does not add a new project, dependency, persistence layer, or gameplay state.
