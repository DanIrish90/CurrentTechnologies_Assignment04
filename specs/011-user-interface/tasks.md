---

description: "Actionable implementation tasks for the User Interface Overlay Refresh"
---

# Tasks: User Interface Overlay Refresh

**Input**: Design documents from `/specs/011-user-interface/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Automated tests are included because the specification requires measurable UI behavior and regression protection for the existing gameplay loop.

**Organization**: Tasks are grouped by the three P1 user stories. Every story has an independent validation path; shared state and asset infrastructure is completed first.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish asset, test, and documentation touchpoints without changing gameplay behavior.

- [X] T001 [P] Add source-path and dimension fixtures for `InteractionButton.png` (128×128), `StaminaBar.png` (320×64), and `GameOver.png` (1024×256) in `tests/unit/test_ui_assets.py`
- [X] T002 [P] Configure reusable headless Pygame initialization and teardown for UI rendering tests in `tests/conftest.py`
- [X] T003 [P] Document the UserInterface assets, removed debug overlays, preserved successful-catch recovery, and clarified pond non-recovery behavior in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared UI projection and asset pipeline required by all user stories.

**⚠️ CRITICAL**: No user story implementation starts until this phase is complete.

- [X] T004 [P] Add centralized UserInterface asset paths, safe margins, lower-third placement values, stamina thresholds, and UI colors in `src/game/config.py`
- [X] T005 [P] Implement validated one-time loading of `InteractionButton.png`, `StaminaBar.png`, and `GameOver.png`, including the two 320×32 `StaminaBar.png` regions, in `src/presentation/ui_assets.py`
- [X] T006 Extend the immutable UI snapshot contract in `src/game/state.py` with `interaction_available`, clamped `stamina_ratio` in `[0, 1]`, `stamina_color_state` (`green` for `[0.5, 1.0]`, `yellow` for `[0.1, 0.5)`, `red` for `[0, 0.1)`), and the existing `game_over` state
- [X] T007 [P] Add foundational snapshot tests for stamina-ratio clamping and exact color thresholds in `tests/unit/test_ui_snapshot.py`
- [X] T008 [P] Add reusable safe-fit, centering, lower-third, and left-anchored fill layout assertions for the reference window sizes in `tests/unit/test_ui_layout.py`

**Checkpoint**: Shared UI state, asset loading, threshold semantics, and layout primitives are testable without changing gameplay rules.

---

## Phase 3: User Story 1 - Klare Interaktionshinweise (Priority: P1) 🎯 MVP

**Goal**: Show `InteractionButton.png` only when an existing document, handover, cast, or accepted Fishing interaction is executable, while removing only the Fishpond/Documents debug overlays.

**Independent Test**: At the document source, a valid handover zone, the eligible Fishing Pond, blocked workflow states, and out-of-range locations, verify on the next frame that the button visibility matches the existing `E` action and that no Fishpond/Documents label or rectangle is drawn.

### Tests for User Story 1

- [X] T009 [P] [US1] Add UI-snapshot tests for document collection, valid handover, Fishing cast, accepted bite/Catching input, blocked workflow, carrying restrictions, GameOver, and out-of-range interaction states in `tests/unit/test_ui_snapshot.py`
- [X] T010 [P] [US1] Add headless renderer tests proving Fishpond/Documents debug overlays are absent and the InteractionButton appears only for actionable states in `tests/smoke/test_launch_contract.py`
- [X] T011 [P] [US1] Add lower-third centering and resize assertions for `InteractionButton.png` at 960×640, 800×600, and 1280×720 in `tests/unit/test_ui_layout.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement the complete `interaction_available` predicate in `src/game/state.py` by reusing existing document, handover, Fishing eligibility, phase, and blocking rules without adding transitions
- [X] T013 [US1] Replace the debug panel and remove only the Fishpond/Documents label and rectangle rendering in `src/presentation/renderer.py`, while retaining gameplay-required Fishing feedback overlays
- [X] T014 [US1] Render `InteractionButton.png` horizontally centered in the lower screen third when `interaction_available` is true and hide it immediately when false in `src/presentation/renderer.py`

**Checkpoint**: User Story 1 is independently playable; contextual interaction feedback works and the underlying Fishing/document objects and rules remain active.

---

## Phase 4: User Story 2 - Kompakte und verständliche Ausdaueranzeige (Priority: P1)

**Goal**: Replace the large stamina debug display with the two-row `StaminaBar.png` while preserving the Fishing mini-game and successful-catch recovery and removing passive pond recovery.

