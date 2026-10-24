# Research: Bureaucratic Document Workflow

**Feature**: `002-bureaucracy-document-workflow`
**Date**: 2026-10-13

The existing project already provides a pure movement state, a Pygame-ce window adapter, placeholder rendering, and pytest. Research therefore focuses on the smallest deterministic workflow design that fits those seams.

## Decision 1: Model workflow transitions as pure state changes

**Decision**: Store the active wave, civil servants, carried document, completion phase, feedback message, and remaining transition time in explicit workflow state. Collection, handover, and time advancement return updated state plus an outcome rather than mutating global state.

**Rationale**: Invalid handovers must preserve valid progress, and the constitution requires deterministic, independently testable rules. Returning typed outcomes also gives the UI enough information to explain acceptance, rejection, permits, and remaining work.

**Alternatives considered**:

- Mutating servant objects from the render loop: rejected because it obscures state transitions and makes invalid-handover regression tests fragile.
- A general event bus: rejected as unnecessary indirection for one workflow and contrary to the simple modular architecture principle.

## Decision 2: Use structured workflow definitions for waves 1 and 2

**Decision**: Define a wave as an ordered list of civil-servant workflow steps. Each step specifies its requested document type, recipient identity, served result, and optional issued document. Wave 1 contains one initial-document step; wave 2 contains an initial-document step that issues a permit followed by a permit step.

**Rationale**: This directly represents the requested wave 2 chain and gives future document types a data-driven extension point. Wave number determines the required servant count, while the definition determines the solvable sequence.

**Alternatives considered**:

- Hard-code `if wave == 1` and `if wave == 2` branches: rejected because new document types would require rewriting the main loop.
- Generate arbitrary requirements at runtime: rejected because every generated wave must be validated as completable and this feature has no randomness requirement.

## Decision 3: Validate workflows before activation

**Decision**: A wave definition is valid only if it has the expected number of unique civil servants, every required document can be supplied by the central source or a preceding successful outcome, and the final step has no unresolved requirement.

**Rationale**: This prevents unwinnable waves and makes wave generation failures deterministic and visible during setup rather than trapping a player mid-session.

**Alternatives considered**:

- Detect impossible workflows only when the player reaches them: rejected because failure would occur too late and violate the solvability principle.
- Permit incomplete definitions for experimentation: deferred to tooling outside the playable game.

## Decision 4: Use a single carried document and explicit interaction

**Decision**: The player has zero or one carried document. The input layer exposes a dedicated interaction action; the workflow layer only attempts collection or handover when the world layer confirms a valid target is in range.

**Rationale**: This matches the clarification, avoids accidental proximity actions, keeps document ownership unambiguous, and makes incorrect-document tests straightforward.

**Alternatives considered**:

- Multiple inventory slots: rejected for this first workflow because it weakens the intended chain and adds UI/state complexity without player value.
- Automatic proximity interactions: rejected by clarification because accidental handovers would be difficult to understand.

## Decision 5: Treat the ten-second transition as elapsed simulation time

**Decision**: On the final successful handover, set a completion feedback phase with `transition_remaining = 10.0`. Each update subtracts elapsed time; when it reaches zero, create the next wave automatically.

**Rationale**: This preserves a responsive main loop, works across frame rates, and makes the timer directly testable with synthetic elapsed durations.

**Alternatives considered**:

- Blocking sleep for ten seconds: rejected because it freezes movement, rendering, and input.
- Counting rendered frames: rejected because the transition duration would vary with frame rate.

## Integration findings

- Existing `GameState` should expose workflow state without moving movement or collision rules into the bureaucracy module.
- Existing `InputState` needs one explicit interaction action while retaining all current movement behavior.
- Existing renderer should receive a workflow snapshot and draw civil servants, the central document source, carried document, and textual feedback using placeholder shapes.
- No storage, network, account, audio, or external API integration is required.

## Decision 6: Cap servants while continuing wave-length escalation

**Decision**: Create `min(wave_number, 4)` civil servants at four fixed authored spawn points, but create exactly `wave_number` document steps. Waves 1–4 use the existing ordered identities. Starting with wave 5, each step after the first four selects one of the three identities other than the previous recipient; the selection uses a seeded random source.

**Rationale**: This preserves the existing escalation in the number of required handovers while preventing the world from filling with more than four officials. It also matches the specified example `1 → 2 → 3 → 4 → 1–3`.

**Alternatives considered**:

- End the wave after every servant has been served once: rejected because it would make the requested post-fourth handover impossible.
- Spawn a new servant for every additional document: rejected because the feature explicitly caps the active servants at four.

## Decision 7: Separate workflow completion from recipient animation state

**Decision**: Keep `CivilServant.served` as the workflow completion flag, but derive presentation animation from both the served state and the current active workflow step. When a previously served servant becomes the next recipient in wave 5 or later, reset that servant's animation to `IDLE` immediately when the next step is assigned, before the player reaches the servant.

**Rationale**: A repeated recipient represents a new actionable document request even though the servant has already completed an earlier step. Reusing `served` alone would incorrectly leave the servant in its completion animation and make the next target unclear.

**Alternatives considered**:

- Reset animation only when the player enters interaction range: rejected because the player needs to identify the next target while navigating toward it.
- Clear the servant's workflow `served` flag: rejected because it would corrupt the distinction between completed steps and the current repeated requirement.

## Decision 8: Remove developer-only Civil Servant text

**Decision**: Remove all debug/developer-only text drawn at or beside Civil Servants. Do not render `PENDING`, `SERVED`, or any other status marker beside the servant; the servant's animation is the sole visual indicator of workflow status. Unrelated workflow feedback may remain in the general gameplay UI.

**Rationale**: Debug labels expose implementation details and compete with the readable player-facing bureaucracy UI. The rule is presentation-only and does not alter workflow state or validation.

**Alternatives considered**:

- Hide debug text only in release mode: rejected because the playable presentation must be clean in every supported runtime.
- Replace debug text with more debug text or status markers: rejected because the clarification requires the animation to be the sole Civil Servant status indicator.
