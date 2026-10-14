# Data Model: Stamina Usage and Recovery

## StaminaState

Represents the player's bounded stamina and the result of the latest update.

| Field | Type | Rules |
|---|---|---|
| `current` | float | Always between `0` and `maximum`; starts at `maximum`. |
| `maximum` | float | `100.0` for the initial balance; greater than zero. |
| `drain_rate` | float | `5.0` stamina points per elapsed second while carrying. |
| `regen_rate` | float | `10.0` stamina points per elapsed second while eligible in the zone. |
| `game_over` | bool | Becomes true exactly when current stamina reaches zero. |

### State transitions

```text
ACTIVE + carrying document       -- elapsed time --> ACTIVE with current - 5 * dt
ACTIVE + empty in recovery zone  -- elapsed time --> ACTIVE with current + 10 * dt
ACTIVE + empty outside zone      -- elapsed time --> ACTIVE with unchanged current
ACTIVE + current <= 0             -----------------> GAME_OVER / exhausted
GAME_OVER                         -- Restart click -> fresh initial ACTIVE state
```

Carrying a document has precedence over recovery-zone membership. Every transition clamps the value to `[0, maximum]`; game over freezes further stamina changes until restart.

## StaminaRegenZone

An immutable world entity that marks where empty-handed players recover.

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique within the world. |
| `bounds` | `Rect` | Must be fully contained by world bounds. |
| `label` | string | Human-readable label, e.g. `STAMINA REGEN ZONE`. |

Eligibility is true when the player's bounds overlap the zone bounds and the player carries no document. The initial world contains exactly one zone.

## GameState additions

The existing immutable `GameState` gains:

- `stamina: StaminaState` — authoritative stamina state.
- `game_over: bool` or equivalent explicit runtime mode — terminal active-run state, independent from the existing `running` quit flag.
- `restart_requested` is represented as a one-frame input action rather than persistent gameplay state.

The existing `workflow.carried_document` remains the source of truth for whether the player is carrying a document; no duplicate carried-document field is introduced.

## UiSnapshot additions

The existing presentation snapshot exposes:

- current and maximum stamina text;
- a stamina status message (`STABLE`, `CARRYING`, `RECOVERING`, or `EXHAUSTED`);
- whether the recovery zone is currently active/eligible;
- game-over message and Restart-button presentation state.

The snapshot remains derived from authoritative state and does not mutate game logic.

## Validation and invariants

- Reject negative elapsed time using the existing state-update convention.
- Reject invalid stamina construction such as non-positive maximum or negative rates.
- Clamp fractional elapsed-time updates without rounding away partial progress.
- Never allow negative stamina, values above maximum, repeated game-over transitions, or workflow mutation after game over.
- Restart must rebuild the normal initial world, player, camera, wave-one workflow, and full stamina.
