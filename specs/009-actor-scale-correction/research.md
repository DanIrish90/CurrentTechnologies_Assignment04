# Research: Actor Scale Correction

## Decision 1: Scale frames once and keep pixel edges sharp

**Decision**: Reduce each loaded 84x128 actor frame to 21x32 once during asset preparation using nearest-neighbor behavior; do not smooth or blend pixels.

**Rationale**: The authored map uses 32x32 pixel-art tiles and the current actor frames appear approximately twice too large. One-time scaling avoids per-frame work and preserves the established pixel-art appearance.

**Alternatives considered**:

- Smooth runtime scaling: rejected because it introduces blurred edges and inconsistent pixel density.
- Separate pre-scaled asset files: rejected because it duplicates replaceable artwork and makes asset maintenance harder.
- Keep native-size frames and alter camera zoom: rejected because it would also scale the entire map and UI, changing the requested world relationship.

## Decision 2: Separate visual size from logical collision size

**Decision**: Use a centralized `8x10` player collision body and a centralized `12x15` civil-servant presentation target. Civil servants remain non-solid.

**Rationale**: Source frame dimensions include transparent padding and are not reliable gameplay bodies. A smaller explicit player body makes movement fit the world while preserving deterministic collision. Servant dimensions are visual/reference data only.

**Alternatives considered**:

- Derive collision directly from the full scaled sprite rectangle: rejected because transparent padding would cause oversized or unstable collision.
- Keep the existing or previously reduced player body: rejected because the user reports that the figures and collision bodies still require one additional halving.
- Add servant collision bodies: rejected because the authored gameplay rule is that servants are non-solid.

## Decision 3: Preserve foot anchors in world coordinates

**Decision**: Place the scaled player and servant surfaces using their `midbottom` foot anchor at the existing world position.

**Rationale**: Scaling changes the top and side extents but should not make actors float, sink, or shift when their direction or animation frame changes. World spawn points and draw-order values remain unchanged.

**Alternatives considered**:

- Center scaled sprites on the old rectangle: rejected because it changes the perceived ground contact point.
- Re-author all Tiled spawn points: rejected because the map is already the source of truth and does not need coordinate changes.

## Decision 4: Validate asset layout before scaling

**Decision**: Retain explicit frame-sheet dimension validation and ensure scaled output dimensions are deterministic.

**Rationale**: A missing or malformed sheet must fail with a useful error instead of silently producing distorted actors. This keeps launch failures diagnosable and protects the animation tests.

**Alternatives considered**:

- Accept arbitrary image sizes: rejected because frame slicing would become ambiguous.
- Silently crop or pad unexpected sheets: rejected because it hides asset mistakes and can break foot anchoring.
