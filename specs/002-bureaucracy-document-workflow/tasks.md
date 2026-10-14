---

description: "Actionable implementation tasks for the bureaucratic document workflow feature"
---

# Tasks: Bureaucratic Document Workflow

**Input**: Design documents from `/specs/002-bureaucracy-document-workflow/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Included because the feature specification and constitution require deterministic pytest coverage for wave progression, document validation, invalid handovers, and elapsed-time transitions.

**Organization**: Tasks are grouped by user story and ordered so each story can be validated as an incremental playable slice.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish workflow constants, baseline regression protection, and shared test fixtures without changing existing gameplay behavior.

- [X] T001 Run the existing feature 001 suite with `./.venv/bin/python -m pytest` and record the baseline result in `specs/002-bureaucracy-document-workflow/quickstart.md` before workflow changes.
- [X] T002 [P] Add `DOCUMENT_TRANSITION_SECONDS = 10.0`, interaction-key configuration, and workflow display constants to `src/game/config.py` without changing movement/collision constants.
- [X] T003 [P] Add reusable workflow fixtures for wave definitions, initial documents, servants, and empty carried-document state in `tests/conftest.py` without initializing a Pygame display.
- [X] T004 [P] Add the workflow module import surface and module-level documentation in `src/game/bureaucracy.py` while keeping the module independent of Pygame.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared state seams that all workflow stories require.

**⚠️ CRITICAL**: Complete this phase before user-story implementation.

- [X] T005 Extend `src/game/input_state.py` with an explicit `interact` action mapped to the configured interaction key, while preserving existing movement and quit behavior.
- [X] T006 Extend `src/game/state.py` with an optional workflow-state field and elapsed-time update seam, keeping player movement, camera updates, and workflow transitions separately callable.
- [X] T007 Extend `src/game/world.py` with structured central document-source and Civil Servant placement data; preserve existing collision bounds and ensure all new positions remain valid world coordinates.
- [X] T008 [P] Add `tests/unit/test_state.py` coverage proving the feature 001 player/camera update still works when a workflow state is present and that negative elapsed time is rejected.

**Checkpoint**: Existing movement/collision/camera behavior remains green, the interaction input exists, and workflow state can be carried by the main game state without display dependencies.

---

## Phase 3: User Story 1 - Complete the First Bureaucratic Wave (Priority: P1) 🎯 MVP

**Goal**: Start wave 1 with one Civil Servant, collect the initial document from the central source, explicitly hand it over, and complete the wave.

**Independent Test**: Run the wave 1 unit/integration tests, then launch the game, press the interaction key at the central source and Civil Servant 1, and confirm one valid handover completes wave 1.

### Tests for User Story 1

- [X] T009 [P] [US1] Add `tests/unit/test_wave_generation.py` covering wave 1 creation with exactly one unique Civil Servant, one ordered step, a valid spawn/placement, and rejection of invalid or unsolvable definitions.
- [X] T010 [P] [US1] Add `tests/unit/test_bureaucracy.py` coverage for wave 1 initial-document collection from the central source, correct handover acceptance, document consumption, served-state update, and wave completion.
- [X] T011 [P] [US1] Extend `tests/smoke/test_launch_contract.py` to assert that a new runtime starts at wave 1 with one Civil Servant, a central document source, and a visible current request without opening an interactive display.
- [X] T012 [P] [US1] Add `tests/unit/test_interaction.py` covering explicit interaction gating: proximity alone does not collect or hand over, while the configured interaction action attempts the in-range operation.

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement `DocumentType`, `Document`, `WorkflowStep`, `CivilServant`, `WaveDefinition`, `WaveProgress`, and stable handover-result types in `src/game/bureaucracy.py`; enforce that the carried-document field is nullable and that a wave contains exactly N unique servants for wave N.
- [X] T014 [US1] Implement wave-definition validation and deterministic wave 1 construction in `src/game/bureaucracy.py`; require the initial document to be supplied by the central source and reject invalid step order, duplicate servant IDs, and unresolved requirements.
- [X] T015 [US1] Implement pure initial-document collection and wave 1 handover transitions in `src/game/bureaucracy.py`; a valid handover must consume the document exactly once, mark the servant served, and complete the wave.
- [X] T016 [US1] Integrate workflow initialization and explicit interaction dispatch into `src/game/state.py`, using existing player/world positions for interaction range while leaving movement and collision rules unchanged.
- [X] T017 [US1] Update `src/presentation/renderer.py` to display wave number, Civil Servant 1 request/served state, central document source, carried-document status, and successful handover feedback using text and distinct placeholder shapes.
- [X] T018 [US1] Update `src/presentation/window.py` to pass the explicit interaction action into workflow collection/handover dispatch and preserve the existing frame-rate-independent main loop.

**Checkpoint**: User Story 1 is independently playable and testable; wave 1 completes after exactly one correct explicit handover.

---

## Phase 4: User Story 2 - Chain Documents Through the Second Wave (Priority: P1)

**Goal**: Add wave 2 with two Civil Servants, issue a permit from Civil Servant 1, require it for Civil Servant 2, and transition automatically after completion.

**Independent Test**: Run wave 2 tests, verify the sequence `central source → Civil Servant 1 → permit → Civil Servant 2`, and confirm wave 2 completes only after both ordered handovers.

### Tests for User Story 2

- [X] T019 [P] [US2] Extend `tests/unit/test_wave_generation.py` to verify wave 2 contains exactly two unique Civil Servants and contiguous ordered steps, and that the definition is completable before activation.
- [X] T020 [P] [US2] Extend `tests/unit/test_bureaucracy.py` with the exact wave 2 chain: initial document accepted by Civil Servant 1, permit issued once, permit required by Civil Servant 2, and completion only after Civil Servant 2 accepts it.
- [X] T021 [P] [US2] Add `tests/unit/test_wave_transition.py` covering completion feedback, a 10.0-second elapsed transition timer, no early next-wave activation, and automatic next-wave activation at zero remaining time.
- [X] T022 [P] [US2] Extend `tests/unit/test_state.py` to verify workflow elapsed time advances with simulation time while player movement and camera updates continue during the 10-second transition.
- [X] T023 [P] [US2] Extend `tests/smoke/test_launch_contract.py` to assert that wave 2 creates two servant placements and exposes a permit as the result of the first successful handover.

### Implementation for User Story 2

- [X] T024 [US2] Add the declarative wave 2 definition to `src/game/bureaucracy.py`: Civil Servant 1 requires `INITIAL_DOCUMENT` from `CENTRAL_SOURCE` and issues `PERMIT`; Civil Servant 2 requires `PERMIT` from `PREVIOUS_HANDOVER`.
- [X] T025 [US2] Implement ordered-step validation and next-step document ownership in `src/game/bureaucracy.py`; only the first unserved step may accept a handover and a permit must be issued exactly once.
- [X] T026 [US2] Implement completion feedback and elapsed-time automatic wave transition in `src/game/bureaucracy.py` and `src/game/state.py`; start `transition_remaining` at exactly `10.0` after the final successful handover and activate the next validated wave at zero.
- [X] T027 [US2] Update `src/presentation/renderer.py` to show both Civil Servants, the active permit, completion feedback, and the visible transition countdown without relying on color alone.
- [X] T028 [US2] Update `src/presentation/window.py` and `main.py` integration to keep movement/rendering active during the 10-second transition and start the next wave without blocking sleep.

**Checkpoint**: User Stories 1 and 2 are playable; wave 2 demonstrates the complete document-to-permit chain and automatic transition.

---

## Phase 5: User Story 3 - Understand and Recover from Bureaucratic Errors (Priority: P2)

**Goal**: Reject missing, incorrect, duplicate, and out-of-order handovers with stable progress and readable feedback.

**Independent Test**: Perform each invalid interaction during waves 1 and 2, verify no valid state changes, then complete the workflow using the correct document sequence.

### Tests for User Story 3

- [X] T029 [P] [US3] Extend `tests/unit/test_bureaucracy.py` with missing-document, wrong-document, wrong-recipient, out-of-order, already-served, and carried-document-preservation cases.
- [X] T030 [P] [US3] Add `tests/unit/test_feedback.py` covering stable feedback reasons for requested document, successful handover, mismatch, no document, duplicate service, newly issued permit, and remaining requirements.
- [X] T031 [P] [US3] Extend `tests/unit/test_interaction.py` to verify a second-document pickup is rejected while carrying a document and proximity alone never changes workflow state.
- [X] T032 [P] [US3] Extend `tests/smoke/test_launch_contract.py` to verify a new session resets to wave 1 with no carried document and no prior served state.

### Implementation for User Story 3

- [X] T033 [US3] Implement stable rejection reasons and immutable failure transitions in `src/game/bureaucracy.py`; invalid attempts must not consume documents, change served states, issue rewards, or advance the wave.
- [X] T034 [US3] Implement single-document inventory protection and deterministic target/step selection in `src/game/state.py` and `src/game/world.py`; preserve the current carried document when collection is blocked.
- [X] T035 [US3] Add readable feedback message construction in `src/game/bureaucracy.py` for requested document, accepted/rejected handover, permit issuance, served count, and remaining requirement.
- [X] T036 [US3] Render all workflow feedback and current requirements in `src/presentation/renderer.py` using text, labels, outlines, and state markers in addition to color.
- [X] T037 [US3] Ensure `src/presentation/window.py` keeps invalid-interaction feedback visible long enough to read without blocking movement or corrupting the active input state.

**Checkpoint**: All three stories are independently demonstrable; invalid bureaucracy creates understandable friction without corrupting progress.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Preserve feature 001, validate the complete workflow, and document the final interaction contract.

- [X] T038 [P] Add public-interface type hints and concise docstrings for workflow entities and transitions in `src/game/bureaucracy.py`, `src/game/state.py`, and `src/game/input_state.py`.
- [X] T039 [P] Add regression assertions to `tests/unit/test_state.py` proving existing movement, collision, camera, and window-close behavior remains unchanged with workflow state active.
- [X] T040 Run the complete suite with `./.venv/bin/python -m pytest` and resolve regressions across `tests/unit/` and `tests/smoke/`.
- [X] T041 Run the manual scenarios in `specs/002-bureaucracy-document-workflow/quickstart.md`, including the wave 1 flow, wave 2 permit chain, invalid handovers, 10-second transition, and feature 001 movement/camera checks.
- [X] T042 Update `README.md` with the interaction key, document-source behavior, wave 1/wave 2 workflow, invalid-handover feedback, and the current out-of-scope boundaries.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; establishes constants, fixtures, and the regression baseline.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all story work.
- **Phase 3 US1**: Depends on Phase 2 and delivers the MVP direct-handover workflow.
- **Phase 4 US2**: Depends on US1's workflow state and interaction seams; adds the permit chain and timer.
- **Phase 5 US3**: Depends on US1/US2 outcomes; hardens rejection and feedback behavior.
- **Phase 6 Polish**: Depends on all desired stories being implemented.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on another workflow story.
- **US2 (P1)**: Depends on US1's wave definition, document collection, handover, and runtime integration.
- **US3 (P2)**: Depends on the success and failure result types established by US1 and the permit sequence established by US2.

### Dependency Graph

```text
Setup (T001-T004)
        |
