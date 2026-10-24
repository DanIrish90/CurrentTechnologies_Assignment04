from __future__ import annotations

from game.state import create_game_state, ui_snapshot
from game.geometry import Vector2
from game.input_state import InputState
from game.fishing import FishingPhase
from game.bureaucracy import collect_initial_document, handover
from dataclasses import replace
from game.state import update_game_state
from game.stamina import StaminaState
from game import config


def _source_position(state):
    assert state.world.document_source is not None
    return state.world.document_source.bounds.center


def _pond_position(state):
    assert state.world.fishing_pond is not None
    return state.world.fishing_pond.bounds.center


def _rest_state(state):
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    return replace(state, workflow=completed)


def test_ui_snapshot_contains_context_state_and_controls() -> None:
    snapshot = ui_snapshot(create_game_state())
    assert snapshot.title
    assert snapshot.state_label
    assert snapshot.control_hint
    assert "WASD" in snapshot.control_hint


def test_ui_snapshot_reports_stamina_and_carrying_status() -> None:
    state = create_game_state()
    assert snapshot_stamina_text(ui_snapshot(state)) == "STAMINA: 100/100"
    collected = update_game_state(
        replace(state, player=state.player.at(_source_position(state))),
        InputState(interact_pressed=True),
        0,
    )
    assert "STAMINA: 100/100" in ui_snapshot(collected).stamina_label
    assert "CARRYING" in ui_snapshot(collected).stamina_status


def snapshot_stamina_text(snapshot) -> str:
    return snapshot.stamina_label


def test_ui_snapshot_does_not_report_passive_recovery_in_fishing_pond() -> None:
    state = _rest_state(create_game_state())
    in_zone = replace(state, player=state.player.at(_pond_position(state)))
    snapshot = ui_snapshot(in_zone)
    assert snapshot.fishing_pond_active
    assert "available" in snapshot.fishing_status.lower()


def test_ui_snapshot_exposes_restart_button_after_game_over() -> None:
    state = create_game_state()
    exhausted = replace(state, game_over=True, stamina=state.stamina.__class__(current=0, game_over=True))
    snapshot = ui_snapshot(exhausted)
    assert snapshot.game_over
    assert snapshot.restart_button_bounds is not None
    assert "GAME OVER" in snapshot.stamina_status


def test_ui_snapshot_reports_fishing_phase_feedback() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(_pond_position(state)))
    casting = update_game_state(pond, InputState(interact_pressed=True), 0)
    snapshot = ui_snapshot(casting)
    assert "WAITING" in snapshot.fishing_status.upper()


def test_ui_snapshot_exposes_catch_game_meters() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(_pond_position(state)))
    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    bite = update_game_state(waiting, InputState(), 2.0)
    catching = update_game_state(bite, InputState(interact_pressed=True), 0)
    snapshot = ui_snapshot(catching)
    assert snapshot.fishing_visible
    assert snapshot.catch_bar_height > 0
    assert 0 <= snapshot.fishing_progress <= 100


def test_ui_snapshot_keeps_catch_game_visible_during_grace_period() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(_pond_position(state)))
    active = update_game_state(
        replace(pond, fishing=pond.fishing.__class__(phase=FishingPhase.CATCHING, fishing_progress=50)),
        InputState(),
        0.1,
    )
    snapshot = ui_snapshot(active)
    assert snapshot.fishing_visible
    assert snapshot.fishing_phase == "catching"


def test_ui_snapshot_exposes_worm_timer_during_rest() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    snapshot = ui_snapshot(replace(state, workflow=completed))
    assert snapshot.rest_countdown_visible
    assert snapshot.rest_wave_number == 1
    assert snapshot.rest_seconds_remaining == 10
    assert snapshot.rest_progress == 1
    assert snapshot.rest_elapsed_progress == 0
    assert snapshot.worm_timer_frame_index == 0


def test_ui_snapshot_derives_worm_progress_and_frame_from_elapsed_rest_time() -> None:
    state = _rest_state(create_game_state())
    halfway = update_game_state(state, InputState(), config.WAVE_REST_DURATION / 2)

    snapshot = ui_snapshot(halfway)

    assert snapshot.rest_elapsed_progress == 0.5
    assert snapshot.worm_timer_frame_index == int(config.WORM_TIMER_FPS * config.WAVE_REST_DURATION / 2) % config.WORM_TIMER_FRAME_COUNT


