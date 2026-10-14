# Research: Wave Rest Countdown

**Feature**: [005-wave-rest-countdown](./spec.md)
**Date**: 2026-10-13

## Decision 1: Reuse the existing workflow transition timer

- **Decision**: Use `WaveProgress.transition_remaining` and `advance_progress` as the single authoritative ten-second rest countdown.
- **Rationale**: The existing bureaucracy workflow already starts the timer when the final servant is served, transitions through completion feedback, clamps remaining time at zero, and creates the next wave exactly once. Reusing it avoids duplicate timers and preserves deterministic wave progression.
- **Alternatives considered**: Add a separate rest-phase timer to `GameState` (rejected because it could drift from workflow progression); use rendering time (rejected because gameplay rules must not depend on rendering).

## Decision 2: Expose a derived countdown UI snapshot

- **Decision**: Add derived rest-countdown fields to `UiSnapshot`: visibility, completed wave number, remaining seconds, and normalized progress.
- **Rationale**: The renderer should consume presentation data without owning workflow state or mutating the timer. The existing workflow phase determines whether the overlay is visible.
- **Alternatives considered**: Read `WaveProgress` directly in the renderer (rejected because it couples presentation to domain state); store a second countdown value in the renderer (rejected because it can become inconsistent).

## Decision 3: Restrict fishing to the rest phase

- **Decision**: Treat `COMPLETION_FEEDBACK` and `TRANSITIONING` as the only workflow phases eligible for casting. Block casting during `ACTIVE` waves, including inside the Fishing Pond.
- **Rationale**: The clarified UX makes the rest phase the exclusive recovery and fishing window, creating a clear separation between document work and stamina recovery.
- **Alternatives considered**: Allow fishing during active waves (rejected by clarification); disable only the Fishing Pond visually (rejected because game rules must enforce the interaction restriction).

## Decision 4: Treat wave expiry as authoritative over stale fishing state

- **Decision**: Advance workflow timing before applying fishing rewards. If the update creates the next wave, reset fishing to `IDLE` and discard any fishing outcome from that same update.
- **Rationale**: This implements the explicit deadline rule and prevents a simultaneous catch from awarding stamina after the next wave has already started.
- **Alternatives considered**: Let a stale fishing state resolve before the wave transition (rejected because it could award a reward in the next wave); pause the countdown during input (rejected because rest time must continue running).

## Decision 5: Render an upward-facing bottom-center clock

- **Decision**: Draw the arc in the upper half of a bottom-center panel, with the completed-wave number and numeric seconds inside it.
- **Rationale**: The clarified orientation makes the clock read as a bow-up semicircle and the bottom-center position keeps the playfield readable while making the transition state prominent.
- **Alternatives considered**: Full circular timer (rejected because the requested visual language is a semicircle); text-only countdown (rejected because it provides weaker spatial progress feedback).
