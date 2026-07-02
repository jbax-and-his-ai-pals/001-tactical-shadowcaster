# CLAUDE.md

This project is LLM-managed. Read this file first, then `AGENTS.md`, then `docs/ARCHITECTURE.md`.

## Quick start

```powershell
python shadowcaster_game.py          # run the game
python -B utils/refactor_tools.py smoke-game   # headless boot check
python -B utils/largest_py_files.py --top 20   # find large files
```

## Where things live

- Game logic: `shadowcaster/mixins/game_*.py` (mixin classes composed into `Game`)
- Region generators: `shadowcaster/regions*.py`
- Rendering: `shadowcaster/rendering*.py`
- Data classes: `shadowcaster/models.py`
- Constants/colors: `shadowcaster/constants.py`
- Save/load: `shadowcaster/persistence.py`

Full module map → `AGENTS.md` § Architecture and § Mixin Map  
Architectural invariants (read before touching regions or rendering) → `AGENTS.md` § Known Invariants  
Refactor tooling commands → `utils/README.md`

## File size target

**Hard rule: every file must stay under 400 lines.** Target is ≤300 lines.

- ≤300 lines → ideal, no action needed
- 301–399 lines → acceptable, monitor
- 400+ lines → **split immediately before adding any new code**

When you finish a task, run `python -B utils/largest_py_files.py --top 20` and
split any file at 400+ before closing out. Never add new functions to a file
already at or near 400 lines without splitting first.

Split strategy: extract cohesive function groups into a new `*_helpers.py` or
thematically named sibling, then re-export the names from the original file so
all callers continue to work unchanged.

## Workflow for structural changes

1. `python -B utils/refactor_tools.py methods <file> <ClassName>` — map methods before splitting
2. `python -B utils/refactor_tools.py extract-methods ... --dry-run` — preview the move
3. Run the real extract, then `sync-imports`, then `wire-mixin`
4. `python -B utils/refactor_tools.py smoke-game` — verify boot

## Key invariants (short form)

- Every edge exit must be reachable from the player start tile
- Town service-building doors are protected tiles — don't seal them with noise
- New overlays need gating in ~15 places: render dispatch, keyboard, controller dpad, controller buttons, touch — grep `tuner_open` to find them all
- Generation is seeded via `Game.seed_scope(...)` — new procedural entry points must use the same pattern
- `effective_melee_damage` / `effective_ranged_damage` / `effective_defense` are the combat values to read, not raw stat fields
