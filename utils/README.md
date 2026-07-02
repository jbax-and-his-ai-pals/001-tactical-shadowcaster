# Utilities

This folder is for repeatable file-management and optimization helpers so future migrations can be driven by commands instead of one-off manual edits.

## Current Tooling

### `python utils/largest_py_files.py`
Shows the largest Python files in the repo by line count.

Examples:

```powershell
python utils/largest_py_files.py
python utils/largest_py_files.py --top 15
python utils/largest_py_files.py shadowcaster
```

### `python utils/refactor_tools.py inventory`
Shows file line counts so we can spot oversized modules quickly.

Examples:

```powershell
python utils/refactor_tools.py inventory
python utils/refactor_tools.py inventory shadowcaster --top 8
python utils/refactor_tools.py inventory shadowcaster --glob "game_*.py"
```

### `python utils/refactor_tools.py methods`
Lists methods in a class with source line ranges. Useful before a split.

Example:

```powershell
python utils/refactor_tools.py methods shadowcaster/mixins/game_ui.py UIMixin
```

### `python utils/refactor_tools.py extract-methods`
Moves named methods from one class file into another class file with minimal structural churn.

Example dry run:

```powershell
python utils/refactor_tools.py extract-methods `
  shadowcaster/mixins/game_ui.py shadowcaster/mixins/game_inspect.py `
  --source-class UIMixin --dest-class InspectMixin `
  --methods inspect_title inspect_tile_info current_inspect_info `
  --dry-run
```

Example real move:

```powershell
python utils/refactor_tools.py extract-methods `
  shadowcaster/mixins/game_ui.py shadowcaster/mixins/game_inspect.py `
  --source-class UIMixin --dest-class InspectMixin `
  --methods inspect_title inspect_tile_info current_inspect_info
```

### `python utils/refactor_tools.py audit-imports`
Reports unresolved global names used by a selected method set inside a class file.

Example:

```powershell
python utils/refactor_tools.py audit-imports `
  shadowcaster/mixins/game_inspect.py InspectMixin `
  --methods inspect_title inspect_tile_info current_inspect_info
```

### `python utils/refactor_tools.py sync-imports`
Copies top-level import statements from the source module into the destination module when the moved methods still depend on them.

Example:

```powershell
python utils/refactor_tools.py sync-imports `
  shadowcaster/mixins/game_ui.py shadowcaster/mixins/game_inspect.py `
  --dest-class InspectMixin `
  --methods inspect_title inspect_tile_info current_inspect_info
```

### `python utils/refactor_tools.py wire-mixin`
Adds the new mixin import to `shadowcaster/game.py` and composes it into the `Game(...)` base list.

Example:

```powershell
python utils/refactor_tools.py wire-mixin `
  shadowcaster/game.py shadowcaster/mixins/game_inspect.py InspectMixin `
  --after UIMixin
```

### `python utils/refactor_tools.py smoke-game`
Runs a headless pygame smoke boot (`Game().start_new_game()`) so we can verify a migration without opening a window.

Example:

```powershell
python utils/refactor_tools.py smoke-game
```

## Notes

- The extractor performs a literal move of method bodies.
- `sync-imports` only copies import statements. If a moved method depends on a top-level helper function or constant definition rather than an import, `audit-imports` will still tell you what remains unresolved.
- Prefer targeting `shadowcaster/mixins/*.py` as the real destination/source files. The top-level `shadowcaster/game_*.py` files are compatibility shims only.
- Recommended migration flow:
  1. Run `methods` to identify a coherent slice.
  2. Run `extract-methods --dry-run`.
  3. Run the real `extract-methods`.
  4. Run `sync-imports` for the moved methods.
  5. Run `wire-mixin` to compose the new mixin into `Game`.
  6. Run `audit-imports` on the destination class.
  7. Run `smoke-game`.

## Refactor Checklist

After any mixin split, sanity-check all of these:

1. The destination mixin has the imports it now needs.
2. `shadowcaster/mixins/__init__.py` exports the new mixin.
3. `shadowcaster/game.py` imports and composes the new mixin.
4. A compatibility shim exists at `shadowcaster/game_<name>.py` if older imports may still reference it.
5. `python -B utils/refactor_tools.py smoke-game` still passes.
6. If the split touched overlays, verify keyboard, mouse, controller, and touch paths still exist.
7. If the split touched region state, verify snapshot/load paths still round-trip.

## Known Tool Caveats

- `wire-mixin` can be fragile around parenthesized multi-line imports in `shadowcaster/game.py`; manual wiring may still be the safer path.
- Some moves still require a manual import cleanup pass in the destination file after extraction.
- `py_compile` may fail in this environment because writing `__pycache__` files is restricted; use import smoke and `smoke-game` as the practical verification path here.

- Pilot migrations already completed with this workflow:
  `inspect_title`, `inspect_tile_info`, and `current_inspect_info` moved from `shadowcaster/mixins/game_ui.py` to `shadowcaster/mixins/game_inspect.py`.
  Controls-modal helpers moved from `shadowcaster/mixins/game_ui.py` to `shadowcaster/mixins/game_controls.py`.

- As more migration patterns prove useful, add them here rather than inventing new ad-hoc scripts elsewhere in the repo.
