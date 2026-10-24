# Feature Specification: Bureaucratic Document Workflow

**Feature Branch**: `002-bureaucracy-document-workflow`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Every new Wave should spawn a Civil Servant who needs a document. The Player has to get the document, and serve it to the Servant. A Wave ends if all Civil Servants have been served. Wave 1 Starts with one Civil Servant. In Wave 2, one additional Servant is spawned, in that case, you give Servant 1 the Documents and you receive a Permit which you have to deliver to Servant 2."

## Clarifications

### Session 2026-10-13

- Q: Soll das Aufnehmen und Übergeben eines Dokuments automatisch bei Nähe oder durch eine separate Interaktionstaste erfolgen? → A: Separate Interaktionstaste, z. B. `E`.
- Q: Soll die nächste Welle nach erfolgreicher Bearbeitung aller Civil Servants automatisch starten oder erst nach einer ausdrücklichen Bestätigung des Spielers? → A: Automatischer Start 10 Sekunden nach dem Abschluss der aktuellen Welle.
- Q: Woher soll der Spieler das jeweils benötigte initiale Dokument erhalten? → A: Eine zentrale Dokumentenstelle liefert das benötigte initiale Dokument.

### Session 2026-10-24

- Q: Soll die Anzahl der Beamten pro Tag/Welle bei 1 starten und bis maximal 4 ansteigen, sodass ab Tag 4 beziehungsweise 5 immer genau 4 Beamte aktiv sind? → A: A — Tag 1 hat 1 Beamten, Tag 2 hat 2, Tag 3 hat 3 und ab Tag 4 sind immer genau 4 Beamte aktiv.
- Q: Ab Tag 5 soll der nächste Dokumentempfänger zufällig aus allen Beamten außer dem zuletzt bedienten Beamten ausgewählt werden? → A: A — Bei jeder Weitergabe wird zufällig aus den drei anderen Beamten gewählt; dadurch sind beispielsweise nach `1 → 2 → 3 → 4` die Beamten 1 bis 3 mögliche nächste Empfänger.
- Q: Soll ein bereits bedienter Beamter wieder die Idle-Animation abspielen, sobald er ab Welle 5 als nächster Dokumentempfänger zufällig ausgewählt wurde? → A: Ja — ab dem Zeitpunkt, an dem er als nächstes Ziel feststeht, wechselt seine Animation zurück zu Idle, damit der Spieler ihn als neue Aufgabe erkennt.
- Q: Soll der bei Civil Servants angezeigte Debug-Text vollständig aus der Spieleransicht entfernt werden? → A: Ja — sämtlicher Debug-Text bei Civil Servants wird restlos entfernt; ausdrücklich vorgesehene Gameplay-Anzeigen wie Dokumentanforderungen, Status und Feedback bleiben erlaubt.
- Q: Soll auch der Text `PENDING` beziehungsweise `SERVED` direkt bei Civil Servants entfernt werden? → A: Ja — diese Statuswörter werden ebenfalls nicht angezeigt; der Status darf nur noch über visuelle Zustände und die übrige Gameplay-Oberfläche erkennbar sein.
- Q: Soll der Status eines Civil Servant ausschließlich anhand seiner Animation erkennbar sein, ohne zusätzliche Formen, Umrandungen, Symbole oder andere Statusmarker? → A: Ja — die Animation ist die einzige visuelle Statusanzeige des Civil Servant.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete the First Bureaucratic Wave (Priority: P1)

As a player, I want to obtain the document requested by the first civil servant and hand it over so that I can complete the first wave and understand the core bureaucratic interaction.

**Why this priority**: The first wave establishes the game's central decision and feedback loop: identify a request, obtain the correct document, serve the civil servant, and receive clear confirmation.

**Independent Test**: Start a new game at wave 1, inspect the civil servant's request, obtain the requested document from the document source, deliver it to that civil servant, and verify that the wave completes.

