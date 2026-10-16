from presentation.renderer import actor_draw_order
from game import config


def test_actor_draw_order_uses_world_foot_position() -> None:
    actors = [(120.0, "player"), (80.0, "npc-1"), (100.0, "npc-2")]
    assert actor_draw_order(actors) == ("npc-1", "npc-2", "player")


def test_map_exposes_draw_order_anchors() -> None:
    from game.map_loader import load_map

    data = load_map("assets/World/World.tmj")
    assert data.draw_order_anchors == ("NPCDrawOrder", "PlayerDrawOrder")


def test_actor_scale_profile_matches_authored_world() -> None:
    assert config.ACTOR_RENDER_SCALE == 0.25
    assert (config.ACTOR_SCALED_FRAME_WIDTH, config.ACTOR_SCALED_FRAME_HEIGHT) == (21, 32)
    assert (config.PLAYER_WIDTH, config.PLAYER_HEIGHT) == (8, 10)
    assert (config.SERVANT_PRESENTATION_WIDTH, config.SERVANT_PRESENTATION_HEIGHT) == (12, 15)


def test_actor_order_is_independent_of_viewport_size() -> None:
    world_order = [(120.0, "player"), (80.0, "npc-1"), (100.0, "npc-2")]
    camera_shifted_order = [(foot_y - 240.0, actor) for foot_y, actor in world_order]
    assert actor_draw_order(world_order) == actor_draw_order(camera_shifted_order)
