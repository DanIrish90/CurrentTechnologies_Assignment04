"""Pure camera positioning constrained to the playable world."""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import Rect, Vector2
from .world import Player, World


@dataclass(frozen=True, slots=True)
class Camera:
    viewport_size: Vector2
    position: Vector2

    @property
    def bounds(self) -> Rect:
        return Rect(self.position.x, self.position.y, self.viewport_size.x, self.viewport_size.y)


def update_camera(player: Player, world: World, viewport_size: Vector2) -> Camera:
    """Center on the player and clamp the viewport to the world."""

    if viewport_size.x <= 0 or viewport_size.y <= 0:
        raise ValueError("viewport dimensions must be positive")
    desired_x = player.center.x - viewport_size.x / 2
    desired_y = player.center.y - viewport_size.y / 2
    max_x = max(world.bounds.width - viewport_size.x, 0)
    max_y = max(world.bounds.height - viewport_size.y, 0)
    position = Vector2(
        min(max(desired_x, world.bounds.x), world.bounds.x + max_x),
        min(max(desired_y, world.bounds.y), world.bounds.y + max_y),
    )
    return Camera(viewport_size=viewport_size, position=position)
