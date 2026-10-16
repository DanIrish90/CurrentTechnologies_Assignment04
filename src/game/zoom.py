"""Validated presentation zoom and logical viewport calculations."""

from __future__ import annotations

import math

from . import config
from .geometry import Vector2


def validate_zoom_multiplier(value: object) -> float:
    """Return a valid zoom multiplier or raise a clear configuration error."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("zoom multiplier must be a finite number")
    multiplier = float(value)
    if not math.isfinite(multiplier):
        raise ValueError("zoom multiplier must be finite")
    if not config.ZOOM_MINIMUM <= multiplier <= config.ZOOM_MAXIMUM:
        raise ValueError(
            f"zoom multiplier must be between {config.ZOOM_MINIMUM} and {config.ZOOM_MAXIMUM}"
        )
    return multiplier


def logical_viewport(display_size: Vector2, multiplier: object) -> Vector2:
    """Calculate the world-coordinate viewport for a display and zoom value."""

    zoom = validate_zoom_multiplier(multiplier)
    if display_size.x <= 0 or display_size.y <= 0:
        raise ValueError("display dimensions must be positive")
    return Vector2(
        float(max(1, round(display_size.x / zoom))),
        float(max(1, round(display_size.y / zoom))),
    )
