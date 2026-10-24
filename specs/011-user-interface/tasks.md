---

description: "Actionable implementation tasks for the User Interface Overlay Refresh"
---

# Tasks: User Interface Overlay Refresh

**Input**: Design documents from `/specs/011-user-interface/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story. Tests are included because the constitution requires automated regression coverage and the specification defines measurable UI outcomes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Register the complete FishingMeter asset and establish presentation configuration.

- [X] T001 [P] Validate `assets/UserInterface/FishingMeter.png` as a 128×448 PNG containing a 64×448 left bar and six 64×64 right-side icon regions in `src/presentation/ui_assets.py`
- [X] T002 [P] Add FishingMeter asset path, native dimensions, icon dimensions, source-region constants, and default `UI_STAMINA_BAR_SCALE = 1.0` in `src/game/config.py`
- [X] T003 [P] Add focused asset-dimension and source-region tests for `FishingMeter.png` in `tests/unit/test_ui_assets.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend the presentation snapshot and layout helpers without moving gameplay rules into rendering.

**⚠️ CRITICAL**: Complete this phase before implementing user stories.

- [X] T004 Extend immutable `UiSnapshot` with FishingMeter phase, selected icon, outcome elapsed time, and visibility fields in `src/game/state.py`
- [X] T005 [P] Add pure FishingMeter source-rectangle, native-size centering, and icon-placement helpers in `src/presentation/ui_assets.py`
- [X] T006 [P] Add unit tests for FishingMeter layout helpers, including 128×448 centering, 64×448 bar bounds, six 64×64 icon regions, small windows, and unchanged native size across zoom values in `tests/unit/test_ui_assets.py`
- [X] T007 Load and cache the FishingMeter sheet and six icon surfaces once in `src/presentation/ui_assets.py`, without loading assets inside the frame loop
- [X] T008 Add FishingMeter presentation-state projection from authoritative `FishingPhase`, `fish_position`, and fishing outcome feedback in `src/game/state.py`

**Checkpoint**: UI snapshot and asset primitives expose all data needed by the three story implementations.

---

## Phase 3: User Story 1 - Clear Interaction and Fishing Feedback (Priority: P1) 🎯 MVP

**Goal**: Show actionable E feedback and replace the placeholder fishing overlay with the supplied centered FishingMeter while preserving the existing fishing state machine.

**Independent Test**: At document source, handover zone, fishing pond, bite window, catching state, blocked states, and out-of-range locations, verify the next rendered frame shows exactly the appropriate interaction/FishingMeter state; verify movement is paused while the modal FishingMeter is active.

### Tests for User Story 1

- [X] T009 [P] [US1] Add UI snapshot tests for bait/default, bite, catching fish, success, catchbar overlay, failure, and hidden FishingMeter states in `tests/unit/test_ui_snapshot.py`
- [X] T010 [P] [US1] Add Fishing state regression tests proving existing cast, bite window, E acceptance, fish movement, catch progress, and cancellation rules remain unchanged in `tests/unit/test_fishing.py`
- [X] T011 [P] [US1] Add state integration tests proving player movement and unrelated interactions remain paused during waiting, bite, and catching phases in `tests/unit/test_state.py`
- [X] T012 [P] [US1] Add headless renderer tests for native 128×448 centering, icon selection, fish-position placement, and absence of old bar-like fish rendering in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 1

- [X] T013 [US1] Update FishingMeter projection so idle/waiting selects bait, `BITE_WINDOW` selects bite, `CATCHING` selects fish at `fish_position`, and outcome feedback selects success/failure for 2.0 simulation seconds in `src/game/state.py`
- [X] T014 [US1] Compose the native 128×448 FishingMeter from the 64×448 bar and phase-selected 64×64 icons in `src/presentation/renderer.py`, centering it without Feature-010 zoom or StaminaBar scaling
- [X] T015 [US1] Render the fifth catchbar overlay over the FishingMeter during catching and outcome composition, preserving existing catch-bar geometry and fish position in `src/presentation/renderer.py`
- [X] T016 [US1] Render success and failure icons centrally over the catchbar overlay for exactly 2.0 elapsed seconds and then clear the feedback presentation state in `src/presentation/renderer.py`
- [X] T017 [US1] Remove placeholder text/rectangle Fishing rendering while retaining gameplay-required FishingMeter feedback and remove only Fishpond/Documents debug overlays in `src/presentation/renderer.py`
- [X] T018 [US1] Ensure `interaction_available` shows InteractionButton for cast and accepted Fishing E actions but hides it for blocked or unavailable phases in `src/game/state.py`
- [X] T019 [US1] Verify modal Fishing state prevents player movement and unrelated document actions while allowing only the existing Fishing input path in `src/game/state.py`

**Checkpoint**: User Story 1 is independently playable: interaction hints and all FishingMeter states work without changing fishing rules.

---

## Phase 4: User Story 2 - Compact Stamina and Fishing Recovery (Priority: P1)

**Goal**: Replace the debug stamina display with the composed StaminaBar while preserving successful-catch recovery and rejecting passive or failed fishing recovery.

**Independent Test**: Render stamina at 100%, 50%, 25%, 10%, below 10%, and 0%; verify frame, clipped fill, threshold colors, scale behavior, successful-catch reward, and no reward for pond occupancy, missed bite, or escaped fish.

### Tests for User Story 2

- [X] T020 [P] [US2] Add stamina ratio, threshold-color, fill clipping, and positive-scale tests for `0.5`, `1.0`, and `1.5` in `tests/unit/test_ui_assets.py`
- [X] T021 [P] [US2] Add stamina and Fishing recovery regression tests proving only a successful catch awards `FISH_STAMINA_REWARD` and pond occupancy, missed bites, and escaped fish award zero in `tests/unit/test_stamina.py`
- [X] T022 [P] [US2] Add smoke coverage for the StaminaBar at 960×640, 800×600, and 1280×720, including no overflow or negative fill width, in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 2

