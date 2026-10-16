# Data Model: Actor Scale Correction

## ActorScaleProfile

The centralized relationship between authored world units, visual frames, and gameplay bodies.

| Field | Type | Value/constraint |
|---|---|---|
| world tile size | integer pair | `32x32`, unchanged |
| render scale | number | `0.25`, pixel-sharp |
| source frame size | integer pair | `84x128` |
| scaled frame size | integer pair | `21x32` |
| player body size | integer pair | `8x10` |
| servant presentation target | integer pair | `12x15` |

The profile is configuration data, not a second world coordinate system. Map coordinates, camera bounds, and interaction rectangles remain in existing world pixels.

## PlayerCollisionBody

The logical axis-aligned rectangle used for movement and world collision.

- Width: `8` world pixels.
- Height: `10` world pixels.
- Position: derived from the player world position and preserved through movement.
- Collision targets: solid rectangle obstacles and authored polygon contours.
- Exclusions: civil servants, pickup zones, drop-off zones, and fishing zones.

## ActorFootAnchor

The world point used to place an actor's visual frame.

- Player anchor: the bottom-center of the logical player body.
- Servant anchor: the existing authored servant world position.
- Direction/frame invariant: changing frame or direction does not change the anchor point.
- Draw-order input: the actor's world foot Y coordinate.

## ScaledActorFrame

A presentation-only image frame generated from a validated source frame.

- Player source grid: 4 columns by 3 rows of 84x128 frames.
- Servant source grid: 2 columns by 2 rows of 84x128 frames.
- Output dimensions: 21x32 per frame.
- Filtering: nearest-neighbor/no smoothing.
- Ownership: animation modules; gameplay logic never depends on surface dimensions.

## CivilServantPresentationTarget

A visual reference rectangle for a servant.

- Size: `12x15` world pixels.
- Anchor: bottom-center at the authored servant position.
- Collision participation: none; servant actors remain non-solid.
- Draw ordering: uses the servant foot Y coordinate.

## Invariants

1. Actor scaling never changes Tiled map dimensions or authored coordinates.
2. The player body is exactly `8x10` for this feature.
3. Servant targets are exactly `12x15` and are never added to collision geometry.
4. Scaled frames are exactly `21x32` and preserve their bottom-center anchor.
5. Existing document, fishing, stamina, wave, camera, and restart state transitions remain unchanged.
