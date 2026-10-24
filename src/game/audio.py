"""Application-scoped soundtrack lifecycle independent from gameplay state."""

from __future__ import annotations

from dataclasses import dataclass
import logging

import pygame

from . import config


@dataclass(slots=True)
class ApplicationMusicSession:
    """Own one looping soundtrack attempt for the lifetime of the application."""

    asset_path: str = config.SOUNDTRACK_ASSET_PATH
    attempted: bool = False
    started: bool = False
    available: bool = False
    looping: bool = False
    loaded_asset_path: str | None = None
    failure_message: str | None = None

    def start(self) -> None:
        """Start the complete soundtrack once; keep failures non-fatal."""

        if self.attempted:
            return
        self.attempted = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            load_errors: list[str] = []
            asset_paths = (self.asset_path, config.SOUNDTRACK_RUNTIME_FALLBACK_PATH)
            for asset_path in dict.fromkeys(asset_paths):
                try:
                    pygame.mixer.music.load(asset_path)
                    pygame.mixer.music.play(loops=config.SOUNDTRACK_LOOP_COUNT)
                    self.loaded_asset_path = asset_path
                    self.started = True
                    self.available = True
                    self.looping = True
                    return
                except (OSError, pygame.error) as error:
                    load_errors.append(f"{asset_path}: {error}")
            raise RuntimeError("; ".join(load_errors))
        except (OSError, pygame.error, RuntimeError) as error:
            self.failure_message = f"Background music unavailable: {error}"
            logging.warning(self.failure_message)

    def shutdown(self) -> None:
        """Release playback only when the application itself is closing."""

        if self.available:
            pygame.mixer.music.stop()
            self.looping = False
