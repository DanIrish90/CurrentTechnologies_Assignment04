from __future__ import annotations

import pygame
import pytest

from presentation.renderer import (
    apply_tiled_transform,
    decode_tiled_gid,
)


HORIZONTAL = 0x80000000
VERTICAL = 0x40000000
DIAGONAL = 0x20000000
HEXAGONAL_120 = 0x10000000


@pytest.mark.parametrize(
    ("flags", "expected"),
    [
        (0, [[1, 2], [3, 4]]),
        (HORIZONTAL, [[2, 1], [4, 3]]),
        (VERTICAL, [[3, 4], [1, 2]]),
        (HORIZONTAL | VERTICAL, [[4, 3], [2, 1]]),
        (DIAGONAL, [[1, 3], [2, 4]]),
        (DIAGONAL | HORIZONTAL, [[3, 1], [4, 2]]),
        (DIAGONAL | VERTICAL, [[2, 4], [1, 3]]),
        (DIAGONAL | HORIZONTAL | VERTICAL, [[4, 2], [3, 1]]),
    ],
)
def test_tiled_transform_preserves_all_orthogonal_orientations(flags: int, expected: list[list[int]]) -> None:
    source = pygame.Surface((2, 2))
    for position, value in [((0, 0), 1), ((1, 0), 2), ((0, 1), 3), ((1, 1), 4)]:
        source.set_at(position, (value, 0, 0, 255))

    transformed = apply_tiled_transform(source, flags)

    assert transformed.get_size() == source.get_size()
    assert [[transformed.get_at((x, y))[0] for x in range(2)] for y in range(2)] == expected


def test_decode_tiled_gid_separates_base_id_and_flags() -> None:
    decoded = decode_tiled_gid(37 | HORIZONTAL | DIAGONAL | HEXAGONAL_120)

    assert decoded.tile_id == 37
    assert decoded.flip_horizontal
    assert not decoded.flip_vertical
    assert decoded.flip_diagonal
    assert decoded.rotated_hexagonal


def test_diagonal_transform_is_the_official_bottom_left_top_right_axis_swap() -> None:
    source = pygame.Surface((2, 2))
    for position, value in [((0, 0), 1), ((1, 0), 2), ((0, 1), 3), ((1, 1), 4)]:
        source.set_at(position, (value, 0, 0, 255))

    transformed = apply_tiled_transform(source, DIAGONAL)

    assert [[transformed.get_at((x, y))[0] for x in range(2)] for y in range(2)] == [
        [1, 3],
        [2, 4],
    ]
