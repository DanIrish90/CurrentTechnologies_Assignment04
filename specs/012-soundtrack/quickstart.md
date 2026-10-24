# Quickstart Validation: Continuous Soundtrack

**Feature**: `012-soundtrack`

## 1. Automated validation

From the repository root:

```bash
./.venv/bin/python -m pytest
```

Expected result: the complete existing suite passes, including audio lifecycle tests for one-time startup, loop configuration, round restart isolation, and graceful unavailable-audio handling.

## 2. Asset validation

Confirm the asset exists at:

```text
assets/Music/I'm Not a Big Fan of.m4a
```

The complete track must be used. Do not substitute a shortened clip or a second soundtrack.

## 3. Manual playback scenario

1. Launch the game with `python main.py`.
2. Confirm the song is audible once the game becomes playable.
3. Leave the game running until the song reaches its end.
4. Confirm the song starts again automatically without user input or a perceptible application-triggered gap.
5. Let the game run through a wave transition and rest phase; confirm playback does not restart.

Expected result: one continuous looping soundtrack accompanies the open application.

## 4. Game-over restart scenario

1. Start the game and note the current musical position.
2. Trigger game over.
3. Start a new round using the existing restart action.
4. Confirm the music continues from its current position rather than restarting.
5. Repeat the restart once more and confirm no volume doubling or overlapping copy occurs.

Expected result: gameplay resets, but the application music session remains unchanged.

## 5. Failure scenario

1. In a disposable validation environment, make the soundtrack unavailable to the loader.
2. Launch the game.
3. Confirm the game reaches a playable state and reports the audio failure without crashing.

Expected result: audio degrades gracefully while movement, workflow, fishing, and restart remain usable.

## Acceptance evidence

Automated validation record: `./.venv/bin/python -m pytest -q` passed with 247 tests on 2026-10-24. The complete M4A source exists and is 209.16 seconds long; the complete OGG runtime fallback is 209.17 seconds long. A headless mixer check showed that the installed Pygame-ce build rejects the Opus-in-M4A container, then the runtime fallback loads successfully and preserves the same full track duration. Desktop audibility, loop-boundary behavior, and game-over continuity still require verification on a machine with an audio device.