**Acceptance Scenarios**:

1. **Given** a new game starts at wave 1, **When** the player enters the play area, **Then** exactly one civil servant is present and visibly indicates which document is required.
2. **Given** the wave 1 civil servant has an outstanding request, **When** the player visits the document source, **Then** the player receives the requested document and the active carried document is shown in the game state.
3. **Given** the player carries the document requested by the wave 1 civil servant, **When** the player serves that civil servant, **Then** the document is accepted, the civil servant is marked served, and the player receives clear feedback.
4. **Given** the only civil servant in wave 1 has been served, **When** the handover is confirmed, **Then** wave 1 ends and the next wave becomes available.

---

### User Story 2 - Chain Documents Through the Second Wave (Priority: P1)

As a player, I want the first handover in wave 2 to produce a permit needed by the second civil servant so that bureaucracy becomes an understandable chain rather than a set of unrelated deliveries.

**Why this priority**: The wave 2 chain is the first escalation of the game's core loop and demonstrates how serving one official can create the next bureaucratic obligation.

**Independent Test**: Start wave 2, verify two civil servants are present, obtain and deliver the first required document to civil servant 1, collect the resulting permit, deliver it to civil servant 2, and verify that the wave completes only after both handovers.

**Acceptance Scenarios**:

1. **Given** wave 1 is complete and wave 2 begins, **When** the wave is displayed, **Then** exactly two civil servants are present at their assigned spawn points, with the active requirement shown through gameplay UI and each servant's workflow status shown exclusively through its animation.
2. **Given** civil servant 1 in wave 2 requires the initial document, **When** the player serves civil servant 1 with that document, **Then** the document is consumed and a permit is issued to the player as the next active document.
3. **Given** the player carries the permit issued by civil servant 1, **When** the player serves civil servant 2, **Then** the permit is accepted and civil servant 2 is marked served.
4. **Given** only civil servant 1 has been served in wave 2, **When** the player attempts to end the wave, **Then** the wave remains active until civil servant 2 has also been served.
5. **Given** both civil servants in wave 2 have been served in the required order, **When** the second handover is confirmed, **Then** wave 2 ends, completion feedback is shown, and the next wave starts automatically after 10 seconds.

---

### User Story 3 - Understand and Recover from Bureaucratic Errors (Priority: P2)

As a player, I want incorrect documents and premature handovers to be rejected with understandable feedback so that I can correct my approach without corrupting wave progress.

**Why this priority**: Bureaucratic difficulty should create humorous pressure without making the rules opaque or allowing an invalid handover to break progression.

**Independent Test**: During waves 1 and 2, attempt to serve a civil servant with no document, the wrong document, or a document intended for another civil servant, then verify that the request remains active and the player can continue with the correct document.

**Acceptance Scenarios**:

1. **Given** the player carries no active document, **When** the player attempts to serve a civil servant, **Then** no service is recorded and the game explains that a document is required.
2. **Given** the player carries a document that does not satisfy the civil servant's current request, **When** the player attempts the handover, **Then** the document is not consumed, the civil servant remains unserved, and the game identifies the mismatch.
3. **Given** wave 2 has issued a permit for civil servant 2, **When** the player tries to give that permit to civil servant 1 again, **Then** the handover is rejected without changing either servant's served state.
4. **Given** a civil servant has already been served, **When** the player interacts with that civil servant again, **Then** no duplicate reward or duplicate progress is created.
5. **Given** an invalid handover occurs, **When** the player obtains or delivers the correct document afterward, **Then** the wave can still be completed normally.

### Edge Cases

