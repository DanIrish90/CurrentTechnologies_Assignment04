from __future__ import annotations

import pytest

from game.geometry import Rect, Vector2
from game.geometry import Polygon, rect_overlaps_polygon


def test_rectangle_overlaps_exact_polygon_contour() -> None:
    polygon = Polygon((Vector2(10, 10), Vector2(50, 10), Vector2(30, 40)))
    assert rect_overlaps_polygon(Rect(25, 20, 8, 8), polygon)
    assert not rect_overlaps_polygon(Rect(60, 60, 8, 8), polygon)


def test_polygon_supports_negative_local_coordinates_after_translation() -> None:
    polygon = Polygon((Vector2(-10, -10), Vector2(10, -10), Vector2(0, 10)))
    translated = Polygon(tuple(Vector2(point.x + 100, point.y + 100) for point in polygon.points))
    assert rect_overlaps_polygon(Rect(95, 95, 10, 10), translated)


def test_vector_and_rect_reject_non_positive_sizes() -> None:
    with pytest.raises(ValueError):
        Rect(0, 0, 0, 10)
    assert Vector2(0, 0) == Vector2(0, 0)


def test_rect_translation_and_center() -> None:
    rect = Rect(10, 20, 30, 40)
    assert rect.center == Vector2(25, 40)
    assert rect.translate(Vector2(5, -10)) == Rect(15, 10, 30, 40)


def test_rect_containment_and_exclusive_edge_overlap() -> None:
    outer = Rect(0, 0, 100, 100)
    touching = Rect(100, 10, 20, 20)
    inside = Rect(10, 10, 20, 20)
    assert outer.contains(inside)
    assert not outer.overlaps(touching)
    assert not touching.overlaps(outer)


def test_rect_overlap_is_symmetric() -> None:
    left = Rect(0, 0, 20, 20)
    right = Rect(10, 10, 20, 20)
    assert left.overlaps(right)
    assert right.overlaps(left)
