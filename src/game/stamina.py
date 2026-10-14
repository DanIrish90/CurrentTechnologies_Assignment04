"""Deterministic stamina rules independent of rendering and input devices."""

from __future__ import annotations

from dataclasses import dataclass, replace

from . import config


@dataclass(frozen=True, slots=True)
class StaminaState:
    current: float = config.STAMINA_MAXIMUM
    maximum: float = config.STAMINA_MAXIMUM
    drain_rate: float = config.STAMINA_DRAIN_RATE
    regen_rate: float = config.STAMINA_REGEN_RATE
    game_over: bool = False

    def __post_init__(self) -> None:
        if self.maximum <= 0:
            raise ValueError("stamina maximum must be positive")
        if self.drain_rate < 0 or self.regen_rate < 0:
            raise ValueError("stamina rates must not be negative")
        if not 0 <= self.current <= self.maximum:
            raise ValueError("stamina current value must be within bounds")
        if self.current == 0 and not self.game_over:
            raise ValueError("zero stamina must be game over")


def create_initial_stamina() -> StaminaState:
    return StaminaState()


def advance_stamina(
    state: StaminaState,
    elapsed_seconds: float,
    *,
    carrying_document: bool,
    in_regen_zone: bool,
) -> StaminaState:
    """Apply one elapsed simulation interval to stamina."""

    if elapsed_seconds < 0:
        raise ValueError("elapsed time must not be negative")
    if state.game_over:
        return state
    if carrying_document:
        delta = -state.drain_rate * elapsed_seconds
    elif in_regen_zone:
        delta = state.regen_rate * elapsed_seconds
    else:
        delta = 0.0
    current = max(0.0, min(state.maximum, state.current + delta))
    return replace(state, current=current, game_over=current == 0.0)
