from __future__ import annotations

from pathlib import Path

import pytest
import pygame

from game import config
from presentation.ui_assets import (
    StaminaColor,
    fishing_meter_rect,
    load_ui_assets,
    split_worm_timer_frames,
    split_fishing_meter,
    stamina_bar_rect,
    stamina_fill_width,
)


def test_user_interface_assets_have_expected_dimensions(pygame_display) -> None:
    for path, expected_size in (
        (config.UI_INTERACTION_BUTTON_ASSET_PATH, (128, 128)),
        (config.UI_STAMINA_BAR_ASSET_PATH, (320, 64)),
        (config.UI_GAME_OVER_ASSET_PATH, (1024, 256)),
        (config.WORM_TIMER_ASSET_PATH, (448, 32)),
    ):
        assert Path(path).is_file()

    assets = load_ui_assets()
    assert assets.interaction_button.get_size() == (128, 128)
    assert assets.stamina_frame.get_size() == (320, 32)
    assert assets.stamina_fill.get_size() == (320, 32)
    assert assets.game_over.get_size() == (1024, 256)
    assert len(assets.worm_timer_frames) == 7
    assert all(frame.get_size() == (64, 32) for frame in assets.worm_timer_frames)


def test_worm_timer_frames_preserve_left_to_right_order(pygame_display) -> None:
    sheet = pygame.Surface((448, 32), pygame.SRCALPHA)
    for index in range(7):
        sheet.fill((index, 0, 0, 255), pygame.Rect(index * 64, 0, 64, 32))

    frames = split_worm_timer_frames(sheet)
    assert [frame.get_at((0, 0))[0] for frame in frames] == list(range(7))


def test_stamina_color_variants_are_available(pygame_display) -> None:
    assets = load_ui_assets()
    for color in StaminaColor:
        assert assets.colorized_stamina_fill(color).get_size() == (320, 32)


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [(0.0, 0), (0.5, 152), (1.0, 304), (2.0, 304), (-1.0, 0)],
)
def test_stamina_fill_width_is_clamped_to_inner_frame(ratio: float, expected: int) -> None:
    assert stamina_fill_width(ratio, config.UI_STAMINA_INNER_WIDTH) == expected


@pytest.mark.parametrize("field", ["WAVE_REST_DURATION", "WORM_TIMER_FPS"])
def test_worm_timer_configuration_requires_positive_timing(monkeypatch, field: str) -> None:
    monkeypatch.setattr(config, field, 0.0)
    with pytest.raises(ValueError, match="must be positive"):
        config.validate_worm_timer_configuration()


def test_fishing_meter_sheet_splits_into_native_bar_and_six_icons(pygame_display) -> None:
    assets = load_ui_assets()
    assert assets.fishing_bar.get_size() == (64, 448)
    assert len(assets.fishing_icons) == 6
    assert all(icon.get_size() == (64, 64) for icon in assets.fishing_icons)


def test_fishing_meter_layout_is_native_and_centered() -> None:
    assert fishing_meter_rect((960, 640)) == pygame.Rect(416, 96, 128, 448)
    assert fishing_meter_rect((800, 600)).size == (128, 448)


def test_fishing_meter_split_rejects_wrong_dimensions(pygame_display) -> None:
    with pytest.raises(ValueError):
        split_fishing_meter(pygame.Surface((64, 448), pygame.SRCALPHA))


@pytest.mark.parametrize("scale", [0.5, 1.0, 1.5])
def test_stamina_bar_scale_changes_only_bar_rect(scale: float) -> None:
    rect = stamina_bar_rect((960, 640), (config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_BAR_HEIGHT), 16, scale)
    assert rect.left == 16
    assert rect.top == 16
    assert rect.width == round(config.UI_STAMINA_BAR_WIDTH * scale)
    assert rect.height == round(config.UI_STAMINA_BAR_HEIGHT * scale)


def test_stamina_bar_scale_must_be_positive() -> None:
    with pytest.raises(ValueError):
        stamina_bar_rect((960, 640), (320, 64), 16, 0)
