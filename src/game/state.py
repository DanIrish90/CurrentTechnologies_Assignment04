"""Explicit runtime state and simulation update orchestration."""

from __future__ import annotations

from dataclasses import dataclass, replace

from . import config
from .bureaucracy import (
    Feedback,
    HandoverResult,
    WaveProgress,
    WorkflowPhase,
    advance_progress,
    collect_initial_document,
    create_wave,
    create_wave_progress,
    handover,
)
from .camera import Camera, update_camera
from .config import VIEWPORT_HEIGHT, VIEWPORT_WIDTH
from .fishing import FishingOutcome, FishingPhase, FishingState, advance_fishing, create_fishing_state, start_cast
from .geometry import Rect, Vector2
from .input_state import InputState
from .movement import move_player
from .stamina import StaminaState, advance_stamina, create_initial_stamina
from .world import Player, World, civil_servant_positions, create_initial_player, create_initial_world


@dataclass(frozen=True, slots=True)
class UiSnapshot:
    title: str
    state_label: str
    control_hint: str
    wave_label: str = "WAVE 1"
    carried_label: str = "Carrying: nothing"
    feedback: Feedback = Feedback("Find the requested document.", False)
    stamina_label: str = "STAMINA: 100/100"
    stamina_status: str = "STABLE"
    fishing_pond_active: bool = False
    game_over: bool = False
    restart_button_bounds: Rect | None = None
    fishing_phase: str = "idle"
    fishing_status: str = "Ready to fish."
    catch_bar_position: float = 0.0
    catch_bar_height: float = 0.0
    fish_position: float = 0.0
    fishing_progress: float = 0.0
    fishing_visible: bool = False
    rest_countdown_visible: bool = False
    rest_wave_number: int = 0
    rest_seconds_remaining: float = 0.0
    rest_progress: float = 0.0


@dataclass(frozen=True, slots=True)
class GameState:
    world: World
    player: Player
    camera: Camera
    elapsed_time: float = 0.0
    running: bool = True
    workflow: WaveProgress | None = None
    stamina: StaminaState = StaminaState()
    game_over: bool = False
    fishing: FishingState = FishingState()


