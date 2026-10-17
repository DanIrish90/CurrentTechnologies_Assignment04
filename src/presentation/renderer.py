"""Pygame-ce rendering for the playable game world and UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pygame

from game import config
from game.camera import Camera
from game.geometry import Rect, Vector2
from game.state import GameState, UiSnapshot, ui_snapshot

from .bureaucrat_animation import BureaucratAnimationManager, bureaucrat_sprite_rect
from .character_animation import CharacterAnimator, character_sprite_rect
from .ui_assets import (
    StaminaColor,
    UiAssets,
    game_over_rect,
    interaction_button_rect,
    load_ui_assets,
    stamina_bar_rect,
    worm_timer_rect,
)


def _screen_rect(world_rect: Rect, camera: Camera) -> pygame.Rect:
    return pygame.Rect(
        round(world_rect.x - camera.position.x),
        round(world_rect.y - camera.position.y),
        round(world_rect.width),
        round(world_rect.height),
    )


_tileset_cache: dict[str, pygame.Surface] = {}
_transformed_tile_cache: dict[tuple[int, int, int], pygame.Surface] = {}

TILED_FLIP_HORIZONTAL = 0x80000000
TILED_FLIP_VERTICAL = 0x40000000
TILED_FLIP_DIAGONAL = 0x20000000
TILED_ROTATED_HEXAGONAL_120 = 0x10000000
TILED_TRANSFORM_FLAGS = (
    TILED_FLIP_HORIZONTAL
    | TILED_FLIP_VERTICAL
    | TILED_FLIP_DIAGONAL
    | TILED_ROTATED_HEXAGONAL_120
)

DRAW_ORDER_ANCHOR_LAYERS = {"NPCDrawOrder", "PlayerDrawOrder"}


@dataclass(frozen=True, slots=True)
class TiledTileReference:
    """A base GID plus the transform flags authored by Tiled."""

    tile_id: int
    flip_horizontal: bool
    flip_vertical: bool
    flip_diagonal: bool
    rotated_hexagonal: bool


def decode_tiled_gid(gid: int) -> TiledTileReference:
    """Separate a Tiled GID from its high-bit transform flags."""

    if gid < 0:
        raise ValueError("Tiled GIDs must not be negative")
    return TiledTileReference(
        tile_id=gid & ~TILED_TRANSFORM_FLAGS,
        flip_horizontal=bool(gid & TILED_FLIP_HORIZONTAL),
        flip_vertical=bool(gid & TILED_FLIP_VERTICAL),
        flip_diagonal=bool(gid & TILED_FLIP_DIAGONAL),
        rotated_hexagonal=bool(gid & TILED_ROTATED_HEXAGONAL_120),
    )


def apply_tiled_transform(tile: pygame.Surface, flags: int) -> pygame.Surface:
    """Apply Tiled's orthogonal transform order to a tile surface.

    Tiled specifies the diagonal flag as an X/Y axis swap (bottom-left and
    top-right corners exchange), followed by horizontal and vertical flips.
    This is deliberately implemented as a coordinate mapping instead of a
    guessed sequence of 90-degree rotations.
    """

    reference = decode_tiled_gid(flags)
    transformed = tile.copy()
    if reference.flip_diagonal:
        width, height = transformed.get_size()
        swapped = pygame.Surface((height, width), pygame.SRCALPHA)
        for source_y in range(height):
            for source_x in range(width):
                swapped.set_at((source_y, source_x), transformed.get_at((source_x, source_y)))
        transformed = swapped
    if reference.flip_horizontal:
        transformed = pygame.transform.flip(transformed, True, False)
    if reference.flip_vertical:
        transformed = pygame.transform.flip(transformed, False, True)
    return transformed


def actor_draw_order(actor_draws: list[tuple[float, object]]) -> tuple[object, ...]:
    """Return actors in stable top-down order using their world foot position."""

    return tuple(actor for _, actor in sorted(actor_draws, key=lambda item: item[0]))


def _tileset(path: str) -> pygame.Surface:
    if path not in _tileset_cache:
        _tileset_cache[path] = pygame.image.load(path).convert_alpha()
    return _tileset_cache[path]


def _draw_tile(surface: pygame.Surface, tileset: pygame.Surface, gid: int, x: float, y: float, camera: Camera) -> None:
    if not gid:
        return
    reference = decode_tiled_gid(gid)
    tile_id = reference.tile_id - 1
    columns = tileset.get_width() // 32
    rows = tileset.get_height() // 32
    if tile_id < 0 or tile_id >= columns * rows:
        return
    source = pygame.Rect((tile_id % columns) * 32, (tile_id // columns) * 32, 32, 32)
    transform_flags = gid & TILED_TRANSFORM_FLAGS
    cache_key = (id(tileset), tile_id, transform_flags)
    tile = _transformed_tile_cache.get(cache_key)
    if tile is None:
        tile = apply_tiled_transform(tileset.subsurface(source), transform_flags)
        _transformed_tile_cache[cache_key] = tile
    surface.blit(tile, (round(x - camera.position.x), round(y - camera.position.y)))


def _draw_map(surface: pygame.Surface, state: GameState, camera: Camera, *, foreground: bool | None = None) -> None:
    if not state.world.render_layers or state.world.tileset_image_path is None:
        return
    path = Path(state.world.tileset_image_path)
    if not path.exists():
        return
    tileset = _tileset(str(path))
    if state.world.render_tiles:
        for tile in state.world.render_tiles:
            if tile.layer_name in DRAW_ORDER_ANCHOR_LAYERS:
                continue
            is_foreground = tile.layer_name in {"FoliageForeground", "ClutterForeground"}
            if foreground is not None and is_foreground != foreground:
                continue
            _draw_tile(
                surface,
                tileset,
                tile.raw_gid,
                tile.layer_position.x,
                tile.layer_position.y,
                camera,
            )
        return
    for layer in state.world.render_layers:
        if not layer.get("visible", True):
            continue
        if layer.get("name") in DRAW_ORDER_ANCHOR_LAYERS:
            continue
        is_foreground = layer.get("name") in {"FoliageForeground", "ClutterForeground"}
        if foreground is not None and is_foreground != foreground:
            continue
        if layer.get("type") == "tilelayer":
            width = int(layer.get("width", 0))
            for index, gid in enumerate(layer.get("data", [])):
                _draw_tile(surface, tileset, gid, (index % width) * 32, (index // width) * 32, camera)
        elif layer.get("type") == "objectgroup":
            for obj in layer.get("objects", []):
                gid = obj.get("gid")
                if gid:
                    _draw_tile(surface, tileset, gid, obj["x"], obj["y"] - obj.get("height", 32), camera)


def render(
    screen: pygame.Surface,
    state: GameState,
    character_animation: CharacterAnimator,
    bureaucrat_animation: BureaucratAnimationManager,
    ui_assets: UiAssets | None = None,
) -> None:
    """Draw world and UI without mutating authoritative state."""

    screen.fill(config.WORLD_COLOR)
    camera = state.camera
    world_rect = _screen_rect(state.world.bounds, camera)
    pygame.draw.rect(screen, config.WORLD_COLOR, world_rect)
    _draw_map(screen, state, camera, foreground=False)

    actor_draws: list[tuple[float, object]] = []
    if state.workflow is not None:
        servant_font = pygame.font.Font(None, 18)
        for servant in state.workflow.definition.servants:
            servant_bounds = Rect(
                servant.position.x - config.SERVANT_PRESENTATION_WIDTH / 2,
                servant.position.y - config.SERVANT_PRESENTATION_HEIGHT,
                config.SERVANT_PRESENTATION_WIDTH,
                config.SERVANT_PRESENTATION_HEIGHT,
            )
            servant_rect = _screen_rect(servant_bounds, camera)
            frame = bureaucrat_animation.frame_for(servant.id)
            status = "SERVED" if servant.served else "PENDING"
            actor_draws.append((servant.position.y, ("npc", frame, servant_rect, servant_font, servant.step_order, status)))

    player_rect = _screen_rect(state.player.bounds, camera)
    actor_draws.append((state.player.bounds.bottom, ("player", character_animation.current_frame, player_rect)))
    for actor in actor_draw_order(actor_draws):
        if actor[0] == "npc":
            _, frame, servant_rect, servant_font, step_order, status = actor
            screen.blit(frame, bureaucrat_sprite_rect(frame, servant_rect))
            screen.blit(servant_font.render(f"S{step_order}", True, config.UI_TEXT_COLOR), servant_rect.move(16, 8))
            screen.blit(servant_font.render(status, True, config.UI_TEXT_COLOR), servant_rect.move(3, 38))
        else:
            _, frame, actor_rect = actor
            screen.blit(frame, character_sprite_rect(frame, actor_rect))
    _draw_map(screen, state, camera, foreground=True)
    snapshot = ui_snapshot(state)
    assets = ui_assets or load_ui_assets()
    _draw_ui(screen, snapshot, assets)
    if snapshot.fishing_visible:
        _draw_fishing_overlay(screen, snapshot)
    if snapshot.rest_countdown_visible:
        _draw_worm_timer(screen, snapshot, assets)


def _draw_ui(screen: pygame.Surface, snapshot: UiSnapshot, assets: UiAssets) -> None:
    _draw_stamina_bar(screen, snapshot, assets)
    if snapshot.interaction_available and not snapshot.game_over:
        button_rect = interaction_button_rect(
            screen.get_size(), assets.interaction_button.get_size(), config.UI_INTERACTION_BUTTON_SAFE_MARGIN
        )
        button = pygame.transform.scale(assets.interaction_button, button_rect.size)
        screen.blit(button, button_rect)
    if snapshot.game_over:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        banner_rect = game_over_rect(
            screen.get_size(), assets.game_over.get_size(), config.UI_MARGIN
        )
        banner = pygame.transform.scale(assets.game_over, banner_rect.size)
        screen.blit(banner, banner_rect)
        _draw_restart_button(screen, snapshot)


def _draw_stamina_bar(screen: pygame.Surface, snapshot: UiSnapshot, assets: UiAssets) -> None:
    bar_rect = stamina_bar_rect(
        screen.get_size(),
        (config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_BAR_HEIGHT),
        config.UI_MARGIN,
        config.UI_STAMINA_BAR_SCALE,
    )
    fill_color = StaminaColor(snapshot.stamina_color_state)
    fill = assets.colorized_stamina_fill(fill_color)
    scaled_fill = pygame.transform.scale(fill, bar_rect.size)
    fill_width = round(bar_rect.width * snapshot.stamina_ratio)
    if fill_width > 0:
        clip = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
        previous_clip = screen.get_clip()
        screen.set_clip(clip)
        screen.blit(scaled_fill, bar_rect)
        screen.set_clip(previous_clip)
    frame = pygame.transform.scale(assets.stamina_frame, bar_rect.size)
    screen.blit(frame, bar_rect)


def _draw_restart_button(screen: pygame.Surface, snapshot: UiSnapshot) -> None:
    font = pygame.font.Font(None, 22)
    if snapshot.restart_button_bounds is not None:
        button = pygame.Rect(
            round(snapshot.restart_button_bounds.x),
            round(snapshot.restart_button_bounds.y),
            round(snapshot.restart_button_bounds.width),
            round(snapshot.restart_button_bounds.height),
        )
        pygame.draw.rect(screen, config.RESTART_BUTTON_COLOR, button)
        pygame.draw.rect(screen, config.UI_TEXT_COLOR, button, width=2)
        label = font.render("Restart", True, config.UI_TEXT_COLOR)
        screen.blit(label, label.get_rect(center=button.center))


def _draw_fishing_overlay(screen: pygame.Surface, snapshot: UiSnapshot) -> None:
    """Draw the placeholder catch game without mutating game state."""

    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    play = pygame.Rect(610, 180, config.FISHING_BAR_WIDTH, config.FISHING_BAR_HEIGHT)
    pygame.draw.rect(screen, config.UI_PANEL_COLOR, play.inflate(24, 56))
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, play, width=2)

    def y_for(position: float) -> int:
        return round(play.bottom - (position / config.FISH_PLAY_HEIGHT) * play.height)

    fish_y = y_for(snapshot.fish_position)
    fish_rect = pygame.Rect(play.x - 8, fish_y - 5, play.width + 16, 10)
    catch_bottom = y_for(snapshot.catch_bar_position)
    catch_top = y_for(snapshot.catch_bar_position + snapshot.catch_bar_height)
    catch_rect = pygame.Rect(play.x - 5, catch_top, play.width + 10, max(4, catch_bottom - catch_top))
    pygame.draw.rect(screen, config.STAMINA_BAR_COLOR, catch_rect)
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, catch_rect, width=2)
    pygame.draw.rect(screen, config.FEEDBACK_SUCCESS_COLOR, fish_rect)
    screen.blit(font.render("FISH", True, config.UI_TEXT_COLOR), (play.x - 8, play.y - 34))
    screen.blit(small_font.render("Press E to pull", True, config.UI_TEXT_COLOR), (play.x - 52, play.bottom + 12))

    progress = pygame.Rect(700, 220, 220, 18)
    pygame.draw.rect(screen, config.STAMINA_BAR_BACKGROUND_COLOR, progress)
    filled = pygame.Rect(progress.x, progress.y, round(progress.width * snapshot.fishing_progress / 100), progress.height)
    pygame.draw.rect(screen, config.FEEDBACK_SUCCESS_COLOR, filled)
    pygame.draw.rect(screen, config.UI_TEXT_COLOR, progress, width=2)
    screen.blit(small_font.render(f"FISHING PROGRESS {snapshot.fishing_progress:.0f}%", True, config.UI_TEXT_COLOR), (700, 190))


def _draw_worm_timer(
    screen: pygame.Surface, snapshot: UiSnapshot, assets: UiAssets
) -> None:
    """Draw the animated WormTimer below the stamina bar during rest."""

    stamina_rect = stamina_bar_rect(
        screen.get_size(),
        (config.UI_STAMINA_BAR_WIDTH, config.UI_STAMINA_BAR_HEIGHT),
        config.UI_MARGIN,
        config.UI_STAMINA_BAR_SCALE,
    )
    frame = assets.worm_timer_frames[snapshot.worm_timer_frame_index]
    timer_rect = worm_timer_rect(
        screen.get_size(),
        stamina_rect,
        frame.get_size(),
        snapshot.rest_elapsed_progress,
    )
    screen.blit(pygame.transform.scale(frame, timer_rect.size), timer_rect)
