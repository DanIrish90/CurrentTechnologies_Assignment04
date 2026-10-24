# Data Model: User Interface Overlay Refresh

## UI Snapshot Extensions

The existing immutable UI snapshot gains derived presentation facts rather than owning gameplay state.

| Field | Type | Rules |
|-------|------|-------|
| interaction_available | boolean | True only when an existing interaction-key action is currently meaningful; otherwise false |
| stamina_ratio | number in `[0, 1]` | Current stamina divided by maximum, clamped to the inclusive range |
| stamina_color_state | enum | `green` for `[0.5, 1.0]`, `yellow` for `[0.1, 0.5)`, `red` for `[0, 0.1)` |
| game_over | boolean | Existing authoritative exhaustion state; controls GameOver asset visibility |
| fishing_meter_phase | enum | Derived from `FishingPhase`: bait/default, bite, catching, outcome, or hidden |
| fishing_meter_icon | enum or null | Explicit sprite-sheet icon selection: bait, bite, fish, success, catchbar overlay, or failure |
| fishing_outcome_elapsed | number ≥ 0 | Simulation elapsed time for success/failure feedback; icon is visible through 2.0 seconds |

The existing feedback, fishing, countdown, and restart fields remain available where their gameplay overlays are still needed. Removing the debug panel does not remove those state values from the model unless they become unused after implementation.

## Interaction Availability

`interaction_available` is derived from the current player/world/workflow state:

- Document collection is available when the player is within the existing document-source interaction range and the workflow permits collection.
- A document handover is available when the player overlaps an applicable drop-off zone and the current workflow exposes a meaningful handover action.
- Fishing interaction is available when the player is eligible to cast or when the current fishing phase accepts the interaction key.
- GameOver, blocked workflow phases, carrying restrictions, and unavailable fishing phases suppress the hint unless the existing input logic explicitly accepts the interaction.

No new gameplay transition is introduced by this entity.

## Existing Fishing and Stamina-Recovery Contract

The UI projection MUST consume, but not alter, the existing Fishing state machine and stamina outcome:

| Stage | Existing rule | UI implication |
|-------|---------------|----------------|
| Eligibility | Fishing is available during wave rest in the Fishing Pond, with empty hands and no active GameOver | The interaction hint may show when the existing cast or accepted Fishing input is available |
| Cast and bite | `E` starts the cast, then the game waits for the configured bite delay and opens a time-limited bite window | Existing Fishing feedback remains visible; removing the Fishpond label does not remove this feedback |
| Catching | Pressing `E` within the bite window starts the Catching mini-game; player input keeps the catch bar aligned with the fish | The UI feature must not auto-start, skip, or simplify the Catching phase |
| Outcome | A successful catch returns the existing configured stamina reward; pond occupancy, a missed bite, and an escaped fish return no stamina reward | Stamina recovery is exclusively tied to a successful catch |

This contract is an existing gameplay state transition, not a new UI-owned entity. The UI may expose derived visibility and stamina display data only.

## Stamina Bar Composition

Source asset: `assets/UserInterface/StaminaBar.png`, 320×64 pixels.

| Region | Source rectangle | Purpose |
|--------|------------------|---------|
| frame | `(0, 0, 320, 32)` | Long upper-row border drawn over the fill |
| fill | `(0, 32, 320, 32)` | Lower-row background/fill clipped to stamina ratio and tinted by state |

The fill is anchored to the left edge of the frame. Its visible width is the frame's inner width multiplied by `stamina_ratio`, clamped so it never exceeds the frame or becomes negative. The frame is drawn last to preserve its border. The complete bar is then sized by the positive `UI_STAMINA_BAR_SCALE` value, defaulting to `1.0`, before the logical surface is passed through Feature-010 zoom.

## FishingMeter Composition

Source asset: `assets/UserInterface/FishingMeter.png`, 128×448 pixels. The left 64×448 region is the vertical Fishing Bar. The six 64×64 regions on the right are selected by explicit source rectangle and composed over the bar as follows:

| State | Icon | Placement |
|-------|------|-----------|
| Idle / waiting for bite | first icon, bait | vertically centered inside the left 64×448 bar |
| Bite window | second icon | vertically centered inside the left 64×448 bar; prompts the E action |
| Catching | third icon, fish | positioned at the existing `fish_position` inside the bar; replaces the old fish bar graphic |
| Success feedback | fourth icon | centered over the catchbar overlay for 2 seconds |
| Catchbar | fifth icon/overlay | represents the catchbar layer during catching and outcome composition |
| Failure feedback | sixth icon | centered over the catchbar overlay for 2 seconds |

The complete composition is exactly 128×448 pixels and centered in the visible surface. During idle/waiting and the bite window, the selected bait/bite icon is rendered inside the left bar at its vertical center; the right icon column is only a source region and is not displayed as an active icon column. The composition is not affected by Feature-010 UI zoom or `UI_STAMINA_BAR_SCALE`. Fishing movement and unrelated actions are paused while this composition is active.

## UI Asset Requirements

| Asset | Source size | Presentation rule |
|-------|-------------|-------------------|
| `InteractionButton.png` | 128×128 | Horizontally centered in the lower screen third while `interaction_available` is true |
| `StaminaBar.png` | 320×64 | Upper row frame over lower row fill; positioned top-left with safe margin and sized by the independent positive StaminaBar scale |
| `GameOver.png` | 1024×256 | Centered while `game_over` is true, proportionally contained within the logical surface |
| `FishingMeter.png` | 128×448 | Native-size centered composition with a 64×448 bar, phase-selected 64×64 icons, and existing fish position |

The ordinary HUD assets are rendered on the Feature 010 logical surface and inherit its configured zoom and final window scaling. Only the StaminaBar additionally uses its own config scale. FishingMeter is the explicit exception and is rendered at native size in the visible surface coordinate system.

## Visibility Transitions

1. `interaction_available: false → true`: show the interaction button on the next rendered frame.
2. `interaction_available: true → false`: hide the interaction button on the next rendered frame.
3. `game_over: false → true`: show the centered GameOver asset and prioritize it over normal HUD elements.
4. `game_over: true → false` after restart: hide GameOver and restore the normal StaminaBar/interactions for the fresh session.
