# Architecture

This project is a compact pygame roguelite that now uses a thin `Game` composition class plus a set of focused mixins under `shadowcaster/mixins/`.

For test entry points and current regression coverage, read `docs/TESTING.md`.

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
| `shadowcaster/mixins/game_world.py` | world/seed policy, danger rules, biome affinity, region-choice helpers |
| `shadowcaster/mixins/game_world_geography.py` | world structure generation: rivers, coast, named zones, city with districts (market/civic/temple/stronghold) |
| `shadowcaster/mixins/game_world_travel.py` | arrivals, exits, world transitions, level-5 region gate, preview region capture |
| `shadowcaster/mixins/game_world_state.py` | region snapshots, save/load application, local-region keys, world-state restoration |
| `shadowcaster/mixins/game_world_map_stats.py` | world-map region stats, labels, palette/theme summaries |
| `shadowcaster/mixins/game_world_map_ui.py` | world map layout, hover/focus behavior, debug-map interaction |
| `shadowcaster/mixins/game_world_map_preview.py` | preview generation queue and local-debug preview caching |
| `shadowcaster/mixins/game_world_map_settlements.py` | settlement size selection, subtitle text, town palette helpers for map display |
| `shadowcaster/mixins/game_towns.py` | town landmarks, building flavor, service entry, `surface_landmark_kinds()` gate in `enter_landmark` |
| `shadowcaster/mixins/game_towns_services.py` | town service application (inn, smith, cartographer, apothecary, bathhouse, armory) |
| `shadowcaster/mixins/game_towns_reveal.py` | cartographer reveal logic: adjacent region reveal, distant region reveal |
| `shadowcaster/mixins/game_town_reactions.py` | town-attitude/response helpers: resident tone, board framing, service flavor |
| `shadowcaster/mixins/game_landmark_services.py` | surface-modal landmark reward handlers (`apply_surface_landmark`) |
| `shadowcaster/mixins/game_rare_npcs.py` | wandering merchants and lorekeepers: seeded once per world, spawn when player enters matching region |
| `shadowcaster/mixins/game_floor_generation.py` | floor construction, endpoints, pickup placement, feature placement, XP checks on entry |
| `shadowcaster/mixins/game_overlay_events.py` | overlay event routing, keyboard/mouse handling per overlay type |
| `shadowcaster/mixins/game_overlay_controller.py` | controller D-pad/button handling for all overlay types |
| `shadowcaster/mixins/game_overlay_input.py` | analog stick navigation, non-event overlay state |
| `shadowcaster/mixins/game_overlay_clicks.py` | mouse/touch click dispatch for overlays and world map |
| `shadowcaster/mixins/game_input.py` | direct gameplay input, action dispatch, touch tap routing |
| `shadowcaster/mixins/game_population.py` | enemy spawn logic, biome pool selection, signature/bookend enemy placement |
| `shadowcaster/mixins/game_residents.py` | resident lookup helpers and resident movement routines |
| `shadowcaster/mixins/game_residents_town.py` | resident spawning: roster selection, biome-flavored roles, patrol assignment |
| `shadowcaster/mixins/game_resident_boons.py` | once-per-town resident boon interactions (heal, ward, ammo, medkit, reveal, etc.) |
| `shadowcaster/mixins/game_movement.py` | player movement, stair/portal travel, click pathing, continuous movement |
| `shadowcaster/mixins/game_combat.py` | combat resolution, status ticks, melee/ranged attack dispatch |
| `shadowcaster/mixins/game_combat_ai.py` | per-enemy AI turn: movement, attack, flanking, reinforcement calls |
| `shadowcaster/mixins/game_abilities.py` | Level 4 ability pool; passive hooks: on_kill, on_hit_received, on_region_enter, light_bonus, cache_double |
| `shadowcaster/mixins/game_xp.py` | XP tracking, level thresholds (L1–L5), level-up trigger, `player_title()`, XP source checks |
| `shadowcaster/mixins/game_respawn.py` | death flow: gold loss, region reset, respawn at homepoint/shrine/origin |
| `shadowcaster/mixins/game_stats.py` | derived stat properties: `light_radius`, `autoexplore_interval`, `melee_range`, `effective_*_damage` |
| `shadowcaster/mixins/game_trade.py` | trade overlay state and logic: trader stock generation, buy/sell, attitude-scaled depth |
| `shadowcaster/mixins/game_harvest.py` | farmland harvest nodes: spec selection, eligibility, generation, turn-in |
| `shadowcaster/mixins/game_social_quests.py` | cross-town social quests: letters, favors, relative visits, rumor follow-ups |
| `shadowcaster/mixins/game_quests.py` | quest board refresh, board quest assignment, quest completion handling |
| `shadowcaster/mixins/game_quest_board.py` | board-attitude gating, reward scaling, trusted-town priority contract generation/themes |
| `shadowcaster/mixins/game_quest_generation.py` | procedural quest construction: destination/reward/target selection per kind |
| `shadowcaster/mixins/game_quest_text.py` | quest description text, journal entry lines, chain stage text, context lines |
| `shadowcaster/mixins/game_ui.py` | general UI helpers, touch dock, shared overlay utilities, sighting messages |
| `shadowcaster/mixins/game_menu_ui.py` | main/pause menu, inventory/journal/log toggles and layout, inventory rows |
| `shadowcaster/mixins/game_tuning.py` | tuner overlay: schema definition, value adjustment, tuner layout |
| `shadowcaster/mixins/game_rewards_ui.py` | reward choice and provisioner choice handling |
| `shadowcaster/mixins/game_death_ui.py` | death overlay layout and stat-tab content |
| `shadowcaster/mixins/game_journal_stats.py` | quest counts, prosperity/standing math, character tab rows, journal summary text |
| `shadowcaster/mixins/game_journal_ui.py` | journal overlay layout/state, quest selection, journal action gating |
| `shadowcaster/mixins/game_log_ui.py` | recent-log overlay layout/state |
| `shadowcaster/mixins/game_autoexplore.py` | frontier scoring, autoexplore targeting, safe route selection |
| `shadowcaster/mixins/game_visibility.py` | visibility, seen-tile logic, exploration metrics, camera sync |
| `shadowcaster/mixins/game_terrain.py` | terrain feature generation and transparency sync |
| `shadowcaster/mixins/game_inventory.py` | inventory and equipment data operations, floor item generation |
| `shadowcaster/mixins/game_inventory_use.py` | item use dispatch: medkit, tonic, consumable effects, equip/unequip |
| `shadowcaster/mixins/game_inspect.py` | inspect panel text and hover/click info helpers |
| `shadowcaster/mixins/game_controls.py` | controls modal, controller label presentation |

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
| `shadowcaster/enemy_catalog.py` | 81 data-driven enemy entries; `biome_pool()`, `weighted_choice()`, `_BIOME_ALIASES` |
| `shadowcaster/item_catalog.py` | weapon/armor/trinket/consumable item definitions; `NEVER_SOLD`, `DROPPABLE` sets |

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
| `shadowcaster/regions_metadata.py` | region naming tables, `region_summary()`, `palette_for_region()` — all region types including legendary/stronghold |

