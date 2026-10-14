# Data Model: Fishing Mini-Game

## FishingPhase

The explicit lifecycle of one fishing attempt:

```text
IDLE
  -- E in pond, empty-handed --> WAITING_FOR_BITE
WAITING_FOR_BITE
  -- 2.0 seconds elapsed --> BITE_WINDOW
BITE_WINDOW
  -- E before 1.0 second --> CATCHING
  -- 1.0 second elapsed --> MISSED_BITE -> IDLE
CATCHING
  -- progress reaches 100 --> CAUGHT -> IDLE + reward
  -- progress reaches 0 --> ESCAPED -> IDLE
  -- game over/conflict --> CANCELED -> IDLE
```

Terminal feedback phases (`MISSED_BITE`, `CAUGHT`, `ESCAPED`, `CANCELED`) may be represented as short-lived result data before returning to `IDLE`; they never accept a second reward.

## FishingState

An immutable state for one active or completed attempt.

| Field | Type | Rules |
|---|---|---|
| `phase` | `FishingPhase` | Determines valid input and time transitions. |
| `phase_elapsed` | float | Non-negative time spent in the current phase. |
| `catch_bar_position` | float | Bounded vertical position within the catch play range. |
| `catch_bar_height` | float | Fixed bounded size within the play bar. |
| `catch_bar_velocity` | float | Bounded vertical velocity; valid E presses apply an upward impulse and gravity changes it downward after the grace period. |
| `time_since_last_press` | float | Non-negative elapsed time since the most recent catch-bar press; reset to zero on every valid press. |
| `catch_bar_upward_impulse` | float | Centralized positive balance value applied to velocity on a valid E press. |
| `catch_bar_gravity` | float | Centralized positive downward acceleration applied after the grace period. |
| `catch_bar_max_speed` | float | Centralized absolute speed limit applied to catch-bar velocity. |
| `catch_bar_grace_seconds` | float | Centralized grace-period duration of 0.15 seconds; gravity does not change velocity during this period. |
| `fish_position` | float | Deterministic vertical fish-symbol position within the play range. |
| `fishing_progress` | float | Bounded 0–100; gains 25/s when aligned and loses 35/s otherwise. |
| `reward_awarded` | bool | Starts false and can become true only once on successful catch. |
| `feedback` | string | Explains casting, bite, catching, miss, escape, cancellation, or success. |

The fish is aligned when its symbol bounds overlap or touch the catch bar bounds. A valid E press is an edge action, not a held-key repeat.

## FishingPond

An immutable world entity replacing the former stamina recovery zone.

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique within the world. |
| `bounds` | `Rect` | Fully contained by world bounds. |
| `label` | string | Player-facing label `FISHING POND`. |

The player is eligible to cast when player bounds overlap the pond, no document is carried, the run is active, and fishing phase is `IDLE`.

## FishingOutcome

The transition result communicates whether a fish was caught and how much stamina to apply.

| Field | Type | Rules |
|---|---|---|
| `accepted` | bool | True only for a valid phase/action transition. |
| `caught` | bool | True exactly when progress reaches 100. |
| `stamina_reward` | float | 25.0 only for a caught fish, otherwise 0.0. |
| `message` | string | Readable feedback for the player. |

## GameState and UI integration

- `GameState` gains `fishing: FishingState` and applies movement pause while the fishing phase is not `IDLE`.
- `GameState` applies `FishingOutcome.stamina_reward` through the existing bounded stamina rules; it never revives a game-over run.
- `UiSnapshot` exposes fishing phase/status, bite prompt state, catch-bar position, fish position, fishing progress, and whether the catch-game overlay is visible.
- `World` exposes `fishing_pond` instead of `stamina_regen_zone`; passive regeneration is removed once fishing is active.

## Invariants

- Negative elapsed time is rejected.
- Bite acceptance requires `phase_elapsed < 1.0`; the one-second boundary misses.
- A valid catch-bar press applies an upward impulse, resets `time_since_last_press`, and starts a 0.15-second grace period.
- During the grace period, gravity does not change catch-bar velocity. Afterwards, gravity changes velocity continuously and elapsed velocity is integrated into position.
- Catch-bar position and velocity are always clamped to their defined limits, and fishing progress remains clamped to 0–100.
- A fish reward is emitted at most once per attempt and is zero for all failure/cancellation paths.
- Active fishing cannot coexist with a carried document or game-over state.
- Restart creates `IDLE` fishing state, full normal stamina, and the existing wave-one setup.
