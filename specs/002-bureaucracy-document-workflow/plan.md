# Implementation Plan: Bureaucratic Document Workflow

**Branch**: `002-bureaucracy-document-workflow` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-bureaucracy-document-workflow/spec.md`

## Summary

Extend the playable top-down slice with a deterministic bureaucratic workflow. A wave definition creates its civil servants and ordered document requirements; the player explicitly interacts with the central document source and servants; valid handovers consume the carried document and may issue the next document, while invalid handovers leave progress unchanged. Wave 1 contains one direct handover, wave 2 contains the required document-to-permit chain, and a completed wave transitions automatically after 10 seconds. Pure workflow state transitions will be tested independently of Pygame and then integrated with the existing movement, rendering, and input loop.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing Pygame-ce presentation layer; pytest for deterministic workflow and integration tests

**Storage**: N/A; wave progress is session-only and resets to wave 1 on a new session

**Testing**: pytest for pure workflow state transitions and headless integration checks; manual desktop validation for interaction feedback and wave flow

**Target Platform**: Existing Windows/Linux desktop game; single-player and offline-first

**Project Type**: Modular Python desktop game / modular monolith

**Performance Goals**: Workflow transitions and validation complete within one normal simulation update; the existing 60 FPS movement and UI responsiveness remain unaffected; the wave-completion timer is elapsed-time based and starts at exactly 10 seconds

**Constraints**: Preserve feature 001 movement/collision/camera behavior; no persistence, network, accounts, or new third-party dependencies; workflow rules must be deterministic, structured, and independent of rendering; invalid handovers must not mutate valid progress

**Scale/Scope**: Session workflow for waves 1 and 2, with one central document source, one carried document, one permit outcome, and a data-driven model ready for additional wave definitions; no save/load, stamina costs, audio, final assets, or special bureaucrats

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gameplay First**: PASS. The workflow is the core bureaucracy loop, adds a meaningful ordered decision, and gives clear reasons for accepted/rejected documents and wave completion.
- **Simple, Modular Python Architecture**: PASS. A focused pure workflow module will own state transitions; existing movement and Pygame presentation remain separate adapters.
- **Deterministic and Testable Game Rules**: PASS. Wave generation, document matching, handover outcomes, completion, and the 10-second timer use explicit state and elapsed time with pytest coverage.
- **Data-Driven Bureaucratic Escalation**: PASS. Civil servants, document requirements, and outcome documents are structured definitions; wave N uses N civil servants and supplied workflows are validated before activation.
- **Stamina and Fishing Survival System**: PASS. Stamina and fishing remain outside this feature; carrying and handover state is designed so future stamina costs can be added without changing document validity rules.
- **Vertical Slices and Continuous Playability**: PASS. Wave 1 is an independently playable MVP, wave 2 adds the first escalation, and the existing launchable movement slice remains intact.
- **Visual Consistency and Satirical Identity**: PASS. Placeholder civil-servant/document/status visuals and text are replaceable, readable, and not color-only; rejection and permit feedback remain explicit.
- **Technical constraints**: PASS. The design uses the existing Python/Pygame-ce/pytest stack, avoids persistence and external services, and keeps dependencies unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/002-bureaucracy-document-workflow/
├── plan.md              # This implementation plan
├── research.md          # Phase 0 decisions and rationale
├── data-model.md        # Workflow entities and state transitions
├── quickstart.md        # Automated and manual validation guide
└── tasks.md             # Created later by $speckit-tasks
```

No `contracts/` directory is needed: this is an internal desktop game feature with no external API, CLI protocol, or service integration.

### Source Code (repository root)

```text
src/game/
├── bureaucracy.py       # Pure wave/document/civil-servant definitions and transitions
├── state.py              # Integrates bureaucracy state with existing player/camera state
├── input_state.py       # Adds explicit interaction input to existing movement input
├── config.py             # Adds interaction and wave timing constants
└── world.py              # Adds central document source and civil-servant world placements
src/presentation/
├── renderer.py          # Draws civil servants, document source, carried document, and feedback
└── window.py             # Dispatches interaction events and advances elapsed workflow time
tests/unit/
├── test_bureaucracy.py  # Pure workflow transitions and invalid handover invariants
├── test_wave_generation.py
└── test_state.py        # Integration of workflow with existing GameState
tests/smoke/
└── test_launch_contract.py # Existing launch checks extended for workflow initialization
```

**Structure Decision**: Add one focused pure `src/game/bureaucracy.py` module and extend existing state/input/world/presentation seams. Do not introduce a general event bus, ECS, persistence layer, or service abstraction; the workflow needs explicit immutable transitions and a small number of structured definitions.

## Phase 0: Research Summary

Research decisions are recorded in [research.md](./research.md):

1. Represent each workflow as immutable structured data and return a new state plus a typed handover result from every interaction.
2. Model the wave 1 direct handover and wave 2 document-to-permit chain declaratively instead of using scattered wave-number conditionals.
3. Treat the 10-second next-wave delay as simulation time owned by the workflow state, not a blocking sleep or render-frame count.
4. Keep explicit interaction input at the presentation/input boundary and call pure collection/handover functions only after range and target selection are determined.

## Phase 1: Design Summary

[data-model.md](./data-model.md) defines the immutable workflow entities, document ownership, validation rules, handover outcomes, and wave/timer transitions. [quickstart.md](./quickstart.md) defines pytest checks and manual scenarios for wave 1, wave 2, invalid handovers, automatic transition, and regression coverage of movement/camera/UI.

## Constitution Check: Post-Design Re-evaluation

- **Gameplay clarity**: PASS. Every valid or invalid interaction produces an explicit outcome and identifies the next requirement.
- **State isolation**: PASS. Workflow transitions are pure and can be tested without opening a Pygame display; rendering consumes snapshots only.
- **Escalation and solvability**: PASS. Wave 1 has one servant, wave 2 has two, the permit chain is explicit, and wave definitions are validated before activation.
- **Timing**: PASS. The 10-second transition uses elapsed simulation time and does not block the main loop.
- **Regression safety**: PASS. Existing movement/collision/camera tests remain part of the full suite and the integration seam preserves feature 001 state.
- **Complexity**: PASS. The feature adds one focused workflow module and extends existing seams without a new framework or dependency.

## Complexity Tracking

No constitution violations require justification. No external contracts, persistence, or additional dependencies are introduced.
