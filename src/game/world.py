"""Structured world, player, and obstacle definitions for the first slice."""

from __future__ import annotations

from dataclasses import dataclass

from . import config
from .geometry import Rect, Vector2


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


@dataclass(frozen=True, slots=True)
class World:
    bounds: Rect
    obstacles: tuple[Obstacle, ...]
    spawn_position: Vector2
    document_source: DocumentSource | None = None
    fishing_pond: FishingPond | None = None

    def __post_init__(self) -> None:
        ids = [obstacle.id for obstacle in self.obstacles]
        if len(ids) != len(set(ids)):
            raise ValueError("obstacle identifiers must be unique")
        if any(not self.bounds.contains(obstacle.bounds) for obstacle in self.obstacles):
            raise ValueError("obstacles must be fully contained by the world")
        if self.document_source is not None and not self.bounds.contains(self.document_source.bounds):
            raise ValueError("document source must be fully contained by the world")
        if self.fishing_pond is not None and not self.bounds.contains(self.fishing_pond.bounds):
            raise ValueError("fishing pond must be fully contained by the world")

    def is_valid_player_position(self, player: Player, position: Vector2 | None = None) -> bool:
        candidate = player.at(position) if position is not None else player
        return self.bounds.contains(candidate.bounds) and not any(
            candidate.bounds.overlaps(obstacle.bounds) for obstacle in self.obstacles
        )


def create_initial_world() -> World:
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
