from __future__ import annotations

import pytest

from presentation.ui_assets import (
    game_over_rect,
    interaction_button_rect,
    stamina_bar_rect,
)


def test_interaction_button_is_centered_in_lower_third() -> None:
    rect = interaction_button_rect((480, 320), (128, 128), 16)
    assert rect.centerx == 240
    assert 320 * 2 / 3 <= rect.centery <= 320
    assert rect.bottom <= 320 - 16


def test_stamina_bar_is_top_left_with_margin() -> None:
    rect = stamina_bar_rect((480, 320), (320, 64), 16)
    assert rect.topleft == (16, 16)
    assert rect.right <= 480
    assert rect.bottom <= 320


def test_stamina_bar_scale_is_positive_and_independent() -> None:
    normal = stamina_bar_rect((960, 640), (320, 64), 16, 1.0)
    half = stamina_bar_rect((960, 640), (320, 64), 16, 0.5)
    enlarged = stamina_bar_rect((960, 640), (320, 64), 16, 1.5)

    assert normal.size == (320, 64)
    assert half.size == (160, 32)
    assert enlarged.size == (480, 96)
    assert half.topleft == enlarged.topleft == normal.topleft == (16, 16)
    with pytest.raises(ValueError):
        stamina_bar_rect((960, 640), (320, 64), 16, 0)


def test_game_over_is_contained_and_centered() -> None:
    rect = game_over_rect((480, 320), (1024, 256), 16)
    assert rect.center == (240, 160)
    assert rect.left >= 16
    assert rect.right <= 480 - 16
    assert rect.top >= 16
    assert rect.bottom <= 320 - 16


@pytest.mark.parametrize("surface_size", [(960, 640), (800, 600), (1280, 720)])
def test_all_ui_layouts_fit_reference_windows(surface_size: tuple[int, int]) -> None:
    width, height = surface_size
    interaction = interaction_button_rect(surface_size, (128, 128), 16)
    stamina = stamina_bar_rect(surface_size, (320, 64), 16)
    game_over = game_over_rect(surface_size, (1024, 256), 16)

    assert interaction.centerx == width // 2
    assert 2 * height / 3 <= interaction.centery <= height
    assert interaction.left >= 16
    assert interaction.right <= width - 16
    assert interaction.bottom <= height - 16
    assert stamina.topleft == (16, 16)
    assert stamina.right <= width - 16
    assert stamina.bottom <= height - 16
    assert game_over.center == (width // 2, height // 2)
    assert game_over.left >= 16
    assert game_over.right <= width - 16
    assert game_over.top >= 16
    assert game_over.bottom <= height - 16
