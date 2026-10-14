# Data Model: Animated Player Character

This feature adds presentation data only. The authoritative `Player` and `GameState` models remain unchanged.

## CharacterDirection

An enum-like presentation value describing the last valid facing direction.

| Value | Sprite row | Horizontal orientation |
|---|---:|---|
| `UP` | 0 | normal |
| `DOWN` | 1 | normal |
| `RIGHT` | 2 | mirrored |
| `LEFT` | 2 | normal |

Rules:

- `dy < 0` selects `UP` when vertical movement dominates.
- `dy > 0` selects `DOWN` when vertical movement dominates.
- `dx > 0` selects `RIGHT` when horizontal movement dominates and uses the mirrored side view.
- `dx < 0` selects `LEFT` when horizontal movement dominates and uses the original side view.
- Zero displacement preserves the previous direction.
- Equal diagonal magnitudes use a documented deterministic tie-breaker; use the vertical axis so the result is never ambiguous.

## CharacterFrameSet

The loaded runtime representation of the supplied tileset.

- Source: `assets/MainCharacter/MainCharacterWalking.png`
- Grid: 3 rows × 4 columns
- Frame dimensions: 84 × 128 pixels
- Each row contains four ordered frames, indexed 0 through 3.
- Side-facing frames may have a cached mirrored counterpart for `RIGHT`.

Validation rules:

- The source must provide exactly 336 × 384 pixels.
- Every extracted frame must have positive dimensions of exactly 84 × 128 pixels.
- Row and frame indexes must be clamped or wrapped into their valid ranges.

## CharacterAnimationState

Presentation-owned mutable state updated once per simulation/render loop.

| Field | Type | Rule |
|---|---|---|
| `direction` | `CharacterDirection` | Starts at `DOWN`; changes only on non-zero actual displacement |
| `frame_index` | integer | Always 0–3; resets to 0 when idle and advances cyclically while moving |
| `elapsed` | non-negative float | Accumulates animation time and consumes complete 0.125-second frame intervals |
| `frame_duration` | positive float | Defaults to 0.125 seconds, equivalent to 8 FPS |

The state is not serialized, placed in `GameState`, or read by gameplay systems.

## Sprite Placement

The rendered frame is anchored to the logical player rectangle:

- `sprite_rect.midbottom = player_screen_rect.midbottom`
- Collision and interaction continue using `player.bounds`.
- Camera conversion is applied to the player rectangle before the sprite anchor is calculated.
