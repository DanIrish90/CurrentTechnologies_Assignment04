from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from game import config
from game.audio import ApplicationMusicSession
from game.config import VIEWPORT_HEIGHT, VIEWPORT_WIDTH
from game.geometry import Rect, Vector2
from game.zoom import logical_viewport

from game.input_state import InputState
from game.state import create_game_state, ui_snapshot, update_game_state
from game.stamina import StaminaState
from game.fishing import FishingPhase, FishingState
from game.bureaucracy import create_wave
from game.world import create_initial_world, create_initial_player
from game.bureaucracy import collect_initial_document, handover
from presentation.ui_assets import (
    StaminaColor,
    game_over_rect,
    fishing_meter_rect,
    interaction_button_rect,
    load_ui_assets,
    split_fishing_meter,
    stamina_bar_rect,
)


def _rest_state(state):
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    return replace(state, workflow=completed)


def _pond_position(state):
    assert state.world.fishing_pond is not None
    return state.world.fishing_pond.bounds.center


def _source_position(state):
    assert state.world.document_source is not None
    return state.world.document_source.bounds.center


def test_initial_world_and_player_are_valid_without_display() -> None:
    world = create_initial_world()
    player = create_initial_player(world)
    assert world.bounds.width >= VIEWPORT_WIDTH
    assert world.bounds.height >= VIEWPORT_HEIGHT
    assert world.is_valid_player_position(player)
    assert world.obstacles


def test_renderer_applies_tiled_diagonal_transform_to_tile_gid() -> None:
    import pygame
    from game.camera import Camera
    from presentation.renderer import _draw_tile

    pygame.display.init()
    pygame.display.set_mode((1, 1))
    try:
        tileset = pygame.Surface((32, 32), pygame.SRCALPHA)
        for position, color in [
            ((0, 0), (1, 0, 0, 255)),
            ((16, 0), (2, 0, 0, 255)),
            ((0, 16), (3, 0, 0, 255)),
            ((16, 16), (4, 0, 0, 255)),
        ]:
            tileset.fill(color, pygame.Rect(*position, 16, 16))
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        _draw_tile(surface, tileset, 1 | 0x20000000, 0, 0, Camera(Vector2(32, 32), Vector2(0, 0)))

        assert surface.get_at((0, 0))[0] == 1
        assert surface.get_at((31, 0))[0] == 3
        assert surface.get_at((0, 31))[0] == 2
        assert surface.get_at((31, 31))[0] == 4
    finally:
        pygame.display.quit()


def test_application_configuration_has_a_real_viewport() -> None:
    assert Rect(0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT).width > 0


def test_soundtrack_configuration_uses_complete_existing_asset_and_loop_mode() -> None:
    soundtrack = Path(config.SOUNDTRACK_ASSET_PATH)
    assert soundtrack == Path("assets/Music/I'm Not a Big Fan of.m4a")
    assert soundtrack.is_file()
    assert Path(config.SOUNDTRACK_RUNTIME_FALLBACK_PATH).is_file()
    assert config.SOUNDTRACK_LOOP_COUNT == -1


def test_soundtrack_is_owned_by_application_boundary_not_gameplay_state() -> None:
    state_source = Path("src/game/state.py").read_text(encoding="utf-8")
    window_source = Path("src/presentation/window.py").read_text(encoding="utf-8")
    assert "ApplicationMusicSession" not in state_source
    assert window_source.count("ApplicationMusicSession()") == 1
    assert "music_session.start()" in window_source
    assert "music_session.shutdown()" in window_source


def test_game_over_restart_preserves_the_single_soundtrack_session(monkeypatch) -> None:
    calls: list[tuple] = []

    class FakeMusic:
        def load(self, path):
            calls.append(("load", path))

        def play(self, loops=0):
            calls.append(("play", loops))

        def stop(self):
            calls.append(("stop",))

    class FakeMixer:
        music = FakeMusic()

        @staticmethod
        def get_init():
            return True

    monkeypatch.setattr("game.audio.pygame.mixer", FakeMixer)
    session = ApplicationMusicSession()
    session.start()
    calls_before_restart = list(calls)

    state = create_game_state()
    exhausted = replace(state, game_over=True, stamina=StaminaState(current=0, game_over=True))
    update_game_state(
        exhausted,
        InputState(mouse_clicked=True, mouse_position=Vector2(480, 370)),
        0,
    )

    assert calls == calls_before_restart


