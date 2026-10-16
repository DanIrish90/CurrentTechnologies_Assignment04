"""Validated UserInterface assets and pure layout helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

import pygame

from game import config


class StaminaColor(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


_STAMINA_COLORS = {
    StaminaColor.GREEN: config.UI_STAMINA_GREEN_COLOR,
    StaminaColor.YELLOW: config.UI_STAMINA_YELLOW_COLOR,
    StaminaColor.RED: config.UI_STAMINA_RED_COLOR,
}


@dataclass(frozen=True, slots=True)
class UiAssets:
    interaction_button: pygame.Surface
    stamina_frame: pygame.Surface
    stamina_fill: pygame.Surface
    game_over: pygame.Surface

    def colorized_stamina_fill(self, color: StaminaColor) -> pygame.Surface:
        tinted = self.stamina_fill.copy()
        tinted.fill((*_STAMINA_COLORS[color], 255), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted


def _load(path: str, expected_size: tuple[int, int]) -> pygame.Surface:
    surface = pygame.image.load(path).convert_alpha()
    if surface.get_size() != expected_size:
        raise ValueError(f"{path} must be {expected_size[0]}x{expected_size[1]}")
    return surface


@lru_cache(maxsize=1)
def load_ui_assets() -> UiAssets:
    """Load and split the fixed UserInterface art once per process."""

    stamina = _load(config.UI_STAMINA_BAR_ASSET_PATH, (config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_BAR_HEIGHT))
    return UiAssets(
        interaction_button=_load(config.UI_INTERACTION_BUTTON_ASSET_PATH, (128, 128)),
        stamina_frame=stamina.subsurface((0, 0, config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_FRAME_HEIGHT)).copy(),
        stamina_fill=stamina.subsurface((0, config.UI_STAMINA_FRAME_HEIGHT, config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_FRAME_HEIGHT)).copy(),
        game_over=_load(config.UI_GAME_OVER_ASSET_PATH, (1024, 256)),
    )


def stamina_fill_width(ratio: float, inner_width: int) -> int:
    return round(max(0.0, min(1.0, ratio)) * inner_width)


def stamina_bar_rect(
    surface_size: tuple[int, int],
    asset_size: tuple[int, int],
    margin: int,
    scale: float = 1.0,
) -> pygame.Rect:
    if scale <= 0:
        raise ValueError("stamina bar scale must be positive")
    width, height = surface_size
    desired_size = (
        max(1, round(asset_size[0] * scale)),
        max(1, round(asset_size[1] * scale)),
    )
    fit = min(
        1.0,
        max(1, width - 2 * margin) / desired_size[0],
        max(1, height - 2 * margin) / desired_size[1],
    )
    size = (max(1, round(desired_size[0] * fit)), max(1, round(desired_size[1] * fit)))
    return pygame.Rect(margin, margin, *size)


def interaction_button_rect(
    surface_size: tuple[int, int], asset_size: tuple[int, int], margin: int
) -> pygame.Rect:
    width, height = surface_size
    lower_third_height = max(1, height // 3 - 2 * margin)
    available_width = max(1, width - 2 * margin)
    size = min(asset_size[0], asset_size[1], lower_third_height, available_width)
    lower_top = (height * 2) // 3
    bottom = height - margin
    center_y = (lower_top + bottom) // 2
    return pygame.Rect((width - size) // 2, center_y - size // 2, size, size)


def game_over_rect(
    surface_size: tuple[int, int], asset_size: tuple[int, int], margin: int
) -> pygame.Rect:
    width, height = surface_size
    available_width = max(1, width - 2 * margin)
    available_height = max(1, height - 2 * margin)
    scale = min(available_width / asset_size[0], available_height / asset_size[1])
    scaled_size = (max(1, round(asset_size[0] * scale)), max(1, round(asset_size[1] * scale)))
    return pygame.Rect(
        (width - scaled_size[0]) // 2,
        (height - scaled_size[1]) // 2,
        *scaled_size,
    )
