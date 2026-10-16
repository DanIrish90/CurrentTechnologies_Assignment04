from __future__ import annotations

import math

import pytest

from game.geometry import Vector2
from game.zoom import logical_viewport, validate_zoom_multiplier


def test_zoom_accepts_reference_fractional_and_boundary_values() -> None:
    assert validate_zoom_multiplier(0.5) == 0.5
    assert validate_zoom_multiplier(1.0) == 1.0
    assert validate_zoom_multiplier(1.25) == 1.25
    assert validate_zoom_multiplier(4.0) == 4.0


@pytest.mark.parametrize("value", [0, -1, 4.01, math.inf, math.nan, "2", True])
def test_zoom_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError):
        validate_zoom_multiplier(value)


def test_logical_viewport_scales_display_dimensions() -> None:
    assert logical_viewport(Vector2(960, 640), 2.0) == Vector2(480, 320)
    assert logical_viewport(Vector2(960, 640), 1.25) == Vector2(768, 512)


def test_logical_viewport_stays_positive_for_supported_zoom() -> None:
    assert logical_viewport(Vector2(1, 1), 4.0) == Vector2(1, 1)


@pytest.mark.parametrize("display_size", [Vector2(0, 640), Vector2(960, 0), Vector2(-1, 640)])
def test_logical_viewport_rejects_non_positive_display_size(display_size: Vector2) -> None:
    with pytest.raises(ValueError):
        logical_viewport(display_size, 1.0)
