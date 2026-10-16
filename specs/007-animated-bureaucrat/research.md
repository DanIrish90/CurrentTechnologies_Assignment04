# Research: Animated Bureaucrats

## Decision: Use the current `CivilServant.served` value as the animation state source

**Rationale:** `served` already represents the authoritative result of the document workflow. Reading it in presentation avoids duplicating workflow rules and guarantees that a newly created or reconstructed wave starts with the correct visual state.

**Alternatives considered:**

- Add animation fields to `CivilServant` or `GameState`: rejected because animation is presentation-only and would couple rendering to immutable gameplay data.
- Infer the state from feedback text: rejected because text is presentation output and is less stable than the structured `served` value.

## Decision: Maintain one animation state per active servant ID

**Rationale:** Multiple servants can be idle or served at the same time and must not share frame counters. Servant IDs are unique within a wave and allow the presentation layer to preserve independent progress across frames.

**Alternatives considered:**

- Use one global Bureaucrat frame counter: rejected because servants would animate in lockstep and state changes could affect unrelated servants.
- Store animation state in each domain entity: rejected because it violates the presentation/game-logic boundary.

## Decision: Reset only the affected servant on a state change

**Rationale:** When `served` changes, the affected servant should visibly begin the corresponding two-frame loop at frame 0. Other servants retain their own frame and elapsed-time progress. If a servant appears already served, initialize it directly in the Permit loop.

**Alternatives considered:**

- Restart every servant whenever any handover succeeds: rejected because it creates misleading visual changes and breaks independent animation.
- Play Permit only once: rejected because the clarified requirement explicitly requires looping while `served=True`.

## Decision: Load a 2 × 2 sheet into reusable native-size frames

**Rationale:** The runtime PNG is 168 × 256 pixels, exactly four 84 × 128 frames. Loading and splitting once avoids per-render work and preserves the pixel-art source dimensions.

**Alternatives considered:**

- Load the Aseprite file at runtime: rejected because the PNG is already the runtime asset and no Aseprite dependency is needed.
- Keep the sheet and crop during each draw: rejected because it adds repeated work and complicates tests.

## Decision: Loop both states at 3 FPS using elapsed time

**Rationale:** Three frames per second lies within the specified 2–4 FPS range and provides a readable two-frame idle/permit motion. Explicit elapsed time makes the result independent of rendering FPS and testable with controlled intervals.

**Alternatives considered:**

- Advance once per render call: rejected because speed would vary with FPS.
- Use wall-clock timers: rejected because explicit simulation/render elapsed time is deterministic and matches the existing architecture.

## Decision: Preserve the existing servant target footprint for anchoring

**Rationale:** The current placeholder bounds are centered on the Civil Servant position and provide the visible target footprint. The 84 × 128 sprite should use the same center-bottom anchor so the visual size changes without moving the interaction target.

**Alternatives considered:**

- Replace the interaction bounds with the sprite rectangle: rejected because the sprite is visual only and would change gameplay behavior.
- Anchor the sprite by its top-left corner: rejected because different frames would not share a stable foot position.
