# Feature Specification: Tiled World Integration

**Feature Branch**: `008-tiled-world-integration`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement the game world from World.tmj, including direct polygon collision support, collision rectangles, servant spawn and document drop-off zones, player spawn, and the NPC/player draw-order placeholders."

## Clarifications

### Session 2026-10-16

- Q: Soll die Spielerkollision mit Polygonen exakt anhand der Polygonkontur erfolgen, oder genügt zunächst eine konservative Bounding-Box-Kollision? → A: Exakte Kollision zwischen der 32×32-Spielerbox und der Polygonkontur.
- Q: Sollen `NPCDrawOrder` und `PlayerDrawOrder` eine dynamische Y-Sortierung der Figuren unterstützen, oder ausschließlich eine feste Reihenfolge zwischen NPCs und Spieler vorgeben? → A: Dynamische Y-Sortierung der Actors nach Fußposition innerhalb der authored Layer-Anker.
- Q: Sollen Civil Servants selbst als physische Hindernisse gelten, oder soll der Spieler durch sie hindurchlaufen und nur mit den Drop-off-Zonen interagieren? → A: Civil Servants sind nicht-solid; nur Drop-off-Zonen steuern die Dokumentabgabe.
- Q: Wie sollen Tiles behandelt werden, die in Tiled gedreht oder anderweitig transformiert wurden? → A: Jede authored Tiled-Tile-Transformation, insbesondere Rotation und Spiegelung, muss beim Rendern übernommen werden, sodass die Darstellung im Spiel der Ausrichtung in Tiled entspricht.
- Q: Wie muss die Transformationslogik gegen die aktuell falschen 180°-Ausrichtungen abgesichert werden? → A: Jede Kombination der in Tiled gespeicherten Transformationsflags muss die exakte authored Orientierung reproduzieren; eine diagonale Transformation darf nicht pauschal als alleinige 90°-Rotation behandelt werden, und kein Tile darf als Seiteneffekt 180° verdreht werden.
- Q: Welches Mapping soll für die Tiled-Transformationsflags verbindlich gelten? → A: Das offizielle Tiled-Mapping für orthogonale Maps: zuerst den diagonalen Flip ausführen, der die untere linke und obere rechte Ecke vertauscht beziehungsweise die X/Y-Achsen spiegelt, danach den horizontalen und den vertikalen Flip in dieser Reihenfolge anwenden; anschließend alle vier hohen GID-Flagbits vor der Tile-ID-Auflösung entfernen.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate the Tiled World (Priority: P1)

As a player, I want to move through the authored Tiled world so that the visible environment, walkable space, and obstacles match the designed map.

**Why this priority**: The world is the foundation for every other interaction and must replace the current abstract or hard-coded world layout.

**Independent Test**: Start the game, verify the map is visible at its authored dimensions, and move the player toward every representative solid area. The player remains inside the world and cannot pass through solid geometry while open-axis movement remains possible.

**Acceptance Scenarios**:

1. **Given** the map is loaded, **When** the game starts, **Then** the world is 60×34 tiles at 32×32 pixels per tile and the rendered world covers 1920×1088 pixels.
2. **Given** the player is in walkable terrain, **When** the player moves against a rectangular collision, **Then** the player is blocked by that collision and can continue moving along an unblocked axis.
3. **Given** the player approaches one of the authored polygon regions, **When** the player attempts to cross its boundary, **Then** the player is blocked by the polygon and cannot tunnel through it during a single movement update.
4. **Given** the player is outside the map boundary, **When** movement is resolved, **Then** the player remains within the authored world bounds.
5. **Given** a visible map layer or tile object contains a Tiled rotation or other tile transformation, **When** the world is rendered, **Then** the tile appears with the same authored orientation as in Tiled.

### User Story 2 - Process Documents at Authored Locations (Priority: P1)

As a player, I want to collect documents at the authored pickup locations and deliver them at the correct drop-off location so that bureaucratic progression follows the world design.

**Why this priority**: Document processing is the central gameplay loop and must use the map's explicit interaction zones rather than proximity to a servant sprite alone.

**Independent Test**: Start a wave, collect a document, enter the matching drop-off zone, and complete the handover. Repeat the test while standing in a non-matching drop-off zone and verify that the handover is rejected without corrupting progress.

**Acceptance Scenarios**:

1. **Given** the player is within an active `DocumentPickupZones` rectangle and has the required interaction state, **When** the player interacts, **Then** the document is acquired from that zone.
2. **Given** the player carries a document for servant ID N and enters `DocumentDropOffZones` with servant ID N, **When** the player interacts, **Then** the document is delivered and the corresponding servant's progress is updated.
3. **Given** the player carries a document for servant ID N and enters a drop-off zone for servant ID M where M differs from N, **When** the player interacts, **Then** the handover is rejected and the valid document/progression state remains unchanged.
4. **Given** a drop-off zone is used, **When** the player is inside the zone, **Then** the zone is physically reachable and is not blocked by the adjacent solid collision geometry.

### User Story 3 - Spawn Actors and Preserve Readable Layering (Priority: P2)