Foundation (T005-T008)
        |
        +--> US1: Wave 1 direct handover (T009-T018)
                 |
                 +--> US2: Wave 2 permit chain + timer (T019-T028)
                          |
                          +--> US3: invalid workflows + feedback (T029-T037)
                                   |
                                   +--> Polish/regression (T038-T042)
```

### Parallel Opportunities

- T002–T004 can run in parallel after the baseline is captured; T003 and T004 touch separate files.
- T008 can run in parallel with the foundational input/state/world seam work.
- US1 tests T009–T012 can run in parallel because they target separate test concerns; T013 and T014 can proceed in parallel before T015–T018 integration.
- US2 tests T019–T023 can run in parallel; T024 and T027 can be developed independently after the data shape is agreed.
- US3 tests T029–T032 can run in parallel; T033 and T035 touch the pure workflow module sequentially, while T034 and T036 can proceed once their interfaces are stable.
- T038 and T039 can run in parallel; T040–T042 follow implementation completion.

## Parallel Example: User Story 1

```text
Track A: T009 tests/unit/test_wave_generation.py -> T014 src/game/bureaucracy.py
Track B: T010 tests/unit/test_bureaucracy.py -> T015 src/game/bureaucracy.py
Track C: T011 tests/smoke/test_launch_contract.py -> T016 src/game/state.py
Track D: T012 tests/unit/test_interaction.py -> T005 src/game/input_state.py
Integration: T016 -> T017 renderer.py -> T018 window.py
```

## Parallel Example: User Story 2

```text
Track A: T019/T020 tests -> T024/T025 src/game/bureaucracy.py
Track B: T021 tests/unit/test_wave_transition.py -> T026 state/timer integration
Track C: T022 tests/unit/test_state.py -> T028 window/main integration
Presentation: T027 src/presentation/renderer.py after workflow snapshot fields are stable
```

## Parallel Example: User Story 3

```text
Track A: T029 tests/unit/test_bureaucracy.py -> T033 src/game/bureaucracy.py
Track B: T030 tests/unit/test_feedback.py -> T035 src/game/bureaucracy.py
Track C: T031 tests/unit/test_interaction.py -> T034 state/world inventory guard
Presentation: T036 renderer.py -> T037 window.py
```

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Setup and Foundational phases.
2. Implement wave 1 with the central document source, explicit interaction, and one valid handover.
3. Stop and validate that wave 1 is completable and feature 001 movement/camera behavior remains intact.
4. Demo the first bureaucracy slice before adding permits or automatic transitions.

### Incremental Delivery

1. Add US2 and validate the exact wave 2 permit chain plus 10-second transition.
2. Add US3 and validate all invalid-handover invariants and feedback.
3. Run the full quickstart and pytest suite.
4. Keep stamina, fishing, persistence, and future special bureaucrats outside this feature until separately specified.

### Completion Evidence

- All 42 tasks are checked off.
- `./.venv/bin/python -m pytest` passes with feature 001 regressions covered.
- `python main.py` launches the workflow-enabled game.
- Wave 1, wave 2, invalid interaction, and 10-second transition scenarios pass.
