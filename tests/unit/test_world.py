from __future__ import annotations

import pytest

from game.geometry import Rect, Vector2
from game.world import FishingPond, Obstacle, Player, World, create_initial_world


def test_world_rejects_outside_obstacle() -> None:
    with pytest.raises(ValueError):
        World(Rect(0, 0, 100, 100), (Obstacle("outside", Rect(90, 90, 20, 20)),), Vector2(10, 10))


def test_world_rejects_duplicate_obstacle_ids() -> None:
    obstacles = (Obstacle("same", Rect(10, 10, 10, 10)), Obstacle("same", Rect(40, 40, 10, 10)))
    with pytest.raises(ValueError):
        World(Rect(0, 0, 100, 100), obstacles, Vector2(70, 70))


def test_world_validates_spawn_against_obstacles() -> None:
    world = World(Rect(0, 0, 100, 100), (Obstacle("wall", Rect(20, 20, 30, 30)),), Vector2(25, 25))
    player = Player(Vector2(25, 25), Vector2(10, 10), 100)
    assert not world.is_valid_player_position(player)


def test_initial_world_contains_a_valid_fishing_pond() -> None:
    world = create_initial_world()
    assert world.fishing_pond is not None
    assert world.fishing_pond.label == "FISHING POND"
    assert world.bounds.contains(world.fishing_pond.bounds)


def test_world_rejects_outside_fishing_pond() -> None:
    with pytest.raises(ValueError):
        World(
            Rect(0, 0, 100, 100),
            (),
            Vector2(10, 10),
            fishing_pond=FishingPond("outside", Rect(90, 90, 20, 20)),
        )
