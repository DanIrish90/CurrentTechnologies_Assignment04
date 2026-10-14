"""Pygame-ce rendering for the placeholder first slice."""

from __future__ import annotations

import math
import pygame

from game import config
from game.camera import Camera
from game.geometry import Rect, Vector2
from game.state import GameState, UiSnapshot, ui_snapshot


def _screen_rect(world_rect: Rect, camera: Camera) -> pygame.Rect:
    return pygame.Rect(
        round(world_rect.x - camera.position.x),
        round(world_rect.y - camera.position.y),
        round(world_rect.width),
        round(world_rect.height),
    )


def render(screen: pygame.Surface, state: GameState) -> None:
    """Draw world and UI without mutating authoritative state."""

    screen.fill(config.WORLD_COLOR)
    camera = state.camera
    world_rect = _screen_rect(state.world.bounds, camera)
    pygame.draw.rect(screen, config.WORLD_COLOR, world_rect)
    for x in range(round(state.world.bounds.x), round(state.world.bounds.right) + 1, 80):
        screen_x = round(x - camera.position.x)
        pygame.draw.line(screen, config.GRID_COLOR, (screen_x, 0), (screen_x, screen.get_height()))
    for y in range(round(state.world.bounds.y), round(state.world.bounds.bottom) + 1, 80):
        screen_y = round(y - camera.position.y)
        pygame.draw.line(screen, config.GRID_COLOR, (0, screen_y), (screen.get_width(), screen_y))

    if state.world.fishing_pond is not None:
        zone = _screen_rect(state.world.fishing_pond.bounds, camera)
        pygame.draw.rect(screen, config.STAMINA_REGEN_ZONE_COLOR, zone)
        pygame.draw.rect(screen, config.STAMINA_REGEN_ZONE_OUTLINE_COLOR, zone, width=2)
        zone_font = pygame.font.Font(None, 20)
        screen.blit(zone_font.render(state.world.fishing_pond.label, True, config.UI_TEXT_COLOR), zone.move(6, 8))

    pygame.draw.rect(screen, config.OBSTACLE_COLOR, world_rect, width=4)
    for obstacle in state.world.obstacles:
        obstacle_rect = _screen_rect(obstacle.bounds, camera)
        pygame.draw.rect(screen, config.OBSTACLE_COLOR, obstacle_rect)
        pygame.draw.rect(screen, config.OBSTACLE_OUTLINE_COLOR, obstacle_rect, width=2)
        obstacle_font = pygame.font.Font(None, 20)
        screen.blit(obstacle_font.render(obstacle.label, True, config.UI_TEXT_COLOR), obstacle_rect.move(4, 4))

    if state.world.document_source is not None:
        source_rect = _screen_rect(state.world.document_source.bounds, camera)
        pygame.draw.rect(screen, config.DOCUMENT_SOURCE_COLOR, source_rect)
        pygame.draw.rect(screen, config.UI_TEXT_COLOR, source_rect, width=2)
        source_font = pygame.font.Font(None, 20)
        screen.blit(source_font.render("DOCUMENTS", True, config.UI_TEXT_COLOR), source_rect.move(4, 26))

    if state.workflow is not None:
        servant_font = pygame.font.Font(None, 18)
        for servant in state.workflow.definition.servants:
            servant_bounds = Rect(servant.position.x - 24, servant.position.y - 30, 48, 60)
            servant_rect = _screen_rect(servant_bounds, camera)
            color = config.SERVED_COLOR if servant.served else config.CIVIL_SERVANT_COLOR
            pygame.draw.rect(screen, color, servant_rect)
            pygame.draw.rect(screen, config.UI_TEXT_COLOR, servant_rect, width=2)
            screen.blit(servant_font.render(f"S{servant.step_order}", True, config.UI_TEXT_COLOR), servant_rect.move(16, 8))
            status = "SERVED" if servant.served else "PENDING"
            screen.blit(servant_font.render(status, True, config.UI_TEXT_COLOR), servant_rect.move(3, 38))

    player_rect = _screen_rect(state.player.bounds, camera)
    pygame.draw.rect(screen, config.PLAYER_COLOR, player_rect)
    pygame.draw.rect(screen, config.PLAYER_OUTLINE_COLOR, player_rect, width=2)
    player_font = pygame.font.Font(None, 18)
    screen.blit(player_font.render("YOU", True, config.UI_TEXT_COLOR), player_rect.move(4, 7))
    snapshot = ui_snapshot(state)
    _draw_ui(screen, snapshot)
    if snapshot.fishing_visible:
        _draw_fishing_overlay(screen, snapshot)
    if snapshot.rest_countdown_visible:
        _draw_rest_countdown(screen, snapshot)


