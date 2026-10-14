"""Pure, deterministic rules for the fishing mini-game."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from . import config


class FishingPhase(str, Enum):
    IDLE = "idle"
    WAITING_FOR_BITE = "waiting_for_bite"
    BITE_WINDOW = "bite_window"
    CATCHING = "catching"


@dataclass(frozen=True, slots=True)
class FishingState:
    phase: FishingPhase = FishingPhase.IDLE
    phase_elapsed: float = 0.0
    catch_bar_position: float = config.FISH_INITIAL_CATCH_BAR_POSITION
    catch_bar_height: float = config.FISH_CATCH_BAR_HEIGHT
    catch_bar_velocity: float = 0.0
    time_since_last_press: float = 0.0
    fish_position: float = config.FISH_INITIAL_POSITION
    fish_velocity: float = config.FISH_MOTION_SPEED
    fishing_progress: float = 0.0
    reward_awarded: bool = False
    feedback: str = "Ready to fish."

    def __post_init__(self) -> None:
        if self.phase_elapsed < 0:
            raise ValueError("fishing phase elapsed time must not be negative")
        if self.time_since_last_press < 0:
            raise ValueError("catch-bar elapsed time must not be negative")
        if abs(self.catch_bar_velocity) > config.FISH_CATCH_BAR_MAX_SPEED:
            raise ValueError("catch-bar velocity must remain within its speed limit")
        if self.catch_bar_height <= 0 or self.catch_bar_height > config.FISH_PLAY_HEIGHT:
            raise ValueError("catch bar height must fit within fishing play height")
        if not 0 <= self.catch_bar_position <= config.FISH_PLAY_HEIGHT - self.catch_bar_height:
            raise ValueError("catch bar position must remain within fishing play bounds")
        if not 0 <= self.fish_position <= config.FISH_PLAY_HEIGHT:
            raise ValueError("fish position must remain within fishing play bounds")
        if not 0 <= self.fishing_progress <= 100:
            raise ValueError("fishing progress must remain between zero and one hundred")


@dataclass(frozen=True, slots=True)
class FishingOutcome:
    accepted: bool = False
    caught: bool = False
    stamina_reward: float = 0.0
    message: str = ""


def create_fishing_state() -> FishingState:
    return FishingState()


def _outcome(message: str, *, accepted: bool = False, caught: bool = False) -> FishingOutcome:
    return FishingOutcome(
        accepted=accepted,
        caught=caught,
        stamina_reward=config.FISH_STAMINA_REWARD if caught else 0.0,
        message=message,
    )


def _reset(state: FishingState, message: str, *, caught: bool = False) -> tuple[FishingState, FishingOutcome]:
    reset = replace(create_fishing_state(), feedback=message)
    return reset, _outcome(message, accepted=True, caught=caught)


def start_cast(state: FishingState, *, eligible: bool) -> tuple[FishingState, FishingOutcome]:
    if state.phase is not FishingPhase.IDLE:
        return state, _outcome("Fishing attempt already active.")
    if not eligible:
        return state, _outcome("You must stand in the Fishing Pond with empty hands.")
    return replace(state, phase=FishingPhase.WAITING_FOR_BITE, phase_elapsed=0.0, feedback="Waiting for a bite..."), _outcome("Cast started.", accepted=True)


def _move_fish(position: float, velocity: float, elapsed_seconds: float) -> tuple[float, float]:
    position += velocity * elapsed_seconds
    while position < 0 or position > config.FISH_PLAY_HEIGHT:
        if position > config.FISH_PLAY_HEIGHT:
            position = config.FISH_PLAY_HEIGHT - (position - config.FISH_PLAY_HEIGHT)
            velocity = -abs(velocity)
        elif position < 0:
            position = -position
            velocity = abs(velocity)
    return position, velocity


def advance_fishing(
    state: FishingState,
    elapsed_seconds: float,
    *,
    interact_pressed: bool,
    eligible: bool,
) -> tuple[FishingState, FishingOutcome]:
    if elapsed_seconds < 0:
        raise ValueError("elapsed time must not be negative")
    if state.phase is FishingPhase.IDLE:
        return state, _outcome("")
    if not eligible:
        return _reset(state, "Fishing canceled.")

    elapsed = state.phase_elapsed + elapsed_seconds
    if state.phase is FishingPhase.WAITING_FOR_BITE:
        if elapsed >= config.FISH_BITE_DELAY_SECONDS:
            return replace(state, phase=FishingPhase.BITE_WINDOW, phase_elapsed=0.0, feedback="A fish bites! Press E now!"), _outcome("Fish bite!", accepted=True)
        return replace(state, phase_elapsed=elapsed), _outcome("")

    if state.phase is FishingPhase.BITE_WINDOW:
        if interact_pressed and state.phase_elapsed < config.FISH_BITE_WINDOW_SECONDS:
            return replace(
                state,
                phase=FishingPhase.CATCHING,
                phase_elapsed=0.0,
                fishing_progress=config.FISH_INITIAL_PROGRESS,
                feedback="Catch the fish!",
            ), _outcome("Catch game started.", accepted=True)
        if elapsed >= config.FISH_BITE_WINDOW_SECONDS:
            return _reset(state, "You missed the bite.")
        return replace(state, phase_elapsed=elapsed), _outcome("")

    catch_bar_position = state.catch_bar_position
    catch_bar_velocity = state.catch_bar_velocity
    time_since_last_press = state.time_since_last_press
    if interact_pressed:
        catch_bar_velocity += config.FISH_CATCH_BAR_UPWARD_IMPULSE
        time_since_last_press = 0.0
        gravity_elapsed = 0.0
    else:
        previous_time = time_since_last_press
        time_since_last_press += elapsed_seconds
        previous_active_time = max(0.0, previous_time - config.FISH_CATCH_BAR_GRACE_SECONDS)
        active_time = max(0.0, time_since_last_press - config.FISH_CATCH_BAR_GRACE_SECONDS)
        gravity_elapsed = active_time - previous_active_time

    catch_bar_position += catch_bar_velocity * elapsed_seconds
    if gravity_elapsed > 0:
        catch_bar_position -= 0.5 * config.FISH_CATCH_BAR_GRAVITY * gravity_elapsed**2
        catch_bar_velocity -= config.FISH_CATCH_BAR_GRAVITY * gravity_elapsed
    catch_bar_velocity = max(
        -config.FISH_CATCH_BAR_MAX_SPEED,
        min(config.FISH_CATCH_BAR_MAX_SPEED, catch_bar_velocity),
    )
    catch_bar_position = max(
        0.0,
        min(config.FISH_PLAY_HEIGHT - state.catch_bar_height, catch_bar_position),
    )
    if catch_bar_position <= 0.0 and catch_bar_velocity < 0:
        catch_bar_velocity = 0.0
    elif catch_bar_position >= config.FISH_PLAY_HEIGHT - state.catch_bar_height and catch_bar_velocity > 0:
        catch_bar_velocity = 0.0
    fish_position, fish_velocity = _move_fish(state.fish_position, state.fish_velocity, elapsed_seconds)
    aligned = catch_bar_position <= fish_position <= catch_bar_position + state.catch_bar_height
    progress_delta = (config.FISH_PROGRESS_GAIN_RATE if aligned else -config.FISH_PROGRESS_LOSS_RATE) * elapsed_seconds
    progress = max(0.0, min(100.0, state.fishing_progress + progress_delta))
    updated = replace(
        state,
        phase_elapsed=elapsed,
        catch_bar_position=catch_bar_position,
        catch_bar_velocity=catch_bar_velocity,
        fish_position=fish_position,
        fish_velocity=fish_velocity,
        time_since_last_press=time_since_last_press,
        fishing_progress=progress,
        feedback="Fish in the catch bar!" if aligned else "Keep the fish in the catch bar!",
    )
    if progress >= 100.0:
        return _reset(updated, "Fish caught! +25 stamina.", caught=True)
    if progress <= 0.0:
        return _reset(updated, "The fish escaped.")
    return updated, _outcome("", accepted=True)
