# Data Model: Tiled World Integration

## World Map

Represents the loaded finite map and authored gameplay data.

| Field | Type | Rules |
|---|---|---|
| width_tiles | integer | 60 for the authored map |
| height_tiles | integer | 34 for the authored map |
| tile_width | integer | 32 |
| tile_height | integer | 32 |
| bounds | rectangle | 1920×1088 pixels |
| render_layers | ordered collection | Preserves visible TMJ layer order |
| collision_shapes | collection | Valid rectangle and polygon solids |
| player_spawn | point | Exactly one valid `PlayerSpawn` point |
| servant_spawns | map<int, point> | Unique positive `servant_id` keys |
| dropoff_zones | map<int, rectangle> | Matching `servant_id` keys |
| pickup_zones | collection | Non-solid document rectangles |
| fishing_zone | rectangle + properties | Non-solid fishing/stamina zone |
| draw_order_anchors | ordered anchors | `NPCDrawOrder` and `PlayerDrawOrder` |

## Collision Shape

### Rectangle Collision

- Source: `Collision` object with positive width and height.
- Required properties: `kind=solid`, `collision_layer=world`.
- Coordinates: Tiled object `x/y` plus width/height in world pixels.
- Objects with non-positive dimensions and no polygon field are ignored.

### Polygon Collision

- Source: `Collision` object containing `polygon`.
- Valid regardless of exported width/height values.
- Vertices are translated by the object's `x/y` origin.
- Exact overlap is evaluated against the player's axis-aligned collision rectangle.
- Vertices may have negative local coordinates.
- The translated polygon must lie within world bounds.

## Player Spawn

- Source: `PlayerSpawn`, exactly one Tiled point.
- Runtime meaning: top-left position of the player's 32×32 collision box.
- Validation: inside world bounds and outside every active collision shape.

## Civil Servant Spawn Point

- Source: `CivilServantSpawnPoints`, Tiled point.
- Identity: unique positive integer `servant_id`.
- Runtime meaning: servant actor foot anchor.
- Collision: non-solid.

## Document Drop-off Zone

- Source: `DocumentDropOffZones`, rectangle.
- Required properties: `kind=document_dropoff`, unique positive integer `servant_id`.
- Relationship: one zone matches each servant spawn ID.
- Interaction: matching documents can be delivered only while the player intersects the zone.
- Validation: inside world bounds and reachable without overlapping solid geometry.

## Document Pickup Zone

- Source: `DocumentPickupZones`, rectangle.
- Required property: `kind=document_pickup`.
- Optional property: `interaction_radius` is preserved.
- Collision: non-solid.

## Fishing Zone

- Source: `FishingZone`, rectangle.
- Required properties: `kind=fishing_zone`, `stamina_regeneration=true`.
- Collision: non-solid.

## Draw-Order Anchor

- Sources: `NPCDrawOrder` and `PlayerDrawOrder`.
- Shape: empty tile layers.
- Runtime meaning: non-visible ordering anchors for actor rendering.
- Actors are sorted by world foot position within the anchor relationship.

## Relationships

```text
WorldMap
├── PlayerSpawn -> Player
├── servant_spawns[servant_id] -> CivilServant
├── dropoff_zones[servant_id] -> Document destination
├── pickup_zones -> Document acquisition
├── fishing_zone -> Fishing/Stamina trigger
├── collision_shapes -> Movement blocking
└── draw_order_anchors -> Actor rendering order
```

## Validation Rules

1. Dimensions and tile size must match the authored world contract.
2. Required layers must exist with expected types.
3. Exactly one valid player spawn must exist.
4. Spawnpoint and drop-off `servant_id` sets must match exactly.
5. Collision polygons are valid even when width and height are zero.
6. Empty non-polygon collision objects are ignored; positive-size rectangles are loaded.
7. Active geometry and interaction zones must lie within 1920×1088.
8. Player spawn and required drop-off zones must not be blocked by solid geometry.
