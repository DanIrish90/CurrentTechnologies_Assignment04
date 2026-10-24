# Research: User Interface Overlay Refresh

## Decision 1: Derive interaction-button visibility from existing actionable states

**Decision**: Add a derived `interaction_available` value to the UI snapshot. It is true when the current player position and workflow/fishing phase make an existing interaction-key action meaningful, and false otherwise. It does not add a new interaction system or change input handling.

**Rationale**: The button must track the same rules as the `E` action to avoid showing misleading prompts. Reusing the existing state predicates keeps the hint deterministic and prevents presentation from duplicating gameplay ranges.

**Alternatives considered**:

- Show the button whenever the player is near any interactive object: rejected because blocked workflow states and unavailable fishing phases would produce misleading prompts.
- Add a separate prompt state to the input loop: rejected because action availability is derived from game state and does not need mutable presentation state.

## Decision 2: Keep world objects but remove their debug-style overlays

**Decision**: Stop drawing the colored pond/document rectangles, labels, and debug HUD panel while leaving the map, world geometry, interaction zones, fishing eligibility, and document workflow unchanged.

**Rationale**: The request targets visual clutter, not gameplay affordances. World art and existing zones remain authoritative; removing only the renderer overlays satisfies the change without risking gameplay regressions.

**Alternatives considered**:

- Remove pond/document data from the world: rejected because fishing and document interactions depend on that data.
- Replace the labels with new world labels: rejected because the requested UI direction removes those overlays entirely.

## Decision 3: Load and split the supplied UI assets once

**Decision**: Treat the supplied PNGs as source assets loaded at presentation initialization. Validate their expected dimensions, split `StaminaBar.png` into two 320×32 regions, and keep reusable surfaces in a small UI asset helper.

**Rationale**: This preserves pixel-art edges, gives deterministic asset errors, and avoids image loading or slicing work in every frame.

**Alternatives considered**:

- Recreate the assets with rectangles and fonts: rejected because it loses the supplied visual identity.
- Load files inside every render call: rejected because it is slower and makes missing-asset behavior harder to diagnose.

## Decision 4: Compose stamina fill beneath the frame with explicit thresholds

**Decision**: Draw the lower StaminaBar sprite as the fill/background region, clip its width to the current ratio, tint it green for ratios from 50% through 100%, yellow for ratios from 10% through below 50%, and red below 10%. Draw the upper 320×32 sprite over it as the frame.

**Rationale**: This follows the supplied two-row asset and the exact threshold semantics in the feature spec. Clipping the fill to the frame prevents overflow while preserving the asset's border.

**Alternatives considered**:

- Keep the existing text and rectangle stamina HUD: rejected because it is the debug presentation being replaced.
- Use only a color-changing full bar: rejected because the requested bar must visibly shorten with current stamina.

## Decision 5: Keep all new UI inside the existing logical render surface

**Decision**: Draw the interaction button, StaminaBar, and GameOver image on the same logical surface already used by Feature 010, then let the existing final surface scaling handle window zoom and resize.

**Rationale**: One presentation coordinate system keeps UI aligned and ensures the new assets follow the configured zoom without separate display/world conversion rules.

**Alternatives considered**:

- Draw UI directly on the physical display after world scaling: rejected because it would make UI size and alignment inconsistent with the configured zoom.
- Add a second UI scaling system: rejected because it duplicates the established zoom boundary.

## Decision 6: Fit GameOver art proportionally and preserve restart controls

**Decision**: Center `GameOver.png` in the logical surface, scale it down proportionally when needed to fit a safe margin, and retain the existing restart button/control behavior below or alongside the banner as space permits.

**Rationale**: The supplied asset is wider than the default logical viewport at zoom 2, so a contain-style fit prevents clipping while preserving its artwork. Restart remains a gameplay requirement and must not be removed by the visual replacement.

**Alternatives considered**:

- Draw the 1024-pixel source at unbounded native size: rejected because it would be cropped at common zoom/window combinations.
- Replace the restart control with a new interaction: rejected because the feature changes presentation, not the established restart behavior.

## Decision 7: Preserve the Fishing mini-game as the stamina-recovery contract

**Decision**: Treat the existing Fishing mini-game and its stamina recovery as an immutable gameplay contract for this UI feature. Fishing remains available during the wave-rest phase when the player is in the Fishing Pond with empty hands; the player casts, waits for the bite, reacts within the bite window, completes the Catching mini-game, and receives the existing configured stamina reward only after a successful catch. The feature removes only the Fishpond debug overlay and retains all gameplay-required Fishing feedback.

**Rationale**: The project constitution defines Fishing and stamina as one survival system, and the clarification explicitly requires the existing recovery method to remain. Making the sequence explicit prevents the visual cleanup from accidentally replacing interaction-based recovery with passive regeneration, automatic success, or altered reward logic.

**Alternatives considered**:

- Remove all Fishing overlays with the Fishpond label: rejected because the bite and Catching feedback are required for the existing skill-based mini-game.
- Recover stamina merely by standing in the pond: rejected because it changes the established recovery method and removes the Fishing challenge.
- Reuse the new interaction hint as the only Fishing feedback: rejected because it cannot replace the existing bite-window and Catching feedback.

