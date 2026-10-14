# I am from the Government Project Constitution

## Core Principles

### I. Gameplay First

I am from the Government  is a small, satirical, single-player survival game about escalating bureaucracy.

- Every feature MUST support the core gameplay loop: process documents, survive bureaucracy, recover stamina through fishing, and advance to the next paragraph.
- The game MUST prioritize responsive controls, readable game states, and understandable feedback.
- New mechanics MUST introduce a meaningful gameplay decision, challenge, or humorous interaction.
- The player MUST be able to understand why stamina was lost, why a document was accepted or rejected, and why the game ended.
- Gameplay balance MUST favor fun and clarity over realism.
- Features that add complexity without improving the player experience MUST be rejected or simplified.

**Rationale:** The absurdity comes from bureaucracy becoming increasingly difficult, not from confusing or frustrating controls.

### II. Simple, Modular Python Architecture

The project MUST use Python and Pygame-ce for its initial desktop implementation.

- Game logic MUST be separated from rendering, input handling, and audio.
- Core gameplay systems MUST use focused, independently testable modules.
- Game states MUST have explicit transitions and clearly defined responsibilities.
- Dependencies MUST flow from the application layer toward game logic, not the reverse.
- Global mutable state MUST be avoided.
- Circular imports MUST NOT be introduced.
- Third-party dependencies MUST be kept minimal and justified by concrete requirements.
- Premature abstractions, generic frameworks, ECS architectures, and unnecessary design patterns MUST be avoided.
- Source code MUST be readable and use type hints for public interfaces and nontrivial functions.

**Rationale:** The game must remain understandable and maintainable by a small team or solo developer working with AI coding agents.

### III. Deterministic and Testable Game Rules

Gameplay rules MUST be testable independently of the Pygame rendering loop.

- Wave progression, document validation, stamina calculations, and game-over conditions MUST have automated unit tests.
- The same game state and player action MUST produce predictable results, except where randomness is explicitly part of the mechanic.
- Random behavior MUST support seeded random-number generation for reproducible tests.
- Game logic MUST use elapsed simulation time rather than depend on rendering frame rate.
- Stamina MUST remain within defined limits.
- Invalid document handovers MUST NOT corrupt progression.
- Wave completion MUST require fulfillment of the currently specified bureaucratic process.
- Critical gameplay regressions MUST block feature completion.
- Tests MUST use pytest.

**Rationale:** Reliable rules allow frequent balancing and changes without accidentally breaking established mechanics.

### IV. Data-Driven Bureaucratic Escalation

Bureaucratic complexity is the central progression mechanic.

- Each paragraph (§) MUST represent a distinct wave.
- Under the initial progression rules, wave N MUST introduce N bureaucrats.
- Bureaucrats MUST participate in an explicit, verifiable document-processing sequence.
- Document types and bureaucrat requirements MUST be modeled as structured game data rather than scattered conditional statements.
- New document types and processing rules SHOULD be addable without rewriting the main game loop.
- The source and destination of each document MUST remain understandable to the player.
- Additional complexity MUST be introduced progressively.
- Future special bureaucrats MAY introduce exceptions, but MUST preserve a solvable sequence.
- Every generated wave MUST be completable under its defined rules.

**Rationale:** Escalating administrative absurdity is the game's primary source of difficulty and humor.

### V. Stamina and Fishing Form One Survival System

Bureaucracy and fishing MUST be mechanically connected.

- Carrying an official document MUST consume stamina according to defined gameplay rules.
- Stamina consumption MUST be independent of rendering frame rate.
- Successful fishing MUST provide stamina recovery.
- Fishing MUST require player interaction and skill rather than simply waiting.
- Fishing MUST use clear visual feedback and predictable controls.
- Stamina MUST have a defined minimum and maximum.
- Reaching zero stamina MUST trigger game over.
- The recovery and consumption systems MUST be adjustable using centralized balancing parameters.
- Fishing MUST remain meaningfully useful as bureaucratic waves become harder.

**Rationale:** The tension between bureaucratic exhaustion and peaceful fishing creates the game's survival loop.

