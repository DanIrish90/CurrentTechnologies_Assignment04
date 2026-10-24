"""Pure, deterministic wave and document workflow state transitions.

This module intentionally has no Pygame dependency. The presentation layer decides
which world target is in interaction range and calls these transitions explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import random
from typing import Callable

from . import config
from .geometry import Vector2


class DocumentType(Enum):
    INITIAL_DOCUMENT = "initial-document"
    PERMIT = "permit"


class SourceKind(Enum):
    CENTRAL_SOURCE = "central-source"
    PREVIOUS_HANDOVER = "previous-handover"


class WorkflowPhase(Enum):
    ACTIVE = "active"
    COMPLETION_FEEDBACK = "completion-feedback"
    TRANSITIONING = "transitioning"


class HandoverReason(Enum):
    ACCEPTED = "accepted"
    NO_DOCUMENT = "no-document"
    WRONG_DOCUMENT = "wrong-document"
    OUT_OF_ORDER = "out-of-order"
    ALREADY_SERVED = "already-served"
    ALREADY_CARRYING = "already-carrying"
    NO_DOCUMENT_AVAILABLE = "no-document-available"
    INACTIVE = "inactive"


@dataclass(frozen=True, slots=True)
class Feedback:
    message: str
    success: bool


@dataclass(frozen=True, slots=True)
class Document:
    document_type: DocumentType
    workflow_id: str
    intended_servant_id: str | None = None
    issued_by_servant_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    order: int
    servant_id: str
    required_document_type: DocumentType
    required_source: SourceKind = SourceKind.CENTRAL_SOURCE
    issued_document_type: DocumentType | None = None
    served: bool = False


@dataclass(frozen=True, slots=True)
class CivilServant:
    id: str
    display_name: str
    position: Vector2
    step_order: int
    served: bool = False


@dataclass(frozen=True, slots=True)
class WaveDefinition:
    wave_number: int
    steps: tuple[WorkflowStep, ...]
    servants: tuple[CivilServant, ...]


@dataclass(frozen=True, slots=True)
class WaveProgress:
    definition: WaveDefinition
    carried_document: Document | None = None
    feedback: Feedback = Feedback("Find the requested document.", False)
    phase: WorkflowPhase = WorkflowPhase.ACTIVE
    transition_remaining: float = 0.0

    @property
    def current_step(self) -> WorkflowStep | None:
        return next((step for step in self.definition.steps if not step.served), None)

    @property
    def wave_completed(self) -> bool:
        return self.current_step is None


@dataclass(frozen=True, slots=True)
class HandoverResult:
    accepted: bool
    reason: HandoverReason
    feedback: Feedback
    issued_document: Document | None = None
    wave_completed: bool = False


def validate_wave(wave: WaveDefinition) -> None:
    """Reject definitions that cannot represent a complete ordered workflow."""

    if wave.wave_number <= 0:
        raise ValueError("wave number must be positive")
    expected_servants = min(wave.wave_number, config.MAX_CIVIL_SERVANTS)
    if len(wave.steps) != wave.wave_number or len(wave.servants) != expected_servants:
        raise ValueError("wave must contain exactly N steps and min(N, four) servants")
    servant_ids = [servant.id for servant in wave.servants]
    if len(servant_ids) != len(set(servant_ids)):
        raise ValueError("servant identifiers must be unique")
    orders = [step.order for step in wave.steps]
    if orders != list(range(1, wave.wave_number + 1)):
        raise ValueError("workflow step orders must be contiguous")
    step_ids = [step.servant_id for step in wave.steps]
    if not set(step_ids).issubset(set(servant_ids)):
        raise ValueError("every workflow step must identify an active wave servant")
    for index, step in enumerate(wave.steps):
        if index == 0 and step.required_source is not SourceKind.CENTRAL_SOURCE:
            raise ValueError("the first workflow step must use the central source")
        if index > 0:
            previous = wave.steps[index - 1]
            if step.required_source is not SourceKind.PREVIOUS_HANDOVER:
                raise ValueError("later workflow steps must use the previous handover")
            if previous.issued_document_type is not step.required_document_type:
                raise ValueError("every later requirement must be issued by its previous step")
    if wave.steps[-1].issued_document_type is not None:
        raise ValueError("the final workflow step must not issue an unresolved document")


def create_wave(
    wave_number: int,
    positions: tuple[Vector2, ...] | None = None,
    *,
    random_seed: int | None = None,
    rng: random.Random | None = None,
) -> WaveDefinition:
    """Create a solvable wave with N handovers and at most four servants.

    The first four recipients remain ordered. Later recipients are selected from
    the three identities other than the previous recipient. Supplying a seed or
    RNG makes the random continuation reproducible for tests.
    """

    if wave_number <= 0:
        raise ValueError("wave number must be positive")
    servant_count = min(wave_number, config.MAX_CIVIL_SERVANTS)
    servant_positions = positions or tuple(
        Vector2(850 + index * 220, 170 + (index % 2) * 220)
        for index in range(servant_count)
    )
    if len(servant_positions) != servant_count:
        raise ValueError("one position is required for each active wave servant")
    servants = tuple(
        CivilServant(
            id=f"servant-{index + 1}",
            display_name=f"Civil Servant {index + 1}",
            position=position,
            step_order=index + 1,
        )
        for index, position in enumerate(servant_positions)
    )
    servant_ids = tuple(servant.id for servant in servants)
    generator = rng or random.Random(random_seed)
    recipients: list[str] = []
    for index in range(wave_number):
        if index < servant_count:
            recipient = servant_ids[index]
        else:
            candidates = [servant_id for servant_id in servant_ids if servant_id != recipients[-1]]
            recipient = generator.choice(candidates)
        recipients.append(recipient)
    steps = tuple(
        WorkflowStep(
            order=index + 1,
            servant_id=recipients[index],
            required_document_type=(
                DocumentType.INITIAL_DOCUMENT if index == 0 else DocumentType.PERMIT
            ),
            required_source=(
                SourceKind.CENTRAL_SOURCE if index == 0 else SourceKind.PREVIOUS_HANDOVER
            ),
            issued_document_type=(DocumentType.PERMIT if index < wave_number - 1 else None),
        )
        for index in range(wave_number)
    )
    wave = WaveDefinition(wave_number, steps, servants)
    validate_wave(wave)
    return wave


def create_wave_progress(wave: WaveDefinition) -> WaveProgress:
    validate_wave(wave)
    return WaveProgress(
        definition=wave,
        feedback=Feedback(f"Wave {wave.wave_number}: find the requested document.", False),
    )


def _result(
    progress: WaveProgress,
    reason: HandoverReason,
    message: str,
    *,
    accepted: bool = False,
    issued_document: Document | None = None,
    wave_completed: bool = False,
) -> tuple[WaveProgress, HandoverResult]:
    feedback = Feedback(message, accepted)
    updated = replace(progress, feedback=feedback)
    return updated, HandoverResult(accepted, reason, feedback, issued_document, wave_completed)


def collect_initial_document(progress: WaveProgress) -> tuple[WaveProgress, HandoverResult]:
    """Collect the current initial document from the central source."""

    if progress.phase is not WorkflowPhase.ACTIVE:
        return _result(progress, HandoverReason.INACTIVE, "This wave is not accepting documents.")
    if progress.carried_document is not None:
        return _result(
            progress,
            HandoverReason.ALREADY_CARRYING,
            "You are already carrying a document.",
        )
    step = progress.current_step
    if step is None or step.required_source is not SourceKind.CENTRAL_SOURCE:
        return _result(
            progress,
            HandoverReason.NO_DOCUMENT_AVAILABLE,
            "No document is available from the central source right now.",
        )
    document = Document(
        document_type=step.required_document_type,
        workflow_id=f"wave-{progress.definition.wave_number}",
        intended_servant_id=step.servant_id,
    )
    updated = replace(
        progress,
        carried_document=document,
        feedback=Feedback(f"Collected the document for {step.servant_id}.", True),
    )
    return updated, HandoverResult(
        True,
        HandoverReason.ACCEPTED,
        updated.feedback,
        issued_document=document,
    )


def handover(progress: WaveProgress, servant_id: str) -> tuple[WaveProgress, HandoverResult]:
    """Attempt an explicit handover to one Civil Servant."""

    if progress.phase is not WorkflowPhase.ACTIVE:
        return _result(progress, HandoverReason.INACTIVE, "This wave is not accepting handovers.")
    if progress.carried_document is None:
        return _result(progress, HandoverReason.NO_DOCUMENT, "You need a document before serving anyone.")
    step = progress.current_step
    if step is None:
        return _result(progress, HandoverReason.INACTIVE, "This wave is already complete.")
    if servant_id != step.servant_id:
        servant = next((servant for servant in progress.definition.servants if servant.id == servant_id), None)
        if servant is not None and servant.served:
            return _result(progress, HandoverReason.ALREADY_SERVED, f"{servant.display_name} is already served.")
        return _result(progress, HandoverReason.OUT_OF_ORDER, f"Serve {step.servant_id} next.")
    document = progress.carried_document
    if (
        document.document_type is not step.required_document_type
        or document.intended_servant_id != servant_id
    ):
        return _result(progress, HandoverReason.WRONG_DOCUMENT, f"{servant_id} needs {step.required_document_type.value}.")

    steps = tuple(replace(item, served=True) if item.order == step.order else item for item in progress.definition.steps)
    servants = tuple(replace(item, served=True) if item.id == servant_id else item for item in progress.definition.servants)
    definition = replace(progress.definition, steps=steps, servants=servants)
    issued_document = None
    if step.issued_document_type is not None:
        next_step = next(item for item in steps if not item.served)
        issued_document = Document(
            document_type=step.issued_document_type,
            workflow_id=f"wave-{definition.wave_number}",
            intended_servant_id=next_step.servant_id,
            issued_by_servant_id=servant_id,
        )
    completed = all(item.served for item in steps)
    updated = replace(
        progress,
        definition=definition,
        carried_document=issued_document,
        feedback=Feedback(
            f"{servant_id} served." + (" Permit issued." if issued_document else " Wave complete." if completed else ""),
            True,
        ),
        phase=WorkflowPhase.COMPLETION_FEEDBACK if completed else WorkflowPhase.ACTIVE,
        transition_remaining=config.WAVE_REST_DURATION if completed else 0.0,
    )
    return updated, HandoverResult(
        True,
        HandoverReason.ACCEPTED,
        updated.feedback,
        issued_document,
        completed,
    )


def advance_progress(
    progress: WaveProgress,
    elapsed_seconds: float,
    next_wave_factory: Callable[[int], WaveDefinition] = create_wave,
) -> WaveProgress:
    """Advance completion feedback and start the next wave at ten seconds."""

    if elapsed_seconds < 0:
        raise ValueError("elapsed time must not be negative")
    if progress.phase is WorkflowPhase.ACTIVE:
        return progress
    remaining = max(progress.transition_remaining - elapsed_seconds, 0.0)
    if remaining > 0:
        return replace(progress, phase=WorkflowPhase.TRANSITIONING, transition_remaining=remaining)
    return create_wave_progress(next_wave_factory(progress.definition.wave_number + 1))
