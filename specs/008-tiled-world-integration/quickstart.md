# Quickstart: Tiled World Integration

## Prerequisites

- Python 3.12+
- Project dependencies installed from `pyproject.toml`
- Repository root as working directory
- `assets/World/World.tmj`, `WorldTileSet.tsx`, and `MasterTileset.png` present

## Automated validation

Run focused tests:

```bash
pytest tests/unit/test_geometry.py tests/unit/test_collision.py tests/unit/test_map_loader.py tests/unit/test_world.py
```

Expected result: polygon, rectangle, map parsing, spawn, zone, transform, and collision tests pass.

Run the full regression suite:

```bash
pytest
```

Expected result: movement, camera, bureaucracy, stamina, fishing, wave, UI, and smoke tests remain green.

The current authored `World.tmj` contains 37 positive-size collision rectangles and four polygon collision objects; tests must validate the loaded authored data rather than an obsolete 29-rectangle baseline.

## Map-data checks

The loader validation must confirm:

1. `World.tmj` is 60×34 tiles with 32×32 tile dimensions.
2. World bounds are 1920×1088 pixels.
3. Four servant spawnpoints and four drop-off zones exist with matching IDs 1–4.
4. `PlayerSpawn` is valid and not inside collision geometry.
5. All four polygon objects in `Collision` load despite zero width/height.
6. Positive-size collision rectangles load and empty non-polygon objects are ignored.
7. Pickup, fishing, and drop-off zones remain non-solid and inside the map.
8. `NPCDrawOrder` and `PlayerDrawOrder` remain empty, non-visible ordering anchors.
9. Transformed tile GIDs retain their Tiled flags when converted to render data; all four high flag bits are cleared only for base-tile lookup, and all eight H/V/D combinations follow the official order: diagonal axis swap first, horizontal flip second, vertical flip third.

## Manual playtest

```bash
python main.py
```

Verify:

1. The map fills a 1920×1088 world without an extra unrendered bottom region.
2. The player starts at `PlayerSpawn` and moves freely in open terrain.
3. Rectangle and all four polygon regions block movement accurately.
4. Large movement deltas cannot tunnel through a polygon and unblocked-axis sliding remains possible.
5. Civil servants appear at matching spawnpoints and do not block the player.
6. A document can be collected and delivered only inside its matching drop-off zone.
7. A mismatched drop-off zone rejects the document without corrupting workflow progress.
8. Fishing is available inside `FishingZone` and unavailable outside it.
9. NPCs and the player are Y-sorted by foot position using the draw-order anchors.
10. Tiles that are rotated, mirrored, or diagonally transformed in Tiled have the same orientation in the running game, with no unintended 180° rotation.

## Failure checks

Unit tests should cover:

- Missing required layer: clear loading error.
- Duplicate or missing `servant_id`: clear mapping error.
- Polygon or zone outside world bounds: clear geometry error.
- Empty collision object: ignored, while actual polygons remain active.
- Transformed tile GID: render the authored orientation rather than the untransformed base tile.
- Transform regression: run the asymmetric eight-combination test using the official Tiled operation order and compare representative transformed tiles from `World.tmj`.
