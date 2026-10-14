# Feature Specification: Fishing Mini-Game

**Feature Branch**: `004-fishing-mini-game`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "The Stamina Regen Zone gets renamed to Fishing Pond. The player now regens Stamina through fishing. Fishing consists of Casting a fishing rod through button press. If a fish bites, another button press must follow in time (under 1 second) to start the catch game. A Bar appears and a small symbol moves up and down representing a fish. Inside the bar is another bar, the catch bar. Through repeated button presses the Catch bar moves up. If no button is pressed the catch bar moves down. If the represented fish symbol is within the catch bar another bar representing the fishing progress is filled up, if not, it is drained. When the fishing progress is full the player has catched the fish and Stamina is restored a certain amount."

## Clarifications

### Session 2026-10-13

- Q: Soll die bestehende Taste `E` für Casting, Bissreaktion und Catch-Bar-Steuerung wiederverwendet werden? → A: `E` für alle Angelaktionen verwenden.
- Q: Soll der Fischbiss nach einer festen Wartezeit oder zufällig auftreten? → A: Fisch beißt nach festen 2 Sekunden.
- Q: Soll der Spieler während des Angelns an der Stelle bleiben und die Bewegung pausieren? → A: Bewegung während des gesamten Angelns pausieren.
- Q: Wie viel Stamina soll ein erfolgreicher Fang wiederherstellen? → A: 25 Stamina-Punkte, begrenzt auf das Maximum.

### Session 2026-10-13 - Catch-Bar-Fallverhalten

- Q: Wie soll die Catch-Bar nach einem Tastendruck fallen? → A: Ursprünglich wurde eine quadratisch zunehmende Distanz mit 0,15-Sekunden-Grace-Period festgelegt; diese Fallformel wurde durch das nachfolgende geschwindigkeitsbasierte Bewegungsmodell ersetzt, die Grace-Period bleibt bestehen.

### Session 2026-10-13 - Catch-Bar-Bewegungsmodell

- Q: Wie soll die Catch-Bar ihre flüssige Auf- und Abbewegung steuern? → A: Die Catch-Bar besitzt eine vertikale Geschwindigkeit; die Schwerkraft erhöht ihre Fallgeschwindigkeit kontinuierlich, jeder Tastendruck erzeugt einen Aufwärtsimpuls, die Grace-Period bleibt erhalten und Position sowie Geschwindigkeit bleiben begrenzt.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cast and react to a fish bite (Priority: P1)

As the player, I want to cast a rod at the Fishing Pond and react quickly when a fish bites, so that fishing becomes an active way to recover from bureaucratic exhaustion.

**Why this priority**: Casting and responding to the bite are the entry point for the entire recovery loop.

**Independent Test**: Stand empty-handed in the Fishing Pond, cast with the interaction button, wait for a bite, and press the button within one second to enter the catch game.

**Acceptance Scenarios**:

1. **Given** the player is inside the Fishing Pond and carries no document, **When** the player presses the interaction button, **Then** a cast begins and the game shows that the player is waiting for a bite.
2. **Given** a cast is waiting for a bite, **When** a fish bites, **Then** the game clearly shows a bite prompt and starts a one-second reaction window.
3. **Given** the bite prompt is active, **When** the player presses the interaction button within one second, **Then** the catch game begins and the catch bar and fish symbol become visible.
4. **Given** the player is outside the Fishing Pond, carries a document, or is in game over, **When** the player presses the interaction button, **Then** no fishing cast begins and the existing gameplay feedback explains why.
5. **Given** a bite prompt is active, **When** the player does not press the interaction button within one second, **Then** the bite is missed, the cast ends, and the player may cast again after the normal reset feedback.

### User Story 2 - Play the catch game (Priority: P1)

As the player, I want to control the catch bar against the moving fish symbol, so that catching a fish depends on timing and repeated input rather than waiting.

**Why this priority**: The catch game supplies the skill-based challenge required for fishing to be meaningful and fun.

**Independent Test**: Start a catch game, press repeatedly while the fish is inside the catch bar, and verify that progress rises; stop pressing or mistime the bar and verify that progress falls.

**Acceptance Scenarios**:

