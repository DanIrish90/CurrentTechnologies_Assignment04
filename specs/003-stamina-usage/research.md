# Research: Stamina Usage and Recovery

**Feature**: [003-stamina-usage](./spec.md)
**Date**: 2026-10-13

## Decision 1: Keep stamina rules in a pure game-logic module

- **Decision**: Add a focused `src/game/stamina.py` module for stamina values, elapsed-time updates, recovery-zone membership, and exhaustion transitions.
- **Rationale**: The constitution requires deterministic, independently testable gameplay rules and separates game logic from Pygame rendering. A small immutable state/update API fits the existing `bureaucracy.py`, `movement.py`, and `state.py` structure.
- **Alternatives considered**: Put arithmetic directly in `state.py` (rejected because it mixes orchestration with rules); use a general entity-component system (rejected as unnecessary complexity for one player and one zone).

## Decision 2: Use elapsed simulation time for both drain and recovery

- **Decision**: Apply 5 stamina points per elapsed second while carrying a document, or 10 points per elapsed second while empty-handed inside the recovery zone. Clamp every result to 0–100.
- **Rationale**: This is the clarified balance and preserves behavior across different rendering frame rates. The existing update loop already receives `elapsed_seconds` and rejects negative values.
- **Alternatives considered**: Frame-count-based changes (rejected because they vary with FPS); timed Pygame events (rejected because they make unit tests and deterministic simulation harder).

## Decision 3: Represent recovery as world geometry

- **Decision**: Add one immutable `StaminaRegenZone` to `World`, using the existing `Rect` geometry and player bounds overlap/containment rules.
- **Rationale**: The zone is a world object with a visible location, and geometry can be tested without a display. Keeping it in `World` makes camera movement and rendering consistent with the existing document source and obstacles.
- **Alternatives considered**: A screen-space UI control (rejected because recovery is a world-space gameplay decision); a hard-coded coordinate check in the update loop (rejected because it is less discoverable and harder to extend/test).

## Decision 4: Treat game over as an explicit runtime state

- **Decision**: Add an explicit game-over flag/mode to `GameState`. Once stamina reaches zero, freeze active simulation and expose exhaustion feedback. A clickable “Restart” button creates a fresh initial game state.
- **Rationale**: An explicit state prevents repeated transitions and accidental workflow mutation. Restart is presentation-driven, so click hit testing should produce an input action while the state reset remains in game logic.
- **Alternatives considered**: Reusing `running=False` (rejected because that flag currently means the application should close); allowing active updates after zero (rejected because it violates the terminal-run requirement).

## Decision 5: Preserve non-color feedback

- **Decision**: Show a numeric stamina value and status text such as `STAMINA: 75/100`, `RECOVERING`, `CARRYING: -5/S`, or `GAME OVER: EXHAUSTED`. Label the recovery zone in the world and provide a rectangular “Restart” button.
- **Rationale**: The constitution requires that visual feedback not depend on color alone. Text and labels also make smoke/manual verification unambiguous.
- **Alternatives considered**: A bar with color changes only (rejected because it fails the accessibility/readability requirement); audio-only feedback (rejected because audio is not required and would not cover all players).

## Decision 6: Keep the first slice to one zone and no new dependencies

- **Decision**: Place one recovery zone in the initial world, centralize its geometry/colors/rates in existing configuration, and use Pygame's existing mouse events for the Restart button.
- **Rationale**: This is the smallest vertical slice that supports the clarified requirements and preserves the current dependency set.
- **Alternatives considered**: A menu/UI framework (rejected because it adds a dependency for one button); multiple dynamic zones (deferred until the fishing/survival loop needs them).
