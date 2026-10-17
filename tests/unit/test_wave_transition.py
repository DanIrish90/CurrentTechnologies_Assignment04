from __future__ import annotations

from game.bureaucracy import (
    WorkflowPhase,
    advance_progress,
    collect_initial_document,
    handover,
)
from game import config


def complete_wave_one(progress):
    carrying, _ = collect_initial_document(progress)
    completed, _ = handover(carrying, "servant-1")
    return completed


def test_transition_does_not_start_before_configured_duration(wave_one_progress) -> None:
    completed = complete_wave_one(wave_one_progress)
    progressing = advance_progress(completed, config.WAVE_REST_DURATION - 0.01)
    assert progressing.phase is WorkflowPhase.TRANSITIONING
    assert progressing.definition.wave_number == 1
    assert progressing.transition_remaining > 0


def test_transition_starts_next_wave_at_configured_duration(wave_one_progress) -> None:
    completed = complete_wave_one(wave_one_progress)
    next_wave = advance_progress(completed, config.WAVE_REST_DURATION)
    assert next_wave.phase is WorkflowPhase.ACTIVE
    assert next_wave.definition.wave_number == 2
    assert len(next_wave.definition.servants) == 2


def test_transition_never_reports_negative_remaining_time(wave_one_progress) -> None:
    completed = complete_wave_one(wave_one_progress)
    next_wave = advance_progress(completed, 999.0)
    assert next_wave.transition_remaining == 0.0
    assert next_wave.definition.wave_number == 2


def test_transition_uses_configurable_rest_duration(monkeypatch, wave_one_progress) -> None:
    monkeypatch.setattr(config, "WAVE_REST_DURATION", 4.0)
    completed = complete_wave_one(wave_one_progress)

    assert completed.transition_remaining == 4.0
    assert advance_progress(completed, 3.99).phase is WorkflowPhase.TRANSITIONING
    assert advance_progress(completed, 4.0).definition.wave_number == 2
