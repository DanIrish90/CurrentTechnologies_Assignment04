# Data Model: Wave Rest Countdown

## Configuration

| Field | Type | Default | Rules |
|---|---|---:|---|
| `WAVE_REST_DURATION` | `float` | `10.0` | Must be positive; authoritative duration for every wave rest phase. |
| `WORM_TIMER_FPS` | `float` | `8.0` | Must be positive; controls only sprite frame changes per second. |
| `WORM_TIMER_ASSET_PATH` | `str` | `assets/UserInterface/WormTimer.png` | Must point to the 448×32 WormTimer sprite sheet. |
| `WORM_TIMER_FRAME_WIDTH` | `int` | `64` | Seven frames fit exactly across the sheet. |
| `WORM_TIMER_FRAME_HEIGHT` | `int` | `32` | Must match the sheet height. |
| `WORM_TIMER_FRAME_COUNT` | `int` | `7` | Horizontal frame count; must satisfy width × count = sheet width. |

## Existing Workflow State

The feature reuses immutable `WaveProgress`.

| Field | Type | Rules |
|---|---|---|
| `definition.wave_number` | `int` | Identifies the completed wave; remains positive. |
| `phase` | `WorkflowPhase` | `ACTIVE` hides WormTimer; completion/transition phases show it until the next wave exists. |
| `transition_remaining` | `float` | Starts at `WAVE_REST_DURATION`, decreases by elapsed simulation time, and is clamped to `0.0`. |
| `definition` | `WaveDefinition` | Replaced exactly once by the next wave when the timer reaches zero. |

## Derived UI Snapshot

| Field | Type | Rules |
|---|---|---|
| `rest_countdown_visible` | `bool` | True only during the active rest phase; false during active waves, first-wave start, and after transition. |
| `rest_seconds_remaining` | `float` | Clamped to `0.0..WAVE_REST_DURATION`. |
| `rest_elapsed_progress` | `float` | `1 - remaining / duration`, clamped to `0.0..1.0`; drives worm position. |
| `worm_timer_frame_index` | `int` | `floor(rest_elapsed_seconds × WORM_TIMER_FPS) % WORM_TIMER_FRAME_COUNT`; loops while rest is active. |

The existing `rest_wave_number` may remain for compatibility with snapshot consumers, but it is no longer rendered as the center of a semicircle.

## UI Asset Model

`UiAssets.worm_timer_frames` is an immutable tuple of seven alpha-enabled Pygame surfaces, each exactly 64×32 pixels, ordered left to right from `WormTimer.png`.

The renderer scales frames consistently with the current UI presentation and positions the selected frame below the stamina bar. The movement track uses the rendered stamina-bar width; the frame remains fully visible at the track endpoints.

## Invariants and State Transitions

- The first wave starts with no rest phase and no WormTimer.
- `WAVE_REST_DURATION > 0` and `WORM_TIMER_FPS > 0`.
- `transition_remaining` and all normalized progress values never become negative or exceed their upper bounds.
- Worm position is monotonic left-to-right during rest and reaches the right endpoint at progress `1.0`.
- Sprite frame selection never changes wave timing or worm position.
- A zero-time boundary creates at most one next wave.
- Rest expiry cancels active fishing before any reward from the expired attempt can be applied.
- Restart returns to Wave 1 with no visible WormTimer.
