# Implementation Plan: Fishing Mini-Game

**Branch**: `004-fishing-mini-game` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-fishing-mini-game/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Replace passive stamina regeneration at the former recovery zone with an active Fishing Pond mini-game. Empty-handed players press `E` to cast, wait a deterministic 2 seconds for a bite, and press again within less than 1 second to enter a catch game. A pure fishing state machine controls the fish position, catch-bar position and velocity, fishing progress, cancellation, and one-time 25-stamina reward; each press applies an upward impulse, gravity accelerates the bar downward after the 0.15-second grace period, and position/speed remain bounded. Presentation renders readable placeholder meters and feedback while the game state pauses movement during fishing.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce; standard-library dataclasses; existing pytest stack

**Storage**: N/A; in-memory single-player session state

**Testing**: pytest unit/state/UI/smoke tests; headless Pygame rendering and quit check

**Target Platform**: Desktop Windows/Linux, offline-first

**Project Type**: Single-player Pygame desktop game

**Performance Goals**: Preserve the 60 FPS target; all fishing timers and meters use elapsed simulation time and constant-time updates.

**Constraints**: No new dependency; `E` is the sole fishing action; movement pauses during active fishing; bite boundary at 1.0 seconds is a miss; catch-bar motion uses elapsed simulation time, bounded velocity, upward impulses, gravity, and the existing 0.15-second grace period; rewards clamp to stamina maximum.

**Scale/Scope**: One player, one Fishing Pond, one active fishing attempt, deterministic fish movement, one fish reward per attempt; no persistence or networking.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|---|---|---|
| Gameplay first | PASS | Fishing adds a skill-based recover-or-risk decision to the bureaucracy survival loop. |
| Modular architecture | PASS | Pure transitions live in `fishing.py`; state, input, world geometry, and rendering remain separated. |
| Deterministic/testable rules | PASS | Fixed bite delay, strict reaction boundary, elapsed-time meters, clamped values, and pytest coverage are defined. |
| Bureaucratic progression | PASS | Fishing only restores stamina; document validation, wave progression, and handovers remain unchanged. |
| Stamina/fishing survival alignment | PASS | The former passive regeneration zone becomes an active Fishing Pond and successful fishing restores 25 stamina. |
| Vertical playability | PASS | One pond, placeholder shapes, existing `E` input, and no new dependency form a launchable slice. |
| Visual/readability | PASS | Labels, status text, symbols, and multiple bars communicate fishing without color alone. |
| Complexity | PASS | No framework, service, persistence, random dependency, or external asset pipeline is introduced. |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file ($speckit-plan command output)
├── research.md          # Phase 0 output ($speckit-plan command)
├── data-model.md        # Phase 1 output ($speckit-plan command)
├── quickstart.md        # Phase 1 output ($speckit-plan command)
├── contracts/           # Phase 1 output ($speckit-plan command)
└── tasks.md             # Phase 2 output ($speckit-tasks command - NOT created by $speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── game/
│   ├── config.py          # fishing timing, meter rates, reward, UI dimensions
│   ├── fishing.py         # pure fishing phases, catch game, outcomes
│   ├── input_state.py     # existing E edge and input snapshots
│   ├── state.py           # fishing integration, movement pause, stamina reward
│   └── world.py           # FishingPond geometry and initial placement
└── presentation/
    ├── renderer.py        # pond label, fishing overlay/meters, phase feedback
    └── window.py          # existing event loop and one-frame input clearing

tests/
├── unit/
│   ├── test_fishing.py
│   ├── test_state.py
│   ├── test_ui_snapshot.py
│   └── test_world.py
└── smoke/
    └── test_launch_contract.py
```

**Structure Decision**: Extend the existing modular monolith. `fishing.py` owns all fishing transitions and velocity/impulse arithmetic; `state.py` composes those results with movement, workflow, and stamina; `world.py` owns the renamed pond geometry; `renderer.py` owns all fishing visuals. No external contracts are needed for this offline desktop game.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The design complies with the constitution without exceptions. |
