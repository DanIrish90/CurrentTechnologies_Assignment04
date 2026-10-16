# Implementation Plan: Configurable Start Zoom

**Branch**: `010-configurable-zoom` | **Date**: 2026-10-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-configurable-zoom/spec.md`

## Summary

Add a centrally configurable floating-point zoom multiplier for the initial game view. The simulation remains in existing world coordinates; the presentation renders into a zoom-adjusted logical surface and scales that surface to the current window. This keeps camera bounds, collision, interaction ranges, movement, and gameplay state independent from presentation zoom while allowing values such as `1.25`, `1.5`, and `2.0` to be tuned in one configuration location.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pygame-ce; existing project dependencies only

**Storage**: N/A; zoom is a runtime configuration constant

**Testing**: pytest for pure configuration/viewport/camera behavior and headless Pygame rendering smoke coverage

**Target Platform**: Desktop Windows and Linux; offline-first

**Project Type**: Single-player desktop game

**Performance Goals**: Preserve the existing 60 FPS target on ordinary desktop hardware; avoid per-frame asset rescaling where cached or surface-level scaling is sufficient

**Constraints**: Preserve pixel-art readability, window resizing, world-bound camera clamping, and all existing gameplay rules; reject or safely normalize non-finite, non-positive, and out-of-range zoom values

**Scale/Scope**: One startup zoom setting, one game window, one logical presentation surface, existing world/player/NPC/UI/overlay render paths, and focused regression tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gameplay First**: PASS. Zoom is presentation-only and preserves movement, interactions, stamina, fishing, waves, and game-over behavior.
- **Simple, Modular Python Architecture**: PASS. The plan extends centralized configuration and the existing window/renderer boundary without adding a framework, service, or dependency.
- **Deterministic and Testable Game Rules**: PASS. Camera and viewport calculations remain pure and testable; no time-dependent gameplay rule is changed.
- **Vertical Slices and Continuous Playability**: PASS. The feature has a small scope, keeps the game launchable, and includes automated plus manual validation.
- **Visual Consistency and Satirical Identity**: PASS with validation. World, actors, UI, and overlays use one presentation scale and must remain readable at the supported range.
- **Technical constraints**: PASS. Python/Pygame-ce, pytest, desktop, offline-first, and 60 FPS goals are unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/010-configurable-zoom/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md              # created by $speckit-tasks, not this command
```

### Source Code (repository root)

```text
src/
├── game/
│   ├── config.py          # zoom multiplier and allowed bounds
│   ├── camera.py          # world-coordinate camera remains authoritative
│   └── state.py           # logical viewport passed to simulation
└── presentation/
    ├── window.py          # display surface and zoom-adjusted frame loop
    └── renderer.py        # render logical frame and scale to display

tests/
├── smoke/
└── unit/
```

**Structure Decision**: Keep the existing modular Python desktop-game layout. Configuration, simulation, camera, window lifecycle, and renderer retain their current ownership boundaries. No `contracts/` directory is needed because this is an internal desktop feature with no external API or service interface.

## Complexity Tracking

No constitution violations. The feature uses the existing window and renderer path and introduces no new architectural layer.

## Post-Design Constitution Check

- **Gameplay First**: PASS. The data model explicitly keeps zoom out of gameplay state and interaction coordinates.
- **Simple, Modular Python Architecture**: PASS. The design adds only a validated configuration value, viewport derivation, and one presentation scaling boundary.
- **Deterministic and Testable Game Rules**: PASS. Pure viewport and camera invariants are covered without requiring the display loop; existing gameplay tests remain authoritative.
- **Vertical Slices and Continuous Playability**: PASS. Quickstart validation covers launch, resizing, representative zoom values, invalid values, and the complete existing gameplay loop.
- **Visual Consistency and Satirical Identity**: PASS. The complete frame is scaled together, non-smoothed scaling preserves the pixel-art intent, and manual readability checks are specified.
- **Gate result**: PASS; no unresolved technical clarifications or justified complexity exceptions remain.
