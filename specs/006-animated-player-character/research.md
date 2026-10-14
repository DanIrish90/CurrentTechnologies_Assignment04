# Research: Animated Player Character

## Decision: Keep animation state outside authoritative GameState

**Rationale:** `GameState` and its nested gameplay values are frozen dataclasses and are used by deterministic unit tests. Animation frame, elapsed animation time, and last visual direction are presentation concerns and do not affect movement, collision, stamina, bureaucracy, fishing, or restart behavior. A presentation-owned animator preserves the existing separation.

**Alternatives considered:**

- Add animation fields to `Player` or `GameState`: rejected because it couples rendering state to gameplay and would expand every state transition.
- Use module-level global animation state: rejected because it would make renderer tests order-dependent and would violate the project’s avoidance of global mutable state.

## Decision: Derive movement animation from actual player displacement

**Rationale:** Input can be pressed while the player is blocked by an obstacle or world boundary. Comparing the player position before and after the simulation update distinguishes actual movement from requested movement and satisfies the requirement that blocked movement does not animate as successful walking.

**Alternatives considered:**

- Use the current `InputState` directly: rejected because it reports intent, not resolved movement.
- Modify collision or movement rules to emit animation events: rejected because the feature is presentation-only and does not need a gameplay event system.

## Decision: Use a fixed 4 × 3 frame grid from the existing PNG

**Rationale:** The asset is 336 × 384 pixels and the visual layout is exactly twelve 84 × 128 frames. Extracting the frames once at load time gives deterministic row/column selection and avoids per-frame file I/O or repeated cropping.

**Alternatives considered:**

- Load the `.aseprite` source at runtime: rejected because the PNG is already the runtime-ready asset and adding an Aseprite loader is unnecessary.
- Recreate the character from individual files: rejected because the project already provides the complete tileset.

## Decision: Use 8 frames per second with elapsed-time advancement

**Rationale:** A fixed frame duration of 0.125 seconds gives the requested animation speed and remains stable when render frame timing varies. Advancement should use a loop or modulo-safe calculation so large elapsed values cannot leave the frame index outside 0–3.

**Alternatives considered:**

- Advance once per render call: rejected because animation speed would depend on FPS.
- Use a timer tied to wall-clock time: rejected because explicit elapsed time is easier to test and follows the project’s deterministic timing rules.

## Decision: Mirror only the side-facing frames for right movement

**Rationale:** The tileset contains one side-facing row whose original orientation is used for left movement. Right movement uses a horizontally flipped copy. The flip can be cached per source frame after loading so rendering does not repeatedly transform the same image.

**Alternatives considered:**

- Add a second side-facing row: rejected because it is not present in the supplied asset.
- Flip every render call: rejected because caching is simple and avoids unnecessary per-frame work.

## Decision: Preserve native frame size and align by feet

**Rationale:** The supplied frames are pixel art intended to be used at their native dimensions initially. The visual rectangle should use the player collision box’s horizontal center and bottom edge as its anchor, keeping feet grounded while leaving the existing 32 × 32 collision box unchanged.

**Alternatives considered:**

- Resize the logical player box to 84 × 128: rejected because it would change collision, interaction range, and movement behavior.
- Scale the sprite in the first implementation: deferred until visual validation shows native size is unreadable.
