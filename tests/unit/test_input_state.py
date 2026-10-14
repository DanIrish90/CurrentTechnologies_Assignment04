from __future__ import annotations

import pygame

from game.geometry import Vector2
from game.input_state import InputState, input_from_events


def test_keyboard_events_map_to_cardinal_and_diagonal_input() -> None:
    state = input_from_events(
        [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d),
        ],
        InputState(),
    )
    assert state.up and state.right


def test_opposing_keys_cancel_in_direction_vector() -> None:
    state = InputState(left=True, right=True, up=True, down=True)
    assert state.direction().x == 0
    assert state.direction().y == 0


def test_unsupported_keys_do_not_change_state() -> None:
    initial = InputState()
    state = input_from_events(
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)], initial
    )
    assert state == initial


def test_close_event_requests_quit() -> None:
    state = input_from_events([pygame.event.Event(pygame.QUIT)], InputState())
    assert state.quit_requested


def test_left_mouse_release_records_click_position() -> None:
    state = input_from_events(
        [pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (400, 350)})],
        InputState(),
    )
    assert state.mouse_clicked
    assert state.mouse_position == Vector2(400, 350)


def test_mouse_click_outside_restart_button_is_still_reported_for_hit_testing() -> None:
    state = input_from_events(
        [pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (10, 10)})],
        InputState(),
    )
    assert state.mouse_clicked
    assert state.mouse_position == Vector2(10, 10)
