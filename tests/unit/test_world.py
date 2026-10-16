from __future__ import annotations

import pytest

from game.geometry import Rect, Vector2
from game.world import FishingPond, Obstacle, Player, World, create_initial_player, create_initial_world


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


def test_initial_player_uses_corrected_logical_body() -> None:
    world = create_initial_world()
    player = create_initial_player(world)
    assert player.size == Vector2(8, 10)
    assert player.position == world.spawn_position


def test_authored_world_contains_polygon_collision() -> None:
    world = create_initial_world()
    assert len(world.collision_polygons) == 4
    assert world.bounds.height == 1088


def test_authored_servants_are_id_mapped_and_non_solid() -> None:
    world = create_initial_world()
    assert set(world.servant_spawns or {}) == {1, 2, 3, 4}
    assert set(world.dropoff_zones or {}) == {1, 2, 3, 4}
    assert all(
        not any(obstacle.bounds.contains(position) for obstacle in world.obstacles)
        for position in (world.servant_spawns or {}).values()
    )
    assert all(
        not any(obstacle.bounds.overlaps(Rect(position.x - 6, position.y - 15, 12, 15)) for obstacle in world.obstacles)
        for position in (world.servant_spawns or {}).values()
    )


def test_fishing_zone_is_non_solid_and_authored() -> None:
    world = create_initial_world()
    assert world.fishing_pond is not None
    assert world.fishing_pond.stamina_regeneration
    assert not any(obstacle.bounds.overlaps(world.fishing_pond.bounds) for obstacle in world.obstacles)


def test_fishing_zone_membership_uses_loaded_rectangle() -> None:
    world = create_initial_world()
    player = Player(world.fishing_pond.bounds.center, Vector2(32, 32), 100)
    outside = player.at(Vector2(0, 0))
    assert player.bounds.overlaps(world.fishing_pond.bounds)
    assert not outside.bounds.overlaps(world.fishing_pond.bounds)


def test_world_rejects_outside_fishing_pond() -> None:
    with pytest.raises(ValueError):
        World(
            Rect(0, 0, 100, 100),
            (),
            Vector2(10, 10),
            fishing_pond=FishingPond("outside", Rect(90, 90, 20, 20)),
        )