@pytest.mark.parametrize("zoom", [1.0, 1.5, 2.0])
def test_zoomed_logical_surface_renders_a_complete_frame(zoom: float) -> None:
    import pygame
    from presentation.bureaucrat_animation import BureaucratAnimationManager, load_bureaucrat_frames
    from presentation.character_animation import CharacterAnimator, load_character_frames
    from presentation.renderer import render

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    viewport = logical_viewport(Vector2(VIEWPORT_WIDTH, VIEWPORT_HEIGHT), zoom)
    surface = pygame.Surface((round(viewport.x), round(viewport.y)))
    state = create_game_state(viewport)
    bureaucrat_animation = BureaucratAnimationManager(load_bureaucrat_frames())
    bureaucrat_animation.update(state.workflow.definition.servants, 0)
    render(surface, state, CharacterAnimator(load_character_frames()), bureaucrat_animation)

    assert surface.get_size() == (round(viewport.x), round(viewport.y))
    assert surface.get_at((0, 0))[:3] != (0, 0, 0)
    assert surface.get_at((surface.get_width() - 1, surface.get_height() - 1))[:3] != (0, 0, 0)

    pygame.font.quit()
    pygame.display.quit()


def test_initial_state_accepts_zoom_adjusted_viewport() -> None:
    viewport = logical_viewport(Vector2(VIEWPORT_WIDTH, VIEWPORT_HEIGHT), 2.0)
    state = create_game_state(viewport)
    assert state.camera.viewport_size == viewport
    assert state.player.position == create_game_state().player.position


@pytest.mark.parametrize("value", [0, -1, 4.01, "zoom", float("inf")])
def test_invalid_zoom_is_rejected_before_render_surface_creation(value: object) -> None:
    with pytest.raises(ValueError):
        logical_viewport(Vector2(VIEWPORT_WIDTH, VIEWPORT_HEIGHT), value)


@pytest.mark.parametrize("display_size", [(960, 640), (800, 600), (1280, 720)])
def test_zoomed_render_surface_can_follow_window_resize(display_size: tuple[int, int]) -> None:
    viewport = logical_viewport(Vector2(*display_size), 1.5)
    assert viewport.x > 0
    assert viewport.y > 0
    assert viewport.x <= display_size[0]
    assert viewport.y <= display_size[1]


def test_runtime_starts_with_wave_one_and_document_source() -> None:
    state = create_game_state()
    assert state.workflow is not None
    assert state.workflow.definition.wave_number == 1
    assert len(state.workflow.definition.servants) == 1
    assert state.world.document_source is not None
    assert state.world.fishing_pond is not None
    assert state.workflow.carried_document is None


def test_wave_two_launch_contract_has_two_servants() -> None:
    wave = create_wave(2)
    assert len(wave.servants) == 2
    assert wave.steps[0].issued_document_type.value == "permit"


def test_game_over_state_can_restart_a_fresh_wave_one_session() -> None:
    state = create_game_state()
    exhausted = replace(state, game_over=True, stamina=StaminaState(current=0, game_over=True))
    restarted = update_game_state(exhausted, InputState(mouse_clicked=True, mouse_position=Vector2(480, 370)), 0)
    assert restarted.stamina.current == restarted.stamina.maximum
    assert not restarted.game_over
    assert restarted.workflow is not None
    assert restarted.workflow.definition.wave_number == 1


def test_fishing_pond_cast_and_reward_contract() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(_pond_position(state)))
    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    assert waiting.fishing.phase is FishingPhase.WAITING_FOR_BITE
    progressed = update_game_state(waiting, InputState(), 0.5)
    assert ui_snapshot(progressed).rest_elapsed_progress > ui_snapshot(waiting).rest_elapsed_progress
    assert ui_snapshot(progressed).rest_countdown_visible
    active = replace(
        pond,
        stamina=StaminaState(current=50),
        fishing=FishingState(
            phase=FishingPhase.CATCHING,
                catch_bar_position=80,
                fish_position=100,
            fish_velocity=0,
            fishing_progress=75,
        ),
    )
    caught = update_game_state(active, InputState(interact_pressed=True), 1)
    assert caught.stamina.current == 75
    assert caught.fishing.phase is FishingPhase.IDLE


