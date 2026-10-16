# Data Model: Animated Bureaucrats

This feature adds presentation data only. `CivilServant`, `WaveProgress`, and `GameState` remain authoritative and unchanged.

## BureaucratFrameSet

The loaded runtime representation of `assets/NPC/Bureaucrat/Bureaucrat-Sheet.png`.

- Source size: 168 × 256 pixels
- Grid: 2 columns × 2 rows
- Frame size: 84 × 128 pixels
- Row 0: Idle frames, columns 0 and 1
- Row 1: Permit frames, columns 0 and 1
- Both rows contain exactly two ordered frames.

Validation rules:

- Reject a source with dimensions other than 168 × 256 pixels.
- Extract exactly four independent frame surfaces.
- Frame indexes must wrap within 0–1.

## BureaucratAnimationKind

The active presentation animation selected from the current domain state:

| Value | Source row | Selected when |
|---|---:|---|
| `IDLE` | 0 | `CivilServant.served is False` |
| `PERMIT` | 1 | `CivilServant.served is True` |

No other animation kinds are in scope.

## BureaucratAnimationState

One mutable presentation state per active `CivilServant.id`.

| Field | Type | Rule |
|---|---|---|
| `kind` | `IDLE` or `PERMIT` | Must match the current `served` value |
| `frame_index` | integer | Always 0 or 1; loops cyclically |
| `elapsed` | non-negative float | Accumulates time until the next frame |
| `frame_duration` | positive float | Defaults to 1/3 second, equivalent to 3 FPS |

State transitions:

```text
served=False + new servant  -> IDLE frame 0
served=False + elapsed time -> IDLE frame 0/1 loop
served=True  + state change -> PERMIT frame 0
served=True  + elapsed time -> PERMIT frame 0/1 loop
served=False after PERMIT  -> IDLE frame 0
```

States for IDs no longer present in the active wave are removed from the presentation mapping. This prevents stale state from leaking into later waves.

## Bureaucrat Sprite Placement

The existing servant target rectangle remains the logical interaction footprint. The visual frame is placed in screen coordinates using that rectangle’s center-bottom anchor:

- horizontal center equals the existing servant target center;
- sprite bottom equals the existing servant target bottom;
- sprite dimensions do not alter distance checks or interaction range.
