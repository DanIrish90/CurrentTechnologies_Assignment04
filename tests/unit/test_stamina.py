from __future__ import annotations

import pytest

from game.stamina import StaminaState, advance_stamina, create_initial_stamina


def test_initial_stamina_is_full() -> None:
    state = create_initial_stamina()
    assert state.current == 100
    assert not state.game_over


def test_document_carrying_drains_five_per_second() -> None:
    updated = advance_stamina(create_initial_stamina(), 2.0, carrying_document=True, in_regen_zone=False)
    assert updated.current == 90


def test_equivalent_elapsed_time_is_frame_rate_independent() -> None:
    one_step = advance_stamina(create_initial_stamina(), 2.0, carrying_document=True, in_regen_zone=False)
    split = advance_stamina(
        advance_stamina(create_initial_stamina(), 1.0, carrying_document=True, in_regen_zone=False),
        1.0,
        carrying_document=True,
        in_regen_zone=False,
    )
    assert one_step.current == split.current


def test_carrying_takes_precedence_over_regeneration() -> None:
    updated = advance_stamina(create_initial_stamina(), 2.0, carrying_document=True, in_regen_zone=True)
    assert updated.current == 90


def test_stamina_clamps_at_zero_and_enters_game_over() -> None:
    state = StaminaState(current=2.0)
    updated = advance_stamina(state, 1.0, carrying_document=True, in_regen_zone=False)
    assert updated.current == 0
    assert updated.game_over


def test_game_over_state_is_frozen() -> None:
    state = StaminaState(current=0, game_over=True)
    assert advance_stamina(state, 10, carrying_document=False, in_regen_zone=True) == state


def test_stamina_rejects_invalid_values_and_negative_time() -> None:
    with pytest.raises(ValueError):
        StaminaState(maximum=0)
    with pytest.raises(ValueError):
        StaminaState(current=-1)
    with pytest.raises(ValueError):
        advance_stamina(create_initial_stamina(), -0.1, carrying_document=False, in_regen_zone=False)
