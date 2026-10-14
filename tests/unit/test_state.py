from __future__ import annotations

import pytest
from dataclasses import replace

from game.geometry import Vector2
from game.bureaucracy import advance_progress, collect_initial_document, handover
from game.bureaucracy import WorkflowPhase
from game.fishing import FishingPhase, FishingState
from game.input_state import InputState
from game.state import create_game_state, update_game_state


def _rest_state(state):
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    return replace(state, workflow=completed)


def test_feature_one_player_and_camera_update_with_workflow_state() -> None:
    state = create_game_state()
    assert state.workflow is not None
    moved = update_game_state(state, InputState(right=True), 0.25)
    assert moved.player.position.x > state.player.position.x
    assert moved.camera.bounds.width == state.camera.bounds.width


def test_state_rejects_negative_elapsed_time() -> None:
    with pytest.raises(ValueError):
        update_game_state(create_game_state(), InputState(), -0.1)


def test_workflow_state_can_be_created_with_custom_viewport() -> None:
    state = create_game_state(Vector2(400, 300))
    assert state.workflow is not None
    assert state.camera.viewport_size == Vector2(400, 300)


def test_explicit_interaction_collects_and_handover_uses_world_range() -> None:
    state = create_game_state()
    source_player = state.player.at(Vector2(220, 130))
    collected = update_game_state(
        replace(state, player=source_player), InputState(interact_pressed=True), 0
    )
    assert collected.workflow is not None
    assert collected.workflow.carried_document is not None

    servant_player = collected.player.at(Vector2(826, 154))
    handed_over = update_game_state(
        replace(collected, player=servant_player), InputState(interact_pressed=True), 0
    )
    assert handed_over.workflow is not None
    assert handed_over.workflow.definition.servants[0].served
    assert handed_over.workflow.carried_document is None


def test_player_can_move_during_transition_feedback() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    transitioning = replace(state, workflow=completed)
    updated = update_game_state(transitioning, InputState(right=True), 0.5)
    assert updated.player.position.x > state.player.position.x
    assert updated.workflow is not None
    assert updated.workflow.transition_remaining == 9.5


def test_rest_countdown_is_independent_from_fishing() -> None:
    state = create_game_state()
    rest = replace(_rest_state(state), player=state.player.at(Vector2(100, 840)))
    cast = update_game_state(rest, InputState(interact_pressed=True), 0)
    advanced = update_game_state(cast, InputState(), 2.5)
    assert advanced.workflow is not None
    assert advanced.workflow.transition_remaining == 7.5
    assert advanced.fishing.phase is FishingPhase.BITE_WINDOW


def test_fishing_is_blocked_during_active_wave_and_rest_timer_is_not_relevant() -> None:
    state = create_game_state()
    active = replace(state, player=state.player.at(Vector2(100, 840)))
    blocked = update_game_state(active, InputState(interact_pressed=True), 0.5)
    assert blocked.fishing.phase is FishingPhase.IDLE


def test_fishing_remains_blocked_after_next_wave_starts() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    rest = replace(completed, phase=WorkflowPhase.TRANSITIONING, transition_remaining=0.1)
    resting = replace(state, workflow=rest, player=state.player.at(Vector2(100, 840)))
    next_wave = update_game_state(resting, InputState(), 0.1)
    cast = update_game_state(next_wave, InputState(interact_pressed=True), 0)
    assert cast.workflow is not None
    assert cast.workflow.definition.wave_number == 2
    assert cast.fishing.phase is FishingPhase.IDLE


@pytest.mark.parametrize("phase", [FishingPhase.WAITING_FOR_BITE, FishingPhase.BITE_WINDOW, FishingPhase.CATCHING])
def test_wave_deadline_cancels_fishing_without_reward(phase: FishingPhase) -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    fishing = FishingState(phase=phase, fishing_progress=99, catch_bar_position=80, fish_position=100)
    rest = replace(
        state,
        workflow=replace(completed, phase=WorkflowPhase.TRANSITIONING, transition_remaining=0.5),
        player=state.player.at(Vector2(100, 840)),
        fishing=fishing,
        stamina=state.stamina.__class__(current=50),
    )
    updated = update_game_state(rest, InputState(interact_pressed=True), 1.0)
    assert updated.workflow is not None
    assert updated.workflow.definition.wave_number == 2
    assert updated.fishing.phase is FishingPhase.IDLE
    assert updated.stamina.current == 50


def test_proximity_alone_does_not_collect_and_second_pickup_is_blocked() -> None:
    state = create_game_state()
    near_source = replace(state, player=state.player.at(Vector2(220, 130)))
    still_empty = update_game_state(near_source, InputState(), 0)
    assert still_empty.workflow is not None
    assert still_empty.workflow.carried_document is None

    collected = update_game_state(near_source, InputState(interact_pressed=True), 0)
    collected_again = update_game_state(
        collected, InputState(interact_pressed=True), 0
    )
    assert collected.workflow is not None
    assert collected_again.workflow is not None
    assert collected_again.workflow.carried_document == collected.workflow.carried_document


def test_new_state_starts_with_full_stamina_and_carried_document_drains() -> None:
    state = create_game_state()
    assert state.stamina.current == 100
    source_player = state.player.at(Vector2(220, 130))
    collected = update_game_state(
        replace(state, player=source_player), InputState(interact_pressed=True), 0
    )
    drained = update_game_state(collected, InputState(), 2.0)
    assert drained.workflow is not None and drained.workflow.carried_document is not None
    assert drained.stamina.current == 90


def test_empty_handed_player_outside_zone_does_not_drain() -> None:
    state = create_game_state()
    updated = update_game_state(state, InputState(), 2.0)
    assert updated.stamina.current == 100


