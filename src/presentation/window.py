"""Pygame-ce window lifecycle and main loop."""

from __future__ import annotations

import pygame
from dataclasses import replace

from game import config
from game.audio import ApplicationMusicSession
from game.geometry import Vector2
from game.input_state import InputState, input_from_events
from game.state import create_game_state, ui_snapshot, update_game_state
from game.zoom import logical_viewport

from .bureaucrat_animation import BureaucratAnimationManager, load_bureaucrat_frames
from .character_animation import CharacterAnimator, load_character_frames
from .renderer import draw_native_fishing_overlay, render
from .ui_assets import load_ui_assets


def run() -> None:
    pygame.init()
    music_session = ApplicationMusicSession()
    music_session.start()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("I am from the Government")
    clock = pygame.time.Clock()
    display_size = Vector2(*screen.get_size())
    viewport = logical_viewport(display_size, config.ZOOM_MULTIPLIER)
    render_surface = pygame.Surface((round(viewport.x), round(viewport.y)))
    state = create_game_state(viewport)
    input_state = InputState()
    character_animation = CharacterAnimator(load_character_frames())
    bureaucrat_animation = BureaucratAnimationManager(load_bureaucrat_frames())
    ui_assets = load_ui_assets()

    try:
        while state.running:
            events = pygame.event.get()
            input_state = input_from_events(events, input_state)
            elapsed_seconds = clock.tick(config.TARGET_FPS) / 1000.0
            display_size = Vector2(*screen.get_size())
            viewport = logical_viewport(display_size, config.ZOOM_MULTIPLIER)
            render_size = (round(viewport.x), round(viewport.y))
            if render_surface.get_size() != render_size:
                render_surface = pygame.Surface(render_size)
            simulation_input = replace(
                input_state,
                mouse_position=Vector2(
                    input_state.mouse_position.x * viewport.x / display_size.x,
                    input_state.mouse_position.y * viewport.y / display_size.y,
                ),
            )
            previous_state = state
            state = update_game_state(state, simulation_input, elapsed_seconds, viewport)
            character_animation.update(
                previous_state.player.position,
                state.player.position,
                elapsed_seconds,
            )
            servants = state.workflow.definition.servants if state.workflow is not None else ()
            active_recipient_id = (
                state.workflow.current_step.servant_id
                if state.workflow is not None and state.workflow.current_step is not None
                else None
            )
            bureaucrat_animation.update(
                servants,
                elapsed_seconds,
                active_recipient_id=active_recipient_id,
            )
            input_state = input_state.clear_interaction()
            input_state = input_state.clear_mouse_click()
            render(render_surface, state, character_animation, bureaucrat_animation, ui_assets)
            pygame.transform.scale(render_surface, screen.get_size(), screen)
            draw_native_fishing_overlay(screen, ui_snapshot(state), ui_assets)
            pygame.display.flip()
    finally:
        music_session.shutdown()
        pygame.quit()
