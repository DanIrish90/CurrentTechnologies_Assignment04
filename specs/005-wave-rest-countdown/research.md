# Research: Wave Rest Countdown

**Feature**: [005-wave-rest-countdown](./spec.md)
**Date**: 2026-10-17

## Decision 1: Keep one authoritative rest timer

- **Decision**: Continue using `WaveProgress.transition_remaining` and `advance_progress`; make the duration come from `config.WAVE_REST_DURATION`, default `10.0`.
- **Rationale**: Wave transition, fishing cancellation, clamping, and one-time next-wave creation already use this timer. A second timer could drift from gameplay state.
- **Alternatives considered**: A renderer-owned timer was rejected because rendering must not drive gameplay; a separate `GameState` timer was rejected because it duplicates workflow state.

## Decision 2: Derive WormTimer presentation state from simulation time

- **Decision**: Extend `UiSnapshot` with rest elapsed progress and a deterministic WormTimer frame index derived from elapsed rest time and `WORM_TIMER_FPS`.
- **Rationale**: The renderer needs stable, testable inputs while remaining independent from domain objects. Movement can use normalized elapsed progress, and animation can loop independently.
- **Alternatives considered**: Advancing frames inside `renderer.py` was rejected because it depends on render frequency; tying worm position to frame index was rejected because animation speed must not alter the rest duration.

## Decision 3: Split the existing asset as seven horizontal frames

- **Decision**: Validate `WormTimer.png` as 448×32 and split it into seven 64×32 surfaces from left to right.
- **Rationale**: This matches the provided asset and the clarified requirement. A small pure helper makes dimensions and frame order directly testable.
- **Alternatives considered**: Treating the image as one static texture was rejected because the feature requires animation; inferring frame size at runtime was rejected because it hides asset errors.

## Decision 4: Anchor movement to the stamina-bar geometry

- **Decision**: Place the worm below the rendered stamina bar and interpolate its anchor from the bar's left edge to its right edge using elapsed rest progress. Apply the existing UI zoom/scale conventions consistently.
- **Rationale**: The bar is the player's stable reference for stamina and gives the rest phase a clear spatial start/end. The endpoint remains correct for every positive rest duration and animation speed.
- **Alternatives considered**: Bottom-center placement was rejected because it conflicts with the clarified position; a fixed pixel speed was rejected because it would fail for configurable durations.

## Decision 5: Preserve the fishing and transition ordering

- **Decision**: Do not alter fishing eligibility or the deadline ordering: when rest expires, the next wave starts once, active fishing is cancelled, and no simultaneous fishing reward is granted.
- **Rationale**: The requested change is visual/configuration-focused and the existing rule is explicitly covered by the feature specification.
- **Alternatives considered**: Pausing the WormTimer while fishing was rejected because rest continues independent of input; awarding a catch at the boundary was rejected by the clarified deadline rule.
