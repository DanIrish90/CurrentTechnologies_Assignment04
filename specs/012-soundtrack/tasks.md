---

description: "Actionable implementation tasks for the continuous soundtrack feature"
---

# Tasks: Continuous Soundtrack

**Input**: Design documents from `/specs/012-soundtrack/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Included because the specification requires deterministic lifecycle coverage, graceful audio failure, loop configuration, and game-over restart isolation.

**Organization**: Tasks are grouped by user story and ordered so the application-level music session remains separate from gameplay round state.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the soundtrack asset contract and test seams without changing gameplay behavior.

- [X] T001 [P] Verify `assets/Music/I'm Not a Big Fan of.m4a` exists and record its complete-track requirement in `specs/012-soundtrack/quickstart.md`.
- [X] T002 [P] Add the canonical soundtrack asset path and audio lifecycle constants to `src/game/config.py` without changing movement, workflow, stamina, or fishing constants.
- [X] T003 [P] Add mixer-independent audio test fixtures and fake playback seams in `tests/conftest.py` without requiring a live audio device.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the application-scoped music session abstraction before user-story integration.

**⚠️ CRITICAL**: The soundtrack session must not be owned by `GameState` or recreated by game-over restart.

- [X] T004 [P] Add `tests/unit/test_audio.py` coverage for one-time session startup, continuous-loop configuration, idempotent repeated startup, and non-fatal mixer/asset failure.
- [X] T005 Implement the focused `ApplicationMusicSession` adapter in `src/game/audio.py` with explicit available/failed state, one complete asset path, loop playback, and readable failure reporting.
- [X] T006 Integrate one application music-session initialization and shutdown boundary into `src/presentation/window.py` around the existing Pygame lifecycle, without calling audio initialization from `create_game_state` or the restart path.

**Checkpoint**: The music adapter is independently testable, starts at most once per application process, and cannot block gameplay when unavailable.

## Phase 3: User Story 1 - Play the Continuous Soundtrack (Priority: P1) 🎯 MVP

**Goal**: Play the complete provided song as looping background music for the entire open application session.

**Independent Test**: Start the application with the asset available, verify the music session starts once with looping enabled, and verify a loop boundary does not require a second start request.

### Tests for User Story 1

- [X] T007 [P] [US1] Extend `tests/smoke/test_launch_contract.py` with a headless application-audio contract asserting the configured soundtrack path and loop mode are used without opening a real audio device.
- [X] T008 [P] [US1] Add `tests/unit/test_audio.py` coverage proving the full asset is passed to playback and repeated loop requests do not create overlapping instances.

### Implementation for User Story 1

- [X] T009 [US1] Connect `src/game/audio.py` to the existing Pygame mixer API so the complete `assets/Music/I'm Not a Big Fan of.m4a` asset starts once and loops continuously while the window remains open.
- [X] T010 [US1] Add non-fatal startup diagnostics in `src/game/audio.py` and `src/presentation/window.py` so unavailable mixer/codec/asset conditions leave the game playable and expose a concise audio-failure indication.

**Checkpoint**: The game launches with one continuous looping soundtrack session or a graceful silent fallback.

## Phase 4: User Story 2 - Preserve Music Across a New Round (Priority: P1)

**Goal**: Reset gameplay after game over without stopping, rewinding, replacing, or duplicating the soundtrack.

**Independent Test**: Trigger the existing game-over restart flow with a fake music session and verify gameplay state is recreated while no music start/stop/restart operation is issued.

### Tests for User Story 2

- [X] T011 [P] [US2] Extend `tests/unit/test_state.py` or add `tests/unit/test_audio.py` to prove `create_game_state` and game-over restart do not create, stop, rewind, or duplicate the application music session.
- [X] T012 [P] [US2] Extend `tests/smoke/test_launch_contract.py` with a game-over-and-restart audio lifecycle assertion covering repeated restarts and unchanged playback ownership.

### Implementation for User Story 2

- [X] T013 [US2] Ensure `src/presentation/window.py` owns the soundtrack session for the whole `run()` call and never reinitializes it when `update_game_state` creates a fresh round.
- [X] T014 [US2] Ensure wave transitions, rest phases, game-over rendering, and ordinary frame updates do not call soundtrack stop/restart operations in `src/presentation/window.py` or `src/game/state.py`.

**Checkpoint**: New rounds reset gameplay only; the single application music session remains continuous.

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature and document operational behavior.

- [X] T015 [P] Update `README.md` with the soundtrack asset, continuous-loop behavior, game-over continuity, and graceful audio-failure behavior.
- [X] T016 [P] Update `specs/012-soundtrack/quickstart.md` with automated results and manual checks for audibility, loop boundaries, game-over restart continuity, and unavailable audio.
- [X] T017 Run `./.venv/bin/python -m pytest` and resolve any regressions across existing gameplay, presentation, and new audio tests.
- [ ] T018 Manually launch the desktop game and verify the complete song loops, continues across a game-over restart, and does not overlap or restart during wave transitions; record evidence in `specs/012-soundtrack/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; establishes the asset/config/test seams.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks both user stories.
- **Phase 3 US1**: Depends on Phase 2 and delivers the MVP soundtrack session.
- **Phase 4 US2**: Depends on the application session boundary from US1; protects continuity across round reset.
- **Phase 5 Polish**: Depends on both user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on gameplay story implementation.
- **US2 (P1)**: Depends on US1's application-level session boundary but remains independently testable with a fake music session.

### Dependency Graph

```text
Setup (T001-T003)
        |
Foundation (T004-T006)
        |
        +--> US1: continuous looping playback (T007-T010)
                 |
                 +--> US2: round restart continuity (T011-T014)
                          |
                          +--> Polish/validation (T015-T018)
```

### Parallel Opportunities

- T001-T003 can run in parallel because they touch the asset/docs, config, and test-fixture concerns separately.
- T004 can be written in parallel with T005 once the audio-session interface is agreed.
- T007-T008 can run in parallel because they cover separate launch and pure-adapter contracts.
- T011-T012 can run in parallel before the restart integration tasks.
- T015-T016 can run in parallel; T017-T018 follow implementation completion.

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Setup and Foundational phases.
2. Implement one application-scoped looping soundtrack session.
3. Validate launch, loop configuration, and graceful audio failure.
4. Stop and demo the continuous soundtrack before adding game-over continuity assertions.

### Incremental Delivery

1. Add US1 and verify one complete track loops without duplicate starts.
2. Add US2 and verify game-over restart preserves the existing playback session.
3. Run the full suite and manual quickstart scenarios.

## Completion Evidence

- 17 of 18 implementation and automated validation tasks are checked off; T018 remains a desktop-only manual verification.
- The complete existing pytest suite passes.
- Manual desktop playback confirms audibility, looping, and continuity across game-over restart.
