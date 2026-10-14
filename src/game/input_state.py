"""Translate Pygame events into a small, deterministic input snapshot."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

import pygame

from .geometry import Vector2


@dataclass(frozen=True, slots=True)
class InputState:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    interact_pressed: bool = False
    mouse_position: Vector2 = Vector2(0, 0)
    mouse_clicked: bool = False
    quit_requested: bool = False

    def direction(self) -> Vector2:
        return Vector2(float(self.right) - float(self.left), float(self.down) - float(self.up))

    def clear_interaction(self) -> InputState:
        return replace(self, interact_pressed=False)

    def clear_mouse_click(self) -> InputState:
        return replace(self, mouse_clicked=False)


_KEY_TO_FIELD = {
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
}


def input_from_events(events: Iterable[pygame.event.Event], current: InputState) -> InputState:
    """Apply supported events to the previous input snapshot."""

    state = current
    for event in events:
        if event.type == pygame.QUIT:
            state = replace(state, quit_requested=True)
        elif event.type in (pygame.WINDOWFOCUSLOST, pygame.ACTIVEEVENT) and getattr(
            event, "gain", 1
        ) == 0:
            state = InputState(quit_requested=state.quit_requested)
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            if getattr(event, "key", None) == pygame.K_e and event.type == pygame.KEYDOWN:
                state = replace(state, interact_pressed=True)
                continue
            field = _KEY_TO_FIELD.get(getattr(event, "key", None))
            if field is not None:
                state = replace(state, **{field: event.type == pygame.KEYDOWN})
        elif event.type == pygame.MOUSEMOTION:
            state = replace(state, mouse_position=Vector2(float(event.pos[0]), float(event.pos[1])))
        elif event.type == pygame.MOUSEBUTTONUP and getattr(event, "button", None) == 1:
            state = replace(
                state,
                mouse_position=Vector2(float(event.pos[0]), float(event.pos[1])),
                mouse_clicked=True,
            )
    return state
