# Implementation Plan: Wave Rest Countdown

**Branch**: `005-wave-rest-countdown` | **Date**: 2026-10-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-wave-rest-countdown/spec.md`

## Summary

Replace the existing bottom-center semicircle countdown with the `WormTimer.png` sprite animation. The existing elapsed-time workflow transition remains authoritative, but its duration becomes the centralized `WAVE_REST_DURATION` setting with a default of 10 seconds. During rest, the worm advances from the left to the right edge of the stamina bar while sprite frames loop at a configurable frames-per-second rate; outside rest, the WormTimer is hidden.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce, standard-library dataclasses, existing pytest stack; no new dependency.

**Storage**: N/A; in-memory single-player session state.

**Testing**: pytest unit tests for configuration, workflow timing, snapshot derivation, asset splitting, and layout; headless Pygame rendering and existing smoke tests.

**Target Platform**: Desktop Windows/Linux, offline-first.

**Project Type**: Single-player Pygame desktop game with separated game logic and presentation.

**Performance Goals**: Preserve the 60 FPS target. Timer updates and WormTimer frame selection are constant-time and independent of render frequency.

**Constraints**: `WAVE_REST_DURATION` must remain positive and default to 10.0 seconds. `WORM_TIMER_FPS` must be positive, default to 8.0 frames per second, and affect only sprite frame selection. `WormTimer.png` is 448×32 and is split into seven horizontal 64×32 frames. Worm movement follows elapsed rest progress, not animation frame count. The first wave has no WormTimer. Fishing remains available only during rest and expires without reward at the wave boundary.

**Scale/Scope**: One player, one active workflow, one WormTimer, no persistence, networking, or external API.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|---|---|---|
| Gameplay first | PASS | The WormTimer makes the fishing/recovery window immediately readable and preserves the existing wave decision. |
| Modular architecture | PASS | `bureaucracy.py` remains authoritative for timing; `state.py` exposes derived UI data; `ui_assets.py` loads frames; `renderer.py` only draws. |
| Deterministic/testable rules | PASS | Rest duration uses elapsed simulation time; movement progress and frame index are deterministic and clamped. |
| Bureaucratic progression | PASS | Existing wave factory, document sequence, and one-time transition remain unchanged. |
| Stamina/fishing alignment | PASS | Fishing eligibility and cancellation behavior remain unchanged; only the rest visual changes. |
| Vertical playability | PASS | Existing asset and Pygame stack are reused; the feature retains a launchable game and adds headless render checks. |
| Visual consistency | PASS | The pixel-art WormTimer is rendered under the existing stamina bar and is not the sole indicator of gameplay state; visibility is tied to the explicit rest state. |
| Complexity | PASS | No new dependency, service, or state machine; only a small animation asset adapter and derived UI fields are added. |

## Project Structure

### Documentation (this feature)

```text
specs/005-wave-rest-countdown/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md                 # generated separately by $speckit-tasks
```

### Source Code

```text
src/
├── game/
│   ├── bureaucracy.py       # existing rest timer and wave transition
│   ├── config.py            # WAVE_REST_DURATION, WORM_TIMER_FPS, sheet constants and asset path
│   └── state.py             # derived rest visibility, movement progress and animation frame
└── presentation/
    ├── ui_assets.py         # load and split WormTimer.png into seven frames
    └── renderer.py          # draw WormTimer below stamina bar and remove semicircle renderer

tests/
├── unit/
│   ├── test_bureaucracy.py
│   ├── test_state.py
│   ├── test_ui_assets.py
│   └── test_ui_snapshot.py
└── smoke/
    └── test_launch_contract.py
```

**Structure Decision**: Extend the existing modular monolith. Keep `WaveProgress.transition_remaining` as the only gameplay timer, replace `DOCUMENT_TRANSITION_SECONDS` with canonical `WAVE_REST_DURATION`, and derive all WormTimer presentation values in `ui_snapshot`. `UiAssets` owns validated sprite surfaces; the renderer receives those surfaces and computes only screen-space placement/scaling. No external contracts are needed for this offline desktop game.

## Phase 0: Research Outputs

Research decisions are recorded in [research.md](./research.md). All technical unknowns are resolved before implementation tasks are generated.

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) defines the configuration, workflow-derived UI fields, sprite frames, and invariants.
- [quickstart.md](./quickstart.md) defines automated and manual validation for configurable duration, animation speed, movement, visibility, and wave/fishing behavior.
- No `contracts/` directory is required: this is an internal desktop game with no public network or inter-process interface.

## Post-Design Constitution Check

| Gate | Status | Evidence |
|---|---|---|
| Gameplay and readability | PASS | The worm is visible only during rest, follows the stamina bar, and reaches its endpoint exactly at transition. |
| Time independence | PASS | Workflow progression uses elapsed simulation time; animation and movement are derived from elapsed rest progress rather than frames rendered. |
| Module boundaries | PASS | Configuration, state derivation, asset loading, and rendering remain separated. |
| Testability | PASS | Pure frame splitting/layout helpers and snapshot calculations can be tested without a display; smoke rendering uses dummy SDL. |
| Scope and complexity | PASS | Existing fishing and wave logic are preserved; only the obsolete semicircle presentation is removed. |

## Complexity Tracking

No constitution violations require justification.
