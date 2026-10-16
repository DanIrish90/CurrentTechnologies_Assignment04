# Data Model: Configurable Start Zoom

## Zoom Configuration

The centralized presentation setting controlling the initial view.

| Field | Type | Rules |
|-------|------|-------|
| multiplier | positive floating-point number | Default `2.0`; `1.0` means unchanged; supported range `0.5`–`4.0` inclusive |
| minimum | positive floating-point number | `0.5`; lower values are invalid |
| maximum | positive floating-point number | `4.0`; higher values are invalid |
| reference behavior | fixed semantic rule | Values greater than `1.0` show a smaller world area enlarged to the window; values below `1.0` show more world area |

### Validation rules

1. The multiplier must be numeric and finite.
2. The multiplier must be within the inclusive supported range.
3. The logical render width and height derived from the current window must remain positive.
4. Invalid configuration must be handled before the game enters its main loop, by a safe documented fallback or a clear startup error.

## Logical Viewport

The world-coordinate dimensions visible before the frame is enlarged to the display window.

| Field | Type | Rules |
|-------|------|-------|
| display width | positive integer | Current window width in display pixels |
| display height | positive integer | Current window height in display pixels |
| zoom multiplier | positive floating-point number | Comes from validated Zoom Configuration |
| logical width | positive viewport dimension | Derived from display width divided by zoom; rounded safely to a positive integer |
| logical height | positive viewport dimension | Derived from display height divided by zoom; rounded safely to a positive integer |

The logical viewport is passed to the existing camera/state update path. It is not a second gameplay coordinate system; it only describes the visible world rectangle.

## Camera at Zoom

The existing camera remains authoritative in world coordinates.

- It centers on the player using the logical viewport dimensions.
- It clamps to the world bounds using those dimensions.
- If the logical viewport is larger than the world, it anchors to the world origin on that axis according to current camera behavior.
- It must never expose coordinates outside the world bounds.

## Presentation Frame

The complete renderable output for one frame:

- World layers and map objects.
- Player and civil-servant sprites.
- HUD and status panel.
- Fishing and wave-rest overlays.
- Game-over and restart presentation.

All components are rendered into the same logical frame and enlarged together, preserving relative alignment. No component changes the underlying `GameState` or gameplay coordinates.

## State Transitions

This feature has no new gameplay state transitions. A configuration change occurs before startup; window resizing recalculates the logical viewport while the existing game state continues running.
