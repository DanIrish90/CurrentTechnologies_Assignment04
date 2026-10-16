from __future__ import annotations

from game.geometry import Polygon, Rect, Vector2
from game.input_state import InputState
from game.movement import move_player
from game.world import Obstacle, Player, World


def blocked_world() -> World:
    return World(
        bounds=Rect(0, 0, 240, 140),
        obstacles=(Obstacle("wall", Rect(80, 20, 20, 100)),),
        spawn_position=Vector2(20, 50),
    )


def test_player_stops_at_obstacle_boundary() -> None:
    player = Player(Vector2(20, 50), Vector2(20, 20), 100)
    moved = move_player(player, blocked_world(), InputState(right=True), 2)
    assert moved.bounds.right <= 80


def test_player_slides_along_unblocked_axis() -> None:
    player = Player(Vector2(20, 20), Vector2(20, 20), 100)
    moved = move_player(
        player, blocked_world(), InputState(right=True, down=True), 1.0
    )
    assert moved.position.x < 60
    assert moved.position.y > player.position.y


def test_large_displacement_cannot_tunnel_through_obstacle() -> None:
    player = Player(Vector2(20, 50), Vector2(20, 20), 1000)
    moved = move_player(player, blocked_world(), InputState(right=True), 10)
    assert moved.bounds.right <= 80


def test_player_stays_inside_world_bounds() -> None:
    world = blocked_world()
    player = Player(Vector2(10, 10), Vector2(20, 20), 100)
    moved = move_player(player, world, InputState(left=True, up=True), 10)
    assert world.bounds.contains(moved.bounds)


def test_player_is_blocked_by_authored_polygon_contour() -> None:
    polygon = Polygon((Vector2(80, 20), Vector2(120, 20), Vector2(100, 70)))
    world = World(Rect(0, 0, 240, 140), (), Vector2(20, 40), collision_polygons=(polygon,))
    player = Player(Vector2(60, 35), Vector2(20, 20), 100)
    moved = move_player(player, world, InputState(right=True), 1.0)
    assert world.is_valid_player_position(moved)
    assert moved.position.x == player.position.x


def test_corrected_player_body_still_slides_through_open_space() -> None:
    world = blocked_world()
    player = Player(Vector2(20, 20), Vector2(8, 10), 100)
    moved = move_player(player, world, InputState(right=True, down=True), 1.0)
    assert moved.position.y > player.position.y
    assert moved.bounds.right <= world.obstacles[0].bounds.x
