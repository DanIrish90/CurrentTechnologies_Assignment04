from __future__ import annotations

import pygame
import pytest

from game.geometry import Vector2
from presentation.character_animation import (
    CharacterAnimator,
    CharacterDirection,
    character_sprite_rect,
    direction_from_displacement,
    load_character_frames,
    split_character_sheet,
)


@pytest.fixture(scope="module", autouse=True)
def pygame_display() -> None:
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


def _frames() -> tuple[pygame.Surface, ...]:
    return load_character_frames().rows[0]


def test_character_frames_are_scaled_to_world_size() -> None:
    frames = load_character_frames()
    assert len(frames.rows) == 3
    assert all(len(row) == 4 for row in frames.rows)
    assert all(frame.get_size() == (21, 32) for row in frames.rows for frame in row)


def test_split_rejects_unexpected_sheet_dimensions() -> None:
    with pytest.raises(ValueError, match="336x384"):
        split_character_sheet(pygame.Surface((32, 32), pygame.SRCALPHA))


@pytest.mark.parametrize(
    ("displacement", "expected"),
    [
        (Vector2(0, -1), CharacterDirection.UP),
        (Vector2(0, 1), CharacterDirection.DOWN),
        (Vector2(1, 0), CharacterDirection.RIGHT),
        (Vector2(-1, 0), CharacterDirection.LEFT),
        (Vector2(1, -2), CharacterDirection.UP),
        (Vector2(-2, 1), CharacterDirection.LEFT),
        (Vector2(1, 1), CharacterDirection.DOWN),
    ],
)
def test_direction_uses_dominant_axis(displacement: Vector2, expected: CharacterDirection) -> None:
    assert direction_from_displacement(displacement, CharacterDirection.RIGHT) is expected


def test_zero_displacement_preserves_previous_direction() -> None:
    assert direction_from_displacement(Vector2(0, 0), CharacterDirection.LEFT) is CharacterDirection.LEFT


def test_animation_advances_at_eight_frames_per_second_and_wraps() -> None:
    animator = CharacterAnimator(load_character_frames())
    start = Vector2(0, 0)
    end = Vector2(1, 0)
    animator.update(start, end, 0.125)
    assert animator.frame_index == 1
    animator.update(end, Vector2(2, 0), 0.375)
    assert animator.frame_index == 0
    animator.update(Vector2(2, 0), Vector2(3, 0), 10.0)
    assert 0 <= animator.frame_index < 4


def test_animation_is_independent_of_update_step_size() -> None:
    whole = CharacterAnimator(load_character_frames())
    split = CharacterAnimator(load_character_frames())
    whole.update(Vector2(0, 0), Vector2(1, 0), 0.25)
    split.update(Vector2(0, 0), Vector2(1, 0), 0.125)
    split.update(Vector2(1, 0), Vector2(2, 0), 0.125)
    assert whole.frame_index == split.frame_index
    assert whole.elapsed == pytest.approx(split.elapsed)


def test_idle_resets_to_first_frame_of_last_direction() -> None:
    animator = CharacterAnimator(load_character_frames())
    animator.update(Vector2(0, 0), Vector2(-1, 0), 0.5)
    animator.update(Vector2(-1, 0), Vector2(-1, 0), 0.0)
    assert animator.direction is CharacterDirection.LEFT
    assert animator.frame_index == 0
    assert animator.current_frame is animator.frames.rows[2][0]


def test_right_movement_uses_mirrored_side_view() -> None:
    animator = CharacterAnimator(load_character_frames())
    animator.update(Vector2(0, 0), Vector2(1, 0), 0.0)
    assert animator.direction is CharacterDirection.RIGHT
    assert animator.current_frame is animator.frames.mirrored_side[0]


def test_sprite_rect_is_centered_and_bottom_anchored() -> None:
    frame = pygame.Surface((21, 32), pygame.SRCALPHA)
    player_rect = pygame.Rect(100, 200, 8, 10)
    sprite_rect = character_sprite_rect(frame, player_rect)
    assert sprite_rect.centerx == player_rect.centerx
    assert sprite_rect.bottom == player_rect.bottom


def test_character_scaling_preserves_nearest_neighbor_colors() -> None:
    source = pygame.Surface((336, 384), pygame.SRCALPHA)
    source.fill((0, 0, 0, 0))
    source.fill((255, 0, 0, 255), pygame.Rect(0, 0, 4, 4))
    frames = split_character_sheet(source)
    assert frames.rows[0][0].get_size() == (21, 32)
    assert frames.rows[0][0].get_at((0, 0)) == (255, 0, 0, 255)
