"""Structured world, player, and obstacle definitions for the first slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import config
from .geometry import Polygon, Rect, Vector2, rect_overlaps_polygon


@dataclass(frozen=True, slots=True)
class Player:
    position: Vector2
    size: Vector2
    speed: float

    def __post_init__(self) -> None:
        if self.size.x <= 0 or self.size.y <= 0:
            raise ValueError("player dimensions must be positive")
        if self.speed <= 0:
            raise ValueError("player speed must be positive")

    @property
    def bounds(self) -> Rect:
        return Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    @property
    def center(self) -> Vector2:
        return self.bounds.center

    def at(self, position: Vector2) -> Player:
        return Player(position=position, size=self.size, speed=self.speed)


@dataclass(frozen=True, slots=True)
class Obstacle:
    id: str
    bounds: Rect
    label: str = "Solid obstacle"


@dataclass(frozen=True, slots=True)
class DocumentSource:
    id: str
    bounds: Rect
    label: str = "Central document source"


@dataclass(frozen=True, slots=True)
class FishingPond:
    id: str
    bounds: Rect
    label: str = "FISHING POND"
    stamina_regeneration: bool = False


@dataclass(frozen=True, slots=True)
class TileReference:
    """A pre-parsed tile reference preserving Tiled's authored transform flags."""

    layer_name: str
    raw_gid: int
    tile_id: int
    flip_horizontal: bool
    flip_vertical: bool
    flip_diagonal: bool
    layer_position: Vector2


@dataclass(frozen=True, slots=True)
class World:
    bounds: Rect
    obstacles: tuple[Obstacle, ...]
    spawn_position: Vector2
    document_source: DocumentSource | None = None
    document_sources: tuple[DocumentSource, ...] = ()
    fishing_pond: FishingPond | None = None
    collision_polygons: tuple[Polygon, ...] = ()
    pickup_zones: tuple[Rect, ...] = ()
    dropoff_zones: dict[int, Rect] | None = None
    servant_spawns: dict[int, Vector2] | None = None
    render_layers: tuple[dict[str, Any], ...] = ()
    render_tiles: tuple[TileReference, ...] = ()
    tileset_image_path: str | None = None

    def __post_init__(self) -> None:
        ids = [obstacle.id for obstacle in self.obstacles]
        if len(ids) != len(set(ids)):
            raise ValueError("obstacle identifiers must be unique")
        if any(not self.bounds.contains(obstacle.bounds) for obstacle in self.obstacles):
            raise ValueError("obstacles must be fully contained by the world")
        if self.document_source is not None and not self.bounds.contains(self.document_source.bounds):
            raise ValueError("document source must be fully contained by the world")
        if any(not self.bounds.contains(source.bounds) for source in self.document_sources):
            raise ValueError("document pickup sources must be fully contained by the world")
        if self.fishing_pond is not None and not self.bounds.contains(self.fishing_pond.bounds):
            raise ValueError("fishing pond must be fully contained by the world")
        if any(not self.bounds.contains(polygon.bounds) for polygon in self.collision_polygons):
            raise ValueError("collision polygons must be fully contained by the world")
        for zone in self.pickup_zones:
            if not self.bounds.contains(zone):
                raise ValueError("document pickup zones must be fully contained by the world")
        for zone in (self.dropoff_zones or {}).values():
            if not self.bounds.contains(zone):
                raise ValueError("document drop-off zones must be fully contained by the world")

    def is_valid_player_position(self, player: Player, position: Vector2 | None = None) -> bool:
        candidate = player.at(position) if position is not None else player
        return (
            self.bounds.contains(candidate.bounds)
            and not any(candidate.bounds.overlaps(obstacle.bounds) for obstacle in self.obstacles)
            and not any(rect_overlaps_polygon(candidate.bounds, polygon) for polygon in self.collision_polygons)
        )


def create_initial_world() -> World:
    from .map_loader import load_map

    return load_map(config.WORLD_MAP_PATH).world


def create_fallback_world() -> World:
    """Create the legacy test world when a caller explicitly needs a fixture."""

    bounds = Rect(0, 0, config.WORLD_WIDTH, config.WORLD_HEIGHT)
    obstacles = (
        Obstacle("filing-cabinet", Rect(500, 250, 220, 120), "Filing cabinet"),
        Obstacle("waiting-bench", Rect(1050, 720, 300, 80), "Waiting bench"),
        Obstacle("government-desk", Rect(1400, 300, 180, 240), "Government desk"),
    )
    source = DocumentSource("central-document-source", Rect(220, 120, 96, 72))
    fishing_pond = FishingPond("fishing-pond", Rect(80, 820, 260, 150))
    return World(
        bounds=bounds,
        obstacles=obstacles,
        spawn_position=Vector2(120, 120),
        document_source=source,
        fishing_pond=fishing_pond,
    )


def civil_servant_positions(count: int) -> tuple[Vector2, ...]:
    if count <= 0:
        raise ValueError("civil servant count must be positive")
    return tuple(
        Vector2(850 + index * 220, 170 + (index % 2) * 220)
        for index in range(count)
    )


def create_initial_player(world: World) -> Player:
    player = Player(
        position=world.spawn_position,
        size=Vector2(config.PLAYER_WIDTH, config.PLAYER_HEIGHT),
        speed=config.PLAYER_SPEED,
    )
    if not world.is_valid_player_position(player):
        raise ValueError("initial player spawn is invalid")
    return player
