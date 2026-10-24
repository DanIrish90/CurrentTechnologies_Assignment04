from __future__ import annotations

import pytest

from game.bureaucracy import (
    CivilServant,
    DocumentType,
    WaveDefinition,
    WorkflowStep,
    create_wave,
    validate_wave,
)
from game.geometry import Vector2


def test_wave_one_has_one_ordered_servant() -> None:
    wave = create_wave(1)
    assert wave.wave_number == 1
    assert len(wave.servants) == 1
    assert len(wave.steps) == 1
    assert wave.steps[0].order == 1
    assert wave.steps[0].required_document_type is DocumentType.INITIAL_DOCUMENT


def test_wave_two_has_two_ordered_servants() -> None:
    wave = create_wave(2)
    assert len(wave.servants) == 2
    assert [step.order for step in wave.steps] == [1, 2]
    assert wave.steps[0].issued_document_type is DocumentType.PERMIT
    assert wave.steps[1].required_document_type is DocumentType.PERMIT


def test_invalid_wave_with_duplicate_servant_ids_is_rejected() -> None:
    servant = CivilServant("servant-1", "Civil Servant 1", Vector2(1, 1), 1)
    steps = (
        WorkflowStep(1, "servant-1", DocumentType.INITIAL_DOCUMENT),
        WorkflowStep(2, "servant-1", DocumentType.PERMIT),
    )
    invalid = WaveDefinition(2, steps, (servant, servant))
    with pytest.raises(ValueError):
        validate_wave(invalid)


def test_wave_count_is_capped_at_four_servants_but_steps_continue() -> None:
    counts = [len(create_wave(number).servants) for number in range(1, 7)]
    steps = [len(create_wave(number).steps) for number in range(1, 7)]
    positions = tuple(Vector2(index * 10, index * 20) for index in range(4))
    capped_wave = create_wave(6, positions)

    assert counts == [1, 2, 3, 4, 4, 4]
    assert steps == [1, 2, 3, 4, 5, 6]
    assert tuple(servant.position for servant in capped_wave.servants) == positions


def test_random_wave_route_is_seeded_and_excludes_previous_recipient() -> None:
    first = create_wave(8, random_seed=17)
    second = create_wave(8, random_seed=17)
    recipients = [step.servant_id for step in first.steps]

    assert recipients == [step.servant_id for step in second.steps]
    assert recipients[:4] == ["servant-1", "servant-2", "servant-3", "servant-4"]
    assert all(current != previous for previous, current in zip(recipients, recipients[1:]))
    assert set(recipients).issubset({"servant-1", "servant-2", "servant-3", "servant-4"})