As a player, I want the player and civil servants to appear at the authored positions and render in a consistent top-down order so that the world remains readable.

**Why this priority**: Correct actor placement and layering make the authored environment usable and prevent characters from appearing behind or in front of the wrong world elements.

**Independent Test**: Start the game and verify the player starts at `PlayerSpawn`, each servant ID uses its matching point in `CivilServantSpawnPoints`, and the actor ordering follows the `NPCDrawOrder` and `PlayerDrawOrder` placeholders.

**Acceptance Scenarios**:

1. **Given** the map contains four servant spawn points with IDs 1–4, **When** a wave activates servant ID N, **Then** that servant uses the spawn point with `servant_id` N.
2. **Given** the map contains a `PlayerSpawn` point, **When** a new game starts, **Then** the player's collision bounds are placed at that point and remain valid and walkable.
3. **Given** NPC and player draw-order placeholders are present, **When** actors are rendered, **Then** actors are dynamically sorted by their foot position within the authored placeholder order while world foreground layers retain their intended masking behavior.
4. **Given** the map contains no valid spawn point for a requested servant ID, **When** the world is loaded, **Then** loading fails with a clear validation error rather than silently selecting an unrelated point.
5. **Given** the player walks through a civil servant, **When** no solid world geometry is intersected, **Then** movement is not blocked by the civil servant sprite.

### User Story 4 - Use the Fishing Zone as a Gameplay Trigger (Priority: P3)

As a player, I want the authored fishing zone to remain usable so that the world layout supports stamina recovery.

**Why this priority**: Fishing is an existing survival system and must continue to be connected to the new world data.

**Independent Test**: Move into `FishingZone`, verify fishing and stamina recovery are available there, and move outside the rectangle to verify the zone is no longer active.

**Acceptance Scenarios**:

1. **Given** the player intersects the authored `FishingZone`, **When** fishing is initiated, **Then** the existing fishing interaction can start.
2. **Given** the player is outside the authored fishing rectangle, **When** fishing is initiated, **Then** the fishing interaction is not available.
3. **Given** the fishing zone has `stamina_regeneration=true`, **When** fishing succeeds, **Then** the existing stamina recovery rules are applied without exceeding the stamina maximum.

### Edge Cases

- Polygon collision objects have `width=0` and `height=0` because their geometry is stored in a `polygon` field; they MUST be treated as valid collision geometry, not discarded as empty objects.
- Rectangle collision objects with non-positive width or height and no polygon geometry MUST be ignored.
- Polygon vertices are local to the Tiled object's `x/y` origin and may contain negative local coordinates; collision evaluation MUST use their translated world coordinates.
- A polygon or rectangle that lies outside the 1920×1088 map bounds MUST cause map validation to fail with an actionable error.
- Duplicate or missing `servant_id` values between servant spawn points and drop-off zones MUST cause map validation to fail.
- Drop-off zones must remain reachable with the existing player collision bounds, including the narrowest authored zone.
- Missing, duplicated, or invalid `PlayerSpawn` data MUST prevent a new game from starting with a clear error.
- Empty draw-order placeholder layers MUST not be rendered as visible map content and MUST not alter collision or interaction behavior.
- Every authored tile rotation or other Tiled tile transformation MUST remain visible in the rendered world; transform flags MUST NOT be discarded during map loading or rendering.
- Transform combinations MUST follow the official Tiled orthogonal-map mapping: apply the diagonal flip first, then the horizontal flip, then the vertical flip. The diagonal flip swaps the tile's bottom-left and top-right corners (an X/Y-axis swap); it MUST NOT be implemented as an unconditional standalone 90° rotation.
- The map must not create a second, conflicting source of hard-coded obstacles, spawns, pickup zones, fishing zones, or servant positions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game MUST load the authored `World.tmj` map as the source of truth for world dimensions, visible map layers, object layers, and gameplay locations.
- **FR-002**: The game MUST render the 60×34 map using 32×32 tiles and preserve the authored layer order for background, foreground, and decorative content.
- **FR-003**: The game MUST interpret positive-size rectangle objects in the `Collision` layer with `kind=solid` and `collision_layer=world` as blocking world geometry.
- **FR-004**: The game MUST interpret every `Collision` object containing a `polygon` field as blocking polygon geometry, regardless of its `width` and `height` values.
- **FR-005**: Polygon collision MUST translate local vertices by the object's world `x/y` position and resolve the player's 32×32 collision box against the exact polygon contour.
- **FR-006**: Exact polygon and rectangle collision MUST prevent tunneling through solid geometry during a single movement update and MUST preserve movement along an unblocked axis where possible.
- **FR-007**: Collision geometry MUST be evaluated independently of rendering and MUST remain deterministic and testable without opening the Pygame window.
- **FR-008**: The game MUST load `PlayerSpawn` as the initial player location and validate it against map bounds and active collision geometry.
- **FR-009**: The game MUST load `CivilServantSpawnPoints` as point locations identified by unique integer `servant_id` properties.
- **FR-010**: The game MUST load `DocumentDropOffZones` as interaction rectangles identified by unique integer `servant_id` properties.
- **FR-011**: Each active servant MUST use the spawn point and drop-off zone with the same `servant_id`; a missing or ambiguous mapping MUST be rejected during map validation.
- **FR-012**: Document delivery MUST require the player to be within the matching drop-off zone and MUST no longer rely solely on proximity to the civil servant sprite.
- **FR-013**: Civil Servants MUST remain non-solid actors and MUST NOT be added to the world collision geometry.
- **FR-014**: The game MUST preserve `DocumentPickupZones` as document acquisition locations and MUST preserve their authored interaction properties.
- **FR-015**: The game MUST load `FishingZone` as a non-solid gameplay trigger and honor its `kind=fishing_zone` and `stamina_regeneration` properties.
- **FR-016**: `NPCDrawOrder` and `PlayerDrawOrder` MUST be recognized as non-visible draw-order placeholders and MUST provide stable ordering anchors for runtime actors.
- **FR-017**: Runtime actors MUST be dynamically sorted by their world foot position within the authored NPC/player draw-order anchors.
- **FR-018**: The game MUST keep actor rendering separate from authoritative movement, collision, document, stamina, and wave state.
- **FR-019**: The game MUST reject malformed required map data with clear validation errors rather than silently falling back to the current hard-coded world definitions.
- **FR-020**: Existing document workflow, movement, stamina, fishing, camera, wave, and restart behavior MUST remain functional after world loading is introduced.
- **FR-021**: The game MUST apply every authored Tiled tile transformation when rendering visible tile layers and tile objects according to the official Tiled global-tile-ID rules for orthogonal maps: read the horizontal, vertical, diagonal, and reserved high-bit flags; clear all four high flag bits before resolving the base tile ID; apply the diagonal flip first, followed by the horizontal flip and then the vertical flip; and preserve the resulting authored orientation without unintended 180° rotations. The diagonal flip MUST swap the tile's bottom-left and top-right corners and MUST NOT be treated as an unconditional standalone 90° rotation.