def create_game_state(viewport_size: Vector2 | None = None) -> GameState:
    world = create_initial_world()
    player = create_initial_player(world)
    viewport = viewport_size or Vector2(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
    camera = update_camera(player, world, viewport)
    wave = create_wave(1, civil_servant_positions(1))
    return GameState(
        world=world,
        player=player,
        camera=camera,
        workflow=create_wave_progress(wave),
        stamina=create_initial_stamina(),
        fishing=create_fishing_state(),
    )


def _within_interaction_range(player: Player, target: Vector2) -> bool:
    return (player.center - target).length() <= config.INTERACTION_RANGE


def _dispatch_interaction(state: GameState) -> WaveProgress | None:
    workflow = state.workflow
    if workflow is None or state.world.document_source is None:
        return workflow
    source = state.world.document_source
    if _within_interaction_range(state.player, source.bounds.center):
        collected, _ = collect_initial_document(workflow)
        return collected
    in_range_servants = sorted(
        (
            servant
            for servant in workflow.definition.servants
            if _within_interaction_range(state.player, servant.position)
        ),
        key=lambda servant: servant.step_order,
    )
    if not in_range_servants:
        return workflow
    handed_over, _ = handover(workflow, in_range_servants[0].id)
    return handed_over


def update_game_state(
    state: GameState,
    input_state: InputState,
    elapsed_seconds: float,
    viewport_size: Vector2 | None = None,
) -> GameState:
    """Advance simulation state without rendering or display access."""

    if elapsed_seconds < 0:
        raise ValueError("elapsed time must not be negative")
    restart_bounds = _restart_button_bounds(viewport_size or state.camera.viewport_size)
    if state.game_over:
        if input_state.mouse_clicked and _point_in_rect(input_state.mouse_position, restart_bounds):
            return create_game_state(viewport_size or state.camera.viewport_size)
        return replace(
            state,
            elapsed_time=state.elapsed_time + elapsed_seconds,
            running=state.running and not input_state.quit_requested,
            fishing=create_fishing_state(),
        )

    pond_before = state.world.fishing_pond
    rest_active = state.workflow is not None and state.workflow.phase is not WorkflowPhase.ACTIVE
    carrying_before = state.workflow is not None and state.workflow.carried_document is not None
    requesting_cast = (
        state.fishing.phase is FishingPhase.IDLE
        and input_state.interact_pressed
        and rest_active
        and pond_before is not None
        and state.player.bounds.overlaps(pond_before.bounds)
        and not carrying_before
    )
    fishing_active = state.fishing.phase is not FishingPhase.IDLE or requesting_cast
    player = state.player if fishing_active else move_player(state.player, state.world, input_state, elapsed_seconds)
    viewport = viewport_size or state.camera.viewport_size
    camera = update_camera(player, state.world, viewport)
    workflow = state.workflow
    fishing = state.fishing
    if not rest_active:
        fishing = create_fishing_state()
    pond = state.world.fishing_pond
    carrying_document = workflow is not None and workflow.carried_document is not None
    in_pond = pond is not None and player.bounds.overlaps(pond.bounds)
    fishing_eligible = (
        in_pond
        and not carrying_document
        and not state.game_over
        and workflow is not None
        and workflow.phase is not WorkflowPhase.ACTIVE
    )
    if fishing.phase is FishingPhase.IDLE and input_state.interact_pressed and fishing_eligible:
        fishing, _ = start_cast(fishing, eligible=True)
    elif workflow is not None and input_state.interact_pressed and not fishing_active:
        workflow = _dispatch_interaction(replace(state, player=player, camera=camera))
    previous_workflow = workflow
    if workflow is not None:
        workflow = advance_progress(workflow, elapsed_seconds)
    wave_started = (
        previous_workflow is not None
        and workflow is not None
        and workflow.definition.wave_number > previous_workflow.definition.wave_number
    )
    carrying_document = workflow is not None and workflow.carried_document is not None
    fishing_eligible = (
        in_pond
        and not carrying_document
        and not state.game_over
        and workflow is not None
        and workflow.phase is not WorkflowPhase.ACTIVE
    )
    if wave_started:
        fishing = create_fishing_state()
        fishing_outcome = FishingOutcome()
    else:
        fishing, fishing_outcome = advance_fishing(
            fishing,
            elapsed_seconds,
            interact_pressed=(
                input_state.interact_pressed
                and fishing.phase in (FishingPhase.BITE_WINDOW, FishingPhase.CATCHING)
            ),
            eligible=fishing_eligible,
        )
    stamina = state.stamina
    if fishing_outcome.stamina_reward > 0 and not stamina.game_over:
        stamina = replace(
            stamina,
            current=min(stamina.maximum, stamina.current + fishing_outcome.stamina_reward),
        )
    in_regen_zone = False
    stamina = advance_stamina(
        stamina,
        elapsed_seconds,
        carrying_document=carrying_document,
        in_regen_zone=in_regen_zone,
    )
    return replace(
        state,
        player=player,
        camera=camera,
        elapsed_time=state.elapsed_time + elapsed_seconds,
        running=state.running and not input_state.quit_requested,
        workflow=workflow,
        stamina=stamina,
        game_over=stamina.game_over,
        fishing=fishing,
    )


def _restart_button_bounds(viewport_size: Vector2) -> Rect:
    x = (viewport_size.x - config.RESTART_BUTTON_WIDTH) / 2
    y = min(config.RESTART_BUTTON_Y, max(24, viewport_size.y - config.RESTART_BUTTON_HEIGHT - 24))
    return Rect(x, y, config.RESTART_BUTTON_WIDTH, config.RESTART_BUTTON_HEIGHT)


def _point_in_rect(point: Vector2, rect: Rect) -> bool:
    return rect.x <= point.x <= rect.right and rect.y <= point.y <= rect.bottom


def ui_snapshot(state: GameState) -> UiSnapshot:
    workflow = state.workflow
    rest_visible = workflow is not None and workflow.phase is not WorkflowPhase.ACTIVE
    rest_seconds = (
        max(0.0, min(config.DOCUMENT_TRANSITION_SECONDS, workflow.transition_remaining))
        if rest_visible and workflow is not None else 0.0
    )
    rest_progress = rest_seconds / config.DOCUMENT_TRANSITION_SECONDS if rest_visible else 0.0
    if workflow is None:
        return UiSnapshot(
            title="I am from the Government",
            state_label="STATUS: awaiting paperwork",
            control_hint="Move: WASD / Arrow Keys | Interact: E",
            stamina_label=f"STAMINA: {state.stamina.current:.0f}/{state.stamina.maximum:.0f}",
            stamina_status="GAME OVER: EXHAUSTED" if state.game_over else "STABLE",
            game_over=state.game_over,
            restart_button_bounds=_restart_button_bounds(state.camera.viewport_size) if state.game_over else None,
            fishing_phase=state.fishing.phase.value,
            fishing_status=state.fishing.feedback,
            catch_bar_position=state.fishing.catch_bar_position,
            catch_bar_height=state.fishing.catch_bar_height,
            fish_position=state.fishing.fish_position,
            fishing_progress=state.fishing.fishing_progress,
            fishing_visible=(
                state.fishing.phase is not FishingPhase.IDLE
                and rest_visible
            ),
            rest_countdown_visible=False,
        )
    carried = workflow.carried_document
    carried_label = "Carrying: nothing" if carried is None else f"Carrying: {carried.document_type.value}"
    in_regen_zone = False
    if state.game_over:
        stamina_status = "GAME OVER: EXHAUSTED"
    elif carried is not None:
        stamina_status = "CARRYING: -5/S"
    elif in_regen_zone:
        stamina_status = "RECOVERING: +10/S"
    else:
        stamina_status = "STABLE"
    return UiSnapshot(
        title="I am from the Government",
        state_label=workflow.feedback.message,
        control_hint="Move: WASD / Arrow Keys | Interact: E",
        wave_label=f"WAVE {workflow.definition.wave_number}",
        carried_label=carried_label,
        feedback=workflow.feedback,
        stamina_label=f"STAMINA: {state.stamina.current:.0f}/{state.stamina.maximum:.0f}",
        stamina_status=stamina_status,
        fishing_pond_active=state.world.fishing_pond is not None
        and state.player.bounds.overlaps(state.world.fishing_pond.bounds),
        game_over=state.game_over,
        restart_button_bounds=_restart_button_bounds(state.camera.viewport_size) if state.game_over else None,
        fishing_phase=state.fishing.phase.value,
        fishing_status=(
            "Fishing available during wave rest."
            if rest_visible and state.fishing.phase is FishingPhase.IDLE
            else "Fishing unavailable during active wave."
            if not rest_visible and state.fishing.phase is FishingPhase.IDLE
            else state.fishing.feedback
        ),
        catch_bar_position=state.fishing.catch_bar_position,
        catch_bar_height=state.fishing.catch_bar_height,
        fish_position=state.fishing.fish_position,
        fishing_progress=state.fishing.fishing_progress,
        fishing_visible=(
            state.fishing.phase is not FishingPhase.IDLE
            and rest_visible
        ),
        rest_countdown_visible=rest_visible,
        rest_wave_number=workflow.definition.wave_number,
        rest_seconds_remaining=rest_seconds,
        rest_progress=rest_progress,
    )