def _draw_ui(screen: pygame.Surface, snapshot: UiSnapshot) -> None:
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    panel_width = max(min(screen.get_width() - 32, 460), 1)
    panel = pygame.Rect(16, 16, panel_width, 220)
    pygame.draw.rect(screen, config.UI_PANEL_COLOR, panel)
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, panel, width=2)
    screen.blit(font.render(f"{snapshot.title} | {snapshot.wave_label}", True, config.UI_TEXT_COLOR), (28, 26))
    screen.blit(small_font.render(snapshot.control_hint, True, config.UI_MUTED_COLOR), (28, 54))
    screen.blit(small_font.render(snapshot.carried_label, True, config.UI_TEXT_COLOR), (28, 77))
    feedback_color = config.FEEDBACK_SUCCESS_COLOR if snapshot.feedback.success else config.UI_TEXT_COLOR
    screen.blit(small_font.render(snapshot.state_label, True, feedback_color), (28, 101))
    screen.blit(small_font.render(snapshot.stamina_label, True, config.UI_TEXT_COLOR), (28, 130))
    bar = pygame.Rect(190, 132, config.STAMINA_BAR_WIDTH, config.STAMINA_BAR_HEIGHT)
    pygame.draw.rect(screen, config.STAMINA_BAR_BACKGROUND_COLOR, bar)
    current_text, maximum_text = snapshot.stamina_label.split(":", 1)[-1].split("/", 1)
    maximum = float(maximum_text)
    ratio = max(0.0, min(1.0, float(current_text) / maximum)) if maximum else 0.0
    if ratio > 0:
        fill = pygame.Rect(bar.x + 2, bar.y + 2, round((bar.width - 4) * ratio), bar.height - 4)
        pygame.draw.rect(screen, config.STAMINA_BAR_COLOR, fill)
    screen.blit(small_font.render(snapshot.stamina_status, True, config.UI_MUTED_COLOR), (28, 158))
    screen.blit(small_font.render(snapshot.fishing_status, True, config.UI_TEXT_COLOR), (28, 184))
    if snapshot.game_over and snapshot.restart_button_bounds is not None:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title = font.render("GAME OVER: EXHAUSTED", True, config.GAME_OVER_COLOR)
        screen.blit(title, title.get_rect(center=(screen.get_width() / 2, 285)))
        button = pygame.Rect(
            round(snapshot.restart_button_bounds.x),
            round(snapshot.restart_button_bounds.y),
            round(snapshot.restart_button_bounds.width),
            round(snapshot.restart_button_bounds.height),
        )
        pygame.draw.rect(screen, config.RESTART_BUTTON_COLOR, button)
        pygame.draw.rect(screen, config.UI_TEXT_COLOR, button, width=2)
        label = small_font.render("Restart", True, config.UI_TEXT_COLOR)
        screen.blit(label, label.get_rect(center=button.center))


def _draw_fishing_overlay(screen: pygame.Surface, snapshot: UiSnapshot) -> None:
    """Draw the placeholder catch game without mutating game state."""

    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    play = pygame.Rect(610, 180, config.FISHING_BAR_WIDTH, config.FISHING_BAR_HEIGHT)
    pygame.draw.rect(screen, config.UI_PANEL_COLOR, play.inflate(24, 56))
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, play, width=2)

    def y_for(position: float) -> int:
        return round(play.bottom - (position / config.FISH_PLAY_HEIGHT) * play.height)

    fish_y = y_for(snapshot.fish_position)
    fish_rect = pygame.Rect(play.x - 8, fish_y - 5, play.width + 16, 10)
    catch_bottom = y_for(snapshot.catch_bar_position)
    catch_top = y_for(snapshot.catch_bar_position + snapshot.catch_bar_height)
    catch_rect = pygame.Rect(play.x - 5, catch_top, play.width + 10, max(4, catch_bottom - catch_top))
    pygame.draw.rect(screen, config.STAMINA_BAR_COLOR, catch_rect)
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, catch_rect, width=2)
    pygame.draw.rect(screen, config.FEEDBACK_SUCCESS_COLOR, fish_rect)
    screen.blit(font.render("FISH", True, config.UI_TEXT_COLOR), (play.x - 8, play.y - 34))
    screen.blit(small_font.render("Press E to pull", True, config.UI_TEXT_COLOR), (play.x - 52, play.bottom + 12))

    progress = pygame.Rect(700, 220, 220, 18)
    pygame.draw.rect(screen, config.STAMINA_BAR_BACKGROUND_COLOR, progress)
    filled = pygame.Rect(progress.x, progress.y, round(progress.width * snapshot.fishing_progress / 100), progress.height)
    pygame.draw.rect(screen, config.FEEDBACK_SUCCESS_COLOR, filled)
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, progress, width=2)
    screen.blit(small_font.render(f"FISHING PROGRESS {snapshot.fishing_progress:.0f}%", True, config.UI_TEXT_COLOR), (700, 190))


def _draw_rest_countdown(screen: pygame.Surface, snapshot: UiSnapshot) -> None:
    """Draw a readable semicircular countdown during the wave rest."""
    center = (
        screen.get_width() // 2,
        screen.get_height() - config.WAVE_REST_COUNTDOWN_BOTTOM_MARGIN,
    )
    rect = pygame.Rect(
        center[0] - config.WAVE_REST_COUNTDOWN_WIDTH // 2,
        center[1] - config.WAVE_REST_COUNTDOWN_HEIGHT // 2,
        config.WAVE_REST_COUNTDOWN_WIDTH,
        config.WAVE_REST_COUNTDOWN_HEIGHT,
    )
    panel = rect.inflate(36, 54)
    pygame.draw.rect(screen, config.UI_PANEL_COLOR, panel)
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, panel, width=2)
    pygame.draw.arc(screen, config.STAMINA_BAR_BACKGROUND_COLOR, rect, 0, math.pi, config.WAVE_REST_COUNTDOWN_ARC_WIDTH)
    if snapshot.rest_progress > 0:
        pygame.draw.arc(screen, config.FEEDBACK_SUCCESS_COLOR, rect, 0, math.pi * snapshot.rest_progress, config.WAVE_REST_COUNTDOWN_ARC_WIDTH)
    font = pygame.font.Font(None, 46)
    small_font = pygame.font.Font(None, 24)
    wave = font.render(str(snapshot.rest_wave_number), True, config.UI_TEXT_COLOR)
    seconds = small_font.render(f"{snapshot.rest_seconds_remaining:.1f}s", True, config.UI_TEXT_COLOR)
    screen.blit(wave, wave.get_rect(center=(center[0], center[1] - 10)))
    screen.blit(seconds, seconds.get_rect(center=(center[0], center[1] + 26)))