### VI. Vertical Slices and Continuous Playability

The project MUST remain playable throughout development.

- Development MUST proceed through small, independently testable vertical slices.
- Every completed slice MUST preserve a launchable version of the game.
- Each slice MUST include its required logic, player interaction, feedback, and tests.
- Placeholder graphics and sounds MUST be preferred over blocking gameplay development.
- Each feature MUST define observable acceptance criteria before implementation.
- Existing gameplay MUST NOT be broken to introduce an unrelated feature.
- The main branch MUST remain in a runnable state.
- New dependencies or architectural complexity MUST be justified by an active feature.

**Rationale:** A small playable game provides more value and better feedback than a large collection of unfinished systems.

### VII. Visual Consistency and Satirical Identity

I am from the Government MUST maintain a coherent retro-inspired visual and humorous identity.

- The visual presentation MUST remain readable at the target resolution.
- Interactive objects, bureaucrats, documents, stamina indicators, and fishing targets MUST be visually distinguishable.
- Gameplay feedback MUST not depend on color alone.
- The game SHOULD use a consistent pixel-art aesthetic.
- Bureaucratic humor MUST be expressed through gameplay, dialogue, presentation, and escalating requirements.
- Humor MUST not prevent players from understanding required actions.
- External assets MUST have documented licenses compatible with their intended use.
- Temporary assets MUST be replaceable without modifying core gameplay logic.

**Rationale:** Clear visual communication makes the bureaucratic absurdity entertaining rather than irritating.

## Technical Constraints

- **Language:** Python 3.12 or newer.
- **Framework:** Pygame-ce.
- **Testing:** pytest.
- **Target platform:** Desktop (Windows and Linux initially).
- **Gameplay:** Single-player, offline-first.
- **Architecture:** Modular monolith with separated game logic and presentation.
- **Data:** Python data structures initially; JSON or TOML for configuration when useful.
- **Runtime:** No mandatory server, account, database, or network connection.
- **Performance:** Aim for 60 FPS on ordinary desktop hardware.
- **Dependencies:** Minimal and explicitly documented.

These constraints MAY be amended when a concrete feature demonstrates the need.

## Development Workflow

Every feature MUST follow the Spec Kit development workflow:

1. **Specify:** Define player-facing behavior, user stories, and acceptance criteria.
2. **Clarify:** Resolve ambiguities affecting gameplay or implementation.
3. **Plan:** Define the minimal architecture and implementation approach.
4. **Tasks:** Break implementation into small, verifiable steps.
5. **Implement:** Implement the feature while preserving playability.
6. **Validate:** Run automated tests and manually verify interactive behavior.

Feature specifications MUST describe expected behavior before implementation details.

Plans MUST include a Constitution Check for architecture, gameplay coherence, testing, and complexity.

Changes to core game rules MUST update relevant specifications and tests.

## Quality Gates

A feature is complete only when:

- Its specified acceptance criteria are satisfied.
- Related automated tests pass.
- The existing gameplay loop remains functional.
- Interactive behavior has been manually verified when applicable.
- Frame-rate independence is preserved for time-based mechanics.
- New code follows the defined module boundaries.
- No unjustified dependency or architectural abstraction has been introduced.
- The game remains launchable using documented instructions.

## Governance

This constitution is the authoritative source for project-wide engineering and gameplay principles.

- All feature specifications, implementation plans, and tasks MUST comply with it.
- Conflicts MUST be resolved before implementing the affected feature.
- Amendments MUST include a rationale and an explicit version update.
- Versioning follows semantic versioning:
  - MAJOR: Removal or incompatible redefinition of existing principles.
  - MINOR: Addition of principles or material governance changes.
  - PATCH: Clarifications and editorial improvements.
- Compliance MUST be reviewed during planning and feature completion.
- Exceptions MUST be explicitly documented with their rationale and scope.
- Temporary exceptions MUST include a condition for removal.

**Version:** 1.0.0  
**Ratified:** 2026-10-13  
**Last Amended:** 2026-10-13
