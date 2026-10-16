"""Presentation-only loading and animation for the main character."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pygame

from game import config
from game.geometry import Vector2


class CharacterDirection(Enum):
    """The last valid facing direction of the character."""

    UP = "up"
    DOWN = "down"
    RIGHT = "right"
    LEFT = "left"


@dataclass(frozen=True, slots=True)
class CharacterFrames:
    """Source and mirrored frames extracted from the walking sheet."""

    rows: tuple[tuple[pygame.Surface, ...], ...]
    mirrored_side: tuple[pygame.Surface, ...]

    def frame(self, direction: CharacterDirection, frame_index: int) -> pygame.Surface:
        index = frame_index % config.CHARACTER_SHEET_COLUMNS
        if direction is CharacterDirection.RIGHT:
            return self.mirrored_side[index]
        row = {
            CharacterDirection.UP: 0,
            CharacterDirection.DOWN: 1,
            CharacterDirection.LEFT: 2,
        }.get(direction)
        if row is None:
            raise ValueError(f"unsupported direction: {direction}")
        return self.rows[row][index]


def split_character_sheet(sheet: pygame.Surface) -> CharacterFrames:
    """Split and pixel-scale a 4x3 walking sheet into reusable frames."""

    expected_size = (
        config.CHARACTER_SHEET_COLUMNS * config.CHARACTER_FRAME_WIDTH,
        config.CHARACTER_SHEET_ROWS * config.CHARACTER_FRAME_HEIGHT,
    )
    if sheet.get_size() != expected_size:
        raise ValueError(
            f"character asset must be {expected_size[0]}x{expected_size[1]}, "
            f"got {sheet.get_width()}x{sheet.get_height()}"
        )

    rows: list[tuple[pygame.Surface, ...]] = []
    for row in range(config.CHARACTER_SHEET_ROWS):
        frames = tuple(
            pygame.transform.scale(
                sheet.subsurface(
                    pygame.Rect(
                        column * config.CHARACTER_FRAME_WIDTH,
                        row * config.CHARACTER_FRAME_HEIGHT,
                        config.CHARACTER_FRAME_WIDTH,
                        config.CHARACTER_FRAME_HEIGHT,
                    )
                ).copy(),
                (config.ACTOR_SCALED_FRAME_WIDTH, config.ACTOR_SCALED_FRAME_HEIGHT),
            )
            for column in range(config.CHARACTER_SHEET_COLUMNS)
        )
        rows.append(frames)

    mirrored_side = tuple(pygame.transform.flip(frame, True, False) for frame in rows[2])
    return CharacterFrames(rows=tuple(rows), mirrored_side=mirrored_side)


def load_character_frames(asset_path: str | Path | None = None) -> CharacterFrames:
    """Load and split the character asset once for a presentation session."""

    path = Path(asset_path or config.CHARACTER_ASSET_PATH)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    sheet = pygame.image.load(path).convert_alpha()
    return split_character_sheet(sheet)


def character_sprite_rect(frame: pygame.Surface, player_rect: pygame.Rect) -> pygame.Rect:
    """Anchor a visual frame to the logical player's center-bottom point."""

    return frame.get_rect(midbottom=player_rect.midbottom)


def direction_from_displacement(displacement: Vector2, previous: CharacterDirection) -> CharacterDirection:
    """Choose the dominant-axis facing direction, preserving idle facing."""

    if displacement.x == 0 and displacement.y == 0:
        return previous
    if abs(displacement.y) >= abs(displacement.x):
        return CharacterDirection.UP if displacement.y < 0 else CharacterDirection.DOWN
    return CharacterDirection.LEFT if displacement.x < 0 else CharacterDirection.RIGHT


@dataclass(slots=True)
class CharacterAnimator:
    """Mutable presentation state for one character animation instance."""

    frames: CharacterFrames
    direction: CharacterDirection = CharacterDirection.DOWN
    frame_index: int = 0
    elapsed: float = 0.0
    frame_duration: float = config.CHARACTER_FRAME_DURATION

    def update(self, previous_position: Vector2, current_position: Vector2, elapsed_seconds: float) -> None:
        """Advance animation from actual resolved player movement."""

        if elapsed_seconds < 0:
            raise ValueError("elapsed time must not be negative")
        displacement = current_position - previous_position
        moving = displacement.x != 0 or displacement.y != 0
        if not moving:
            self.frame_index = 0
            self.elapsed = 0.0
            return

        self.direction = direction_from_displacement(displacement, self.direction)
        self.elapsed += elapsed_seconds
        completed_frames = int(self.elapsed / self.frame_duration)
        if completed_frames:
            self.frame_index = (self.frame_index + completed_frames) % config.CHARACTER_SHEET_COLUMNS
            self.elapsed -= completed_frames * self.frame_duration

    @property
    def current_frame(self) -> pygame.Surface:
        return self.frames.frame(self.direction, self.frame_index)
