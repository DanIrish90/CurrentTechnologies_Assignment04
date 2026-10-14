# Feature Specification: Stamina Usage and Recovery

**Feature Branch**: `003-stamina-usage`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "The Player has a StaminaBar. If he has documents in his Hands the Stamina drains. When the Stamina reaches 0 the Game is Over. Add a Stamina Regen Zone, if the Player stands in it and has no documents the Stamina regenerates."

## Clarifications

### Session 2026-10-13

- Q: Welche festen Balancing-Werte sollen für maximale Ausdauer, Dokumentenverbrauch und Regeneration gelten? → A: Maximum 100, Verbrauch 5/s, Regeneration 10/s.
- Q: Wie soll der Spieler nach dem Game Over eine neue Sitzung starten? → A: Über einen anklickbaren „Restart“-Button.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Track stamina while carrying documents (Priority: P1)

As the player, I want to see my remaining stamina and understand that carrying official documents exhausts me, so that I can decide when to complete bureaucratic work and when to recover.

**Why this priority**: Stamina creates the survival pressure that connects movement and document processing.

**Independent Test**: Start a session, collect a document, and carry it for a measured period while observing the stamina indicator and its explanatory feedback.

**Acceptance Scenarios**:

1. **Given** a new session, **When** the player observes the game, **Then** the stamina indicator shows full stamina and communicates its current state without relying on color alone.
2. **Given** the player is carrying a document, **When** simulation time passes, **Then** stamina decreases continuously according to elapsed time.
3. **Given** the player is not carrying a document, **When** simulation time passes outside a recovery zone, **Then** stamina does not decrease.

### User Story 2 - Recover stamina at a regeneration zone (Priority: P1)

As the player, I want a clearly identifiable recovery zone, so that I can safely restore stamina before continuing the paperwork.

**Why this priority**: Recovery makes the drain survivable and gives the player a meaningful route-planning decision.

**Independent Test**: Enter the recovery zone without a document, wait for a measured period, then leave or pick up a document and verify the corresponding stamina behavior.

**Acceptance Scenarios**:

1. **Given** the player is inside the stamina recovery zone and carries no document, **When** simulation time passes, **Then** stamina increases according to elapsed time until it reaches its maximum.
2. **Given** the player is outside the recovery zone and carries no document, **When** simulation time passes, **Then** stamina does not increase.
3. **Given** the player is inside the recovery zone while carrying a document, **When** simulation time passes, **Then** the document-carrying drain remains active and recovery is suppressed.
4. **Given** stamina is already full, **When** the player remains in the recovery zone without a document, **Then** stamina remains at its maximum and does not overflow.

### User Story 3 - Understand and respond to game over (Priority: P1)

As the player, I want an unmistakable game-over state when stamina is exhausted, so that I understand why the run ended and can start a new attempt.

**Why this priority**: Exhaustion is the feature's primary failure condition and must be fair, visible, and actionable.

**Independent Test**: Carry a document until stamina reaches zero and verify the displayed reason, stable game-over state, and restart behavior.

**Acceptance Scenarios**:

1. **Given** the player is carrying a document with only a small amount of stamina remaining, **When** stamina reaches zero, **Then** the game enters game over and explicitly explains that exhaustion caused the loss.
2. **Given** the game is over, **When** simulation time passes or movement/input continues, **Then** stamina cannot become negative and no further drain or regeneration changes the finished run.
3. **Given** the game-over message and a clickable “Restart” button are displayed, **When** the player clicks the button, **Then** the new session begins with full stamina and normal play resumes.

### Edge Cases

