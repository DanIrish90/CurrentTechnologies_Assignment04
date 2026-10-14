from __future__ import annotations

import math

from game.input_state import InputState
from game.movement import requested_displacement


def test_zero_input_stops_immediately() -> None:
    assert requested_displacement(InputState(), speed=240, elapsed_seconds=1) == (0, 0)


def test_cardinal_movement_uses_elapsed_time() -> None:
    displacement = requested_displacement(InputState(right=True), speed=240, elapsed_seconds=0.5)
    assert displacement == (120, 0)


def test_diagonal_movement_is_normalized() -> None:
    x, y = requested_displacement(
        InputState(right=True, down=True), speed=240, elapsed_seconds=1
    )
    assert math.isclose(math.hypot(x, y), 240)


def test_opposing_input_does_not_increase_speed() -> None:
    assert requested_displacement(
        InputState(left=True, right=True, down=True), speed=240, elapsed_seconds=1
    ) == (0, 240)
