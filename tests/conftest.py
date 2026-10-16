"""Reusable display-independent fixtures for game-rule tests."""

from __future__ import annotations

import pytest
import pygame

from game.geometry import Vector2
from game.input_state import InputState
from game.world import Player, World, create_initial_world
from game.bureaucracy import (
    WorkflowPhase,
    collect_initial_document,
    create_wave,
    create_wave_progress,
    handover,
)
from game.stamina import StaminaState, create_initial_stamina
from game.fishing import FishingState, create_fishing_state


@pytest.fixture
def pygame_display():
    """Provide a shared display/font lifecycle for headless Pygame tests."""

    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.font.quit()
    pygame.display.quit()


@pytest.fixture
def player() -> Player:
    return Player(position=Vector2(100.0, 100.0), size=Vector2(8.0, 10.0), speed=240.0)


@pytest.fixture
def world() -> World:
    return create_initial_world()


@pytest.fixture
def idle_input() -> InputState:
    return InputState()


@pytest.fixture
def wave_one_progress():
    return create_wave_progress(create_wave(1))


@pytest.fixture
def wave_two_progress():
    return create_wave_progress(create_wave(2))


@pytest.fixture
def full_stamina() -> StaminaState:
    return create_initial_stamina()


@pytest.fixture
def idle_fishing() -> FishingState:
    return create_fishing_state()


@pytest.fixture
def completed_wave_rest(wave_one_progress):
    carrying, _ = collect_initial_document(wave_one_progress)
    completed, _ = handover(carrying, "servant-1")
    return completed


@pytest.fixture
def transitioning_wave_rest(completed_wave_rest):
    return completed_wave_rest.__class__(
        definition=completed_wave_rest.definition,
        carried_document=completed_wave_rest.carried_document,
        feedback=completed_wave_rest.feedback,
        phase=WorkflowPhase.TRANSITIONING,
        transition_remaining=5.0,
    )
