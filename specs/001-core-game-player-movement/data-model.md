# Data Model: Core Game Window and Player Movement

**Feature**: `001-core-game-player-movement`

The model is intentionally small. Authoritative gameplay state is plain Python data and does not depend on a display or Pygame surface.

## Coordinate and geometry conventions

- The world uses a top-left origin with increasing horizontal position to the right and increasing vertical position downward.
- World and screen coordinates use the same units for this first slice.
- Rectangles use `x`, `y`, `width`, and `height`; `x` and `y` identify the top-left corner.
- A rectangle's right and bottom edges are treated as exclusive for overlap checks, preventing edge-touching objects from counting as overlapping.

## Entities and value objects

### `Vector2`

Represents a 2D direction or displacement.

| Field | Type | Rules |
|---|---|---|
| `x` | float | May be negative, zero, or positive. |
| `y` | float | May be negative, zero, or positive. |

Behavior:

- Input vectors are normalized before movement when their length is greater than one.
- A zero vector produces no movement.

### `Rect`

Represents an axis-aligned occupied or visible area.

| Field | Type | Rules |
|---|---|---|
| `x` | float | World or screen horizontal position. |
| `y` | float | World or screen vertical position. |
| `width` | float | Must be positive. |
| `height` | float | Must be positive. |

Required operations:

- Determine overlap with another rectangle.
- Determine containment within another rectangle.
- Return center coordinates.
- Translate by a displacement without changing dimensions.

### `Player`

The controllable character and its movement configuration.

| Field | Type | Rules |
|---|---|---|
| `position` | `Vector2` | Represents the top-left of the collision bounds. |
| `size` | `Vector2` | Positive dimensions. |
| `speed` | float | Positive world units per second. |

Derived state:

- `bounds`: rectangle from `position` and `size`.
- `center`: center of `bounds` for camera targeting.

Invariants:

- The player's bounds remain inside the world bounds after each update.
- The player's bounds do not overlap a solid obstacle after each update.
- The player starts in a valid, non-overlapping position.

### `Obstacle`

A static solid object in the playable world.

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique within the world definition. |
| `bounds` | `Rect` | Positive dimensions and fully contained by the world. |
| `label` | string | Optional human-readable placeholder for debugging or UI. |

Obstacles do not move during this feature and have no gameplay state beyond their bounds.

### `World`

The bounded space containing the player and obstacles.

| Field | Type | Rules |
|---|---|---|
| `bounds` | `Rect` | Positive dimensions; at least as large as the viewport. |
| `obstacles` | sequence of `Obstacle` | Each obstacle is contained by `bounds`; obstacle bounds do not need to touch. |
| `spawn_position` | `Vector2` | Produces player bounds inside `bounds` and outside every obstacle. |

Validation rules:

- World dimensions must be positive.
- The viewport must not be larger than the world in a dimension unless the camera explicitly handles that case by anchoring to the world edge.
- Every obstacle must be fully inside the world.
- The spawn position must be valid.

### `Camera`

The visible world rectangle derived from the player and viewport.

| Field | Type | Rules |
|---|---|---|
| `viewport_size` | `Vector2` | Positive screen dimensions. |
| `position` | `Vector2` | Top-left world coordinate of the visible view. |

Update behavior:

1. Target the player's center.
2. Place the viewport center on that target.
3. Clamp the camera position to the world bounds.
4. If the world is smaller than the viewport in an axis, anchor the camera to the world start for that axis.

Invariant: the camera never displays world coordinates outside the world bounds.

### `InputState`

The input snapshot consumed by one simulation update.

| Field | Type | Rules |
|---|---|---|
| `left` | bool | True while the left movement control is active. |
| `right` | bool | True while the right movement control is active. |
| `up` | bool | True while the up movement control is active. |
| `down` | bool | True while the down movement control is active. |
| `quit_requested` | bool | True after a supported close request. |

Opposing directions cancel on the same axis. Unsupported keys do not change this state.

### `GameState`

The authoritative runtime state passed between input, simulation, and presentation.

| Field | Type | Rules |
|---|---|---|
| `world` | `World` | Fixed for this feature. |
| `player` | `Player` | Updated by movement rules. |
| `camera` | `Camera` | Recomputed or updated from player/world state. |
| `elapsed_time` | float | Non-negative simulation time. |
| `running` | bool | False after a clean close request. |

The renderer receives a read-only view/snapshot of this state; it does not authoritatively mutate player position, collision, or camera rules.

### `UiSnapshot`

Presentation-ready values for the starter UI.

| Field | Type | Rules |
|---|---|---|
| `title` | string | Identifies the game or current context. |
| `state_label` | string | Describes the initial player-state placeholder. |
| `control_hint` | string | Identifies supported movement controls. |

The snapshot is intentionally not a gameplay entity. Later features can replace the placeholder state with stamina and bureaucratic status without changing movement rules.

## State transitions

```text
Not running
  -> Running after successful window and world initialization
Running
  -> Running after each input/update/render cycle
Running
  -> Closing when a supported close request is received
Closing
  -> Not running after the window and presentation resources are released
```

Within each running update:

```text
InputState -> requested displacement -> collision-resolved Player -> clamped Camera -> UiSnapshot/render view
```

## Error and invalid-state handling

- Invalid dimensions, obstacle placement, or spawn placement should fail during world construction with a clear validation error.
- Invalid or unsupported input is ignored rather than converted into movement.
- A collision update must return a valid player position even if the requested displacement is large enough to cross an obstacle in one update.
- Window closure is a normal state transition, not an exception path.
