# Architecture

This project is a compact pygame roguelite that now uses a thin `Game` composition class plus a set of focused mixins under `shadowcaster/mixins/`.

## Boot Flow

1. Run `python shadowcaster_game.py`
2. `shadowcaster_game.py` forwards into `shadowcaster.main`
3. `shadowcaster.main` constructs `shadowcaster.game.Game`
4. `Game` is a composition shell that inherits from the mixins listed below
5. `GameCoreMixin.__init__` initializes pygame, shared runtime state, controllers, and the main menu
6. `Game.run()` drives the main loop:
   - `handle_input()`
   - `update_continuous_movement()`
   - `render()`

## Composition Map

`shadowcaster/game.py` should stay thin. It is responsible for:
- assembling the `Game(...)` MRO
- holding shared class-level catalogs such as weapons and armor
- staying a stable import target for the rest of the codebase

Current gameplay mixins:

| File | Responsibility |
|---|---|
| `shadowcaster/mixins/game_core.py` | app bootstrap, shared state, tuning schema, top-level run/render shell |
| `shadowcaster/mixins/game_world.py` | world/seed policy, danger rules, region-choice helpers |
| `shadowcaster/mixins/game_world_travel.py` | arrivals, exits, world transitions, preview region capture |
| `shadowcaster/mixins/game_towns.py` | town landmarks, building flavor, resident interactions, service logic |
| `shadowcaster/mixins/game_world_state.py` | region snapshots, save/load application, local-region keys, world-state restoration |
| `shadowcaster/mixins/game_floor_generation.py` | floor construction, endpoints, pickup placement, feature placement |
| `shadowcaster/mixins/game_world_map_preview.py` | preview generation queue and local-debug preview caching |
| `shadowcaster/mixins/game_world_map_stats.py` | world-map region stats, labels, palette/theme summaries |
| `shadowcaster/mixins/game_world_map_ui.py` | world map layout, hover/focus behavior, debug-map interaction |
| `shadowcaster/mixins/game_overlay_events.py` | overlay event routing, overlay key/controller-button handling |
| `shadowcaster/mixins/game_overlay_input.py` | overlay navigation helpers and non-event overlay state |
| `shadowcaster/mixins/game_overlay_clicks.py` | mouse click dispatch for overlays and world map |
| `shadowcaster/mixins/game_input.py` | direct gameplay input, controller movement, touch/map clicks, action dispatch |
| `shadowcaster/mixins/game_population.py` | enemy spawn logic and hostile population helpers |
| `shadowcaster/mixins/game_residents.py` | resident spawn logic, routines, and resident lookup helpers |
| `shadowcaster/mixins/game_movement.py` | player movement, stair/portal travel, click pathing, continuous movement |
| `shadowcaster/mixins/game_ui.py` | general UI helpers, touch dock, shared overlay utilities, sighting messages |
| `shadowcaster/mixins/game_menu_ui.py` | main/pause menu, tuner, inventory/journal/log toggles and layout |
| `shadowcaster/mixins/game_rewards_ui.py` | reward choice and provisioner choice handling |
| `shadowcaster/mixins/game_death_ui.py` | death overlay layout and stat-tab content |
| `shadowcaster/mixins/game_journal_ui.py` | journal overlay layout/state, quest selection, journal action gating |
| `shadowcaster/mixins/game_log_ui.py` | recent-log overlay layout/state |
| `shadowcaster/mixins/game_autoexplore.py` | frontier scoring, autoexplore targeting, safe route selection |
| `shadowcaster/mixins/game_combat.py` | combat resolution, statuses, ranged/melee attacks, end-of-turn enemy actions |
| `shadowcaster/mixins/game_visibility.py` | visibility, seen-tile logic, exploration metrics, camera sync |
| `shadowcaster/mixins/game_terrain.py` | terrain feature generation and transparency sync |
| `shadowcaster/mixins/game_inventory.py` | inventory and equipment data operations |
| `shadowcaster/mixins/game_inspect.py` | inspect panel text and hover/click info helpers |
| `shadowcaster/mixins/game_controls.py` | controls modal, controller label presentation |
| `shadowcaster/mixins/game_quests.py` | notice board quests and quest completion |

Mixin types are declared in `shadowcaster/game_typing.py` (`GameMixinBase`). All shared `self.*` attributes used across mixins should be declared there so Pylance can resolve them without false positives.

## Non-Mixin Modules

**Data / support:**

| File | Responsibility |
|---|---|
| `shadowcaster/constants.py` | colors, dimensions, bindings, timing constants |
| `shadowcaster/config.py` | global deterministic seed configuration |
| `shadowcaster/models.py` | dataclasses for enemies, items, landmarks, residents, rooms, quests |
| `shadowcaster/dungeon.py` | BSP dungeon generation primitives |
| `shadowcaster/systems.py` | shadowcasting, A*, reachability, heuristics |
| `shadowcaster/persistence.py` | save/load entry points; re-exports serializers from persistence_serializers |
| `shadowcaster/persistence_serializers.py` | all `*_to_data` / `*_from_data` functions and `SavedMap` |
| `shadowcaster/game_typing.py` | `GameMixinBase` and `RegionMapLike` stubs; declare shared `self.*` attributes here to suppress Pylance false positives |

