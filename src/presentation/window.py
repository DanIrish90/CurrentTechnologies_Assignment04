"""Pygame-ce window lifecycle and main loop."""

from __future__ import annotations

import pygame

from game import config
from game.geometry import Vector2
from game.input_state import InputState, input_from_events
from game.state import create_game_state, update_game_state

from .renderer import render


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("I am from the Government")
    clock = pygame.time.Clock()
    state = create_game_state(Vector2(*screen.get_size()))
    input_state = InputState()

    try:
        while state.running:
            events = pygame.event.get()
            input_state = input_from_events(events, input_state)
            elapsed_seconds = clock.tick(config.TARGET_FPS) / 1000.0
            viewport = Vector2(*screen.get_size())
            state = update_game_state(state, input_state, elapsed_seconds, viewport)
            input_state = input_state.clear_interaction()
            input_state = input_state.clear_mouse_click()
            render(screen, state)
            pygame.display.flip()
    finally:
        pygame.quit()