- [X] T023 [US2] Set and validate `UI_STAMINA_BAR_SCALE` default `1.0` in `src/game/config.py`, rejecting non-positive values without changing gameplay or other UI scales
- [X] T024 [US2] Compose the two 320×32 StaminaBar rows with left-anchored clamped fill and exact green/yellow/red thresholds in `src/presentation/renderer.py`
- [X] T025 [US2] Apply the independent StaminaBar scale only to the rendered bar while preserving safe margins and existing Feature-010 zoom behavior in `src/presentation/renderer.py`
- [X] T026 [US2] Preserve successful-catch stamina application and remove passive pond regeneration without changing the Fishing state machine in `src/game/state.py` and `src/game/stamina.py`
- [X] T027 [US2] Replace old stamina/debug text rendering and keep existing WormTimer and gameplay-required Fishing state data available in `src/presentation/renderer.py`

**Checkpoint**: User Story 2 is independently testable: stamina display and recovery rules are correct while User Story 1 Fishing feedback remains functional.

---

## Phase 5: User Story 3 - Understandable GameOver (Priority: P1)

**Goal**: Show a centered, contained GameOver image with visual priority while preserving restart behavior.

**Independent Test**: Exhaust stamina, verify centered `GameOver.png` at supported window sizes with normal HUD suppressed, then restart and verify the normal HUD and Fishing eligibility return.

### Tests for User Story 3

- [X] T028 [P] [US3] Add GameOver visibility, centering, aspect-ratio, HUD-priority, and restart snapshot tests in `tests/unit/test_ui_snapshot.py`
- [X] T029 [P] [US3] Add headless resize tests proving `GameOver.png` stays fully visible and centered at 960×640, 800×600, and 1280×720 in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 3

- [X] T030 [US3] Render `GameOver.png` proportionally contained and centered with visual priority over normal HUD while retaining the existing restart control in `src/presentation/renderer.py`
- [X] T031 [US3] Ensure GameOver clears FishingMeter, interaction hint, and active fishing state without disabling the existing restart transition in `src/game/state.py`

**Checkpoint**: User Story 3 is independently testable: GameOver is readable, contained, restartable, and does not corrupt Fishing or stamina state.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete vertical slice and update documentation without expanding gameplay scope.

- [X] T032 [P] Update asset and UI behavior documentation, including native FishingMeter dimensions and icon mapping, in `README.md`
- [X] T033 [P] Add quickstart references for FishingMeter states, 2-second outcomes, native sizing, stamina thresholds, and resize behavior in `specs/011-user-interface/quickstart.md`
- [X] T034 Run focused UI, Fishing, stamina, state, and zoom tests with `SDL_VIDEODRIVER=dummy` and record results in `specs/011-user-interface/quickstart.md`
- [X] T035 Run the complete pytest suite, verify the existing unrelated Map Loader baseline separately if it remains, and document failure classification in `specs/011-user-interface/quickstart.md`
- [X] T036 Execute every manual scenario in `specs/011-user-interface/quickstart.md`, including all six FishingMeter states and window sizes, before marking the feature complete
- [X] T037 [US1] Reposition the waiting-for-bite bait icon and bite-window icon to the vertical center of the left 64×448 Fishing Bar, hide the right-side active placement, and add regression coverage in `src/presentation/renderer.py` and `tests/smoke/test_launch_contract.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; asset/config inspection can start immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; integrates with FishingMeter but can be tested independently after the shared snapshot exists.
- **User Story 3 (Phase 5)**: Depends on Foundational; integrates with HUD priority rules but can be tested independently.
- **Polish (Phase 6)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2; defines the FishingMeter presentation used by the Fishing recovery flow.
- **US2 (P1)**: Can start after Phase 2; shares state and renderer files with US1, so same-file tasks should be sequenced rather than edited concurrently.
- **US3 (P1)**: Can start after Phase 2; its GameOver priority must be integrated after the shared HUD renderer is stable.

### Parallel Opportunities

- T001–T003 can run in parallel because they inspect/configure separate asset and test concerns.
- T005–T007 can run in parallel after T004’s snapshot contract is agreed.
- T009–T012 can run in parallel because they target separate test files or independent test sections.
- T020–T022 and T028–T029 can run in parallel with their respective implementation planning.
- T032–T033 can run in parallel during polish.
- User stories can be developed in parallel after Phase 2 only when changes to shared `src/game/state.py` and `src/presentation/renderer.py` are coordinated.

## Parallel Example: User Story 1

```text
Task T009: UI snapshot state tests in tests/unit/test_ui_snapshot.py
Task T010: Fishing rule regressions in tests/unit/test_fishing.py
Task T012: Headless render tests in tests/smoke/test_launch_contract.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 interaction and FishingMeter presentation.
3. Run US1 focused tests and manually verify all FishingMeter states.
4. Stop and validate the playable Fishing interaction before adding stamina and GameOver slices.

### Incremental Delivery

1. Add US2 for the StaminaBar and recovery regressions.
2. Add US3 for GameOver and restart priority.
3. Complete cross-cutting validation and manual resize checks.

## Notes

- Every task uses the required checkbox, sequential ID, optional `[P]` marker, story label where applicable, and an explicit file path.
- No external API contracts are needed for this internal offline Pygame application.
- Gameplay rules remain in `src/game/fishing.py`; rendering consumes derived state and must not create a second fishing state machine.
