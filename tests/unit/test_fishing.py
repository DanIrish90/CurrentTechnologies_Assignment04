from __future__ import annotations

from dataclasses import replace

import pytest

from game import config
from game.fishing import FishingPhase, FishingState, advance_fishing, create_fishing_state, start_cast


def test_initial_fishing_state_is_idle_and_bounded() -> None:
    state = create_fishing_state()
    assert state.phase is FishingPhase.IDLE
    assert 0 <= state.catch_bar_position <= 80
    assert state.catch_bar_velocity == 0
    assert 0 <= state.fish_position <= 100
    assert 0 <= state.fishing_progress <= 100


def test_fishing_state_rejects_invalid_bounds_and_negative_time() -> None:
    with pytest.raises(ValueError):
        FishingState(phase_elapsed=-0.1)
    with pytest.raises(ValueError):
        FishingState(catch_bar_position=81)
    with pytest.raises(ValueError):
        FishingState(fishing_progress=101)
    with pytest.raises(ValueError):
        FishingState(catch_bar_velocity=1000)


def test_cast_waits_two_seconds_then_opens_bite_window() -> None:
    waiting, result = start_cast(create_fishing_state(), eligible=True)
    assert result.accepted
    assert waiting.phase is FishingPhase.WAITING_FOR_BITE
    still_waiting, _ = advance_fishing(waiting, 1.9, interact_pressed=False, eligible=True)
    assert still_waiting.phase is FishingPhase.WAITING_FOR_BITE
    bite, _ = advance_fishing(still_waiting, 0.1, interact_pressed=False, eligible=True)
    assert bite.phase is FishingPhase.BITE_WINDOW


def test_pressing_inside_bite_window_starts_catch_game() -> None:
    waiting, _ = start_cast(create_fishing_state(), eligible=True)
    bite, _ = advance_fishing(waiting, 2.0, interact_pressed=False, eligible=True)
    catching, outcome = advance_fishing(bite, 0.5, interact_pressed=True, eligible=True)
    assert outcome.accepted
    assert catching.phase is FishingPhase.CATCHING


def test_press_at_one_second_misses_bite() -> None:
    waiting, _ = start_cast(create_fishing_state(), eligible=True)
    bite, _ = advance_fishing(waiting, 2.0, interact_pressed=False, eligible=True)
    missed, outcome = advance_fishing(bite, 1.0, interact_pressed=False, eligible=True)
    assert outcome.accepted
    assert missed.phase is FishingPhase.IDLE
    assert "missed" in missed.feedback.lower()


def _catching_state() -> FishingState:
    waiting, _ = start_cast(create_fishing_state(), eligible=True)
    bite, _ = advance_fishing(waiting, 2.0, interact_pressed=False, eligible=True)
    catching, _ = advance_fishing(bite, 0.5, interact_pressed=True, eligible=True)
    return catching


def test_catch_bar_rises_on_press_and_falls_without_input() -> None:
    state = _catching_state()
    raised, _ = advance_fishing(state, 0, interact_pressed=True, eligible=True)
    assert raised.catch_bar_velocity > state.catch_bar_velocity
    grace, _ = advance_fishing(raised, 0.15, interact_pressed=False, eligible=True)
    assert grace.catch_bar_velocity == raised.catch_bar_velocity
    assert grace.catch_bar_position > raised.catch_bar_position


def test_catch_bar_grace_period_restarts_after_every_press() -> None:
    state = _catching_state()
    first_press, _ = advance_fishing(state, 0.0, interact_pressed=True, eligible=True)
    after_grace, _ = advance_fishing(first_press, 0.15, interact_pressed=False, eligible=True)
    second_press, _ = advance_fishing(after_grace, 0.0, interact_pressed=True, eligible=True)
    restarted_grace, _ = advance_fishing(second_press, 0.15, interact_pressed=False, eligible=True)
    assert restarted_grace.catch_bar_velocity == second_press.catch_bar_velocity
    assert restarted_grace.time_since_last_press == pytest.approx(0.15)


