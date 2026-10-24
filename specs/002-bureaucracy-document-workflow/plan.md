# Implementation Plan: Bureaucratic Document Workflow

**Branch**: `002-bureaucracy-document-workflow` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-bureaucracy-document-workflow/spec.md`

## Summary

Extend the playable top-down slice with a deterministic bureaucratic workflow. A wave definition creates up to four civil servants at their authored spawn points and an ordered document sequence containing N handovers for wave N. Waves 1–4 retain the existing ordered recipient flow; from wave 5 onward, handovers after the initial four choose a recipient randomly from the three civil servants other than the immediately previous recipient. When a previously served servant becomes the next recipient, its presentation returns to the idle animation as soon as that step is assigned. Developer-only debug text is never rendered beside servants. Pure workflow state transitions remain independently testable through seeded randomness and integrate with the existing movement, rendering, and input loop.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Existing Pygame-ce presentation layer; pytest for deterministic workflow and integration tests

**Storage**: N/A; wave progress is session-only and resets to wave 1 on a new session

**Testing**: pytest for pure workflow state transitions and headless integration checks; manual desktop validation for interaction feedback and wave flow

**Target Platform**: Existing Windows/Linux desktop game; single-player and offline-first

**Project Type**: Modular Python desktop game / modular monolith

**Performance Goals**: Workflow transitions and validation complete within one normal simulation update; the existing 60 FPS movement and UI responsiveness remain unaffected; random recipient selection is constant-time for four servants and reproducible with a seed

**Constraints**: Preserve feature 001 movement/collision/camera behavior; no persistence, network, accounts, or new third-party dependencies; workflow rules must be deterministic, structured, and independent of rendering; invalid handovers must not mutate valid progress

**Presentation constraints**: Animation selection must distinguish workflow completion (`served`) from the currently active recipient; a Civil Servant's workflow status is communicated exclusively through its animation, with no status text, shape, outline, icon, marker, or overlay.

**Scale/Scope**: Session workflow for waves 1 onward, with one central document source, one carried document, four fixed servant spawn points, N handovers in wave N, and a data-driven random continuation from wave 5; no save/load, stamina costs, audio, final assets, or special bureaucrats

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gameplay First**: PASS. The workflow is the core bureaucracy loop, adds a meaningful ordered decision, and gives clear reasons for accepted/rejected documents and wave completion.
- **Simple, Modular Python Architecture**: PASS. A focused pure workflow module will own state transitions; existing movement and Pygame presentation remain separate adapters.
- **Deterministic and Testable Game Rules**: PASS. Wave generation, document matching, handover outcomes, completion, and the 10-second timer use explicit state and elapsed time with pytest coverage.
- **Data-Driven Bureaucratic Escalation**: PASS. Civil servants, fixed spawn points, document requirements, and random recipient choices are structured definitions; wave N uses `min(N, 4)` civil servants and N handovers, with seeded randomness for reproducible tests.
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
├── bureaucrat_animation.py # Selects idle/completion animation from workflow presentation state
└── window.py             # Dispatches interaction events and advances elapsed workflow time
tests/unit/
├── test_bureaucracy.py  # Pure workflow transitions and invalid handover invariants
├── test_wave_generation.py
├── test_bureaucrat_animation.py
└── test_state.py        # Integration of workflow with existing GameState
tests/smoke/
└── test_launch_contract.py # Existing launch checks extended for workflow initialization
```

**Structure Decision**: Add one focused pure `src/game/bureaucracy.py` module and extend existing state/input/world/presentation seams. Do not introduce a general event bus, ECS, persistence layer, or service abstraction; the workflow needs explicit immutable transitions and a small number of structured definitions.

## Phase 0: Research Summary

Research decisions are recorded in [research.md](./research.md):

1. Represent each workflow as immutable structured data and return a new state plus a typed handover result from every interaction.
2. Model N ordered handovers separately from the capped set of four servant identities; wave 5+ recipient sequences are generated with a seeded random source and exclude the immediately previous recipient.
3. Treat the 10-second next-wave delay as simulation time owned by the workflow state, not a blocking sleep or render-frame count.
4. Keep explicit interaction input at the presentation/input boundary and call pure collection/handover functions only after range and target selection are determined.
5. Keep workflow `served` state separate from presentation animation state so a previously served servant can return to `IDLE` when selected as the next recipient.
6. Treat developer/debug labels and Civil Servant status markers as out of scope for the final presentation; render workflow status only through animation while keeping unrelated workflow feedback in the general UI.

## Phase 1: Design Summary

[data-model.md](./data-model.md) defines the immutable workflow entities, document ownership, validation rules, handover outcomes, presentation animation state, and wave/timer transitions. [quickstart.md](./quickstart.md) defines pytest checks and manual scenarios for wave 1, wave 2, invalid handovers, automatic transition, repeated-recipient animation, debug-text absence, and regression coverage of movement/camera/UI.

## Constitution Check: Post-Design Re-evaluation

- **Gameplay clarity**: PASS. Every valid or invalid interaction produces an explicit outcome and identifies the next requirement.
- **State isolation**: PASS. Workflow transitions are pure and can be tested without opening a Pygame display; rendering consumes snapshots only.
- **Escalation and solvability**: PASS. Wave N has `min(N, 4)` fixed-position servants and N handovers; wave 5+ random routes are generated from valid recipients and validated before activation.
- **Timing**: PASS. The 10-second transition uses elapsed simulation time and does not block the main loop.
- **Regression safety**: PASS. Existing movement/collision/camera tests remain part of the full suite and the integration seam preserves feature 001 state.
- **Presentation clarity**: PASS. Re-targeted servants visibly return to idle before the player approaches them, and all Civil Servant status text/markers are excluded while unrelated workflow feedback remains available.
- **Complexity**: PASS. The feature adds one focused workflow module and extends existing seams without a new framework or dependency.

## Complexity Tracking

No constitution violations require justification. No external contracts, persistence, or additional dependencies are introduced.