- Stamina must never fall below zero or rise above its defined maximum, including when a time step crosses the exhaustion boundary.
- A document picked up at the same moment the player enters a recovery zone must be treated as carrying a document; carrying takes precedence over regeneration.
- Leaving the recovery zone stops regeneration on the next simulation update.
- Dropping or successfully handing over a document stops the carrying drain and allows recovery only if the player is in the zone.
- The recovery zone must remain distinguishable from document sources and civil servants, including for players who cannot distinguish colors.
- A game-over transition must happen once and must not repeatedly reset, duplicate feedback, or corrupt the active document workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game MUST maintain a stamina value for the player with a minimum of 0 and a maximum of 100.
- **FR-002**: A new session MUST begin with the player at maximum stamina.
- **FR-003**: The game MUST display the player's current stamina during active play using a readable bar and a non-color-only indicator such as a value or status label.
- **FR-004**: While the player carries at least one active document, the game MUST decrease stamina by 5 points per second of elapsed simulation time.
- **FR-005**: The carrying drain MUST be independent of rendering frame rate and MUST stop when no document is carried.
- **FR-006**: The game MUST provide at least one clearly marked stamina recovery zone in the playable area.
- **FR-007**: While the player is inside the recovery zone and carries no document, the game MUST increase stamina by 10 points per second of elapsed simulation time.
- **FR-008**: The game MUST NOT regenerate stamina outside the recovery zone, and MUST NOT regenerate while a document is carried.
- **FR-009**: Stamina drain MUST take precedence over regeneration if the player is both inside the recovery zone and carrying a document.
- **FR-010**: Stamina changes MUST be clamped to the defined minimum and maximum.
- **FR-011**: When stamina reaches 0, the game MUST enter a game-over state and clearly communicate that exhaustion ended the run.
- **FR-012**: Once game over begins, the game MUST stop stamina changes and prevent further gameplay actions from altering the finished run.
- **FR-013**: The game-over state MUST display a clickable “Restart” button; clicking it MUST start a new session with full stamina and a usable initial gameplay state.
- **FR-014**: Adding stamina behavior MUST preserve document handovers, wave progression, movement, camera behavior, and existing interaction feedback during active play.
- **FR-015**: The game MUST provide understandable visual or textual feedback for entering the recovery zone and for losing access to recovery while carrying a document.

### Key Entities

- **Player Stamina**: The player's bounded current energy, including its current value, maximum, and whether active play or game over is in effect.
- **Stamina Indicator**: The on-screen representation of current stamina and its critical or exhausted state.
- **Stamina Recovery Zone**: A marked area in the world that restores stamina only when the player is inside it and carries no document.
- **Carried Document**: The active document held by the player; its presence drives stamina consumption and suppresses recovery.
- **Game-Over State**: The terminal state of a run caused by stamina reaching zero, including the exhaustion reason and a clickable “Restart” button.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 20 test sessions, every session starts with the stamina indicator at its maximum and with a readable numeric or textual state.
- **SC-002**: Across 20 repeated tests with the same carried-document duration, final stamina values differ by no more than 5% of the maximum, regardless of display frame rate.
- **SC-003**: In 20 tests inside the recovery zone without a document, stamina rises toward the maximum; in 20 matching tests outside the zone, stamina does not rise.
- **SC-004**: In 20 tests where stamina is driven to zero while carrying a document, every run enters game over without allowing a negative stamina value.
- **SC-005**: At least 90% of playtesters can identify the current stamina state, the recovery zone, and the exhaustion reason without external explanation.
- **SC-006**: Existing movement and document-workflow smoke tests remain passing after stamina behavior is enabled.

## Assumptions

- The initial balance uses a maximum stamina of 100, a document-carrying drain of 5 points per second, and recovery of 10 points per second in the recovery zone; these values are centralized tuning values and may be adjusted during later balancing.
- A single recovery zone is sufficient for the first playable slice; additional zones or fishing-specific recovery can be added later.
- The player can carry at most one active document under the existing document workflow, so “has documents” means the current carried document is present.
- The recovery zone is available from the start of a run and is represented with placeholder visuals that can later be replaced without changing the rules.
- Game over applies to the current run; clicking the “Restart” button resets the player and stamina while preserving the game's normal initial setup.
- This feature does not redesign document types, wave sequencing, movement controls, or the future skill-based fishing interaction.
