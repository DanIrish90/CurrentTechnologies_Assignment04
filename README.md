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

Launch the game:

```bash
python main.py
```

The first slice uses the arrow keys or WASD for movement. The window can be resized, the camera follows the player inside the fixed world, and the game exits through the normal window close action.

The bureaucracy slice adds an explicit `E` interaction key. Visit the central document source, collect the requested document, and hand it to the indicated Civil Servant. Wave 2 introduces the permit chain from Civil Servant 1 to Civil Servant 2; completed waves enter a 10-second rest phase before the next wave starts automatically.

The stamina slice starts each run at `100/100`. Carrying a document consumes 5 stamina per second. The `FISHING POND` replaces passive regeneration: cast with `E`, wait 2 seconds for a bite, press `E` within 1 second, and complete the catch game to restore 25 stamina. During fishing, movement is paused. Reaching zero shows an exhaustion game-over screen; click `Restart` to begin a fresh wave-one run.

Fishing uses a vertical fish/catch bar. Press `E` to apply an upward impulse; the bar keeps its velocity during the 0.15-second grace period, then gravity accelerates it downward. Position and speed stay bounded, and repeated presses alter the bar's momentum. Keep the fish inside the catch bar to fill fishing progress. If progress reaches zero the fish escapes; at 100 the catch succeeds.

During the rest phase, a bottom-centered semicircular countdown shows the completed wave number and remaining seconds; its arc opens downward so the bow faces upward. Fishing is available exclusively during this rest phase and is blocked during active-wave document work.
