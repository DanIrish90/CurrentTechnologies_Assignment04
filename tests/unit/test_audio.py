from __future__ import annotations

from dataclasses import replace

import pygame

from game import config
from game.audio import ApplicationMusicSession
from game.geometry import Vector2
from game.input_state import InputState
from game.stamina import StaminaState
from game.state import create_game_state, update_game_state


def test_music_session_loads_complete_asset_once_and_loops(fake_music_mixer) -> None:
    session = ApplicationMusicSession()

    session.start()
    session.start()

    assert session.available
    assert session.started
    assert session.looping
    assert fake_music_mixer == [
        ("load", config.SOUNDTRACK_ASSET_PATH),
        ("play", config.SOUNDTRACK_LOOP_COUNT),
    ]


def test_music_session_initializes_mixer_when_needed(monkeypatch) -> None:
    calls: list[tuple] = []

    class FakeMusic:
        def load(self, path):
            calls.append(("load", path))

        def play(self, loops=0):
            calls.append(("play", loops))

    class FakeMixer:
        music = FakeMusic()

        @staticmethod
        def get_init():
            return False

        @staticmethod
        def init():
            calls.append(("init",))

    monkeypatch.setattr("game.audio.pygame.mixer", FakeMixer)
    ApplicationMusicSession().start()

    assert calls == [
        ("init",),
        ("load", config.SOUNDTRACK_ASSET_PATH),
        ("play", config.SOUNDTRACK_LOOP_COUNT),
    ]


def test_music_failure_does_not_raise_or_block_gameplay(monkeypatch) -> None:
    class FakeMusic:
        def load(self, path):
            raise pygame.error("unsupported audio format")

    class FakeMixer:
        music = FakeMusic()

        @staticmethod
        def get_init():
            return True

    monkeypatch.setattr("game.audio.pygame.mixer", FakeMixer)
    session = ApplicationMusicSession()

    session.start()

    assert not session.available
    assert not session.started
    assert not session.looping
    assert "unsupported audio format" in session.failure_message


def test_game_over_restart_does_not_touch_application_music(monkeypatch) -> None:
    calls: list[tuple] = []

    class FakeMusic:
        def load(self, path):
            calls.append(("load", path))

        def play(self, loops=0):
            calls.append(("play", loops))

        def stop(self):
            calls.append(("stop",))

    class FakeMixer:
        music = FakeMusic()

        @staticmethod
        def get_init():
            return True

    monkeypatch.setattr("game.audio.pygame.mixer", FakeMixer)
    session = ApplicationMusicSession()
    session.start()
    playback_calls = list(calls)

    state = create_game_state()
    exhausted = replace(state, game_over=True, stamina=StaminaState(current=0, game_over=True))
    restarted = update_game_state(
        exhausted,
        InputState(mouse_clicked=True, mouse_position=Vector2(480, 370)),
        0,
    )

    assert not restarted.game_over
    assert calls == playback_calls
