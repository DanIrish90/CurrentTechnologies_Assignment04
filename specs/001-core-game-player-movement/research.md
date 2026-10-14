# Research: Core Game Window and Player Movement

**Feature**: `001-core-game-player-movement`
**Date**: 2026-10-13

This feature has no unresolved technical unknowns after applying the project constitution and the existing repository state. The repository currently contains only a starter `main.py`, so decisions favor a small, explicit architecture that can grow through vertical slices.

## Decision 1: Use elapsed-time movement updates

**Decision**: Compute movement from the current input direction, a configured speed, and elapsed simulation time. Normalize diagonal input before applying speed.

**Rationale**: The constitution requires frame-rate independence. Normalization prevents diagonal movement from being faster than cardinal movement. A pure update function is straightforward to unit test with fixed time steps.

**Alternatives considered**:

- Fixed pixels per rendered frame: rejected because speed changes with frame rate.
- A full physics engine: rejected because this slice needs only deterministic kinematic movement and a few static obstacles.

## Decision 2: Use axis-aligned rectangles for initial collision

**Decision**: Store the player's collision bounds and each obstacle's occupied bounds as simple axis-aligned rectangles. Resolve the horizontal and vertical portions of a requested movement independently, retaining movement on an unblocked axis.

**Rationale**: Rectangular top-down obstacles are sufficient for the initial placeholder world, deterministic, easy to visualize, and support the required sliding behavior. The approach avoids premature geometry abstractions.

**Alternatives considered**:

- Pixel-perfect masks: rejected as unnecessary for placeholder geometry and harder to test as authoritative rules.
- A tilemap collision system: deferred until the world needs many repeated tiles; static rectangles are clearer for this first slice.

## Decision 3: Keep the camera as a pure bounded transform

**Decision**: Calculate a camera rectangle from the player's center and visible viewport, then clamp it to the playable world rectangle. At world edges, the camera stops instead of revealing invalid space.

**Rationale**: This directly satisfies the camera acceptance scenarios and allows camera tests to run without a display. The camera has no independent mutable behavior beyond its current computed position.

**Alternatives considered**:

- Screen-space player movement: rejected because it makes world collision and later world interactions harder to reason about.
- A cinematic smoothing system: deferred; it adds latency and tuning before the basic camera behavior is validated.

## Decision 4: Isolate Pygame-ce at the application boundary

**Decision**: Pygame-ce owns the window, event polling, clock, fonts, and drawing. It converts events into a small input-state value and consumes render snapshots from the game logic.

**Rationale**: The constitution requires game logic to be independently testable and dependencies to flow toward the application layer. This also makes headless unit tests possible and keeps later UI or asset changes from changing collision rules.

**Alternatives considered**:

- Put all logic in `main.py`: rejected because it conflicts with the required module boundaries and would make rule tests depend on the window loop.
- Add an ECS or scene framework: rejected as unjustified complexity for one player and a handful of static objects.

## Decision 5: Use placeholder visuals and a small state UI

**Decision**: Draw simple, clearly distinct shapes and labels for the player, obstacles, world, game title/context, and a placeholder player-state indicator.

**Rationale**: The constitution favors a playable vertical slice and replaceable temporary assets. Shape, text, and position preserve readability without requiring final art or external assets.

**Alternatives considered**:

- Block implementation until final pixel art exists: rejected because it delays gameplay validation.
- Add an asset pipeline now: deferred until the feature needs authored assets.

## Dependency and integration findings

- Pygame-ce is required by the project constitution and is limited to presentation and input/window concerns for this feature.
- pytest is required by the constitution and will cover movement, collision, camera, and input translation.
- No storage, network, account, audio, or external API integration is needed.
- No contracts artifact is created because this is an internal desktop application feature rather than a service or public library.
