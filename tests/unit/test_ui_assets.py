from __future__ import annotations

from pathlib import Path

import pytest

from game import config
from presentation.ui_assets import (
    StaminaColor,
    load_ui_assets,
    stamina_fill_width,
)


def test_user_interface_assets_have_expected_dimensions(pygame_display) -> None:
    for path, expected_size in (
        (config.UI_INTERACTION_BUTTON_ASSET_PATH, (128, 128)),
        (config.UI_STAMINA_BAR_ASSET_PATH, (320, 64)),
        (config.UI_GAME_OVER_ASSET_PATH, (1024, 256)),
    ):
        assert Path(path).is_file()

    assets = load_ui_assets()
    assert assets.interaction_button.get_size() == (128, 128)
    assert assets.stamina_frame.get_size() == (320, 32)
    assert assets.stamina_fill.get_size() == (320, 32)
    assert assets.game_over.get_size() == (1024, 256)


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