def test_empty_handed_player_in_fishing_pond_does_not_passively_recover() -> None:
    state = create_game_state()
    in_zone = replace(state, player=state.player.at(Vector2(100, 840)), stamina=state.stamina.__class__(current=50))
    updated = update_game_state(in_zone, InputState(), 2.0)
    assert updated.stamina.current == 50


def test_fishing_pond_does_not_passively_regenerate_and_carrying_still_drains() -> None:
    state = create_game_state()
    in_zone = replace(state, player=state.player.at(Vector2(100, 840)), stamina=state.stamina.__class__(current=95))
    capped = update_game_state(in_zone, InputState(), 2.0)
    assert capped.stamina.current == 95

    source_player = state.player.at(Vector2(220, 130))
    carrying = update_game_state(replace(state, player=source_player), InputState(interact_pressed=True), 0)
    carrying_in_zone = replace(carrying, player=carrying.player.at(Vector2(100, 840)))
    drained = update_game_state(carrying_in_zone, InputState(), 2.0)
    assert drained.stamina.current == 90


def test_zero_stamina_enters_game_over_and_freezes_active_state() -> None:
    state = create_game_state()
    source_player = state.player.at(Vector2(220, 130))
    carrying = update_game_state(
        replace(state, player=source_player, stamina=state.stamina.__class__(current=2)),
        InputState(interact_pressed=True),
        0,
    )
    exhausted = update_game_state(carrying, InputState(), 1.0)
    assert exhausted.game_over
    assert exhausted.stamina.current == 0
    frozen = update_game_state(exhausted, InputState(right=True, interact_pressed=True), 10.0)
    assert frozen.player == exhausted.player
    assert frozen.workflow == exhausted.workflow
    assert frozen.stamina == exhausted.stamina


def test_restart_click_creates_fresh_session() -> None:
    state = create_game_state()
    exhausted = replace(state, game_over=True, stamina=state.stamina.__class__(current=0, game_over=True))
    restarted = update_game_state(exhausted, InputState(mouse_clicked=True, mouse_position=Vector2(480, 370)), 0)
    assert restarted is not exhausted
    assert restarted.stamina.current == 100
    assert not restarted.game_over
    assert restarted.workflow is not None
    assert restarted.workflow.definition.wave_number == 1


def test_fishing_cast_requires_pond_and_pauses_movement() -> None:
    state = create_game_state()
    state = _rest_state(state)
    pond_player = state.player.at(Vector2(100, 840))
    cast = update_game_state(
        replace(state, player=pond_player), InputState(interact_pressed=True, right=True), 0.25
    )
    assert cast.fishing.phase.value == "waiting_for_bite"
    assert cast.player == pond_player
    moved = update_game_state(cast, InputState(right=True), 0.5)
    assert moved.player == pond_player


def test_fishing_cast_is_blocked_while_carrying_document() -> None:
    state = create_game_state()
    source_player = state.player.at(Vector2(220, 130))
    carrying = update_game_state(
        replace(state, player=source_player), InputState(interact_pressed=True), 0
    )
    pond_carrying = replace(carrying, player=carrying.player.at(Vector2(100, 840)))
    blocked = update_game_state(pond_carrying, InputState(interact_pressed=True), 0)
    assert blocked.fishing.phase.value == "idle"


def test_catch_game_snapshot_is_visible_and_movement_stays_paused() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(Vector2(100, 840)))
    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    bite = update_game_state(waiting, InputState(), 2.0)
    catching = update_game_state(bite, InputState(interact_pressed=True, right=True), 0.1)
    assert catching.fishing.phase.value == "catching"
    assert catching.player == pond.player
    assert catching.fishing.fishing_progress >= 0


def test_state_integration_preserves_catch_bar_grace_and_progress_rules() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(Vector2(100, 840)))
    active = replace(
        pond,
        fishing=FishingState(
            phase=FishingPhase.CATCHING,
            catch_bar_position=40,
            fish_position=60,
            fish_velocity=0,
            fishing_progress=50,
        ),
    )
    pressed = update_game_state(active, InputState(interact_pressed=True), 0)
    during_grace = update_game_state(pressed, InputState(), 0.1)
    assert during_grace.fishing.catch_bar_position > pressed.fishing.catch_bar_position
    assert during_grace.fishing.catch_bar_velocity == pressed.fishing.catch_bar_velocity
    assert during_grace.fishing.fishing_progress > pressed.fishing.fishing_progress


def test_successful_fishing_restores_25_stamina_and_resets_attempt() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(Vector2(100, 840)), stamina=state.stamina.__class__(current=50))
    active = replace(
        pond,
        fishing=FishingState(
            phase=FishingPhase.CATCHING,
            catch_bar_position=80,
            fish_position=100,
            fish_velocity=0,
            fishing_progress=75,
        ),
    )
    caught = update_game_state(active, InputState(interact_pressed=True), 1.0)
    assert caught.stamina.current == 75
    assert caught.fishing.phase is FishingPhase.IDLE
    assert "caught" in caught.fishing.feedback.lower()


def test_fishing_does_not_revive_game_over() -> None:
    state = create_game_state()
    exhausted = replace(
        state,
        player=state.player.at(Vector2(100, 840)),
        game_over=True,
        stamina=state.stamina.__class__(current=0, game_over=True),
        fishing=FishingState(phase=FishingPhase.CATCHING, fishing_progress=99),
    )
    updated = update_game_state(exhausted, InputState(interact_pressed=True), 1.0)
    assert updated.game_over
    assert updated.stamina.current == 0
