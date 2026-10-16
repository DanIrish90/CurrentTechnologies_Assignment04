"""Presentation-only loading and state-driven animation for Civil Servants."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable

import pygame

from game import config
from game.bureaucracy import CivilServant


class BureaucratAnimationKind(Enum):
    IDLE = "idle"
    PERMIT = "permit"


@dataclass(frozen=True, slots=True)
class BureaucratFrames:
    """Reusable native-size frames extracted from the Bureaucrat sheet."""

    rows: tuple[tuple[pygame.Surface, ...], ...]

    def frame(self, kind: BureaucratAnimationKind, frame_index: int) -> pygame.Surface:
        row = 0 if kind is BureaucratAnimationKind.IDLE else 1
        return self.rows[row][frame_index % config.BUREAUCRAT_SHEET_COLUMNS]


def split_bureaucrat_sheet(sheet: pygame.Surface) -> BureaucratFrames:
    """Split the expected 2x2 sheet into four independent frame surfaces."""

    expected_size = (
        config.BUREAUCRAT_SHEET_COLUMNS * config.BUREAUCRAT_FRAME_WIDTH,
        config.BUREAUCRAT_SHEET_ROWS * config.BUREAUCRAT_FRAME_HEIGHT,
    )
    if sheet.get_size() != expected_size:
        raise ValueError(
            f"Bureaucrat sheet must be {expected_size[0]}x{expected_size[1]}, "
            f"got {sheet.get_width()}x{sheet.get_height()}"
        )

    rows: list[tuple[pygame.Surface, ...]] = []
    for row in range(config.BUREAUCRAT_SHEET_ROWS):
        frames = tuple(
            sheet.subsurface(
                pygame.Rect(
                    column * config.BUREAUCRAT_FRAME_WIDTH,
                    row * config.BUREAUCRAT_FRAME_HEIGHT,
                    config.BUREAUCRAT_FRAME_WIDTH,
                    config.BUREAUCRAT_FRAME_HEIGHT,
                )
            ).copy()
            for column in range(config.BUREAUCRAT_SHEET_COLUMNS)
        )
        rows.append(frames)
    return BureaucratFrames(rows=tuple(rows))


def load_bureaucrat_frames(asset_path: str | Path | None = None) -> BureaucratFrames:
    """Load and split the Bureaucrat PNG once for a presentation session."""

    path = Path(asset_path or config.BUREAUCRAT_ASSET_PATH)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    return split_bureaucrat_sheet(pygame.image.load(path).convert_alpha())


def bureaucrat_sprite_rect(frame: pygame.Surface, target_rect: pygame.Rect) -> pygame.Rect:
    """Anchor a Bureaucrat frame to the existing target's center-bottom point."""

    return frame.get_rect(midbottom=target_rect.midbottom)


@dataclass(slots=True)
class BureaucratAnimationState:
    kind: BureaucratAnimationKind
    frame_index: int = 0
    elapsed: float = 0.0
    frame_duration: float = config.BUREAUCRAT_FRAME_DURATION

    def advance(self, elapsed_seconds: float) -> None:
        if elapsed_seconds < 0:
            raise ValueError("elapsed time must not be negative")
        self.elapsed += elapsed_seconds
        completed_frames = int(self.elapsed / self.frame_duration)
        if completed_frames:
            self.frame_index = (self.frame_index + completed_frames) % config.BUREAUCRAT_SHEET_COLUMNS
            self.elapsed -= completed_frames * self.frame_duration


@dataclass(slots=True)
class BureaucratAnimationManager:
    """Maintain one independent looping animation state per servant ID."""

    frames: BureaucratFrames
    states: dict[str, BureaucratAnimationState] = field(default_factory=dict)

    @staticmethod
    def _kind_for(servant: CivilServant) -> BureaucratAnimationKind:
        return BureaucratAnimationKind.PERMIT if servant.served else BureaucratAnimationKind.IDLE

    def update(self, servants: Iterable[CivilServant], elapsed_seconds: float) -> None:
        """Synchronize active servants and advance each loop independently."""

        if elapsed_seconds < 0:
            raise ValueError("elapsed time must not be negative")
        active_servants = tuple(servants)
        active_ids = {servant.id for servant in active_servants}
        self.states = {servant_id: state for servant_id, state in self.states.items() if servant_id in active_ids}

        for servant in active_servants:
            kind = self._kind_for(servant)
            state = self.states.get(servant.id)
            if state is None or state.kind is not kind:
                self.states[servant.id] = BureaucratAnimationState(kind=kind)
            else:
                state.advance(elapsed_seconds)

    def frame_for(self, servant_id: str) -> pygame.Surface:
        try:
            state = self.states[servant_id]
        except KeyError as error:
            raise KeyError(f"no animation state for servant {servant_id!r}") from error
        return self.frames.frame(state.kind, state.frame_index)
