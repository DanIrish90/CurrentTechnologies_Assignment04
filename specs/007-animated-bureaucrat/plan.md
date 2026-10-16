# Implementation Plan: Animated Bureaucrats

**Branch**: `007-animated-bureaucrat` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-animated-bureaucrat/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Replace the current Civil Servant rectangles with the supplied 2 × 2 Bureaucrat sheet. A presentation-only animation module will load and split the four 84 × 128 frames once, maintain an independent animation state per servant ID, loop row 0 while `served=False`, and loop row 1 while `served=True`. State changes reset only the affected servant to frame 0; the existing immutable game state, workflow rules, interaction positions, and UI remain authoritative.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing Pygame-ce 2.5.x; no new dependency

**Storage**: Existing PNG asset; no runtime persistence

**Testing**: pytest unit tests and Pygame surface smoke tests

**Target Platform**: Existing Windows/Linux desktop target

**Project Type**: Single-player desktop game

**Performance Goals**: Preserve the existing 60 FPS target; no per-frame asset I/O or frame extraction; support all servants in a wave independently

**Constraints**: Keep animation in presentation state; preserve the existing Civil Servant position and interaction range; loop at 3 FPS by default; do not add a sprite framework or gameplay state

**Scale/Scope**: One Bureaucrat sheet, four frames, two animation states, and one presentation state per active servant ID; no new NPC types

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The design passes the constitution gates:

- Gameplay First: adds clear visual feedback for successful document handovers without changing the survival loop.
- Simple, Modular Python Architecture: uses one focused presentation module and reuses the existing renderer/window flow.
- Deterministic and Testable Game Rules: animation selection depends only on the current `served` value and elapsed time; no gameplay state is mutated.
- Vertical Slices and Continuous Playability: replaces only the Civil Servant presentation and preserves the launch path.
- Visual Consistency: uses the supplied pixel-art sheet, keeps labels readable, and preserves the logical interaction target.

No constitution violation or complexity exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/007-animated-bureaucrat/
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
│   ├── bureaucracy.py
│   ├── state.py
│   └── config.py
└── presentation/
    ├── renderer.py
    ├── window.py
    └── bureaucrat_animation.py   # new presentation-only module

tests/
├── unit/
│   └── test_bureaucrat_animation.py  # new animation/state tests
└── smoke/
    └── test_launch_contract.py        # extend render coverage
```

**Structure Decision**: Keep the existing single Python project. Add `src/presentation/bureaucrat_animation.py` and focused tests. The presentation loop owns a mapping from active servant ID to animation state; `GameState`, `WaveProgress`, and `CivilServant` remain unchanged. The renderer receives the presentation context explicitly so tests do not depend on global mutable state. No external contracts are needed because this is an internal desktop application.

## Complexity Tracking

No violations. The feature adds one focused presentation module and a per-servant presentation mapping, without adding dependencies, persistence, or gameplay state.