1. **Given** the catch game is active, **When** the player presses the interaction button, **Then** the catch bar moves upward by a predictable step and remains within its limits.
2. **Given** the catch game is active, **When** no interaction button is pressed during an update, **Then** the catch bar retains its current velocity during the 0.15-second grace period and subsequently accelerates downward under gravity while remaining within its position and speed limits.
3. **Given** the fish symbol is within the catch bar during an update, **When** simulation time passes, **Then** fishing progress increases.
4. **Given** the fish symbol is outside the catch bar during an update, **When** simulation time passes, **Then** fishing progress decreases.
5. **Given** the player leaves the Fishing Pond or the active run reaches game over, **When** the catch game updates, **Then** the catch game ends without awarding a fish or stamina.
6. **Given** fishing progress reaches zero before the fish is caught, **When** the catch game updates, **Then** the fish escapes, the catch game ends, and stamina is not restored.

### User Story 3 - Catch a fish and recover stamina (Priority: P1)

As the player, I want a successful catch to restore stamina, so that skilled fishing lets me return to document processing.

**Why this priority**: The reward connects the mini-game to the existing survival loop and makes the Fishing Pond strategically useful.

**Independent Test**: Complete the catch game by keeping the fish in the catch bar until progress is full, then verify the fish result, restored stamina, and return to normal play.

**Acceptance Scenarios**:

1. **Given** the catch game is active, **When** fishing progress becomes full, **Then** the player catches one fish, receives clear success feedback, and the catch game ends.
2. **Given** a fish has been caught, **When** the reward is applied, **Then** stamina increases by the fishing reward amount without exceeding its maximum.
3. **Given** the player has full stamina, **When** a fish is caught, **Then** the catch still succeeds and stamina remains at its maximum.
4. **Given** a fish is caught, **When** the player starts another cast, **Then** the new cast is a separate attempt and does not reuse the previous catch progress.
5. **Given** the player successfully catches a fish, **When** the player resumes movement and document processing, **Then** existing waves, handovers, and document-carrying drain continue to work.

### Edge Cases

- The bite reaction window is strictly less than one second; a press at or after the one-second boundary misses the bite.
- Extra interaction presses while waiting for a bite do not skip the bite window or start multiple catch games.
- The catch bar and fishing progress must remain within their minimum and maximum values even when an update crosses a boundary.
- The catch bar must preserve the existing grace period after a press; after the grace period, gravity changes its vertical velocity continuously rather than directly setting its position.
- A press at the same time as a fish-symbol boundary is handled consistently; being on the boundary counts as inside the catch bar.
- A caught fish cannot award stamina more than once, even if additional input arrives during success feedback.
- Stamina restoration is clamped at maximum and cannot undo game over in the current run.
- Casting, bite prompts, and catch games do not replace or corrupt a document currently held by the player.
- Fishing state is reset after a missed bite, escaped fish, successful catch, leaving the pond, or restarting after game over.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The world MUST rename the existing stamina recovery area to “Fishing Pond” in player-facing labels and feedback.
- **FR-002**: The Fishing Pond MUST be a clearly marked world area distinguishable from document sources, civil servants, and obstacles without relying on color alone.
- **FR-003**: The player MUST be able to start a fishing cast by pressing `E` while inside the Fishing Pond, carrying no document, and in an active run.
- **FR-004**: A cast MUST enter a visible waiting-for-bite state and MUST NOT immediately award stamina or a fish.
- **FR-005**: When a cast produces a fish bite, the game MUST display a bite prompt and allow less than one second for the player to press the interaction button.
- **FR-006**: A valid press during the bite window MUST transition exactly once into the catch game; a late or absent press MUST end the attempt without entering the catch game.
- **FR-007**: The catch game MUST display a bounded vertical play bar, a moving fish symbol, a catch bar, and a fishing-progress bar with readable labels or status text.
- **FR-008**: During the catch game, the catch bar MUST maintain a bounded vertical velocity. Each interaction-button press MUST apply a predictable upward impulse and start or reset a 0.15-second grace period. After the grace period, gravity MUST continuously increase the downward velocity; position and velocity MUST remain within their defined limits.
- **FR-009**: The fish symbol MUST move up and down within the catch-game area according to predictable simulation time.
- **FR-010**: When the fish symbol is within or on the catch bar, fishing progress MUST increase over elapsed time.
- **FR-011**: When the fish symbol is outside the catch bar, fishing progress MUST decrease over elapsed time.
- **FR-012**: Catch-bar position and fishing progress MUST be clamped to their defined minimum and maximum values.
- **FR-013**: When fishing progress reaches its maximum, the game MUST award exactly one caught fish, end the catch game, and provide success feedback.
- **FR-014**: A successful catch MUST restore 25 stamina points, clamped to the player's stamina maximum.
- **FR-015**: The player MUST NOT receive stamina for a missed bite, escaped fish, canceled cast, or failed catch game.
- **FR-016**: Fishing MUST pause player movement during casting, the bite window, and the catch game; fishing MUST be canceled when the player enters game over or begins a conflicting document interaction, and canceled fishing MUST not award stamina.
- **FR-017**: Fishing MUST use elapsed simulation time for bite windows, fish movement, catch-bar velocity, gravity, impulses, grace periods, progress changes, and stamina restoration behavior; outcomes MUST be independent of rendering frame rate.
- **FR-018**: Fishing state MUST reset cleanly after each attempt and MUST preserve existing movement, document handovers, wave progression, stamina drain, game-over behavior, and Restart behavior.
- **FR-019**: The game MUST provide understandable feedback for casting, waiting for a bite, a bite prompt, a missed bite, active catching, an escaped fish, and a successful catch.

