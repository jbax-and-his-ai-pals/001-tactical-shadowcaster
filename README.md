# Tactical Shadowcaster

Small pygame tactics crawler prototype focused on line of sight, exploration, tactical movement, and an emerging region-based world.

## Run
```bash
python shadowcaster_game.py
```

## Deterministic Seeds
- Set `DEFAULT_WORLD_SEED` in `shadowcaster/config.py` to an integer or short string if you want new runs to generate the same world every time
- You can also set the environment variable `SHADOWCASTER_WORLD_SEED` instead
- Save files now persist the active `world_seed`, so loading a run keeps its world identity intact

## Project Notes
- Architecture, invariants, and known debt for future coding conversations: `AGENTS.md`
- Implemented features and planned next steps: `ROADMAP.md`
- Main package code lives in `shadowcaster/`