- If the player visits the document source before a new request is active, the source provides only the currently required initial document or explains that no document is currently available.
- If the player tries to collect a second document while already carrying one, the game preserves the carried document and clearly communicates that it must be delivered or discarded according to the current rules.
- If the player leaves the wave area while carrying a document, the carried document remains associated with the current wave and cannot be silently replaced by a later wave's document.
- If the player interacts with two civil servants at the same location, the game uses a deterministic interaction order and displays which civil servant received or rejected the handover.
- If the player closes or restarts the game during a wave, this feature does not promise persistence; a new session starts from its defined initial wave state.
- If a wave's required sequence cannot be completed from its generated requirements, the wave must be rejected during setup rather than trapping the player in an unwinnable state.
- If the player attempts to advance without every current-wave civil servant served, the game keeps the current wave active and identifies the remaining requirement.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game MUST represent each wave as a distinct, ordered bureaucratic challenge.
- **FR-002**: Wave 1 MUST begin with exactly one civil servant and wave 2 MUST begin with exactly two civil servants.
- **FR-003**: For wave N, the game MUST spawn `min(N, 4)` civil servants: one in wave 1, two in wave 2, three in wave 3, and exactly four from wave 4 onward.
- **FR-003a**: Each of the four supported civil-servant identities MUST have a defined spawn point, and an active civil servant MUST remain at that identity's assigned spawn point for the entire wave.
- **FR-004**: Every active civil servant MUST have a visible current request for a specific document; the Civil Servant's workflow status MUST be communicated exclusively through its animation and MUST NOT use status text, shapes, outlines, icons, or other additional status markers.
- **FR-005**: The player MUST be able to obtain the currently required initial document from the single central document source.
- **FR-006**: The player MUST be able to carry an active document and see which document is currently carried.
- **FR-007**: A civil servant MUST accept a handover only when the carried document matches that civil servant's current request and the civil servant has not already been served.
- **FR-008**: A successful handover MUST consume the delivered document, mark the civil servant served, and provide visible confirmation.
- **FR-009**: In wave 1, serving the only civil servant with the requested initial document MUST complete the wave.
- **FR-010**: In wave 2, serving civil servant 1 with the initial document MUST issue a permit that becomes the next required carried document for civil servant 2.
- **FR-011**: In wave 2, civil servant 2 MUST accept the permit issued by civil servant 1, and the wave MUST NOT complete before that handover.
- **FR-012**: A wave MUST end only after all of its civil servants are served in the required sequence.
- **FR-012a**: After a wave ends, the game MUST show completion feedback and MUST automatically start the next wave 10 seconds after the final successful handover.
- **FR-012b**: For wave 5 and every later wave, after each successful handover the next document MUST be assigned to a randomly selected civil servant from the three identities that were not the immediately previous recipient; the current recipient MUST NOT be selected again directly.
- **FR-012c**: The existing document handover rules for waves 1 through 4 MUST remain unchanged; the random recipient rule MUST begin only with wave 5.
- **FR-012d**: When a Civil Servant is selected as the next recipient for an additional document in wave 5 or later, that Civil Servant MUST switch back to the `IDLE` animation as soon as the next workflow step is assigned, even if the Civil Servant was served earlier in the same wave. The switch MUST occur before the player reaches or interacts with the Civil Servant.
- **FR-012e**: The game MUST NOT render any debug, developer-only, `PENDING`, or `SERVED` text at or beside Civil Servants. The Civil Servant animation MUST be the only visual indicator of that servant's workflow status; no additional shape, outline, icon, marker, or status overlay may be used. Workflow feedback may identify served progress elsewhere in the gameplay UI.
- **FR-013**: The game MUST reject missing, incorrect, or out-of-order documents without consuming the incorrect document or changing valid progress.
- **FR-014**: The game MUST prevent duplicate service rewards and duplicate wave progress when a served civil servant is interacted with again.
- **FR-015**: The game MUST provide feedback that identifies the requested document, successful handover, rejected handover, newly issued permit, served civil servants, and remaining wave requirements.
- **FR-016**: Wave requirements and document outcomes MUST be represented as structured game data so additional document types and civil servant sequences can be added without rewriting the core game loop.
- **FR-017**: Every generated wave MUST be validated as completable before it becomes active.
- **FR-018**: Invalid handovers MUST NOT corrupt the active wave, carried-document state, civil servant served states, or progression state.
- **FR-019**: The feature MUST preserve the existing top-down movement, collision, camera, and basic UI behavior from the core game slice.
- **FR-020**: The player MUST use a separate interaction action to collect a document or attempt a handover; proximity alone MUST NOT collect or deliver a document.

