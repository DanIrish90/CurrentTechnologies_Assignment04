# Implementation Plan: Stamina Usage and Recovery

**Branch**: `003-stamina-usage` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-stamina-usage/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a bounded stamina survival system to the existing Pygame game. Carrying the active bureaucracy document drains 5 stamina points per elapsed second; being empty-handed inside one world recovery zone restores 10 points per second. Stamina is visible through a readable bar/value and status text, reaches game over at zero, freezes the current run, and can be reset through a clickable “Restart” button. The implementation keeps rules in pure game logic, world geometry in `World`, and presentation/input responsibilities in their existing layers.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce; existing standard-library dataclasses and pytest stack

**Storage**: N/A; in-memory single-player session state

**Testing**: pytest unit and smoke tests; headless Pygame launch check

**Target Platform**: Desktop Windows/Linux, offline-first

**Project Type**: Single-player Pygame desktop game

**Performance Goals**: Preserve the existing 60 FPS target; stamina updates are constant-time per frame and independent of frame rate.

**Constraints**: No new dependency; deterministic elapsed-time rules; stamina clamped to 0–100; no gameplay mutation after game over except Restart.

**Scale/Scope**: One player, one active document, one recovery zone, existing wave/document workflow; no persistence or networking.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|---|---|---|
| Gameplay first | PASS | Stamina adds a clear carry-versus-recover decision and explains exhaustion. |
| Modular architecture | PASS | Pure stamina rules, existing state orchestration, world geometry, input, and renderer remain separated. |
| Deterministic/testable rules | PASS | All changes use elapsed seconds, bounded values, explicit transitions, and pytest coverage. |
| Bureaucratic progression | PASS | Existing document workflow remains authoritative for carried-document status and wave progression. |
| Stamina/fishing survival alignment | PASS | This slice implements document consumption and a recovery zone; future skill-based fishing remains compatible and out of scope. |
| Vertical playability | PASS | One zone and placeholder visuals preserve a launchable game with no new dependency. |
| Visual/readability | PASS | Numeric/status feedback and labeled geometry avoid color-only communication. |
| Complexity | PASS | No new framework, service, persistence, or abstraction layer is introduced. |

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
│   ├── config.py          # stamina rates, colors, UI dimensions
│   ├── input_state.py     # restart click action and existing movement/input
│   ├── stamina.py         # pure stamina state/update rules
│   ├── state.py           # simulation orchestration and game-over/restart transitions
│   └── world.py           # StaminaRegenZone and initial world placement
└── presentation/
    ├── renderer.py        # stamina UI, recovery-zone label, game-over overlay/button
    └── window.py          # Pygame event-to-input translation and frame loop

tests/
├── unit/
│   ├── test_stamina.py
│   ├── test_state.py
│   ├── test_input_state.py
│   ├── test_ui_snapshot.py
│   └── test_world.py
└── smoke/
    └── test_launch_contract.py
```

**Structure Decision**: Extend the existing modular monolith. `src/game/stamina.py` owns pure calculations, `state.py` composes stamina with the current workflow, `world.py` owns the recovery-zone geometry, and `presentation` owns drawing and click feedback. Existing document workflow and movement modules remain unchanged except for their integration points.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The design complies with the constitution without exceptions. |
