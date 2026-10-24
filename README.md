# I am from the Government

A small satirical, single-player survival game about escalating bureaucracy.

## Development setup

Use Python 3.12 or newer, then install the runtime and test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run the automated checks:

```bash
python -m pytest
```

The runtime loads the authored world from `assets/World/World.tmj` and its tileset from `assets/World/MasterTileset.png`; both assets must be present when launching the game. The map is a 60×34 grid of 32×32 tiles (1920×1088 pixels), and its collision, spawn, pickup, drop-off, fishing, and draw-order data are validated during startup.

Launch the game:

```bash
python main.py
```

The first slice uses the arrow keys or WASD for movement. The window can be resized, the camera follows the player inside the fixed world, and the game exits through the normal window close action.

The startup presentation zoom is controlled by `ZOOM_MULTIPLIER` in `src/game/config.py`. Values from `0.5` through `4.0` are supported, fractional values such as `1.25` are allowed, `1.0` is the reference view, and the default `2.0` shows a closer view. This setting changes presentation only; world coordinates and gameplay rules remain unchanged.

The UserInterface presentation uses `InteractionButton.png` for currently available E-actions, `StaminaBar.png` for the compact top-left stamina display, `GameOver.png` for exhaustion, and `FishingMeter.png` for the modal Fishing mini-game. `FishingMeter.png` is a native 128×448 sheet: a 64×448 vertical bar on the left and six 64×64 state icons on the right for bait, bite, fish, success, catchbar overlay, and failure. The former `FISHING POND`, `DOCUMENTS`, and large debug-HUD overlays are intentionally hidden; the underlying gameplay objects and interactions remain active. Fine-tune the StaminaBar's UI size with the positive `UI_STAMINA_BAR_SCALE` setting in `src/game/config.py` (default `1.0`); it is independent of the global presentation zoom. FishingMeter remains native-sized and centered regardless of the global UI zoom.

The authored Tiled world is loaded from `assets/World/World.tmj`. Tile rotations, diagonal transforms, and horizontal/vertical mirroring authored in Tiled are preserved when the map is rendered in-game.

The complete `assets/Music/I'm Not a Big Fan of.m4a` track is the application's looping soundtrack. Playback starts once when the game launches and remains owned by the application across wave transitions and game-over restarts. The repository also contains a complete OGG runtime fallback derived from that track because some Pygame-ce installations cannot decode Opus audio inside an M4A container; if both formats are unavailable, the game continues silently and logs a concise warning.

Actors use a quarter-scale, pixel-sharp presentation against the 32x32 world grid. The player uses an 8x10 logical collision body and civil servants use a 12x15 visual target while remaining non-solid; map coordinates and interaction zones remain unchanged.

The bureaucracy slice adds an explicit `E` interaction key. Visit the central document source, collect the requested document, and hand it to the indicated Civil Servant. Waves 1–3 use one, two, and three Civil Servants; wave 4 and later waves use exactly four fixed Civil Servant spawn points. Wave N requires N document handovers. Waves 1–4 retain their ordered handover route; from wave 5 onward, additional recipients are selected randomly from the three Civil Servants other than the one most recently served. Wave 2 introduces the permit chain from Civil Servant 1 to Civil Servant 2; completed waves enter a 10-second rest phase before the next wave starts automatically.

When a previously served Civil Servant is selected again as the next recipient from wave 5 onward, its animation returns to idle immediately when the new step is assigned. Developer-only debug text is not displayed beside Civil Servants, and a Civil Servant's workflow status is communicated exclusively through its animation.

The stamina slice starts each run at `100/100`. Carrying a document consumes 5 stamina per second. The `FISHING POND` replaces passive regeneration: cast with `E`, wait 2 seconds for a bite, press `E` within 1 second, and complete the catch game to restore 25 stamina. During fishing, the centered FishingMeter is modal, movement and unrelated actions are paused, and success or failure feedback remains visible for 2 seconds. Reaching zero shows an exhaustion game-over screen; click `Restart` to begin a fresh wave-one run.

Fishing uses a vertical fish/catch bar. Press `E` to apply an upward impulse; the bar keeps its velocity during the 0.15-second grace period, then gravity accelerates it downward. Position and speed stay bounded, and repeated presses alter the bar's momentum. Keep the fish inside the catch bar to fill fishing progress. If progress reaches zero the fish escapes; at 100 the catch succeeds.

During the rest phase, a bottom-centered semicircular countdown shows the completed wave number and remaining seconds; its arc opens downward so the bow faces upward. Fishing is available exclusively during this rest phase and is blocked during active-wave document work.