### Key Entities

- **Wave**: An ordered bureaucratic challenge with a number, active state, civil servants, current requirements, and completion status.
- **Civil Servant**: A wave participant with an identifier, location, current requested document, served state, and possible resulting document.
- **Document**: A carryable item with a type, source context, intended recipient or workflow step, and active/consumed state.
- **Permit**: A document issued by a successful civil-servant handover and used as the next step in the wave 2 workflow.
- **Document Source**: The place or interaction that supplies an initial document when the active wave requires one.
- **Handover**: A player interaction that attempts to deliver the carried document to a civil servant and produces acceptance or rejection feedback.
- **Wave Progress**: The current ordered workflow state, including served civil servants, carried document, and the next required action.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 20 new-game sessions, wave 1 starts with exactly one civil servant and can be completed through one correct document handover in every session.
- **SC-002**: In 20 wave 2 sessions, exactly two civil servants appear, the first handover issues a permit, and the second handover completes the wave in at least 19 sessions.
- **SC-003**: In 100 invalid-handover attempts covering missing, incorrect, duplicate, and out-of-order documents, zero attempts consume an invalid document or advance valid wave progress.
- **SC-004**: At least 9 out of 10 first-time testers can identify the active document request, obtain the initial document, complete wave 1, and describe why the wave ended without external instruction.
- **SC-005**: At least 9 out of 10 first-time testers can complete the wave 2 document-to-permit chain using only the on-screen requests and feedback.
- **SC-006**: Every generated wave in the supported progression is validated as completable before activation, with zero test fixtures creating an unwinnable wave.
- **SC-007**: In a 10-minute play session, all tested valid and invalid handovers preserve the existing movement and UI responsiveness without a crash or corrupted state.
- **SC-008**: In test sessions for waves 1 through 6, the active civil-servant counts are exactly 1, 2, 3, 4, 4, and 4, and every active civil servant remains at its assigned spawn point throughout its wave.
- **SC-009**: In at least 100 seeded wave-5-or-later handover selections, every selected recipient is one of the three civil servants other than the immediately previous recipient, and no direct recipient repetition occurs.

## Assumptions

- The existing top-down movement, collision, camera, and UI from feature 001 remain available and are reused.
- A single central document source exists in the play area and supplies the initial document required by the active workflow.
- The player carries at most one active document at a time in this feature; collecting a replacement is blocked until the current document is delivered or otherwise resolved.
- A successful handover occurs when the player is within the normal interaction range of the intended civil servant and explicitly presses the separate interaction action.
- Wave 1 and wave 2 are the required playable scope of this feature; the structured wave/document model is designed to support later waves without defining every future document rule here.
- The wave count determines the number of active civil servants as `min(wave number, 4)`; from wave 4 onward the same four civil-servant identities and their assigned spawn points are used.
- Waves 1 through 4 retain the existing deterministic document handover flow. Starting with wave 5, each next recipient is independently selected from the three identities other than the immediately previous recipient; random selection is part of the gameplay rule and must be reproducible in tests through seeded randomness.
- Wave 2 uses the explicitly defined chain: initial document to civil servant 1, permit from civil servant 1 to civil servant 2.
- The 10-second transition timer begins immediately after the final successful handover and does not require an additional player confirmation.
- Civil servants and document sources use placeholder visuals and text in this feature; final art, dialogue, audio, stamina costs, and persistence are outside scope.
- A new session starts at wave 1, and saving or restoring mid-wave progress is outside scope.
