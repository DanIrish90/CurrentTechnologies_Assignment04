from __future__ import annotations

from game.bureaucracy import (
    DocumentType,
    HandoverReason,
    WorkflowPhase,
    collect_initial_document,
    handover,
)


def test_wave_one_collects_and_accepts_initial_document(wave_one_progress) -> None:
    collected, collection_result = collect_initial_document(wave_one_progress)
    assert collection_result.accepted
    assert collected.carried_document is not None
    assert collected.carried_document.document_type is DocumentType.INITIAL_DOCUMENT

    completed, result = handover(collected, "servant-1")
    assert result.accepted
    assert result.reason is HandoverReason.ACCEPTED
    assert result.wave_completed
    assert completed.carried_document is None
    assert completed.phase is WorkflowPhase.COMPLETION_FEEDBACK
    assert completed.definition.servants[0].served


def test_collection_is_not_available_while_carrying_document(wave_one_progress) -> None:
    carrying, _ = collect_initial_document(wave_one_progress)
    unchanged, result = collect_initial_document(carrying)
    assert not result.accepted
    assert result.reason is HandoverReason.ALREADY_CARRYING
    assert unchanged.carried_document == carrying.carried_document


def test_wave_two_issues_permit_then_accepts_it(wave_two_progress) -> None:
    carrying, _ = collect_initial_document(wave_two_progress)
    after_first, first_result = handover(carrying, "servant-1")
    assert first_result.accepted
    assert first_result.issued_document is not None
    assert first_result.issued_document.document_type is DocumentType.PERMIT
    assert after_first.carried_document == first_result.issued_document
    assert after_first.definition.servants[0].served
    assert not after_first.definition.servants[1].served

    completed, second_result = handover(after_first, "servant-2")
    assert second_result.accepted
    assert second_result.wave_completed
    assert completed.carried_document is None
    assert all(servant.served for servant in completed.definition.servants)


def test_wave_two_rejects_permit_back_to_already_served_servant(wave_two_progress) -> None:
    carrying, _ = collect_initial_document(wave_two_progress)
    after_first, _ = handover(carrying, "servant-1")
    unchanged, result = handover(after_first, "servant-1")
    assert not result.accepted
    assert result.reason is HandoverReason.ALREADY_SERVED
    assert unchanged.carried_document == after_first.carried_document
