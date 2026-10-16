# Research: Configurable Start Zoom

## Decision 1: Keep gameplay coordinates independent from presentation zoom

**Decision**: Apply zoom only at the presentation boundary. The player, world, collision rectangles, interaction zones, stamina rules, wave progression, and camera calculations continue to use world coordinates. The camera receives a viewport representing the visible world area after zoom.

**Rationale**: This preserves existing gameplay behavior and makes `1.0` a direct compatibility reference. It avoids rewriting map data, spawn positions, collision logic, or interaction distances for every visual tuning change.

**Alternatives considered**:

- Scaling every world object and gameplay rectangle: rejected because it duplicates presentation concerns in simulation code and risks changing collision and interaction behavior.
- Changing map and spawn data for each desired zoom: rejected because authored world coordinates are authoritative and should not depend on display preference.

## Decision 2: Render one logical frame, then scale the complete frame to the window

**Decision**: Derive a positive logical render size from the current window size and zoom multiplier, render world, actors, UI, and overlays to that logical surface, then scale the complete surface to the display surface.

**Rationale**: A single frame-scale boundary keeps UI and overlays aligned with the world and prevents separate zoom math from spreading through every renderer helper. It also supports fractional zoom values without changing asset loading or gameplay state.

**Alternatives considered**:

- Multiply every renderer coordinate and rectangle individually: rejected because it is error-prone for text, overlays, actor anchors, and future draw paths.
- Render at a fixed internal resolution regardless of window size: rejected because the existing application supports resizing and should keep using the available display area.

## Decision 3: Use one centralized floating-point setting with explicit bounds

**Decision**: Store the default zoom as `2.0`, preserve `1.0` as the unchanged reference, support fractional values, and constrain the supported range to `0.5` through `4.0` inclusive. Validate the value before creating the runtime presentation surface.

**Rationale**: A floating-point setting enables fine tuning while bounds prevent zero-sized logical surfaces, unusable extreme views, and accidental invalid arithmetic. The range covers zoom-out and readable zoom-in tuning for the current 960x640 window.

**Alternatives considered**:

- Integer-only zoom levels: rejected because the requested feature explicitly needs fine tweaking.
- Unbounded positive values: rejected because values close to zero or extremely large can make the view unusable and exceed practical surface dimensions.
- Silent clamping of all invalid values: rejected as the only behavior because a non-numeric or non-finite configuration error should be visible; a safe fallback may still be used if graceful startup is preferred.

## Decision 4: Preserve pixel-art intent with non-smoothed frame scaling

**Decision**: Use the existing pixel-oriented rendering style and a non-smoothed final surface scale. Validate fractional zooms visually and with smoke tests for full-frame coverage.

**Rationale**: Smooth filtering can blur the project's pixel-art presentation. A single final scale also avoids repeatedly resampling individual sprites.

**Alternatives considered**:

- Smooth interpolation: rejected as the default because it conflicts with the established pixel-sharp visual direction.
- Per-asset scaling: rejected because actors are already loaded at their presentation size and per-asset zoom would duplicate work.

## Decision 5: Test through pure helpers and headless rendering

**Decision**: Add focused tests for zoom validation and logical viewport derivation, camera invariants at zoom-adjusted viewport sizes, and headless rendering at representative zoom values. Keep existing gameplay tests as regression coverage.

**Rationale**: The critical risk is the boundary between window dimensions and logical world viewport. Pure tests cover arithmetic deterministically, while headless render checks catch empty-surface and overlay integration regressions.

**Alternatives considered**:

- Manual testing only: rejected because invalid values and camera invariants are easy to regress.
- Rewriting all existing gameplay tests around zoom: rejected because zoom must not alter gameplay rules; focused regression coverage is sufficient.
