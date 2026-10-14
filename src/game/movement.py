"""Deterministic movement and axis-aligned collision resolution."""

from __future__ import annotations

import math

from .geometry import Vector2
from .input_state import InputState
from .world import Player, World


def requested_displacement(
    input_state: InputState, speed: float, elapsed_seconds: float
) -> tuple[float, float]:
    """Return frame-rate-independent movement for one simulation update."""

    if elapsed_seconds <= 0 or speed <= 0:
        return (0, 0)
    direction = input_state.direction().normalized()
    displacement = direction * (speed * elapsed_seconds)
    return (displacement.x, displacement.y)


def move_player(player: Player, world: World, input_state: InputState, elapsed_seconds: float) -> Player:
    """Move a player without crossing world bounds or solid obstacles.

    The requested displacement is subdivided so a large update cannot tunnel through
    a thin obstacle. Each sub-step resolves horizontal and vertical movement in turn,
    allowing the player to slide along an obstacle's free axis.
    """

    dx, dy = requested_displacement(input_state, player.speed, elapsed_seconds)
    distance = max(abs(dx), abs(dy))
    step_limit = max(min(player.size.x, player.size.y) / 2, 1)
    steps = max(1, math.ceil(distance / step_limit))
    step_x = dx / steps
    step_y = dy / steps
    position = player.position

    for _ in range(steps):
        horizontal = player.at(Vector2(position.x + step_x, position.y))
        if world.is_valid_player_position(horizontal):
            position = horizontal.position
        vertical = player.at(Vector2(position.x, position.y + step_y))
        if world.is_valid_player_position(vertical):
            position = vertical.position

    return player.at(position)
