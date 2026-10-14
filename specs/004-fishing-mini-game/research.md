# Research: Fishing Mini-Game

**Feature**: [004-fishing-mini-game](./spec.md)
**Date**: 2026-10-13

## Decision 1: Model fishing as a pure deterministic state machine

- **Decision**: Add `src/game/fishing.py` with immutable fishing-attempt states and pure elapsed-time transition functions for casting, the fixed bite delay, the one-second reaction window, and the catch game.
- **Rationale**: The constitution requires independently testable deterministic rules. Explicit phases prevent invalid transitions such as starting two catch games or awarding a fish twice.
- **Alternatives considered**: Put fishing branches directly in `state.py` (rejected because it would mix orchestration and rules); use Pygame timers (rejected because frame/event timing would make tests less deterministic).

## Decision 2: Use the existing `E` interaction edge for every fishing action

- **Decision**: Reuse the existing one-frame `interact_pressed` action for casting, reacting to the bite, and raising the catch bar.
- **Rationale**: This was clarified by the user and keeps the control scheme consistent with document interaction.
- **Alternatives considered**: Add a second key or mouse-only fishing controls (rejected because they increase control complexity without adding value).

## Decision 3: Use fixed timing and centralized balance values

- **Decision**: Use a fixed 2-second bite delay, a reaction window strictly under 1 second, a 0.15-second post-press grace period, bounded catch-bar velocity, predictable upward impulses, and centralized gravity/max-speed values. Use aligned progress gain of 25/s, misaligned progress loss of 35/s, and a 25-stamina reward.
- **Rationale**: Fixed timing makes the first slice reproducible. A velocity-based model preserves momentum and produces smoother control than directly calculating position from elapsed time. All values remain centralized so balancing does not require rewriting transitions.
- **Alternatives considered**: Direct linear or quadratic position decay (rejected because velocity changes are discontinuous and input feels less fluid); random bite timing (deferred until seeded variation is useful); frame-count updates (rejected because they violate frame-rate independence).

## Decision 8: Model the catch bar as a bounded velocity system

- **Decision**: Store catch-bar velocity in `FishingState`. Each valid `E` press adds a bounded upward impulse and resets the grace timer. During the grace period gravity does not add downward acceleration; afterwards gravity changes velocity continuously. Integrate velocity into position using elapsed simulation time, then clamp both position and velocity.
- **Rationale**: This gives repeated presses meaningful momentum, makes the catch bar respond smoothly, and keeps behavior deterministic across frame rates while preserving the already-tuned grace period.
- **Alternatives considered**: Keep the quadratic position formula (rejected because it has no persistent velocity); introduce a general physics engine (rejected because it adds unnecessary dependency and complexity for one bounded meter).

## Decision 4: Pause movement during an active fishing attempt

- **Decision**: While the phase is waiting for a bite, reacting to a bite, or playing the catch game, movement input does not move the player.
- **Rationale**: The user clarified that fishing should keep the player focused and prevent accidental pond exits during the skill challenge.
- **Alternatives considered**: Allow movement throughout fishing (rejected because it creates avoidable cancellation and input conflicts); pause only during catching (rejected because the bite reaction also needs focused timing).

## Decision 5: Rename the world entity to FishingPond

- **Decision**: Replace the player-facing and domain name `StaminaRegenZone` with `FishingPond`, preserving the existing rectangle-based world geometry and one initial pond placement.
- **Rationale**: The old name describes an obsolete passive behavior. The pond is now the location for an active recovery interaction.
- **Alternatives considered**: Keep the old class/name and only change its label (rejected because it leaves contradictory domain terminology in the game logic).

## Decision 6: Keep reward and cancellation authoritative in game state

- **Decision**: A successful fishing transition emits exactly one 25-point stamina reward; missed bites, escaped fish, and cancellations emit no reward. `GameState` applies the reward and resets the fishing attempt.
- **Rationale**: The fishing module should calculate outcomes, while the game state owns the player's stamina and workflow. This prevents duplicate rewards and preserves game-over rules.
- **Alternatives considered**: Let the renderer award stamina on an animation (rejected because presentation must not mutate authoritative state); allow fishing to revive game over (rejected by the stamina specification).

## Decision 7: Use placeholder, text-labeled catch-game presentation

- **Decision**: Render a vertical play bar, fish symbol, catch bar, fishing-progress bar, and phase/status text with existing Pygame drawing primitives; do not add assets or dependencies.
- **Rationale**: The project constitution favors replaceable placeholders and requires readable feedback that does not depend on color alone.
- **Alternatives considered**: External sprite/audio assets (deferred because they are not required for the gameplay slice); color-only meters (rejected for accessibility/readability).
