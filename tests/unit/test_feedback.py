from __future__ import annotations

from dataclasses import replace

from game.bureaucracy import Document, DocumentType, HandoverReason, collect_initial_document, handover


def test_missing_document_feedback_preserves_progress(wave_one_progress) -> None:
    unchanged, result = handover(wave_one_progress, "servant-1")
    assert not result.accepted
    assert result.reason is HandoverReason.NO_DOCUMENT
    assert unchanged.definition == wave_one_progress.definition
    assert unchanged.carried_document == wave_one_progress.carried_document
    assert unchanged.phase == wave_one_progress.phase


def test_wrong_document_feedback_preserves_carried_document(wave_two_progress) -> None:
    carrying, _ = collect_initial_document(wave_two_progress)
    unchanged, result = handover(carrying, "servant-2")
    assert not result.accepted
    assert result.reason is HandoverReason.OUT_OF_ORDER
    assert unchanged.carried_document == carrying.carried_document


def test_wrong_document_type_is_rejected_without_consumption(wave_one_progress) -> None:
    carrying, _ = collect_initial_document(wave_one_progress)
    wrong = Document(
        document_type=DocumentType.PERMIT,
        workflow_id=carrying.carried_document.workflow_id,
        intended_servant_id="servant-1",
    )
    carrying = replace(carrying, carried_document=wrong)
    unchanged, result = handover(carrying, "servant-1")
    assert not result.accepted
    assert result.reason is HandoverReason.WRONG_DOCUMENT
    assert unchanged.carried_document == wrong
