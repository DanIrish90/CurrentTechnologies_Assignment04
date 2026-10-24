# Quickstart Validation: Bureaucratic Document Workflow

**Feature**: `002-bureaucracy-document-workflow`

This guide validates the workflow without breaking feature 001 movement, collision, camera, or UI behavior. It assumes the existing Python environment has been installed with Pygame-ce and pytest.

## 1. Automated validation

From the repository root:

```bash
./.venv/bin/python -m pytest
```

Expected result: all existing feature 001 tests and the new workflow tests pass. The workflow tests must cover wave generation, document collection, correct handovers, permit issuance, invalid-handover invariants, duplicate prevention, 10-second progression, and integration with the existing game state.

Baseline before workflow implementation: the existing feature 001 suite passed 25 tests.

The authoritative entities and transitions are documented in [data-model.md](./data-model.md).

## 2. Wave 1 manual scenario

1. Launch the game with `python main.py`.
2. Confirm the UI identifies wave 1, one Civil Servant, the requested initial document, and the central document source.
3. Walk to the central document source.
4. Press the documented interaction key, expected to be `E`.
5. Confirm the carried-document UI identifies the initial document.
6. Walk to Civil Servant 1 and press the interaction key.
7. Confirm the handover is accepted, the document is consumed, the servant is marked served, and completion feedback appears.
8. Confirm the next wave starts automatically 10 seconds after the final successful handover.

Expected result: wave 1 contains exactly one servant and completes after one valid handover.

## 3. Wave 2 permit-chain scenario

1. Confirm wave 2 contains exactly two Civil Servants.
2. Confirm Civil Servant 1 requests the initial document and Civil Servant 2 is visibly pending the next workflow item.
3. Collect the initial document from the central document source with the interaction key.
4. Hand it to Civil Servant 1.
5. Confirm the initial document is consumed and a permit is issued as the carried document.
6. Attempt to hand the permit to Civil Servant 2.
7. Confirm the permit is accepted and Civil Servant 2 becomes served.
8. Confirm wave 2 completes only after both servants are served, then observe the 10-second automatic transition.

Expected result: the required sequence is `central source → Civil Servant 1 → permit → Civil Servant 2`.

## 4. Invalid-interaction scenario

1. Attempt a handover while carrying no document.
2. Collect the initial document and attempt to hand it to the wrong servant or at the wrong workflow point.
3. Attempt to hand the wave 2 permit back to Civil Servant 1 after it was issued for Civil Servant 2.
4. Attempt to interact with a served servant again.
5. Collect or deliver the correct document afterward.

Expected result: each invalid attempt gives a readable reason, consumes no invalid document, produces no duplicate reward, and leaves the valid wave sequence completable.

## 5. Regression and timing validation

1. Move while the workflow is active and confirm feature 001 movement, collision, camera, and UI remain responsive.
2. Trigger the final handover and measure the transition.
3. Confirm the next wave starts after 10 elapsed seconds even if rendering load changes.
4. Close and relaunch the game.

Expected result: no persistence is assumed; a new session starts at wave 1, and the previous session's carried document or wave progress is not reused.

## 6. Acceptance evidence

Record:

- pytest output and total test count;
- wave 1 completion result across 20 deterministic runs;
- wave 2 permit-chain completion result across 20 deterministic runs;
- invalid-handover count and confirmation that no invalid attempt mutates valid progress;
- measured transition time for at least 10 completed waves;
- manual confirmation of readable requests, carried-document status, rejection reasons, completion feedback, and preserved movement/camera behavior.

Implementation validation record: 47 pytest tests passed on 2026-10-13. A headless Pygame run processed resize, explicit interaction, focus-loss, and close events without error; visual confirmation should still be performed on a desktop display.

Latest automated validation: 240 pytest tests passed after implementing the repeated-recipient animation and Civil Servant debug-text removal. Manual desktop visual confirmation remains required for the final presentation check.

## 7. Four-servant cap and random continuation

1. Create waves 1 through 6 with a fixed set of four authored spawn positions.
2. Confirm the servant counts are `1, 2, 3, 4, 4, 4` while the handover-step counts are `1, 2, 3, 4, 5, 6`.
3. In wave 5, complete the first four handovers in the existing order `servant-1 → servant-2 → servant-3 → servant-4`.
4. Confirm the fifth document is assigned to one of servants 1–3 and never directly to servant 4.
5. Repeat wave 5 with a fixed random seed and confirm the recipient sequence is identical; use a different seed and confirm a valid alternative sequence can be produced.

Expected result: no wave creates more than four servants, all servants stay at their assigned spawn points, and every random continuation excludes only the immediately previous recipient.

## 8. Repeated-recipient animation and presentation cleanup

1. Start a seeded wave 5 or later and complete the first four handovers.
2. Note the randomly selected next recipient and verify that the recipient's animation is `IDLE` immediately after the handover assigns the next step, even if that servant was already served earlier in the wave.
3. Confirm the recipient remains in the idle animation while the player approaches and before the next interaction.
4. Inspect the rendered Civil Servants and confirm no debug or developer-only text is displayed beside them.
5. Confirm the current document requirement and general workflow feedback remain readable, while no status text, status marker, or separate served-state indicator appears beside the Civil Servant.

Expected result: the next recipient is visually identifiable before approach, and Civil Servant workflow status is communicated only through animation in every supported runtime presentation.
