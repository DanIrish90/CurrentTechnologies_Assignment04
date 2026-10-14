from __future__ import annotations

from game.state import create_game_state, ui_snapshot
from game.geometry import Vector2
from game.input_state import InputState
from game.fishing import FishingPhase
from game.bureaucracy import collect_initial_document, handover
from dataclasses import replace
from game.state import update_game_state


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
        replace(state, player=state.player.at(Vector2(220, 130))),
        InputState(interact_pressed=True),
        0,
    )
    assert "STAMINA: 100/100" in ui_snapshot(collected).stamina_label
    assert "CARRYING" in ui_snapshot(collected).stamina_status


def snapshot_stamina_text(snapshot) -> str:
    return snapshot.stamina_label


def test_ui_snapshot_does_not_report_passive_recovery_in_fishing_pond() -> None:
    state = _rest_state(create_game_state())
    in_zone = replace(state, player=state.player.at(Vector2(100, 840)))
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
    pond = replace(state, player=state.player.at(Vector2(100, 840)))
    casting = update_game_state(pond, InputState(interact_pressed=True), 0)
    snapshot = ui_snapshot(casting)
    assert "WAITING" in snapshot.fishing_status.upper()


def test_ui_snapshot_exposes_catch_game_meters() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(Vector2(100, 840)))
    waiting = update_game_state(pond, InputState(interact_pressed=True), 0)
    bite = update_game_state(waiting, InputState(), 2.0)
    catching = update_game_state(bite, InputState(interact_pressed=True), 0)
    snapshot = ui_snapshot(catching)
    assert snapshot.fishing_visible
    assert snapshot.catch_bar_height > 0
    assert 0 <= snapshot.fishing_progress <= 100


def test_ui_snapshot_keeps_catch_game_visible_during_grace_period() -> None:
    state = _rest_state(create_game_state())
    pond = replace(state, player=state.player.at(Vector2(100, 840)))
    active = update_game_state(
        replace(pond, fishing=pond.fishing.__class__(phase=FishingPhase.CATCHING, fishing_progress=50)),
        InputState(),
        0.1,
    )
    snapshot = ui_snapshot(active)
    assert snapshot.fishing_visible
    assert snapshot.fishing_phase == "catching"


def test_ui_snapshot_exposes_rest_countdown_and_completed_wave() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    snapshot = ui_snapshot(replace(state, workflow=completed))
    assert snapshot.rest_countdown_visible
    assert snapshot.rest_wave_number == 1
    assert snapshot.rest_seconds_remaining == 10
    assert snapshot.rest_progress == 1


def test_ui_snapshot_shows_rest_with_fishing_active() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    completed, _ = handover(carrying, "servant-1")
    rest = replace(state, workflow=completed, player=state.player.at(Vector2(100, 840)))
    casting = update_game_state(rest, InputState(interact_pressed=True), 0)
    snapshot = ui_snapshot(casting)
    assert snapshot.rest_countdown_visible
    assert snapshot.fishing_visible
    assert snapshot.fishing_phase == "waiting_for_bite"
    assert "waiting" in snapshot.fishing_status.lower()
