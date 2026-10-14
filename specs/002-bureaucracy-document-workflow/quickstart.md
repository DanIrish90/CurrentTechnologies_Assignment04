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
