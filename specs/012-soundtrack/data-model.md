# Data Model: Continuous Soundtrack

**Feature**: `012-soundtrack`

The soundtrack model is application-session state. It is intentionally separate from gameplay `GameState`, which may be replaced when a new round starts.

## `SoundtrackAsset`

The immutable supplied audio asset.

| Field | Type | Rules |
|---|---|---|
| `path` | path | Must identify `assets/Music/I'm Not a Big Fan of.m4a`. |
| `complete_track` | boolean | Always true; the entire song is used rather than a clipped segment. |

## `ApplicationMusicSession`

The single music playback owner for one application launch.

| Field | Type | Rules |
|---|---|---|
| `asset` | `SoundtrackAsset` | The one configured soundtrack. |
| `started` | boolean | Becomes true after a successful start attempt. |
| `available` | boolean | False when mixer initialization or asset loading fails. |
| `looping` | boolean | True for successful playback; the track repeats automatically. |
| `failure_message` | string or null | Readable diagnostic when audio is unavailable; must not stop gameplay. |

## Ownership and lifecycle

```text
Application starts
  -> initialize mixer and load SoundtrackAsset
  -> PLAYING + looping when successful
  -> UNAVAILABLE + readable warning when initialization/loading fails

Game round starts or restarts
  -> gameplay GameState is created independently
  -> ApplicationMusicSession is reused unchanged

Song reaches end
  -> mixer loops the same complete asset

Application closes
  -> application music session ends with the process
```

## Invariants

- There is at most one `ApplicationMusicSession` per application process.
- `create_game_state` and game-over restart must not initialize, stop, rewind, or duplicate the soundtrack.
- Wave transitions, rest phases, and gameplay state updates do not mutate music-session ownership.
- Audio failure never makes the gameplay loop or a new round unavailable.
