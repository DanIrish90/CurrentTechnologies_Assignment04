from __future__ import annotations

import pytest

from game.geometry import Rect, Vector2


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
