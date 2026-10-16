"""Small immutable geometry values used by the game simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Vector2:
    """A two-dimensional point, direction, or displacement."""

    x: float
    y: float

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self) -> float:
        return (self.x * self.x + self.y * self.y) ** 0.5

    def normalized(self) -> Vector2:
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)


@dataclass(frozen=True, slots=True)
class Rect:
    """An axis-aligned rectangle with exclusive right and bottom edges."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("rectangle width and height must be positive")

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Vector2:
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)

    def translate(self, displacement: Vector2) -> Rect:
        return Rect(self.x + displacement.x, self.y + displacement.y, self.width, self.height)

    def contains(self, other: Rect) -> bool:
        return (
            self.x <= other.x
            and self.y <= other.y
            and other.right <= self.right
            and other.bottom <= self.bottom
        )

    def overlaps(self, other: Rect) -> bool:
        return (
            self.x < other.right
            and self.right > other.x
            and self.y < other.bottom
            and self.bottom > other.y
        )


@dataclass(frozen=True, slots=True)
class Polygon:
    """A simple polygon in world coordinates."""

    points: tuple[Vector2, ...]

    def __post_init__(self) -> None:
        if len(self.points) < 3:
            raise ValueError("polygon must contain at least three points")

    @property
    def bounds(self) -> Rect:
        xs = [point.x for point in self.points]
        ys = [point.y for point in self.points]
        return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def contains_point(self, point: Vector2) -> bool:
        inside = False
        previous = self.points[-1]
        for current in self.points:
            if ((current.y > point.y) != (previous.y > point.y)):
                crossing_x = (previous.x - current.x) * (point.y - current.y) / (previous.y - current.y) + current.x
                if point.x < crossing_x:
                    inside = not inside
            previous = current
        return inside

    def edges(self) -> Iterable[tuple[Vector2, Vector2]]:
        return zip(self.points, self.points[1:] + self.points[:1])


def _orientation(a: Vector2, b: Vector2, c: Vector2) -> float:
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def _on_segment(a: Vector2, b: Vector2, point: Vector2) -> bool:
    return (
        min(a.x, b.x) <= point.x <= max(a.x, b.x)
        and min(a.y, b.y) <= point.y <= max(a.y, b.y)
        and abs(_orientation(a, b, point)) < 1e-9
    )


def segments_intersect(a: Vector2, b: Vector2, c: Vector2, d: Vector2) -> bool:
    """Return whether two closed line segments intersect, including touching."""

    orientations = (_orientation(a, b, c), _orientation(a, b, d), _orientation(c, d, a), _orientation(c, d, b))
    if orientations[0] == 0 and _on_segment(a, b, c):
        return True
    if orientations[1] == 0 and _on_segment(a, b, d):
        return True
    if orientations[2] == 0 and _on_segment(c, d, a):
        return True
    if orientations[3] == 0 and _on_segment(c, d, b):
        return True
    return (orientations[0] > 0) != (orientations[1] > 0) and (orientations[2] > 0) != (orientations[3] > 0)


def rect_overlaps_polygon(rect: Rect, polygon: Polygon) -> bool:
    """Return exact contour/containment overlap for an axis-aligned rectangle."""

    if not rect.overlaps(polygon.bounds) and not polygon.contains_point(rect.center):
        return False
    corners = (
        Vector2(rect.x, rect.y),
        Vector2(rect.right, rect.y),
        Vector2(rect.right, rect.bottom),
        Vector2(rect.x, rect.bottom),
    )
    if any(polygon.contains_point(corner) for corner in corners):
        return True
    rectangle_edges = tuple(zip(corners, corners[1:] + corners[:1]))
    return any(segments_intersect(a, b, c, d) for a, b in rectangle_edges for c, d in polygon.edges())