**Independent Test**: Render stamina at 100%, 50%, 25%, 10%, below 10%, and 0%; verify frame/fill composition, exact colors, proportional left-anchored clipping, document drain, pond non-recovery, successful-catch reward, maximum, and GameOver behavior.

### Tests for User Story 2

- [X] T015 [P] [US2] Add asset-composition tests for the upper 320×32 frame, lower 320×32 fill, tint variants, and source dimensions in `tests/unit/test_ui_assets.py`
- [X] T016 [P] [US2] Add render assertions for ratios `1.0`, `0.5`, `0.25`, `0.1`, `0.09`, and `0.0`, including fill bounds and exact threshold colors, in `tests/smoke/test_launch_contract.py`
- [X] T017 [P] [US2] Add regression tests proving document stamina drain, pond non-recovery, maximum clamping, and zero-stamina GameOver remain unchanged in `tests/unit/test_stamina.py` and `tests/unit/test_state.py`
- [X] T018 [P] [US2] Add Fishing recovery regression coverage for rest-phase eligibility, cast, bite delay, bite window, Catching input, successful-catch stamina reward, missed bite, and escaped fish in `tests/unit/test_fishing.py` and `tests/smoke/test_launch_contract.py`

### Implementation for User Story 2

- [X] T019 [US2] Implement the composed StaminaBar renderer in `src/presentation/renderer.py` using the lower row as a colorized fill, the upper row as the frame drawn last, and a fill width clamped to the ratio range `[0, 1]`
- [X] T020 [US2] Position the StaminaBar at the configured top-left safe margin and keep it on the existing Feature 010 logical zoom surface in `src/presentation/renderer.py`
- [X] T021 [US2] Preserve the existing Fishing mini-game and successful-catch stamina recovery in `src/game/fishing.py`, `src/game/stamina.py`, and `src/game/state.py`; remove pond-only recovery

**Checkpoint**: User Story 2 is independently testable; stamina presentation changes without altering drain, pond non-recovery, Fishing interaction, successful-catch reward, or GameOver rules.

---

## Phase 5: User Story 3 - Verständliche GameOver-Darstellung (Priority: P1)

**Goal**: Show `GameOver.png` centered and fully contained while preserving the existing restart interaction and normal HUD restoration.

**Independent Test**: Force zero stamina at 960×640, 800×600, and 1280×720; verify centered aspect-preserving GameOver art, visual priority, valid stamina state, no competing debug panel, and successful restart.

### Tests for User Story 3

- [X] T022 [P] [US3] Add proportional-fit, safe-margin, and exact-centering tests for `GameOver.png` in `tests/unit/test_ui_assets.py` and `tests/unit/test_ui_layout.py`
- [X] T023 [P] [US3] Add headless GameOver, restart, Fishing-rest, and resize render coverage proving only intended gameplay overlays remain visible in `tests/smoke/test_launch_contract.py`

### Implementation for User Story 3

- [X] T024 [US3] Implement aspect-preserving centered `GameOver.png` layout with safe containment on the logical surface in `src/presentation/ui_assets.py`
- [X] T025 [US3] Draw GameOver with visual priority over normal HUD while preserving the existing restart control and fresh-session reset in `src/presentation/renderer.py` and `src/game/state.py`

**Checkpoint**: All three user stories work together; GameOver is clear, contained, restartable, and does not disrupt the Fishing or stamina systems.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full feature against the design documents and preserve launchability.

- [X] T026 [P] Run focused UI, Fishing, stamina, state, and zoom tests with `SDL_VIDEODRIVER=dummy` and record any failures in `specs/011-user-interface/quickstart.md`
- [X] T027 [P] Run the complete automated test suite and investigate only feature-related regressions in `tests/`
- [X] T028 Validate all manual and headless scenarios from `specs/011-user-interface/quickstart.md`, including action visibility, removed world overlays, Fishing recovery, stamina thresholds, GameOver, restart, zoom, and resize
- [X] T029 Review `src/game/state.py`, `src/presentation/ui_assets.py`, and `src/presentation/renderer.py` for duplicated loading, world-coordinate changes, frame-rate-dependent gameplay changes, or debug UI remnants
- [X] T030 Update task completion markers and implementation notes in `specs/011-user-interface/tasks.md` after validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; asset and test touchpoints can be prepared in parallel.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user-story implementation.
- **Phase 3 (US1)**: Depends on Phase 2; delivers the MVP interaction hint and overlay removal.
- **Phase 4 (US2)**: Depends on Phase 2; can proceed in parallel with US1 after shared foundations, but its integration validation should include US1's renderer path.
- **Phase 5 (US3)**: Depends on Phase 2; can proceed in parallel with US1/US2, with final combined validation after their renderer changes are integrated.
- **Phase 6 (Polish)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on another user story after Phase 2.
- **US2 (P1)**: No gameplay dependency on US1; shares the UI snapshot and asset foundation.
- **US3 (P1)**: No gameplay dependency on US1 or US2; shares the renderer and asset foundation, so final integration must resolve renderer ordering.