### Key Entities

- **Fishing Pond**: The world area where an empty-handed player may cast and fish; formerly the stamina recovery zone.
- **Fishing Attempt**: The lifecycle of one cast, including waiting for a bite, bite reaction, catch game, success, miss, escape, and cancellation.
- **Fish Bite Window**: The short reaction period after a bite during which the player must press the interaction button in under one second.
- **Fish Symbol**: The moving target in the catch game that determines whether progress is gained or lost.
- **Catch Bar**: The player-controlled bounded region with a vertical position and velocity; button presses apply upward impulses, while gravity accelerates it downward after the grace period.
- **Fishing Progress**: The bounded success meter that rises while the fish is inside the catch bar and falls while it is outside.
- **Caught Fish Reward**: The single successful result of a fishing attempt, restoring a defined stamina amount and resetting the attempt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 20 attempts inside the Fishing Pond, every valid cast enters a visible waiting-for-bite state without changing stamina.
- **SC-002**: In 20 bite reactions, a press made before one second enters the catch game, while a press made at or after one second never enters it.
- **SC-003**: In 20 catch-game tests, repeated valid presses apply upward impulses, the catch bar responds smoothly with bounded velocity, and gravity produces progressively faster downward movement after the 0.15-second grace period without exceeding position or speed limits.
- **SC-004**: In 20 controlled fish-position tests, progress increases whenever the fish is inside/on the catch bar and decreases whenever it is outside.
- **SC-005**: In 20 successful catches, exactly one fish is awarded and stamina increases by the defined reward without exceeding maximum; in 20 failed attempts, stamina never increases.
- **SC-006**: At least 90% of playtesters can identify how to cast, when to react to a bite, how to control the catch bar, and why a catch succeeded or failed without external explanation.
- **SC-007**: Existing movement, document workflow, stamina drain, game-over, and Restart tests remain passing after fishing is enabled.

## Assumptions

- The existing interaction button `E` is reused for casting, responding to a bite, and pressing the catch bar; movement controls remain unchanged.
- The bite occurs after a fixed waiting period of 2 seconds in the first playable slice, making automated tests deterministic; later waves may vary this timing.
- The initial catch game uses a fishing-progress range of 0–100, a catch-bar range matching the play bar, and a successful-catch stamina reward of 25 points; these are centralized balancing values.
- The catch bar uses centralized balance values for upward impulse, downward gravity, maximum speed, and the existing 0.15-second grace period. Each press changes velocity rather than directly teleporting the bar. Fishing progress changes at 25 units per second while aligned and 35 units per second while misaligned. These values may be tuned during balancing.
- The fish symbol follows a deterministic vertical oscillation and remains inside the catch-game area; randomness is not required for the first slice.
- The player must be empty-handed to fish, because carrying a document remains the active stamina-drain condition.
- Leaving the Fishing Pond cancels the current fishing attempt; the player can return and cast again.
- Player movement is paused during the complete fishing attempt, so leaving the Fishing Pond can only cancel an attempt through an external state transition such as game over or future forced movement.
- Fishing rewards stamina but does not itself create a new document, advance a wave, or change civil-servant workflow.
- Fishing visuals use replaceable placeholder shapes and text consistent with the existing retro-inspired presentation.
