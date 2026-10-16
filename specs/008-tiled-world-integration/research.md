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

**Rationale**: Exact static overlap can use point-in-polygon and segment-intersection tests. Bounded substeps preserve the existing movement model while preventing large updates from tunneling through polygons. The map has only four polygons and 29 active rectangles.

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
