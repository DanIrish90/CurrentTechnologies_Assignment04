from __future__ import annotations

from game.config import VIEWPORT_HEIGHT, VIEWPORT_WIDTH
from game.geometry import Rect
from dataclasses import replace

from game.geometry import Vector2
from game.input_state import InputState
from game.state import create_game_state, update_game_state
from game.stamina import StaminaState
from game.fishing import FishingPhase, FishingState
from game.bureaucracy import create_wave
from game.world import create_initial_world, create_initial_player
from game.bureaucracy import collect_initial_document, handover


def _rest_state(state):
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    return replace(state, workflow=completed)


def test_initial_world_and_player_are_valid_without_display() -> None:
    world = create_initial_world()
    player = create_initial_player(world)
    assert world.bounds.width >= VIEWPORT_WIDTH
    assert world.bounds.height >= VIEWPORT_HEIGHT
    assert world.is_valid_player_position(player)
    assert world.obstacles


def test_application_configuration_has_a_real_viewport() -> None:
    assert Rect(0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT).width > 0


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
    pond = replace(state, player=state.player.at(Vector2(100, 840)))
    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    assert waiting.fishing.phase is FishingPhase.WAITING_FOR_BITE
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


def test_countdown_overlay_renders_during_rest_without_display_errors() -> None:
    import pygame
    from presentation.character_animation import CharacterAnimator, load_character_frames
    from presentation.renderer import render

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    screen = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    rest = replace(state, workflow=completed, player=state.player.at(Vector2(100, 840)))
    render(screen, rest, CharacterAnimator(load_character_frames()))
    pygame.font.quit()
    pygame.display.quit()
