from __future__ import annotations

import pygame

from game.input_state import InputState, input_from_events


def test_interaction_requires_explicit_key_event() -> None:
    idle = InputState()
    assert not idle.interact_pressed
    pressed = input_from_events(
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)], idle
    )
    assert pressed.interact_pressed


def test_interaction_press_is_a_single_frame_action() -> None:
    state = input_from_events(
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)], InputState()
    )
    assert not state.clear_interaction().interact_pressed
