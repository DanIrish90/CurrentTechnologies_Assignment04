# Implementation Plan: User Interface Overlay Refresh

**Branch**: `011-user-interface` | **Date**: 2026-10-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-user-interface/spec.md`

## Summary

Replace the current debug-style HUD and world-object labels with the existing UserInterface art. The simulation will expose only the UI state needed for presentation: whether an interaction is currently actionable, the normalized stamina ratio, and whether GameOver is active. A focused presentation layer will load and validate `InteractionButton.png`, `StaminaBar.png`, and `GameOver.png`, compose the stamina frame/fill, apply a separately configurable StaminaBar scale, draw the interaction hint in the lower third, and center the GameOver banner. The Fishing mini-game remains unchanged; stamina recovery is exclusively awarded after a successful catch, while passive recovery from merely standing in the pond is removed.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce; existing project dependencies only

**Storage**: N/A; UI assets are existing local PNG files and UI state is derived at runtime

**Testing**: pytest for pure UI-state/color/geometry behavior and headless Pygame rendering tests for asset composition and layout

**Target Platform**: Desktop Windows and Linux; offline-first

**Project Type**: Single-player desktop game

**Performance Goals**: Preserve the existing 60 FPS target; load and split UI assets once rather than repeatedly loading files in the frame loop; apply the StaminaBar scale through layout calculations without per-frame asset reloads

**Constraints**: Keep gameplay state and world coordinates unchanged; preserve pixel-art readability, the Feature 010 zoom surface, window resizing, fishing overlays that are still gameplay-required, the existing restart interaction, and the exact Fishing mini-game sequence and successful-catch stamina reward. Remove pond-only stamina recovery, and expose a positive StaminaBar scale with default `1.0` that affects only the StaminaBar in addition to Feature-010 zoom.

**Scale/Scope**: One HUD replacement, one contextual interaction hint, one independently scalable stamina indicator, one GameOver banner, three existing PNG assets, the Fishing/stamina regression adjustment, and focused render/state regressions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gameplay First**: PASS. The feature improves action clarity and stamina/GameOver feedback while preserving Fishing as the only successful stamina-recovery mechanic; pond proximity alone is not a recovery action.
- **Simple, Modular Python Architecture**: PASS. Asset loading/composition remains in presentation modules; `GameState` gains only derived UI snapshot data.
- **Deterministic and Testable Game Rules**: PASS. Action visibility, recovery eligibility, stamina thresholds, and the positive presentation scale are deterministic; the Fishing mini-game remains time-based and frame-rate independent while only successful catches award recovery.
- **Vertical Slices and Continuous Playability**: PASS. The feature is split into independently testable interaction, stamina, and GameOver presentation slices.
- **Visual Consistency and Satirical Identity**: PASS. Existing pixel-art assets replace debug text, world labels are removed, and all UI is rendered through the Feature 010 zoom surface.
- **Technical constraints**: PASS. Python/Pygame-ce, pytest, desktop, offline-first, and minimal dependencies remain unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/011-user-interface/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md              # created by $speckit-tasks, not this command
```

### Source Code (repository root)

```text
assets/UserInterface/
├── InteractionButton.png
├── StaminaBar.png
└── GameOver.png

src/game/
└── state.py              # derived interaction visibility and UI snapshot data

src/presentation/
├── ui_assets.py          # validated loading and sprite-region composition
└── renderer.py           # asset-based HUD, contextual hint, and GameOver layout

tests/
├── smoke/
└── unit/
```

**Structure Decision**: Keep the existing modular desktop-game layout. The state layer computes presentation facts from authoritative gameplay state; the presentation layer owns asset loading, sprite slicing, colors, positioning, and rendering. No external contract or new dependency is required.

## Complexity Tracking

No constitution violations. Existing rendering and state boundaries are sufficient; a small UI asset helper avoids duplicating image-loading and sprite-region logic in the renderer.

## Post-Design Constitution Check

- **Gameplay First**: PASS. The interaction hint is driven by existing actionable states, stamina/GameOver feedback becomes clearer, and recovery remains tied to successful Fishing skill rather than pond occupancy.
- **Simple, Modular Python Architecture**: PASS. The design adds one focused asset helper and extends the existing immutable UI snapshot rather than introducing a UI framework.
- **Deterministic and Testable Game Rules**: PASS. Thresholds, action visibility, layout/scale calculations, pond non-recovery, and successful-fishing reward have deterministic coverage; headless tests cover actual asset rendering.
- **Vertical Slices and Continuous Playability**: PASS. Quickstart scenarios cover normal play, fishing, rest, exhaustion, restart, and resize.
- **Visual Consistency and Satirical Identity**: PASS. The source art is reused, the debug panel and world labels are removed, and the zoom pipeline remains the single presentation scale boundary.
- **Gate result**: PASS; no unresolved technical clarifications or complexity exceptions remain.