def test_catch_bar_gravity_accelerates_downward_after_grace() -> None:
    state = replace(_catching_state(), catch_bar_position=50, fish_position=100, fish_velocity=0)
    grace, _ = advance_fishing(state, 0.15, interact_pressed=False, eligible=True)
    first = advance_fishing(grace, 0.1, interact_pressed=False, eligible=True)[0]
    second = advance_fishing(first, 0.1, interact_pressed=False, eligible=True)[0]
    assert grace.catch_bar_velocity == 0
    assert first.catch_bar_velocity < 0
    assert second.catch_bar_velocity < first.catch_bar_velocity
    assert first.catch_bar_position - second.catch_bar_position > grace.catch_bar_position - first.catch_bar_position


def test_catch_bar_velocity_is_independent_of_update_chunk_size() -> None:
    state = replace(_catching_state(), catch_bar_position=50, fish_position=100, fish_velocity=0)
    coarse, _ = advance_fishing(state, 0.65, interact_pressed=False, eligible=True)
    fine, _ = advance_fishing(state, 0.15, interact_pressed=False, eligible=True)
    fine, _ = advance_fishing(fine, 0.25, interact_pressed=False, eligible=True)
    fine, _ = advance_fishing(fine, 0.25, interact_pressed=False, eligible=True)
    assert fine.catch_bar_position == pytest.approx(coarse.catch_bar_position)
    assert fine.catch_bar_velocity == pytest.approx(coarse.catch_bar_velocity)


def test_catch_bar_stays_within_bounds() -> None:
    state = replace(
        _catching_state(),
        catch_bar_position=0,
        catch_bar_velocity=-config.FISH_CATCH_BAR_MAX_SPEED,
        fish_position=100,
        fishing_progress=50,
    )
    lowered, _ = advance_fishing(state, 0.1, interact_pressed=False, eligible=True)
    assert lowered.catch_bar_position == 0
    assert lowered.catch_bar_velocity == 0
    raised, _ = advance_fishing(replace(state, catch_bar_position=80), 0, interact_pressed=True, eligible=True)
    assert raised.catch_bar_position == 80


def test_fish_motion_is_deterministic_and_bounded() -> None:
    state = replace(_catching_state(), fish_position=50, fish_velocity=45)
    first, _ = advance_fishing(state, 1.0, interact_pressed=False, eligible=True)
    second, _ = advance_fishing(state, 1.0, interact_pressed=False, eligible=True)
    assert first.fish_position == second.fish_position
    assert 0 <= first.fish_position <= 100


def test_progress_gains_when_fish_is_inside_and_loses_when_outside() -> None:
    aligned = replace(_catching_state(), catch_bar_position=80, fish_position=100, fish_velocity=0, fishing_progress=50)
    gained, _ = advance_fishing(aligned, 1.0, interact_pressed=True, eligible=True)
    assert gained.fishing_progress == 75

    outside = replace(_catching_state(), catch_bar_position=0, fish_position=100, fish_velocity=0, fishing_progress=50)
    lost, _ = advance_fishing(outside, 1.0, interact_pressed=False, eligible=True)
    assert lost.fishing_progress == 15


def test_full_progress_catches_once_and_returns_reward() -> None:
    state = replace(
        _catching_state(),
        catch_bar_position=80,
        fish_position=100,
        fish_velocity=0,
        fishing_progress=75,
    )
    caught, outcome = advance_fishing(state, 1.0, interact_pressed=True, eligible=True)
    assert caught.phase is FishingPhase.IDLE
    assert outcome.caught
    assert outcome.stamina_reward == 25
    assert caught.reward_awarded is False


def test_zero_progress_escapes_without_reward() -> None:
    state = replace(_catching_state(), catch_bar_position=0, fish_position=100, fish_velocity=0, fishing_progress=10)
    escaped, outcome = advance_fishing(state, 1.0, interact_pressed=False, eligible=True)
    assert escaped.phase is FishingPhase.IDLE
    assert not outcome.caught
    assert outcome.stamina_reward == 0