def test_ui_snapshot_hides_worm_timer_during_active_wave() -> None:
    snapshot = ui_snapshot(create_game_state())

    assert not snapshot.rest_countdown_visible
    assert snapshot.rest_elapsed_progress == 0.0
    assert snapshot.worm_timer_frame_index == 0


def test_ui_snapshot_shows_rest_with_fishing_active() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    rest = replace(state, workflow=completed, player=state.player.at(_pond_position(state)))
    casting = update_game_state(rest, InputState(interact_pressed=True), 0)
    snapshot = ui_snapshot(casting)
    assert snapshot.rest_countdown_visible
    assert snapshot.fishing_visible
    assert snapshot.fishing_phase == "waiting_for_bite"
    assert "waiting" in snapshot.fishing_status.lower()


def test_ui_snapshot_exposes_stamina_ratio_and_color_thresholds() -> None:
    state = create_game_state()
    assert ui_snapshot(state).stamina_ratio == 1.0
    assert ui_snapshot(state).stamina_color_state == "green"
    assert ui_snapshot(replace(state, stamina=StaminaState(current=50))).stamina_color_state == "green"
    assert ui_snapshot(replace(state, stamina=StaminaState(current=49))).stamina_color_state == "yellow"
    assert ui_snapshot(replace(state, stamina=StaminaState(current=10))).stamina_color_state == "yellow"
    assert ui_snapshot(replace(state, stamina=StaminaState(current=9))).stamina_color_state == "red"


def test_ui_snapshot_only_exposes_actionable_interactions() -> None:
    state = create_game_state()
    assert not ui_snapshot(state).interaction_available
    source = replace(state, player=state.player.at(_source_position(state)))
    assert ui_snapshot(source).interaction_available
    collected = update_game_state(source, InputState(interact_pressed=True), 0)
    assert not ui_snapshot(collected).interaction_available
    servant = replace(collected, player=collected.player.at(collected.world.dropoff_zones[1].center))
    assert ui_snapshot(servant).interaction_available


def test_ui_snapshot_matches_fishing_action_phases_and_blocked_states() -> None:
    state = create_game_state()
    pond_position = _pond_position(state)
    active_pond = replace(state, player=state.player.at(pond_position))
    assert not ui_snapshot(active_pond).interaction_available

    rest = _rest_state(state)
    pond = replace(rest, player=rest.player.at(pond_position))
    assert ui_snapshot(pond).interaction_available

    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    assert not ui_snapshot(waiting).interaction_available
    bite = update_game_state(waiting, InputState(), 2.0)
    assert ui_snapshot(bite).interaction_available
    catching = update_game_state(bite, InputState(interact_pressed=True), 0)
    assert ui_snapshot(catching).interaction_available

    exhausted = replace(
        pond,
        game_over=True,
        stamina=StaminaState(current=0, game_over=True),
    )
    assert not ui_snapshot(exhausted).interaction_available


def test_ui_snapshot_maps_fishing_phases_to_fishing_meter_icons() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(_pond_position(state)))

    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    assert ui_snapshot(waiting).fishing_meter_icon == "bait"

    bite = update_game_state(waiting, InputState(), 2.0)
    assert ui_snapshot(bite).fishing_meter_icon == "bite"

    catching = update_game_state(bite, InputState(interact_pressed=True), 0)
    catching_snapshot = ui_snapshot(catching)
    assert catching_snapshot.fishing_meter_icon == "fish"
    assert catching_snapshot.fishing_meter_phase == "catching"


def test_ui_snapshot_exposes_two_second_fishing_outcome_feedback() -> None:
    state = replace(_rest_state(create_game_state()), fishing_feedback="success", fishing_feedback_elapsed=1.5)
    snapshot = ui_snapshot(state)
    assert snapshot.fishing_meter_visible
    assert snapshot.fishing_meter_phase == "success"
    assert snapshot.fishing_outcome_elapsed == 1.5