### Key Entities

- **World Map**: The authored 60×34 tile world, including visible layers and object layers, with a 1920×1088 pixel playable boundary.
- **Collision Shape**: A solid rectangle or polygon from the `Collision` layer. Polygon vertices are translated from local object coordinates into world coordinates.
- **Player Spawn**: A single point defining the player's initial world position.
- **Civil Servant Spawn Point**: A point identified by `servant_id` that defines where one civil servant is placed.
- **Civil Servant**: A non-solid actor identified by `servant_id`; it is rendered and participates in document workflow but does not create world collision.
- **Document Pickup Zone**: A rectangle where the player can acquire the current document.
- **Document Drop-off Zone**: A rectangle identified by `servant_id` where the matching document can be delivered.
- **Fishing Zone**: A non-solid rectangle that enables the existing fishing and stamina recovery interaction.
- **Draw-Order Placeholder**: An empty map layer used as an authored ordering anchor for NPC and player rendering.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a valid map, the game starts with the authored 1920×1088 world visible and the player at the authored `PlayerSpawn` in 100% of automated startup checks.
- **SC-002**: Automated geometry tests cover all four authored polygon collision objects and all positive-size rectangle collision objects, with zero cases where the player ends a movement update inside solid geometry.
- **SC-003**: The four servant spawn points and four drop-off zones produce four unique, correct `servant_id` mappings in every valid map-load test.
- **SC-004**: In acceptance tests, a matching document handover succeeds only inside its matching drop-off zone, while a mismatched-zone handover is rejected without state corruption.
- **SC-005**: The player can enter and use the authored fishing zone, and cannot activate fishing outside it, in automated interaction tests.
- **SC-006**: The complete existing test suite remains green and the game remains launchable at the target 60 FPS after world integration.
- **SC-007**: A manual traversal of representative terrain, rectangles, polygons, pickup zones, drop-off zones, spawn locations, and the fishing zone reveals no inaccessible required interaction caused by map collision.
- **SC-008**: Automated rendering checks cover all eight orthogonal horizontal/vertical/diagonal flag combinations with asymmetrical tiles plus representative authored transformed map tiles, confirming zero unintended 180° rotations and no silently dropped transform.

## Assumptions

- `World.tmj` and its referenced `WorldTileSet.tsx` remain available at their current repository paths at runtime.
- The map's coordinate system is top-left-origin with pixel coordinates, matching the existing world and camera model.
- Existing player movement uses a 32×32 logical collision box unless a later feature explicitly changes that contract.
- The initial version supports the authored orthogonal Tiled map and polygon/rectangle collision shapes; tile rotations and mirror transformations are part of the authored visual map contract, while rotated or ellipse collision objects remain out of scope unless added to the map.
- `servant_id` values are unique positive integers and are shared between servant spawn points and their corresponding drop-off zones.
- `NPCDrawOrder` and `PlayerDrawOrder` are intentionally empty marker layers; actor sorting remains a presentation concern and does not change gameplay rules.
- The current gameplay systems continue to own wave progression, document requirements, stamina rules, fishing rules, and interaction timing.
- No networking, persistence, database, or external service is required.