def test_worm_timer_renders_during_rest_without_display_errors() -> None:
    import pygame
    from presentation.bureaucrat_animation import BureaucratAnimationManager, load_bureaucrat_frames
    from presentation.character_animation import CharacterAnimator, load_character_frames
    from presentation.renderer import render

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    screen = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    rest = replace(state, workflow=completed, player=state.player.at(_pond_position(state)))
    bureaucrat_animation = BureaucratAnimationManager(load_bureaucrat_frames())
    bureaucrat_animation.update(rest.workflow.definition.servants, 0)
    render(
        screen,
        rest,
        CharacterAnimator(load_character_frames()),
        bureaucrat_animation,
    )
    renderer_source = Path("src/presentation/renderer.py").read_text(encoding="utf-8")
    assert "pygame.draw.arc" not in renderer_source
    assert "worm_timer_frames" in renderer_source
    pygame.font.quit()
    pygame.display.quit()


def test_interaction_button_renders_only_for_actionable_source_state() -> None:
    import pygame
    from presentation.bureaucrat_animation import BureaucratAnimationManager, load_bureaucrat_frames
    from presentation.character_animation import CharacterAnimator, load_character_frames
    from presentation.renderer import render

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    state = create_game_state()
    actionable = replace(state, player=state.player.at(_source_position(state)))
    assets = load_ui_assets()
    surface = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
    animations = BureaucratAnimationManager(load_bureaucrat_frames())
    animations.update(actionable.workflow.definition.servants, 0)
    render(surface, actionable, CharacterAnimator(load_character_frames()), animations, assets)
    button_rect = interaction_button_rect(surface.get_size(), assets.interaction_button.get_size(), 16)
    assert ui_snapshot(actionable).interaction_available
    assert surface.get_at(button_rect.center)[:3] != (34, 40, 49)

    pygame.font.quit()
    pygame.display.quit()


def test_renderer_no_longer_contains_removed_world_overlay_labels() -> None:
    renderer_source = Path("src/presentation/renderer.py").read_text(encoding="utf-8")
    assert "FISHING POND" not in renderer_source
    assert "DOCUMENTS" not in renderer_source


def test_renderer_does_not_draw_civil_servant_debug_labels() -> None:
    renderer_source = Path("src/presentation/renderer.py").read_text(encoding="utf-8")
    assert 'f"S{step_order}"' not in renderer_source
    assert 'f"DEBUG' not in renderer_source
    assert '"SERVED"' not in renderer_source
    assert '"PENDING"' not in renderer_source


def test_fishing_meter_asset_has_native_bar_and_icon_regions() -> None:
    import pygame

    pygame.display.init()
    pygame.display.set_mode((1, 1))
    try:
        assets = load_ui_assets()
        assert assets.fishing_bar.get_size() == (64, 448)
        assert len(assets.fishing_icons) == 6
        assert all(icon.get_size() == (64, 64) for icon in assets.fishing_icons)
        assert fishing_meter_rect((960, 640)).size == (128, 448)
        assert split_fishing_meter(pygame.Surface((128, 448), pygame.SRCALPHA))[0].get_size() == (64, 448)
    finally:
        pygame.display.quit()


def test_fishing_meter_renders_modal_catching_and_outcome_states() -> None:
    import pygame
    from presentation.bureaucrat_animation import BureaucratAnimationManager, load_bureaucrat_frames
    from presentation.character_animation import CharacterAnimator, load_character_frames
    from presentation.renderer import render

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    try:
        state = create_game_state()
        carrying, _ = collect_initial_document(state.workflow)
        completed, _ = handover(carrying, "servant-1")
        rest = replace(state, workflow=completed, player=state.player.at(_pond_position(state)))
        waiting = update_game_state(rest, InputState(interact_pressed=True), 0)
        bite = update_game_state(waiting, InputState(), 2.0)
        catching = update_game_state(bite, InputState(interact_pressed=True), 0)
        assets = load_ui_assets()
        animations = BureaucratAnimationManager(load_bureaucrat_frames())
        animations.update(catching.workflow.definition.servants, 0)
        surface = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
        render(surface, catching, CharacterAnimator(load_character_frames()), animations, assets)
        meter = fishing_meter_rect(surface.get_size())
        assert surface.get_at(meter.center)[:3] != config.WORLD_COLOR

        outcome = replace(catching, fishing_feedback="success", fishing_feedback_elapsed=1.0)
        render(surface, outcome, CharacterAnimator(load_character_frames()), animations, assets)
    finally:
        pygame.font.quit()
        pygame.display.quit()


