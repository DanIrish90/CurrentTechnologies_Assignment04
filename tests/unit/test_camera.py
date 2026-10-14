from __future__ import annotations

from game.camera import update_camera
from game.geometry import Rect, Vector2
from game.world import Player, World


def test_camera_follows_player_and_stays_in_world() -> None:
    world = World(Rect(0, 0, 1000, 800), (), Vector2(50, 50))
    player = Player(Vector2(700, 500), Vector2(20, 20), 100)
    camera = update_camera(player, world, Vector2(400, 300))
    assert camera.bounds.width == 400
    assert world.bounds.contains(camera.bounds)
    assert camera.position == Vector2(510, 360)


def test_camera_clamps_at_world_edges() -> None:
    world = World(Rect(0, 0, 1000, 800), (), Vector2(50, 50))
    player = Player(Vector2(980, 780), Vector2(20, 20), 100)
    camera = update_camera(player, world, Vector2(400, 300))
    assert camera.position == Vector2(600, 500)
    assert world.bounds.contains(camera.bounds)


def test_camera_anchors_smaller_world_to_origin() -> None:
    world = World(Rect(0, 0, 300, 200), (), Vector2(10, 10))
    player = Player(Vector2(100, 100), Vector2(20, 20), 100)
    camera = update_camera(player, world, Vector2(400, 300))
    assert camera.position == Vector2(0, 0)
