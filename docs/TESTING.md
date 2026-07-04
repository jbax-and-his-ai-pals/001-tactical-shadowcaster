# Testing

The project now includes a lightweight in-repo test suite under `shadowcaster/tests/`.

## Run

Use:

```powershell
python run_tests.py
```

For the direct unittest invocation:

```powershell
python -m unittest discover -s shadowcaster\tests -t .
```

This runs headless with pygame's dummy video driver through shared helpers in `shadowcaster/tests/support.py`.

## Current Coverage

- `test_smoke.py`
  - boots `Game`
  - starts a new run
  - verifies a playable region is created
- `test_generation.py`
  - sweeps multiple seeds to ensure connected-region edge exits are reachable
  - verifies town and monster-town service doors remain reachable from the plaza
  - verifies transparent blocking terrain still allows FOV beyond it
- `test_gameplay_rules.py`
  - verifies surface-landmark rewards are one-time only
  - verifies visible hostiles interrupt auto-move logic
  - verifies non-hostile points of interest only interrupt on first sighting
- `test_overlays.py`
  - verifies pending choices block other overlays
  - verifies inventory/world-map overlay gating
  - verifies opening the main menu closes the world map
- `test_routing.py`
  - verifies click-pathing avoids exit tiles unless they are the explicit destination
  - verifies click-pathing prefers a non-hazardous seen route when one exists
  - verifies journal `Show Map` only enables for discovered selected quest destinations
  - verifies abandoning the last active quest clears journal selection state
- `test_autoexplore.py`
  - verifies autoexplore is blocked by on-screen hostiles
  - verifies autoexplore can still proceed when a hostile is visible but off-screen
- `test_board_and_preview.py`
  - verifies notice-board refresh preserves selection when the same posting still exists
  - verifies accepted postings no longer present as confirmable board entries
  - verifies local-debug world-map mode seeds preview targets and preview generation
- `test_persistence.py`
  - verifies save/load preserves the current local-region context
  - verifies save/load round-trips region-level claimed surface landmarks

## Conventions

- Prefer `unittest` so the suite works with stdlib-only Python while staying pytest-compatible later.
- Keep tests deterministic by setting `game.config_world_seed` or using direct generation helpers with stable context.
- Favor invariant tests over brittle screenshot-style assertions.
- When adding new procedural systems, add a small seed sweep instead of a single lucky example when practical.
- For overlay or input regressions, isolate state helpers where possible instead of trying to drive full interactive sessions.

## Good Next Additions

- broader world/local region snapshot round-trip coverage beyond landmark claims
- autoexplore route-avoidance tests around exits, hazards, and off-screen enemies
- journal, notice-board, and world-map state tests for deeper selection/scroll behavior