`generate_region` (the dispatcher in `regions.py`) uses a lazy import of `regions_town` inside the function body to avoid a circular import — do not change this.

**Rendering:**

| File | Responsibility |
|---|---|
| `shadowcaster/rendering.py` | `render_game` orchestrator, `render_region_banner` |
| `shadowcaster/rendering_viewport.py` | `render_viewport` (tile loop, entities, terrain footprints) and `render_side_panel` (status chips, inspect, log) |
| `shadowcaster/rendering_primitives.py` | `draw_tile`, `draw_marker`, `draw_health_bar`, `draw_status_pips`, `wrap_text`, `draw_section_header`, `draw_tabs` |
| `shadowcaster/rendering_shapes.py` | entity/tile shape rendering; re-exports from rendering_terrain |
| `shadowcaster/rendering_terrain.py` | `terrain_marker_color`, `draw_terrain_marker`, `draw_feature_footprint` |
| `shadowcaster/rendering_world_map.py` | `render_world_map_overlay`, `draw_world_map_section`; re-exports from helpers |
| `shadowcaster/rendering_world_map_helpers.py` | draw helpers: chips, connections, routes, site markers, settlement icons |
| `shadowcaster/rendering_world_map_icons.py` | icon/symbol drawing for world map: rivers, coast, zone labels, city markers |
| `shadowcaster/rendering_world_map_quest_helpers.py` | quest annotation helpers for world map region detail panel |
| `shadowcaster/rendering_game_overlays.py` | in-play overlays: completion modal, reward choice, tuner, inventory, game-over, travel |
| `shadowcaster/rendering_levelup.py` | level-up modal and Level 4 ability card selection UI |
| `shadowcaster/rendering_trade.py` | two-column trade overlay: stock panel, pack panel, buy/sell rows |
| `shadowcaster/rendering_menu_overlays.py` | menu overlay; re-exports from rendering_journal_overlays |
| `shadowcaster/rendering_journal_overlays.py` | `render_notice_board_overlay`, `render_journal_overlay` (with Character tab), `render_log_overlay` |
| `shadowcaster/rendering_overlays.py` | re-export shim — imports from all overlay modules for backward compat |

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
