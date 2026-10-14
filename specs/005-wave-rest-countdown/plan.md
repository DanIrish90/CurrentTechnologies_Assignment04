# Implementation Plan: Wave Rest Countdown

**Branch**: `005-wave-rest-countdown` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-wave-rest-countdown/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a visible ten-second rest countdown after each completed wave. Reuse the existing deterministic workflow transition timer, expose its remaining time and completed wave number through the UI snapshot, render an upward-facing semicircular clock centered at the bottom of the screen, and make fishing available only while the rest countdown is active.

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

**Performance Goals**: Preserve the 60 FPS target; countdown and transitions use constant-time elapsed simulation updates.

**Constraints**: No new dependency; the existing ten-second workflow timer remains authoritative; the countdown never goes below zero; the upward-facing clock is bottom-center; fishing input is allowed only during rest and blocked during active-wave play; fishing at a deadline is cancelled without reward; the first wave has no rest countdown.

**Scale/Scope**: One player, one active workflow, one visible rest countdown, deterministic wave transitions; no persistence or networking.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|---|---|---|
| Gameplay first | PASS | The countdown creates a clear planning window and makes rest the dedicated recovery/fishing window. |
| Modular architecture | PASS | Existing workflow state owns timing; `state.py` composes transition and fishing cancellation; renderer owns the semicircle. |
| Deterministic/testable rules | PASS | Existing elapsed-time transition timer is reused, clamped at zero, and covered by pytest. |
| Bureaucratic progression | PASS | The existing ordered wave factory and servant/document rules remain authoritative. |
| Stamina/fishing alignment | PASS | Fishing is available only during rest, preserving recovery as a deliberate inter-wave decision. |
| Vertical playability | PASS | The feature adds a readable overlay without new dependencies and enforces the explicit fishing window. |
| Visual/readability | PASS | Rest time, completed wave number, and upward-facing arc progress are shown together and do not rely on color alone. |
| Complexity | PASS | No new state machine or service is introduced; existing workflow phases are reused. |

## Project Structure

### Documentation (this feature)

```text
specs/005-wave-rest-countdown/
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
│   ├── bureaucracy.py       # existing rest timer and wave transition state
│   ├── state.py             # countdown snapshot and fishing cancellation at transition
│   └── config.py            # rest duration and presentation constants
└── presentation/
    └── renderer.py          # bottom-center upward-facing countdown overlay and labels

tests/
├── unit/
│   ├── test_bureaucracy.py
│   ├── test_state.py
│   └── test_ui_snapshot.py
└── smoke/
    └── test_launch_contract.py
```

**Structure Decision**: Extend the existing modular monolith. Keep the authoritative ten-second timer in `WaveProgress.transition_remaining` and the existing `advance_progress` transition. Add only the minimum UI snapshot fields and renderer overlay required for the player-facing countdown. `state.py` allows casting only while the workflow is in a rest phase, blocks fishing during active-wave play, detects the transition to the next wave, and resets fishing before reward application. The renderer draws the arc in the upper half of its bottom-center panel. No external contracts are needed for this offline desktop game.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The design reuses existing workflow timing and module boundaries. |
