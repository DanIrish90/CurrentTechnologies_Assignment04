# Feature Specification: Actor Scale Correction

**Feature Branch**: `009-actor-scale-correction`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Reduce player and civil-servant visual and collision scale to match the 32x32 Tiled world while preserving foot anchoring, gameplay interactions, and map coordinates."

## Clarifications

### Session 2026-10-16

- Q: Welche logische Kollisionsbox soll der Spieler nach der Skalierung erhalten? → A: Der zunächst festgelegte Zielwert wurde durch die zusätzliche Halbierung in Q4 ersetzt; die finale Größe ist dort festgehalten.
- Q: Welche Zielgröße soll für die sichtbare Civil-Servant-Darstellung verwendet werden? → A: Der zunächst festgelegte Zielwert wurde durch die zusätzliche Halbierung in Q4 ersetzt; die finale Größe ist dort festgehalten.
- Q: Soll die Halbierung der Pixel-Art mit harter, pixelgenauer Darstellung ohne Glättung erfolgen? → A: Ja; die Skalierung bewahrt klare Pixelkanten und die bestehende Pixel-Art-Optik.
- Q: Soll die zusätzliche Halbierung auch auf die logischen Größen angewendet werden? → A: Ja; Frames werden `21×32`, die Playerbox `8×10` und die Servant-Referenz `12×15`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See Actors at World Scale (Priority: P1)

As a player, I want the player character and civil servants to have a size that fits the authored world tiles so that rooms, paths, furniture, and characters are visually readable.

**Why this priority**: The current actors still appear approximately twice as large as intended after the first correction and make the playable space look incorrectly scaled.

**Independent Test**: Start the game in the authored world and compare the character and servant silhouettes against nearby 32x32 tiles; both actor types must occupy the intended quarter-scale presentation relative to the original source frames without changing the map layout.

**Acceptance Scenarios**:

1. **Given** the authored 32x32 world is displayed, **When** the player and a civil servant are visible, **Then** neither actor appears approximately twice the intended world scale.
2. **Given** an actor is standing on terrain, **When** the actor changes animation frame or direction, **Then** its feet remain anchored to the same world position.

### User Story 2 - Use Correct Actor Collision Size (Priority: P1)

As a player, I want the movement collision body to match the corrected character scale so that narrow paths remain usable and collision does not happen far away from the visible actor.

**Why this priority**: Visual correction alone would leave movement feeling broken because the existing player collision body is also oversized.

**Independent Test**: Move the player through open terrain and against representative map obstacles; the collision body must match the corrected actor footprint and still prevent passage through solid geometry.

**Acceptance Scenarios**:

1. **Given** the player is in open terrain, **When** movement is applied, **Then** the player can use space consistent with the corrected body size.
2. **Given** the player approaches a solid rectangle or polygon, **When** movement would overlap it, **Then** movement stops at the collision boundary without tunneling.
3. **Given** the player walks through a civil servant, **When** no world collision is intersected, **Then** the civil servant does not block movement.

### User Story 3 - Preserve Gameplay Anchors (Priority: P2)

As a player, I want the scale correction to preserve map coordinates and interaction anchors so that spawning, document handling, fishing, camera behavior, and actor layering continue to work as before.

**Why this priority**: Scale correction must fix presentation and movement without silently moving gameplay locations or changing the authored world.

**Independent Test**: Start a new session, collect and deliver a document, enter the fishing zone, and observe actor ordering before and after movement; all interactions must use the existing map locations.

**Acceptance Scenarios**:

1. **Given** a new session, **When** the game starts, **Then** player and civil-servant spawn coordinates remain those authored in the world map.
2. **Given** the player enters a pickup, drop-off, or fishing zone, **When** the relevant interaction is performed, **Then** the interaction uses the existing zone and is not shifted by actor rescaling.
3. **Given** actors have different foot positions, **When** they overlap visually, **Then** they remain ordered by their world foot position.

### Edge Cases

