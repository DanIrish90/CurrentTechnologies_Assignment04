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
    fishing_bar: pygame.Surface
    fishing_icons: tuple[pygame.Surface, ...]
    worm_timer_frames: tuple[pygame.Surface, ...]

    def colorized_stamina_fill(self, color: StaminaColor) -> pygame.Surface:
        tinted = self.stamina_fill.copy()
        tinted.fill((*_STAMINA_COLORS[color], 255), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted


def _load(path: str, expected_size: tuple[int, int]) -> pygame.Surface:
    surface = pygame.image.load(path).convert_alpha()
    if surface.get_size() != expected_size:
        raise ValueError(f"{path} must be {expected_size[0]}x{expected_size[1]}")
    return surface


def split_worm_timer_frames(surface: pygame.Surface) -> tuple[pygame.Surface, ...]:
    expected_size = (
        config.WORM_TIMER_FRAME_WIDTH * config.WORM_TIMER_FRAME_COUNT,
        config.WORM_TIMER_FRAME_HEIGHT,
    )
    if surface.get_size() != expected_size:
        raise ValueError(
            f"WormTimer sheet must be {expected_size[0]}x{expected_size[1]}"
        )
    return tuple(
        surface.subsurface(
            (
                index * config.WORM_TIMER_FRAME_WIDTH,
                0,
                config.WORM_TIMER_FRAME_WIDTH,
                config.WORM_TIMER_FRAME_HEIGHT,
            )
        ).copy()
        for index in range(config.WORM_TIMER_FRAME_COUNT)
    )


def split_fishing_meter(surface: pygame.Surface) -> tuple[pygame.Surface, tuple[pygame.Surface, ...]]:
    expected_size = (config.UI_FISHING_METER_WIDTH, config.UI_FISHING_METER_HEIGHT)
    if surface.get_size() != expected_size:
        raise ValueError(f"FishingMeter sheet must be {expected_size[0]}x{expected_size[1]}")
    bar = surface.subsurface((0, 0, config.UI_FISHING_BAR_WIDTH, config.UI_FISHING_METER_HEIGHT)).copy()
    icons = tuple(
        surface.subsurface(
            (
                config.UI_FISHING_BAR_WIDTH,
                index * config.UI_FISHING_ICON_SIZE,
                config.UI_FISHING_ICON_SIZE,
                config.UI_FISHING_ICON_SIZE,
            )
        ).copy()
        for index in range(config.UI_FISHING_ICON_COUNT)
    )
    return bar, icons


@lru_cache(maxsize=1)
def load_ui_assets() -> UiAssets:
    """Load and split the fixed UserInterface art once per process."""

    config.validate_worm_timer_configuration()
    config.validate_ui_configuration()
    stamina = _load(config.UI_STAMINA_BAR_ASSET_PATH, (config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_BAR_HEIGHT))
    worm_timer = _load(
        config.WORM_TIMER_ASSET_PATH,
        (
            config.WORM_TIMER_FRAME_WIDTH * config.WORM_TIMER_FRAME_COUNT,
            config.WORM_TIMER_FRAME_HEIGHT,
        ),
    )
    fishing_meter = _load(
        config.UI_FISHING_METER_ASSET_PATH,
        (config.UI_FISHING_METER_WIDTH, config.UI_FISHING_METER_HEIGHT),
    )
    fishing_bar, fishing_icons = split_fishing_meter(fishing_meter)
    return UiAssets(
        interaction_button=_load(config.UI_INTERACTION_BUTTON_ASSET_PATH, (128, 128)),
        stamina_frame=stamina.subsurface((0, 0, config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_FRAME_HEIGHT)).copy(),
        stamina_fill=stamina.subsurface((0, config.UI_STAMINA_FRAME_HEIGHT, config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_FRAME_HEIGHT)).copy(),
        game_over=_load(config.UI_GAME_OVER_ASSET_PATH, (1024, 256)),
        fishing_bar=fishing_bar,
        fishing_icons=fishing_icons,
        worm_timer_frames=split_worm_timer_frames(worm_timer),
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


def worm_timer_rect(
    surface_size: tuple[int, int],
    stamina_rect: pygame.Rect,
    frame_size: tuple[int, int],
    progress: float,
    gap: int = 2,
) -> pygame.Rect:
    """Place a WormTimer frame below the stamina bar along its width."""

    width, height = surface_size
    normalized = max(0.0, min(1.0, progress))
    scale = stamina_rect.width / config.UI_STAMINA_BAR_WIDTH
    scaled_size = (
        max(1, round(frame_size[0] * scale)),
        max(1, round(frame_size[1] * scale)),
    )
    travel = max(0, stamina_rect.width - scaled_size[0])
    x = stamina_rect.left + round(travel * normalized)
    y = stamina_rect.bottom + gap
    return pygame.Rect(
        max(0, min(x, width - scaled_size[0])),
        max(0, min(y, height - scaled_size[1])),
        *scaled_size,
    )


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


def fishing_meter_rect(surface_size: tuple[int, int]) -> pygame.Rect:
    width, height = surface_size
    return pygame.Rect(
        max(0, (width - config.UI_FISHING_METER_WIDTH) // 2),
        max(0, (height - config.UI_FISHING_METER_HEIGHT) // 2),
        config.UI_FISHING_METER_WIDTH,
        config.UI_FISHING_METER_HEIGHT,
    )
