# Research: Continuous Soundtrack

**Feature**: `012-soundtrack`
**Date**: 2026-10-24

## Decision 1: Reuse the existing Pygame-ce mixer

**Decision**: Use the audio functionality already included with Pygame-ce rather than adding a new dependency or external playback service.

**Rationale**: The project is an offline Pygame desktop game and already initializes Pygame in the window layer. Reusing the existing runtime keeps packaging and lifecycle ownership small.

**Asset finding**: `assets/Music/I'm Not a Big Fan of.m4a` exists, is approximately 3.4 MB, and contains a 209.16-second stereo Opus stream at 48 kHz. Runtime support must be verified because container/codec support can vary by SDL_mixer installation.

**Alternatives considered**:

- Add a new audio library: rejected because it increases dependencies and packaging risk for one soundtrack.
- Convert or replace the provided asset: rejected because the feature requires the complete supplied song and no conversion step was requested.

## Decision 2: Scope playback to the application session

**Decision**: Start one music session from the application window lifecycle and keep it outside `GameState` and round-reset logic.

**Rationale**: Game over creates a fresh round state, but it must not stop, rewind, or duplicate the soundtrack. Application close remains the natural end of the session.

**Alternatives considered**:

- Start music inside `create_game_state`: rejected because restart calls this function and would restart or overlap the music.
- Store mixer state in `GameState`: rejected because audio playback is a presentation/application concern, not gameplay state.

## Decision 3: Use continuous loop playback with non-fatal failure handling

**Decision**: Load the provided asset once and request continuous looping. Catch mixer initialization and load failures, log a concise warning, and continue with playable silent gameplay.

**Rationale**: Looping is the requested behavior, while graceful degradation satisfies the requirement that an unavailable soundtrack must not prevent launch.

**Alternatives considered**:

- Terminate when audio fails: rejected because music is ambient and must not make the game unusable.
- Manually restart the song from the frame loop: rejected because it risks duplicate playback and unnecessary per-frame work.