## Decision 8: Award stamina only for a successful catch

**Decision**: Keep the Fishing Pond as the eligibility area and preserve the complete cast, bite-window, and Catching mini-game, but remove stamina recovery caused solely by entering or remaining in the pond. A missed bite and an escaped fish return no stamina; only the existing successful-catch reward is applied.

**Rationale**: The clarification makes successful Fishing skill the sole stamina-recovery event. This preserves the survival decision and prevents passive pond occupancy from bypassing the mini-game.

**Alternatives considered**:

- Keep pond occupancy regeneration alongside the catch reward: rejected because it violates the clarified exclusive recovery rule.
- Grant a partial reward for a missed bite or escaped fish: rejected because recovery must require a successful catch.

## Decision 9: Add an independent StaminaBar presentation scale

**Decision**: Add a positive `UI_STAMINA_BAR_SCALE` configuration value with default `1.0`. Apply it only to the StaminaBar's logical-surface dimensions, in addition to the existing Feature-010 display zoom; do not scale the InteractionButton, GameOver, world, gameplay values, or other UI.

**Rationale**: A dedicated scale allows manual visual fine-tuning without coupling the bar to global zoom or changing gameplay coordinates. Keeping the scale in centralized config makes adjustments data-driven and testable.

**Alternatives considered**:

- Reuse the global zoom multiplier: rejected because it also changes unrelated UI and world presentation.
- Scale the source PNG or alter the asset: rejected because the source art should remain replaceable and pixel-accurate.
- Store the scale in mutable game state: rejected because this is a presentation configuration, not gameplay state.

## Decision 10: Treat FishingMeter.png as a vertical bar plus six icon regions

**Decision**: Validate `FishingMeter.png` as a 128×448 sheet. Use the left 64×448 region as the vertical Fishing Bar and select the six 64×64 regions on the right by explicit state index: bait/default, bite, catching fish, success, catchbar overlay, and failure.

**Rationale**: Explicit source rectangles preserve the supplied art layout and prevent image-order assumptions from spreading through the renderer. The bar and icons can be composed deterministically at native size.

**Alternatives considered**:

- Recreate the meter with primitive rectangles and text: rejected because it discards the supplied visual asset.
- Scale or crop the whole sheet as one image: rejected because the right-side icons must be independently selected and overlaid.

## Decision 11: Keep FishingMeter native-size and centered

**Decision**: Render the FishingMeter composition at exactly 128×448 pixels, centered in the visible surface, without Feature-010 UI zoom or the StaminaBar scale. The world remains visible behind it, while movement and unrelated actions are paused during active fishing.

**Rationale**: The clarified requirement makes the FishingMeter a fixed-size gameplay instrument rather than ordinary HUD decoration. A modal overlay gives the E input and changing icon states a stable target.

**Alternatives considered**:

- Apply global UI zoom: rejected because the requirement explicitly preserves native dimensions.
- Render a full-screen fishing view: rejected because the world should remain visible behind the centered mini-game.
- Leave movement active: rejected because unrelated movement would make the modal interaction ambiguous.

## Decision 12: Derive icon selection from FishingPhase and outcome feedback

**Decision**: Use the existing FishingPhase as the authoritative state: idle/waiting uses the bait icon, BITE_WINDOW uses the bite icon, CATCHING uses the fish icon at the current fish position, and outcome feedback selects success or failure for exactly two elapsed seconds. The catchbar overlay remains visible as the fifth asset state during catching/outcome composition.

**Rationale**: This preserves the existing deterministic fishing state machine while replacing only the placeholder renderer. The fish icon follows the existing `fish_position`; no parallel animation or gameplay state is introduced.

**Alternatives considered**:

- Add a second UI-owned fishing state machine: rejected because it can drift from gameplay outcomes.
- Infer state from rendered text: rejected because text is presentation and not authoritative.

## Decision 13: Keep outcome timing simulation-driven

**Decision**: Store or derive outcome feedback elapsed time from the simulation clock and hide the success/failure icon after exactly two seconds, with no blocking sleep or frame-count timing.

**Rationale**: Simulation-time timing is frame-rate independent and can be tested with deterministic elapsed-time steps.

**Alternatives considered**:

- Use a render-frame counter: rejected because display frame rate changes visible duration.
- Block rendering for two seconds: rejected because it freezes the game loop and violates responsive input behavior.

## Decision 14: Center bait and bite icons inside the Fishing Bar

**Decision**: During waiting-for-bite and the bite window, render the selected bait or bite icon at the vertical center of the left 64×448 Fishing Bar. The right-side icon column remains a source region only and is not shown as an active display column.

**Rationale**: The manual test confirmed that placing these states beside the bar is visually misleading. Centering them in the bar gives the player one stable focal area for the fishing interaction while retaining the supplied sprite sheet.

**Alternatives considered**:

- Keep bait and bite icons in the right column: rejected because the active state reads as detached from the Fishing Bar.
- Add a separate text prompt: rejected because it duplicates the supplied visual feedback and weakens pixel-art consistency.