- An animation frame has transparent padding or a different visible silhouette; its bottom/foot anchor must remain stable.
- The corrected player body approaches a rectangle or polygon at an axis or diagonal; collision must remain stable and frame-rate independent.
- A servant is visible near a player but must not become a solid obstacle as a side effect of resizing.
- A viewport or camera boundary is reached; actor scale must not alter world bounds or camera clamping.
- Existing assets are missing or have unexpected dimensions; startup must report a clear asset validation error rather than silently rendering a distorted actor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game MUST present the player character and civil servants at a consistent scale appropriate for the authored 32x32 world grid.
- **FR-002**: The game MUST apply the additional half-scale correction to the already reduced actor presentation, resulting in final character frames of exactly `21x32` from the original `84x128` source frames.
- **FR-002a**: Actor frames MUST be reduced without smoothing or blended pixels so their edges remain pixel-sharp and consistent with the authored tileset.
- **FR-003**: The player collision body MUST be a centralized `8x10` logical rectangle, anchored to the visible player's foot position and used for all movement collision checks.
- **FR-004**: The civil-servant visual footprint and presentation target rectangle MUST use a centralized `12x15` target size while civil servants remain non-solid.
- **FR-005**: Player and civil-servant visuals MUST remain anchored by their feet to their existing world positions across animation frames and facing directions.
- **FR-006**: Actor resizing MUST NOT modify the authored map dimensions, tile dimensions, spawn coordinates, collision geometry, pickup zones, drop-off zones, fishing zone, or camera world bounds.
- **FR-007**: Corrected player movement MUST continue to block against all existing solid rectangles and polygons, including large-displacement and axis-sliding behavior.
- **FR-008**: Document pickup, matching drop-off, fishing, stamina, wave progression, and restart behavior MUST remain functionally unchanged.
- **FR-009**: Actor draw ordering MUST continue to use world foot positions after resizing.
- **FR-010**: The game MUST validate actor asset dimensions and provide a clear error if an expected asset cannot be loaded or does not match its supported frame layout.
- **FR-011**: Automated tests MUST cover corrected frame dimensions, foot anchoring, player collision dimensions, servant non-solid behavior, and regression of existing gameplay interactions.

### Key Entities

- **Actor Scale Profile**: The shared visual and logical size relationship between world tiles, player presentation, servant presentation, and collision bodies.
- **Player Collision Body**: The logical footprint used for movement validation against solid world geometry.
- **Actor Foot Anchor**: The world position at which an actor's visual frame is placed, independent of transparent frame padding.
- **Civil Servant Presentation Body**: The resized visual/reference footprint for servants, which does not participate in world collision.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a rendered session, player and civil-servant frame dimensions are exactly 25% of their original 84x128 source-frame dimensions, yielding `21x32` pixel-sharp presentation frames.
- **SC-002**: The corrected player collision body measures exactly `8x10` world pixels and remains aligned with the visible player's foot position during movement.
- **SC-003**: At least 95% of actor-frame and movement-collision regression tests pass without special-case coordinate adjustments, and the complete existing test suite remains green.
- **SC-004**: Player and servant feet remain within one world pixel of their pre-rescale authored anchor positions when changing animation frame or direction.
- **SC-005**: A manual traversal confirms that the player can reach representative pickup, matching drop-off, fishing, spawn, and collision locations without scale-induced inaccessible paths.
- **SC-006**: The game maintains the existing target of 60 frames per second during normal map traversal with resized actors.

## Assumptions

- The authored world remains a 32x32 tile grid and is the source of truth for world scale.
- The source character and bureaucrat sheets remain available in their current frame layouts; this feature rescales their presentation rather than replacing the artwork.
- The final presentation is one quarter of the original source-frame dimensions because the additional half-scale correction is applied to the previous half-scale implementation.
- The player collision body is fixed at `8x10` world pixels for this feature; later tuning requires a separate gameplay decision.
- The civil-servant presentation target is fixed at `12x15` world pixels; it is a visual anchor only and does not participate in world collision.
- Actor resizing is limited to player and civil-servant presentation and logical body sizing; map geometry and interaction-zone coordinates are out of scope.
