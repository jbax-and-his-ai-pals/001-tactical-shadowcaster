# Tactical Shadowcaster

**A persistent-world exploration roguelite built with Python and pygame.** Wander a procedurally generated overworld, scout named places under recursive-shadowcasting line of sight, fight turn-based skirmishes, and watch towns respond to the work you do for them.

> The arc is *stranger → shaper*: you arrive knowing nothing, and over many hours the world becomes more legible and more developed because you were in it.

## Highlights

- **Seeded, persistent world.** Rivers, coastlines, named geographic zones, a multi-district capital city, and 12+ biome and settlement region types. The same seed always yields the same world, and your discoveries, quests and towns persist between sessions.
- **Tactical line-of-sight play.** Recursive shadowcasting FOV, grid movement with diagonals, melee and ranged combat, A* enemy pursuit gated by what they can see, and status effects and terrain hazards.
- **Living settlements.** Towns have districts, service buildings (inn, smith, apothecary, cartographer, bathhouse, armory), recurring residents with routines and boons, notice-board quest chains, and an attitude system that changes what they offer.
- **Build identity.** Four archetype tracks (Scout, Delver, Warden, Hunter), a skill system, levelled unlocks, and an ability pool, plus gear with composable effects and a four-tier rarity model.
- **81 data-driven enemies** with distinct behaviours (pursuers, kiters, chargers, flankers, ambushers), traits, and named elites.
- **Persistent death.** Dying costs carried gold and resets the region's enemies. The rest of the world stays as you left it.
- **Full input support.** Keyboard and mouse, gamepad, and touch, including a world map with zoom, pan, and region detail.

## Quick start

Requires Python 3.10+ and [pygame](https://www.pygame.org/) (the `pygame-ce` fork works too).

```bash
pip install -r requirements.txt
python shadowcaster_game.py
```

The default controls are WASD or arrows to move, `Space` to attack or talk, `M` for the world map, and `I` for inventory. The [Player Guide](docs/PLAYER_GUIDE.md) has the complete control tables, including controller and touch.

## Deterministic seeds

- Set `DEFAULT_WORLD_SEED` in `shadowcaster/config.py` to an integer or short string to generate the same world every run.
- Or set the `SHADOWCASTER_WORLD_SEED` environment variable.
- Save files record the active `world_seed`, so loading a run keeps its world identity.

## Tests

```bash
python run_tests.py
```

Tests run headless using pygame's dummy video driver. See [docs/TESTING.md](docs/TESTING.md) for coverage details.

## Repository layout

| Path | Contents |
|---|---|
| `shadowcaster_game.py` | Entry point |
| `shadowcaster/` | Game package: `game.py` composition shell, `mixins/` for gameplay systems, `regions*.py` generators, `rendering*.py`, `persistence*.py`, data catalogs |
| `shadowcaster/tests/` | Headless unittest suite |
| `docs/` | Player guide, architecture, testing notes |
| `utils/` | Refactoring and file-size tooling (see [utils/README.md](utils/README.md)) |
| `saves/`, `music/` | Save slots and audio assets |

## Documentation

| Document | Audience | What it covers |
|---|---|---|
| [docs/PLAYER_GUIDE.md](docs/PLAYER_GUIDE.md) | Players | Controls, the world loop, gear, enemies, progression |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Contributors | Boot flow, mixin composition, module map |
| [docs/TESTING.md](docs/TESTING.md) | Contributors | Running and extending tests |
| [ROADMAP.md](ROADMAP.md) | Everyone | Shipped features and planned phases |
| [AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md) | LLM agents and contributors | Invariants, conventions, workflow rules |

## Contributing

This project is developed with LLM assistance, so the conventions are written down. Read `CLAUDE.md`, then `AGENTS.md`, then `docs/ARCHITECTURE.md` before changing code. Key rules: keep every file under 400 lines, generate procedural content inside `Game.seed_scope(...)`, and make sure every region edge exit is reachable from the player start.
