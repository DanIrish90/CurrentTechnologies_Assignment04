# Research: Tiled World Integration

## Decision 1: Use a focused JSON map loader

**Decision**: Parse `World.tmj` with Python's standard library and convert only required Tiled structures into internal world data.

**Rationale**: The map is finite, orthogonal, and already exported as JSON. A focused loader keeps Tiled parsing out of movement, state, and rendering code and avoids a new dependency.

**Alternatives considered**:

- Parse TMJ data in the renderer: rejected because it mixes asset parsing with presentation.
- Add a full Tiled runtime library: rejected because the project needs only a small subset of the format.

## Decision 2: Support rectangle and polygon collision shapes

**Decision**: Treat positive-size rectangle objects in `Collision` as rectangles. Treat any object with a `polygon` field as valid polygon geometry, even when Tiled reports `width=0` and `height=0`. Ignore only non-positive-size objects without polygon geometry.

**Rationale**: Tiled polygon objects store geometry in local vertex arrays and can legitimately have zero bounding-box fields. The current map contains four such polygon objects.

**Alternatives considered**:

- Ignore all zero-size objects: rejected because it removes the authored polygon regions.
- Approximate every polygon with its world bounding box: rejected by the clarification because it causes false blocking.

## Decision 3: Exact overlap with deterministic movement subdivision

**Decision**: Use exact overlap checks between the axis-aligned 32×32 player rectangle and translated polygon contours. Resolve movement independently per axis and subdivide a requested displacement into bounded substeps before accepting each position.

**Rationale**: Exact static overlap can use point-in-polygon and segment-intersection tests. Bounded substeps preserve the existing movement model while preventing large updates from tunneling through polygons. The current authored map has four polygons and 37 active rectangles.

**Alternatives considered**:

- Bounding-box-only collision: rejected by clarification.
- Physics engine: rejected due to dependency and complexity.
- Full continuous collision-response solver: deferred; bounded substeps fit the existing axis-independent movement contract.

## Decision 4: Preserve authored layer order and actor anchors

**Decision**: Load visible tile/object layers in TMJ order. Treat `NPCDrawOrder` and `PlayerDrawOrder` as non-rendered anchors. Sort runtime actors by foot position within those anchors.

**Rationale**: The map separates background, foreground, clutter, and actor-order intent. Empty marker layers must not create visible content or collision.

**Alternatives considered**:

- Hard-code actor order: rejected because it ignores map-authored intent.
- Use only global Y sorting: rejected because it cannot express authored NPC/player layer boundaries.

## Decision 5: Map data replaces hard-coded world locations

**Decision**: Use TMJ data for dimensions, player spawn, servant spawnpoints, pickup/drop-off zones, fishing zone, and collision shapes. Retain existing workflow and stamina rules.

**Rationale**: Duplicate hard-coded positions would create drift between visuals and gameplay.

**Compatibility notes**:

- The authored map is 1920×1088 pixels; the runtime must not expose an unrendered 1920×1280 area.
- Civil servants remain non-solid; only `Collision` objects block movement.
- Drop-off mapping is keyed by integer `servant_id` shared by spawnpoint and zone.

## Decision 6: Decode Tiled tile transformations before rendering

**Decision**: Treat the high transform bits embedded in Tiled GIDs as part of the tile reference, decode them before resolving the tileset source rectangle, and apply the complete authored orientation to every visible tile-layer and tile-object tile. Transform handling must support horizontal and vertical mirroring, diagonal transforms, and their combinations.

**Rationale**: `World.tmj` contains transformed GIDs, including values with the Tiled horizontal, vertical, and diagonal flip flags. The current renderer extracts the base tile ID but does not reproduce the full Tiled transform semantics, so rotated map art appears unrotated or incorrectly oriented in-game. Keeping transform decoding in the presentation boundary preserves the raw map as the source of truth and leaves collision/world coordinates unchanged.

**Alternatives considered**:

- Ignore transform flags and render the base tile: rejected because the game no longer matches the authored map.
- Bake transformed PNG copies into the asset folder: rejected because it duplicates authored data and prevents map edits from propagating.
- Add a Tiled runtime dependency: rejected because the finite orthogonal map needs only a small deterministic transform decoder.

## Decision 7: Apply the official Tiled orthogonal transform order

**Decision**: Follow Tiled's documented global-tile-ID rules for orthogonal maps. Read the horizontal, vertical, diagonal, and reserved high-bit flags; clear all four high bits before resolving the base tile ID; apply the diagonal transformation first as an X/Y-axis swap that exchanges the bottom-left and top-right corners; then apply the horizontal flip and the vertical flip. The implementation should use a direct pixel-coordinate mapping (or an equivalently proven operation) and cache transformed tile surfaces by tileset, local tile ID, and flag combination.

**Rationale**: The official documentation defines the operation order, while a direct coordinate mapping removes ambiguity about the direction of a 90° rotation and prevents a diagonal flag from being mistaken for a standalone rotation. Asymmetric marker tiles make all eight combinations observable, including the combinations that previously appeared 180° wrong.

**Alternatives considered**:

- Use a hand-written table of named rotations/reflections: rejected because the direction labels are easy to invert and the previous table contradicted the official diagonal operation.
- Apply `rotate(90)` for every diagonal flag and then flip: rejected because the diagonal flag is an axis swap, not an unconditional standalone 90° rotation.
- Compare only rendered screenshots: rejected because screenshots are difficult to diagnose and do not cover every flag combination deterministically.

The reference is the [official Tiled Global Tile IDs documentation](https://doc.mapeditor.org/en/stable/reference/global-tile-ids/), especially its orthogonal/isometric rule that the diagonal flip is performed first, followed by horizontal and vertical flips.