### Within Each User Story

- Tests should be written before the corresponding implementation and fail for the missing behavior.
- State predicates and asset/layout helpers precede renderer integration.
- Gameplay rules in `src/game/fishing.py`, `src/game/stamina.py`, and related state transitions are regression-protected and must not be rewritten for this UI feature.
- Complete each story's checkpoint before moving to combined polish validation.

### Parallel Opportunities

- T001–T003 can run in parallel.
- T004, T005, T007, and T008 can run in parallel after setup.
- Within US1, T009–T011 can run in parallel; T012–T014 then integrate them.
- Within US2, T015–T018 can run in parallel; T019–T021 then integrate them.
- Within US3, T022–T023 can run in parallel; T024–T025 then integrate them.
- US1, US2, and US3 can be assigned to separate implementers after Phase 2, provided renderer edits are merged deliberately.

---

## Parallel Example: User Story 1

```text
Task: "Add UI-snapshot tests for document, handover, Fishing, blocked, GameOver, and out-of-range states in tests/unit/test_ui_snapshot.py"
Task: "Add headless renderer tests for removed Fishpond/Documents overlays in tests/smoke/test_launch_contract.py"
Task: "Add InteractionButton resize and lower-third layout assertions in tests/unit/test_ui_layout.py"
```

## Parallel Example: User Story 2

```text
Task: "Add StaminaBar asset-composition tests in tests/unit/test_ui_assets.py"
Task: "Add stamina threshold render assertions in tests/smoke/test_launch_contract.py"
Task: "Add stamina drain/regeneration and Fishing recovery regressions in tests/unit/test_stamina.py, tests/unit/test_state.py, tests/unit/test_fishing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 shared UI state and asset foundations.
3. Complete Phase 3 User Story 1.
4. Stop and validate action visibility, removed debug overlays, and preserved Fishing/document interactions.
5. Demo the contextual UI before adding stamina and GameOver presentation.

### Incremental Delivery

1. Add US1 for contextual interaction feedback and overlay removal.
2. Add US2 for the compact stamina display with Fishing/stamina regression coverage.
3. Add US3 for GameOver and restart presentation.
4. Run Phase 6 cross-cutting validation and the quickstart scenarios.

### Notes

- Every task uses the required `- [ ] T###` checklist format.
- `[P]` marks only tasks that can work on different files without incomplete dependencies.
- `[US1]`, `[US2]`, and `[US3]` map directly to the P1 user stories in `spec.md`.
- No external contract tasks are included because this is an internal offline desktop game.

## Phase 7: Clarification Follow-up

**Purpose**: Implement the clarified stamina recovery boundary and independently configurable StaminaBar scale.

- [X] T031 Add the positive `UI_STAMINA_BAR_SCALE` config value with default `1.0`, apply it only to StaminaBar layout in `src/game/config.py`, `src/presentation/ui_assets.py`, and `src/presentation/renderer.py`, and cover `0.5`, `1.0`, `1.5`, and invalid values in `tests/unit/test_ui_layout.py` and `tests/smoke/test_launch_contract.py`
- [X] T032 Remove passive pond recovery from stamina advancement and UI status reporting while keeping authored pond metadata intact in `src/game/stamina.py` and `src/game/state.py`
- [X] T033 Update state and stamina regressions so pond occupancy, missed bites, escaped fish, and cancelled fishing award no stamina, while successful catches retain the configured reward in `tests/unit/test_stamina.py`, `tests/unit/test_state.py`, `tests/unit/test_fishing.py`, and `tests/smoke/test_launch_contract.py`
- [X] T034 Document the clarified recovery behavior and independent StaminaBar scale in `README.md` and the feature quickstart
- [X] T035 Run focused and full validation, record unrelated baseline failures only, and verify all implementation tasks are marked complete
