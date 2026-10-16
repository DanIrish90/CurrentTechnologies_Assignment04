"""Load and validate the authored Tiled world without rendering dependencies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import config
from .geometry import Polygon, Rect, Vector2, rect_overlaps_polygon
from .world import DocumentSource, FishingPond, Obstacle, TileReference, World


class MapValidationError(ValueError):
    """Raised when required authored world data is missing or malformed."""


@dataclass(frozen=True, slots=True)
class MapData:
    world: World
    servant_spawns: dict[int, Vector2]
    dropoff_zones: dict[int, Rect]
    dropoff_properties: dict[int, dict[str, Any]]
    pickup_zones: tuple[Rect, ...]
    pickup_properties: tuple[dict[str, Any], ...]
    tile_layers: tuple[dict[str, Any], ...]
    object_layers: tuple[dict[str, Any], ...]
    render_tiles: tuple[TileReference, ...]
    draw_order_anchors: tuple[str, ...]


def _layers(data: dict[str, Any], name: str, layer_type: str | None = None) -> list[dict[str, Any]]:
    found = [layer for layer in data.get("layers", []) if layer.get("name") == name]
    if layer_type is not None:
        found = [layer for layer in found if layer.get("type") == layer_type]
    return found


def _single_layer(data: dict[str, Any], name: str, layer_type: str) -> dict[str, Any]:
    found = _layers(data, name, layer_type)
    if len(found) != 1:
        raise MapValidationError(f"expected exactly one {layer_type} layer named {name}")
    return found[0]


def _properties(obj: dict[str, Any]) -> dict[str, Any]:
    return {item["name"]: item.get("value") for item in obj.get("properties", [])}


def _rect(obj: dict[str, Any]) -> Rect:
    if obj.get("width", 0) <= 0 or obj.get("height", 0) <= 0:
        raise MapValidationError(f"object {obj.get('id')} is not a positive rectangle")
    return Rect(float(obj["x"]), float(obj["y"]), float(obj["width"]), float(obj["height"]))


def _collision_shapes(layer: dict[str, Any]) -> tuple[tuple[Obstacle, ...], tuple[Polygon, ...]]:
    rectangles: list[Obstacle] = []
    polygons: list[Polygon] = []
    for obj in layer.get("objects", []):
        props = _properties(obj)
        if props.get("kind") != "solid" or props.get("collision_layer") != "world":
            continue
        if obj.get("polygon"):
            points = tuple(Vector2(float(obj["x"]) + point["x"], float(obj["y"]) + point["y"]) for point in obj["polygon"])
            try:
                polygons.append(Polygon(points))
            except ValueError as exc:
                raise MapValidationError(f"collision polygon {obj.get('id')} is malformed") from exc
        elif obj.get("width", 0) > 0 and obj.get("height", 0) > 0:
            rectangles.append(Obstacle(f"tmj-collision-{obj['id']}", _rect(obj)))
    return tuple(rectangles), tuple(polygons)


def _tile_reference(layer_name: str, gid: int, position: Vector2) -> TileReference:
    flags = 0xF0000000
    base_gid = gid & ~flags
    return TileReference(
        layer_name=layer_name,
        raw_gid=gid,
        tile_id=base_gid,
        flip_horizontal=bool(gid & 0x80000000),
        flip_vertical=bool(gid & 0x40000000),
        flip_diagonal=bool(gid & 0x20000000),
        layer_position=position,
    )


def _render_tiles(data: dict[str, Any]) -> tuple[TileReference, ...]:
    references: list[TileReference] = []
    tile_width = int(data["tilewidth"])
    tile_height = int(data["tileheight"])
    for layer in data.get("layers", []):
        if not layer.get("visible", True):
            continue
        name = str(layer.get("name", ""))
        if layer.get("type") == "tilelayer":
            width = int(layer.get("width", data["width"]))
            for index, gid in enumerate(layer.get("data", [])):
                if not gid:
                    continue
                references.append(
                    _tile_reference(
                        name,
                        int(gid),
                        Vector2((index % width) * tile_width, (index // width) * tile_height),
                    )
                )
        elif layer.get("type") == "objectgroup":
            for obj in layer.get("objects", []):
                gid = obj.get("gid")
                if not gid:
                    continue
                references.append(
                    _tile_reference(
                        name,
                        int(gid),
                        Vector2(float(obj["x"]), float(obj["y"]) - float(obj.get("height", tile_height))),
                    )
                )
    return tuple(references)


def load_map(path: str | Path) -> MapData:
    map_path = Path(path)
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MapValidationError(f"cannot load map {map_path}: {exc}") from exc
    if (data.get("width"), data.get("height"), data.get("tilewidth"), data.get("tileheight")) != (60, 34, 32, 32):
        raise MapValidationError("map must be 60x34 tiles with 32x32 tile dimensions")
    collision_layer = _single_layer(data, "Collision", "objectgroup")
    rectangles, polygons = _collision_shapes(collision_layer)
    spawn_layer = _single_layer(data, "CivilServantSpawnPoints", "objectgroup")
    servant_spawns: dict[int, Vector2] = {}
    for obj in spawn_layer.get("objects", []):
        props = _properties(obj)
        servant_id = props.get("servant_id")
        if not isinstance(servant_id, int) or servant_id <= 0 or servant_id in servant_spawns:
            raise MapValidationError("servant spawn IDs must be unique positive integers")
        servant_spawns[servant_id] = Vector2(float(obj["x"]), float(obj["y"]))
    drop_layer = _single_layer(data, "DocumentDropOffZones", "objectgroup")
    dropoff_zones: dict[int, Rect] = {}
    dropoff_properties: dict[int, dict[str, Any]] = {}
    for obj in drop_layer.get("objects", []):
        props = _properties(obj)
        servant_id = props.get("servant_id")
        if (
            props.get("kind") != "document_dropoff"
            or not isinstance(servant_id, int)
            or servant_id <= 0
            or servant_id in dropoff_zones
        ):
            raise MapValidationError("drop-off zones require unique integer servant_id and kind=document_dropoff")
        dropoff_zones[servant_id] = _rect(obj)
        dropoff_properties[servant_id] = props
    if set(servant_spawns) != set(dropoff_zones):
        raise MapValidationError("servant spawn and drop-off servant_id sets must match")
    player_objects = _single_layer(data, "PlayerSpawn", "objectgroup").get("objects", [])
    if len(player_objects) != 1:
        raise MapValidationError("PlayerSpawn must contain exactly one point")
    player_spawn = Vector2(float(player_objects[0]["x"]), float(player_objects[0]["y"]))
    bounds = Rect(0, 0, 1920, 1088)
    fishing_objects = _single_layer(data, "FishingZone", "objectgroup").get("objects", [])
    if len(fishing_objects) != 1:
        raise MapValidationError("FishingZone must contain exactly one rectangle")
    fishing_properties = _properties(fishing_objects[0])
    if (
        fishing_properties.get("kind") != "fishing_zone"
        or fishing_properties.get("stamina_regeneration") is not True
    ):
        raise MapValidationError("FishingZone requires kind=fishing_zone and stamina_regeneration=true")
    fishing = FishingPond(
        "fishing-zone",
        _rect(fishing_objects[0]),
        stamina_regeneration=fishing_properties.get("stamina_regeneration") is True,
    )
    pickup_layer = _single_layer(data, "DocumentPickupZones", "objectgroup")
    pickup_objects = pickup_layer.get("objects", [])
    if any(_properties(obj).get("kind") != "document_pickup" for obj in pickup_objects):
        raise MapValidationError("DocumentPickupZones objects require kind=document_pickup")
    pickup_zones = tuple(_rect(obj) for obj in pickup_objects)
    pickup_properties = tuple(_properties(obj) for obj in pickup_objects)
    document_sources = tuple(
        DocumentSource(f"document-source-{index}", zone)
        for index, zone in enumerate(pickup_zones, start=1)
    )
    document_source = document_sources[0] if document_sources else None
    render_tiles = _render_tiles(data)
    world = World(
        bounds,
        rectangles,
        player_spawn,
        document_source=document_source,
        document_sources=document_sources,
        fishing_pond=fishing,
        collision_polygons=polygons, pickup_zones=pickup_zones,
        dropoff_zones=dropoff_zones, servant_spawns=servant_spawns,
        render_layers=tuple(data.get("layers", [])),
        render_tiles=render_tiles,
        tileset_image_path=str(map_path.parent / "MasterTileset.png"),
    )
    player = Rect(player_spawn.x, player_spawn.y, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
    if not bounds.contains(player) or any(player.overlaps(obstacle.bounds) for obstacle in rectangles):
        raise MapValidationError("PlayerSpawn is outside the world or inside rectangle collision")
    from .geometry import rect_overlaps_polygon
    if any(rect_overlaps_polygon(player, polygon) for polygon in polygons):
        raise MapValidationError("PlayerSpawn is inside polygon collision")
    if any(not bounds.contains(Rect(position.x, position.y, 1, 1)) for position in servant_spawns.values()):
        raise MapValidationError("CivilServantSpawnPoints must be inside world bounds")
    for servant_id, zone in dropoff_zones.items():
        if any(zone.overlaps(obstacle.bounds) for obstacle in rectangles) or any(
            rect_overlaps_polygon(zone, polygon) for polygon in polygons
        ):
            raise MapValidationError(f"drop-off zone {servant_id} overlaps solid collision")
    return MapData(
        world=world,
        servant_spawns=servant_spawns,
        dropoff_zones=dropoff_zones,
        dropoff_properties=dropoff_properties,
        pickup_zones=pickup_zones,
        pickup_properties=pickup_properties,
        tile_layers=tuple(layer for layer in data.get("layers", []) if layer.get("type") == "tilelayer"),
        object_layers=tuple(layer for layer in data.get("layers", []) if layer.get("type") == "objectgroup"),
        render_tiles=render_tiles,
        draw_order_anchors=tuple(name for name in ("NPCDrawOrder", "PlayerDrawOrder") if _layers(data, name, "tilelayer")),
    )