def test_fishing_waiting_and_bite_icons_are_centered_inside_bar() -> None:
    import pygame
    from presentation.renderer import _draw_fishing_overlay
    from game.state import UiSnapshot

    pygame.display.init()
    pygame.display.set_mode((1, 1))
    try:
        assets = load_ui_assets()
        surface = pygame.Surface((960, 640), pygame.SRCALPHA)
        surface.fill((1, 2, 3, 255))
        snapshot = UiSnapshot(
            title="test",
            state_label="test",
            control_hint="test",
            fishing_meter_visible=True,
            fishing_meter_phase="waiting_for_bite",
            fishing_meter_icon="bait",
        )
        _draw_fishing_overlay(surface, snapshot, assets)
        meter = fishing_meter_rect(surface.get_size())
        bar_center = (meter.x + 32, meter.y + 224)
        right_center = (meter.x + 96, meter.y + 224)
        assert surface.get_at(bar_center)[:3] != (1, 2, 3)
        assert surface.get_at(right_center)[:3] == (1, 2, 3)
    finally:
        pygame.display.quit()


def test_game_over_banner_renders_centered_and_restart_state_remains_valid() -> None:
    import pygame
    from presentation.bureaucrat_animation import BureaucratAnimationManager, load_bureaucrat_frames
    from presentation.character_animation import CharacterAnimator, load_character_frames
    from presentation.renderer import render

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    state = create_game_state()
    exhausted = replace(state, game_over=True, stamina=StaminaState(current=0, game_over=True))
    assets = load_ui_assets()
    surface = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
    animations = BureaucratAnimationManager(load_bureaucrat_frames())
    animations.update(exhausted.workflow.definition.servants, 0)
    render(surface, exhausted, CharacterAnimator(load_character_frames()), animations, assets)
    banner_rect = game_over_rect(surface.get_size(), assets.game_over.get_size(), 16)
    assert banner_rect.center == surface.get_rect().center
    assert surface.get_at(banner_rect.center)[:3] != (34, 40, 49)

    pygame.font.quit()
    pygame.display.quit()


@pytest.mark.parametrize(
    ("current", "color"),
    [(100, StaminaColor.GREEN), (50, StaminaColor.GREEN), (25, StaminaColor.YELLOW), (10, StaminaColor.YELLOW), (9, StaminaColor.RED), (0, StaminaColor.RED)],
)
def test_stamina_bar_render_uses_ratio_and_threshold_color(current: float, color: StaminaColor) -> None:
    import pygame
    from presentation.renderer import _draw_stamina_bar

    pygame.display.init()
    pygame.display.set_mode((1, 1))
    try:
        state = replace(
            create_game_state(),
            game_over=current == 0,
            stamina=StaminaState(current=current, game_over=current == 0),
        )
        assets = load_ui_assets()
        surface = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
        surface.fill((0, 0, 0))
        snapshot = ui_snapshot(state)
        _draw_stamina_bar(surface, snapshot, assets)

        bar_rect = stamina_bar_rect(
            surface.get_size(),
            (config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_BAR_HEIGHT),
            config.UI_MARGIN,
            config.UI_STAMINA_BAR_SCALE,
        )
        expected_fill = pygame.transform.scale(
            assets.colorized_stamina_fill(color), bar_rect.size
        )
        fill_width = round(bar_rect.width * snapshot.stamina_ratio)
        expected = pygame.Surface(surface.get_size())
        expected.fill((0, 0, 0))
        if fill_width:
            expected.set_clip(pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height))
            expected.blit(expected_fill, bar_rect)
            expected.set_clip(None)
        expected_frame = pygame.transform.scale(assets.stamina_frame, bar_rect.size)
        expected.blit(expected_frame, bar_rect)
        assert pygame.image.tobytes(surface.subsurface(bar_rect), "RGBA") == pygame.image.tobytes(
            expected.subsurface(bar_rect), "RGBA"
        )
        assert 0 <= fill_width <= bar_rect.width
    finally:
        pygame.display.quit()