**Region generation:**

| File | Responsibility |
|---|---|
| `shadowcaster/regions.py` | data classes, path utilities, `generate_region` dispatch, palettes, naming |
| `shadowcaster/regions_generators.py` | overworld biome generators (forest, desert, mountain, swamp, plains, badlands, tundra, volcanic, cave, castle, maze, ruins) |
| `shadowcaster/regions_farmland.py` | farmland generator (`_place_building`, `generate_farmland`) |
| `shadowcaster/regions_town.py` | `generate_monster_town`, `generate_interior`; re-exports `generate_town` |
| `shadowcaster/regions_generate_town.py` | public API: `heuristic_city_distance`, `town_profile`, `generate_town` orchestrator |
| `shadowcaster/regions_generate_town_helpers.py` | early-phase `generate_town` helpers (`_setup_region_base`, `_place_houses`) |
| `shadowcaster/regions_generate_town_civic.py` | civic/decor/building assignment helpers used by `generate_town` |

`generate_region` (the dispatcher in `regions.py`) uses a lazy import of `regions_town` inside the function body to avoid a circular import — do not change this.

**Rendering:**

| File | Responsibility |
|---|---|
| `shadowcaster/rendering.py` | `render_game` orchestrator, `render_region_banner` |
| `shadowcaster/rendering_viewport.py` | `render_viewport` (tile loop, entities, terrain footprints) and `render_side_panel` (status chips, inspect, log) |
| `shadowcaster/rendering_primitives.py` | `draw_tile`, `draw_marker`, `draw_health_bar`, `draw_status_pips`, `wrap_text`, `draw_section_header`, `draw_tabs` |
| `shadowcaster/rendering_shapes.py` | entity/tile shape rendering; re-exports from rendering_terrain |
| `shadowcaster/rendering_terrain.py` | `terrain_marker_color`, `draw_terrain_marker`, `draw_feature_footprint` |
| `shadowcaster/rendering_world_map.py` | `render_world_map_overlay`, `draw_world_map_section`; re-exports from rendering_world_map_helpers |
| `shadowcaster/rendering_world_map_helpers.py` | pure draw helpers: chips, connections, routes, site markers, settlement icons |
| `shadowcaster/rendering_game_overlays.py` | in-play overlays: completion modal, reward choice, tuner, inventory, game-over, travel |
| `shadowcaster/rendering_menu_overlays.py` | menu overlay; re-exports from rendering_journal_overlays |
| `shadowcaster/rendering_journal_overlays.py` | `render_notice_board_overlay`, `render_journal_overlay`, `render_log_overlay` |
| `shadowcaster/rendering_overlays.py` | re-export shim — imports from both overlay modules for backward compat |

When adding a new overlay renderer, add it to `rendering_game_overlays.py` or `rendering_journal_overlays.py` (for journal-style) or `rendering_menu_overlays.py` (for menu-style), then re-export from `rendering_overlays.py` and dispatch from `render_game` in `rendering.py`.

## Cross-Cutting State

Some state is intentionally shared across many mixins:
- `self.dungeon`, `self.player`, `self.enemies`, `self.residents`
- `self.visible_tiles`, `self.seen_tiles`, `self.floor_explorable_tiles`
- overlay booleans like `self.world_map_open`, `self.inventory_open`, `self.tuner_open`
- world/local state like `self.world_regions`, `self.local_regions`, `self.current_local_region`
- journal/log state such as `self.journal_index`, `self.journal_scroll`, `self.log_scroll`, and selected quest gating helpers used by both input and rendering

If you add a new subsystem, check whether it is:
- render-only
- state-only
- input-only
- or truly cross-cutting

Only the last category belongs in a broad mixin.

## Input Model

Input handling is split intentionally:
- `game_overlay_input.py` handles modal and overlay routing
- `game_input.py` handles core world input and action dispatch
- `game_movement.py` handles repeated movement/path execution

When adding a new overlay:
1. add render function in `rendering_game_overlays.py` or `rendering_menu_overlays.py`
2. re-export it from `rendering_overlays.py` and dispatch it from `render_game` in `rendering.py`
3. add gating in overlay checks (`active_non_menu_overlay`, all input handlers — see AGENTS.md invariant on overlay flags)
4. add keyboard, mouse, controller, and touch paths
5. smoke-test combinations with other overlays

## World Model

There are two persistent map layers:
- overworld regions keyed by world coordinate
- local regions keyed by landmark/base/depth identity

Important consequences:
- entering a landmark snapshots the current parent region first
- lower floors are separate persisted local-region states
- preview-generated world-map regions must not leak visible play-state
- “Discovered” and “previewed” world regions are intentionally different. UI that gates player-facing actions like journal `Show Map` should rely on true discovered-region membership (`world_regions` / current region), not the broader preview layer used by the world map

## Verification

Minimum safe verification after structural changes:
- `python -B utils/refactor_tools.py smoke-game`
- `python -B utils/largest_py_files.py --top 20`
- import smoke for any new mixin shim if relevant

For generation-sensitive work, also fuzz multiple seeds headlessly.
