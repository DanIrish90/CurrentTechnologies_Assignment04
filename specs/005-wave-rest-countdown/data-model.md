# Data Model: Wave Rest Countdown

## Existing Workflow State

The feature reuses the existing immutable `WaveProgress` state.

| Field | Type | Rules |
|---|---|---|
| `definition.wave_number` | int | Identifies the completed wave shown during rest; remains positive. |
| `phase` | `WorkflowPhase` | `ACTIVE` for normal play, `COMPLETION_FEEDBACK` immediately after completion, and `TRANSITIONING` while the rest timer advances. |
| `transition_remaining` | float | Starts at `10.0` after the final handover, decreases with elapsed simulation time, and is clamped to `0.0`. |
| `definition` | `WaveDefinition` | When the timer reaches zero, is replaced exactly once by the next wave definition. |

## Wave Rest Countdown Snapshot

Derived UI data exposed through `UiSnapshot`:

| Field | Type | Rules |
|---|---|---|
| `rest_countdown_visible` | bool | True while workflow phase is `COMPLETION_FEEDBACK` or `TRANSITIONING`; false during `ACTIVE` and the first wave before completion. |
| `rest_wave_number` | int | The completed wave number shown in the center of the overlay. |
| `rest_seconds_remaining` | float | Clamped remaining time in the range `0.0–10.0`; displayed as a readable countdown. |
| `rest_progress` | float | Normalized remaining fraction in the range `0.0–1.0`, derived from `rest_seconds_remaining / 10.0`. |

## Fishing Interaction Window

- While the rest countdown is visible, an empty-handed player inside the Fishing Pond may enter `WAITING_FOR_BITE`, `BITE_WINDOW`, or `CATCHING`.
- During `ACTIVE` wave play, cast input is rejected even inside the Fishing Pond.
- If an active fishing state exists when advancing the workflow creates the next wave, fishing is reset to `IDLE` before any reward from that update is applied.

## Invariants

- The first wave begins with no rest countdown.
- `transition_remaining` never becomes negative.
- A zero-time boundary creates at most one next wave.
- The completed wave number remains visible until the next wave is created.
- The countdown does not mutate document or servant state except through the existing wave transition.
- Fishing is eligible only during the rest countdown; wave expiry cancels fishing without fish or stamina reward.
- The countdown clock is rendered as an upward-facing semicircle in the horizontal bottom-center area of the viewport.
- Restart creates the existing initial wave-one state with no active rest countdown.
