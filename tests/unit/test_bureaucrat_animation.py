from __future__ import annotations

import pygame
import pytest

from game.bureaucracy import CivilServant
from game.geometry import Vector2
from presentation.bureaucrat_animation import (
    BureaucratAnimationKind,
    BureaucratAnimationManager,
    load_bureaucrat_frames,
    split_bureaucrat_sheet,
    bureaucrat_sprite_rect,
)


@pytest.fixture(scope="module", autouse=True)
def pygame_display() -> None:
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


def servant(servant_id: str, served: bool = False) -> CivilServant:
    return CivilServant(servant_id, servant_id, Vector2(100, 100), 1, served)


def test_bureaucrat_frames_are_scaled_to_world_size() -> None:
    frames = load_bureaucrat_frames()
    assert len(frames.rows) == 2
    assert all(len(row) == 2 for row in frames.rows)
    assert all(frame.get_size() == (21, 32) for row in frames.rows for frame in row)


def test_split_rejects_unexpected_sheet_dimensions() -> None:
    with pytest.raises(ValueError, match="168x256"):
        split_bureaucrat_sheet(pygame.Surface((32, 32), pygame.SRCALPHA))


def test_unserved_servant_loops_idle_frames() -> None:
    frames = load_bureaucrat_frames()
    manager = BureaucratAnimationManager(frames)
    idle = servant("servant-1")
    manager.update((idle,), 0)
    assert manager.states["servant-1"].kind is BureaucratAnimationKind.IDLE
    assert manager.states["servant-1"].frame_index == 0
    manager.update((idle,), 1 / 3)
    assert manager.states["servant-1"].frame_index == 1
    manager.update((idle,), 1 / 3)
    assert manager.states["servant-1"].frame_index == 0


def test_served_servant_loops_permit_frames_and_resets_on_state_change() -> None:
    frames = load_bureaucrat_frames()
    manager = BureaucratAnimationManager(frames)
    unserved = servant("servant-1", served=False)
    served = servant("servant-1", served=True)
    manager.update((unserved,), 0)
    manager.update((served,), 0)
    assert manager.states["servant-1"].kind is BureaucratAnimationKind.PERMIT
    assert manager.states["servant-1"].frame_index == 0
    manager.update((served,), 1 / 3)
    assert manager.states["servant-1"].frame_index == 1
    manager.update((unserved,), 0)
    assert manager.states["servant-1"].kind is BureaucratAnimationKind.IDLE
    assert manager.states["servant-1"].frame_index == 0


def test_already_served_servant_starts_in_permit_animation() -> None:
    manager = BureaucratAnimationManager(load_bureaucrat_frames())
    manager.update((servant("servant-1", served=True),), 0)
    assert manager.states["servant-1"].kind is BureaucratAnimationKind.PERMIT
    assert manager.frame_for("servant-1") is manager.frames.rows[1][0]


def test_previously_served_next_recipient_returns_to_idle_before_interaction() -> None:
    manager = BureaucratAnimationManager(load_bureaucrat_frames())
    previously_served = servant("servant-1", served=True)

    manager.update((previously_served,), 1 / 3)
    manager.update((previously_served,), 0, active_recipient_id="servant-1")

    assert manager.states["servant-1"].kind is BureaucratAnimationKind.IDLE
    assert manager.states["servant-1"].frame_index == 0
    assert manager.frame_for("servant-1") is manager.frames.rows[0][0]


def test_servant_animation_states_are_independent_and_pruned() -> None:
    manager = BureaucratAnimationManager(load_bureaucrat_frames())
    first = servant("servant-1")
    second = servant("servant-2", served=True)
    third = servant("servant-3")
    manager.update((first, second, third), 0)
    manager.update((first, second, third), 1 / 3)
    assert manager.states["servant-1"].frame_index == 1
    assert manager.states["servant-2"].frame_index == 1
    assert manager.states["servant-3"].frame_index == 1
    manager.update((first,), 0)
    assert set(manager.states) == {"servant-1"}


def test_large_elapsed_interval_wraps_safely() -> None:
    manager = BureaucratAnimationManager(load_bureaucrat_frames())
    current = servant("servant-1")
    manager.update((current,), 0)
    manager.update((current,), 100)
    assert 0 <= manager.states["servant-1"].frame_index < 2


def test_sprite_placement_preserves_target_center_bottom() -> None:
    frame = pygame.Surface((21, 32), pygame.SRCALPHA)
    target = pygame.Rect(826, 140, 12, 15)
    placed = bureaucrat_sprite_rect(frame, target)
    assert placed.centerx == target.centerx
    assert placed.bottom == target.bottom


def test_bureaucrat_scaling_preserves_nearest_neighbor_colors() -> None:
    source = pygame.Surface((168, 256), pygame.SRCALPHA)
    source.fill((0, 0, 0, 0))
    source.fill((0, 255, 0, 255), pygame.Rect(0, 0, 4, 4))
    frames = split_bureaucrat_sheet(source)
    assert frames.rows[0][0].get_size() == (21, 32)
    assert frames.rows[0][0].get_at((0, 0)) == (0, 255, 0, 255)
