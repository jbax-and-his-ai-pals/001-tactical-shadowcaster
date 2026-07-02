# AGENTS.md

## Project Goal
Build and iterate on a compact pygame tactics roguelite that is growing from dungeon crawling into a broader region-based world, while staying centered on visibility, movement, and readable combat.

## Design North Star
- Treat the game as a world-expedition roguelite rather than "just another dungeon crawler"
- The intended player loop is: discover a place, understand what makes it interesting, decide whether it is worth the risk, return with something meaningful, and see the world respond
- The most important long-term hooks are exploration, route choice, light character identity, settlement attachment, and meaningful non-combat discovery
- When choosing between features, prefer the one that gives the player a stronger reason to care where they go next

## Runbook
- Primary entrypoint: `python shadowcaster_game.py`
- Roadmap summary: `ROADMAP.md`
- `ROADMAP.md` is now intentionally sequential: prefer working from the `Near-Term Queue` and current phase rather than cherry-picking later-phase ideas unless the user explicitly reprioritizes
- Package code lives under `shadowcaster/`
- Global seed config: `shadowcaster/config.py` via `DEFAULT_WORLD_SEED` or env var `SHADOWCASTER_WORLD_SEED`
- Refactor/file-management helpers live under `utils/` and currently start with `python utils/refactor_tools.py ...`

## File size rule

**Every file must stay under 400 lines. Target is ≤300 lines.**

- ≤300 lines → ideal
- 301–399 lines → acceptable, monitor
- 400+ lines → split before adding new code

After completing any task, run `python -B utils/largest_py_files.py --top 20`. If any file is at 400+, split it first. Extract cohesive function groups into a thematically named sibling (e.g. `rendering_x_helpers.py`), then re-export the names from the original so all callers continue to work.

## Architecture

Use `python -B utils/largest_py_files.py --top 20` for live line counts. The canonical file responsibilities:

**Game logic (mixins):**
- `shadowcaster/game.py`: thin composition shell; assembles `Game` MRO, holds shared class-level catalogs
- `shadowcaster/mixins/`: all gameplay mixin classes (see Mixin Map below)
- `shadowcaster/game_typing.py`: `GameMixinBase` and `RegionMapLike` stubs for Pylance; declare shared `self.*` attributes here

**Region generation:**
- `shadowcaster/regions.py`: data classes (`Region`, `RegionChoice`, `RegionMap`), path utilities, `generate_region` dispatch, palettes, naming
- `shadowcaster/regions_generators.py`: overworld biome generators (forest, desert, mountain, swamp, plains, badlands, tundra, volcanic, cave, castle, maze, ruins)
- `shadowcaster/regions_farmland.py`: farmland generator (`_place_building`, `generate_farmland`)
- `shadowcaster/regions_town.py`: `generate_monster_town`, `generate_interior`; re-exports `generate_town` from regions_generate_town
- `shadowcaster/regions_generate_town.py`: public API — `heuristic_city_distance`, `town_profile`, `generate_town` orchestrator
- `shadowcaster/regions_generate_town_helpers.py`: private phase helpers for `generate_town` (`_setup_region_base`, `_place_houses`, `_add_decor`, `_add_civic_features`, `_assign_buildings`)

**Rendering:**
- `shadowcaster/rendering.py`: `render_game` orchestrator and `render_region_banner`; imports from sub-modules
- `shadowcaster/rendering_viewport.py`: `render_viewport` (tile loop, entities, terrain) and `render_side_panel` (status, inspect, log)
- `shadowcaster/rendering_primitives.py`: low-level helpers: `draw_tile`, `draw_marker`, `draw_health_bar`, `draw_status_pips`, `wrap_text`, `draw_section_header`, `draw_tabs`
- `shadowcaster/rendering_shapes.py`: entity/tile shape rendering; re-exports from rendering_terrain
- `shadowcaster/rendering_terrain.py`: terrain marker rendering (`terrain_marker_color`, `draw_terrain_marker`, `draw_feature_footprint`)
- `shadowcaster/rendering_world_map.py`: `render_world_map_overlay`, `draw_world_map_section`; re-exports helpers from rendering_world_map_helpers
- `shadowcaster/rendering_world_map_helpers.py`: pure draw helpers for world map chips, connections, routes, site markers, settlement icons
- `shadowcaster/rendering_game_overlays.py`: in-play overlays (completion modal, reward choice, tuner, inventory, game-over, travel)
- `shadowcaster/rendering_menu_overlays.py`: menu overlay; re-exports journal/log overlays from rendering_journal_overlays
- `shadowcaster/rendering_journal_overlays.py`: `render_notice_board_overlay`, `render_journal_overlay`, `render_log_overlay`
- `shadowcaster/rendering_overlays.py`: re-export shim for backward-compatible imports

**Support:**
- `shadowcaster/constants.py`: colors, dimensions, input bindings, timing constants
- `shadowcaster/config.py`: global seed configuration
- `shadowcaster/models.py`: dataclasses for enemies, items, landmarks, residents, rooms, quests
- `shadowcaster/dungeon.py`: BSP dungeon generation primitives
- `shadowcaster/systems.py`: FOV (recursive shadowcasting), A*, flood-fill reachability
- `shadowcaster/persistence.py`: save/load entry points; re-exports serializers from persistence_serializers
- `shadowcaster/persistence_serializers.py`: all `*_to_data` / `*_from_data` functions and `SavedMap`
- `shadowcaster/main.py`: tiny launcher
- `shadowcaster_game.py` (repo root): stable entrypoint wrapper
- `utils/refactor_tools.py`: CLI for file inventory, method listing, extract-methods, sync-imports, wire-mixin, smoke-game

## Mixin Map

Line counts drift — run `python -B utils/largest_py_files.py shadowcaster/mixins --top 25` for current sizes.

| Mixin file | Responsibility |
|---|---|
| `game_core.py` | bootstrap, shared runtime state, tuning defaults, top-level run/render shell |
| `game_world.py` | world generation, floor construction, exits, transitions, danger rules |
| `game_towns.py` | towns, service interiors, resident interactions, building flavor |
| `game_world_state.py` | region snapshots, local-region keys, save/load application |
| `game_world_map_stats.py` | world-map region stats and settlement display |
| `game_world_map_ui.py` | world-map layout, preview generation, debug-map behavior |
| `game_world_map_preview.py` | preview region generation and caching |
| `game_world_travel.py` | world-map selection, travel routing, connected-region logic |
| `game_overlay_events.py` | overlay open/close events, controller overlay navigation |
| `game_overlay_input.py` | menus, overlays, dialogs, world-map overlay input |
| `game_overlay_clicks.py` | mouse click dispatch for overlays and world map |
| `game_input.py` | gameplay input, action dispatch, touch/map clicks, controller movement |
| `game_population.py` | enemy spawning, resident spawning, ambient resident movement |
| `game_movement.py` | movement resolution, stair travel, click-pathing, continuous movement |
| `game_combat.py` | combat resolution, status ticks, enemy turn logic |
| `game_ui.py` | general UI helpers, menus/toggles, reward/death/provisioner helpers |
| `game_menu_ui.py` | menu layout, menu activation, visible option filtering |
| `game_rewards_ui.py` | reward and provisioner choice system |
| `game_death_ui.py` | death overlay layout and stat tab content |
| `game_journal_ui.py` | journal and recent-log overlay layout/state |
| `game_autoexplore.py` | autoexplore targeting, frontier scoring, path selection |
| `game_visibility.py` | FOV, seen tiles, exploration progress, terrain feature generation |
| `game_terrain.py` | terrain candidate selection and vision transparency sync |
| `game_inventory.py` | inventory and equipment operations |
| `game_inspect.py` | inspect panel text and hover/click info |
| `game_controls.py` | controls modal and controller labeling |
| `game_quests.py` | quest board, quest generation, quest completion |
| `game_residents.py` | resident boons, adjacent-resident interaction, resident routines |
| `game_floor_generation.py` | floor item/pickup placement, feature placement, floor endpoints |

For a fuller walkthrough, read `docs/ARCHITECTURE.md`.

## Known Invariants - read before touching region generation or rendering
- **Every region edge exit must be reachable from the player's start tile.** `Game.carve_edge_exit` (game.py) carves the exit then unions `floor_explorable_tiles` via `flood_reachable_tiles`, carving a connecting corridor (`carve_path` from `regions.py`) if the exit landed in a disconnected pocket. This is a generic safety net for all region generators. If you add a new region type with island/pocket-style generation (like swamp), do not assume the generator alone guarantees connectivity; the net catches it, but prefer fixing it at the generator level when cheap.
- **Town and monster-town service-building doors are protected tiles.** `generate_monster_town` exempts each service building's door tile from wall-noise and explicitly corridor-links it to the plaza. If you add new town features with single-tile doors, register them the same way or they can get silently sealed.
- **Visibility-gated tiles must be drawn in `render_game`, not just tracked in game state.** Every special tile type (stairs, return portal, pickups, the bottom-floor `delve_goal` terminus) needs its own color/marker branch in `rendering.py`, each checking current visibility versus the dimmer remembered state. A tile that's only revealed by a discrete event handler instead of FOV membership will look like blank terrain until walked on.
- **Don't cache derived per-frame state without an invalidation plan.** `floor_explorable_tiles`, `seen_tiles`, and similar sets are recomputed or unioned at well-defined points; any new cached lookup needs the same discipline or it will go stale.
- **Transparent blockers need explicit treatment.** Some terrain should block movement without blocking visibility (`pond`, `deep_bog`, and similar tiles). If you add new terrain in that family, update both movement and FOV assumptions instead of treating everything non-walkable like a wall.
- **Generation determinism now hangs off `Game.seed_scope(...)`.** World-region choice and floor/local-region generation are intentionally reseeded from `world_seed` plus stable keys like world coordinates or local-region ids, then the previous RNG state is restored. If you add new procedural generation entry points, wrap them in the same pattern or identical seeds will drift into different worlds depending on play order.
- **Every "is an overlay open" gating check is duplicated across many call sites, not centralized.** `tuner_open`/`inventory_open`/`world_map_open`/`has_pending_choice()`/`game_over`/`travel_mode` are combined in ~15 different `if` expressions across keyboard input, controller dpad navigation, controller button handling, touch dispatch, and the various `toggle_X()` guard clauses. Adding a new full-screen overlay means greping for `tuner_open` and adding your new flag everywhere it appears, in all of: the render dispatch chain in `rendering.py`, the keyboard block in `handle_input`, the controller dpad block in `update_controller_overlay_navigation`, the controller button block in `handle_controller_button`, `touch_action_at`, `handle_touch_tap`, and every other `toggle_X()`'s own guard. Missing one spot doesn't crash, it just leaves a silent input leak (e.g. world map openable while inventory is up) — verify by toggling every overlay combination, not just opening yours in isolation.

## Known Debt
- No automated test suite exists. Verification for region-generation/connectivity changes has been done via ad-hoc scripts (headless pygame with `SDL_VIDEODRIVER=dummy`, simulate many seeds, flood-fill-check edge exits and doors). Worth setting up `pytest` plus a handful of these checks as real regression tests if this keeps coming up.
- `regions_town.py` (~555 lines) is the largest remaining non-mixin module. `generate_town` alone is ~420 lines and could be split further if it grows.
- The top-level `shadowcaster/game_*.py` shims exist for backward compat but add navigation overhead. They can be removed once all import sites are confirmed to use `shadowcaster/mixins/` directly.
- Rendering and regions split is complete, but `rendering_primitives.py` (~505 lines) could eventually be split into shape-drawing helpers vs. text/layout helpers if it grows.

## Handoff Workflow
- Read `AGENTS.md` first for runbook, invariants, and current gameplay rules
- Read `docs/ARCHITECTURE.md` next for the mixin/file responsibility map
- Use `python -B utils/largest_py_files.py --top 20` to find current heavy files
- Use `python -B utils/refactor_tools.py methods <file> <ClassName>` before any split
- After a structural change, run `python -B utils/refactor_tools.py smoke-game`

## Current Design Constraints
- Keep files relatively small and focused
- Preserve a simple run loop with low implementation overhead
- Favor parameterized variation over large new subsystems
- Keep the inventory/equipment system light: one consumable list plus weapon/armor slots, no crafting, no stat-sprawl gear tiers beyond the existing catalog tables
- Prefer discrete named regions and local maps before attempting seamless overworld simulation
- Do not add coast/ocean-style biomes as free-floating overworld picks without also defining a world-scale water continuity rule (edge orientation, neighboring water/land expectations, or a higher-level water mask)
- Avoid generic roguelite sprawl that does not deepen the expedition fantasy, such as large crafting trees, loot floods, or many enemy variants with only tiny gameplay differences

## Current Controls
- Move: `WASD`, arrows, `QEZC`, numpad diagonals
- Numpad actions: `5` melee, `0` autoexplore, `.` use/descend, `+` medkit, `-` tonic, `*` ranged, `/` world map
- Melee: `Space`
- Ranged: `F`
- Heal: `H`
- Cleanse: `G`
- Autoexplore: `X`
- World map: `M`
- Tuner: `T`
- Inventory: `I`
- Menu: `Esc`
- Descend stairs: `Enter` or `.`
- Click a seen tile to auto-path there
- Travel routes: `1`, `2`, `3`, or click a route card
- Controller movement: left stick or D-pad
- Controller actions: south button melee/interact, west button ranged, north button autoexplore, left shoulder medkit, right shoulder tonic
- Controller meta actions: back/view opens world map, start/menu opens pause menu, right-stick click opens tuner
- Touch: tap the map to move/interact, or use the on-screen action dock (`Atk`, `Shot`, `Auto`, `Use`, `Kit`, `Tonic`, `Map`, `Inv`, `Menu`)
- Inventory has no direct one-button controller shortcut yet (all controller face/shoulder/trigger buttons are already mapped); controller users can still reach it through the pause menu, then navigate items with stick or D-pad and confirm with the south face button

## Current Input Support
- Keyboard and mouse remain the primary authoring baseline, but controller and touch are now far enough along that menu/modal changes should be sanity-checked across all three surfaces
- Analog navigation is supported across the main menu, pause menu, world map, reward dialogs, tuner, controls modal, and death modal
- The controls modal now has scrollable `Keyboard/Mouse` and `Controller` tabs instead of one long static list
- If controller prompts change, keep the controls modal and `controller_button_labels()` in sync so Xbox, PlayStation, Nintendo, and generic naming stays coherent
- Touch support is intentionally first-pass: the important thing is that common flows work end-to-end, not that every desktop hover affordance has a touch equivalent yet

## Important Gameplay Rules
- Enemies only act while visible to the player
- Auto-move stops when a newly sighted point of interest appears
- For non-hostile important tiles, only the first sighting should matter; once already discovered, they should not keep interrupting auto-travel
- Full floor exploration now offers a choice reward modal (`Vitality`, `Power`, or `Recovery`)
- Bottom-floor delve clears use the same choice-modal pattern, with stronger delve-specific rewards
- Floor upgrades currently cycle through `light`, `vitality`, `power`, `haste`, and `reach`
- Combat is now multi-turn: player and enemies have health pools, damage values, and status effects
- Player tools now include `H` medkits and `G` tonics that grant temporary ward; both are `Item` instances in `game.inventory` (category `"consumable"`), not separate counters — `H`/`G` are shortcuts for `use_item("medkit")`/`use_item("tonic")`, and the full inventory (`I`) lists everything including unequipped gear
- Weapons and armor are `Item` instances too (category `"weapon"`/`"armor"`), bought from the provisioner's barter screen and equipped via the inventory overlay; `Game.effective_melee_damage`/`effective_ranged_damage`/`effective_defense` layer the equipped item's bonus on top of the base progression stats — combat code should read these, not the raw `melee_damage`/`ranged_damage` fields, or equipped gear silently does nothing
- `Game.WEAPON_CATALOG`/`ARMOR_CATALOG` are the source of truth for buyable gear stats; adding a new piece of gear is one dict entry plus nothing else, since `add_item`/`equip_item`/`use_item`/`inventory_rows` are all data-driven off `Item` fields rather than per-kind branches
- Floor loot now also exists as `GroundItem` wrappers around `Item` data. Rendering, inspect text, region snapshots, and save/load all expect `floor_items` to move together; if you add a new item pickup path, update both the current region snapshot and persistence serializers or the pickup will vanish on region transitions/save load
- The app boots to a main menu and supports multi-save menu actions backed by numbered files under `saves/`, with legacy `savegame.json` compatibility
- Runs now carry a persisted `world_seed`; setting `DEFAULT_WORLD_SEED` or `SHADOWCASTER_WORLD_SEED` should make world generation repeat exactly across new games and saves, while runtime-only randomness like dialogue choice can still vary
- Regions now have randomized type-appropriate names and a top banner label
- Delves are now entered through overworld landmarks instead of the old 3-choice destination picker
- Towns contain wandering friendly residents and animals; monster towns replace them with hostile inhabitants
- Town residents now have lightweight functional interactions: guides can reveal one local landmark, scouts can reveal one adjacent overworld region, and farmers can heal 1 HP once per town
- Biome-flavored settlement residents can now also offer small once-per-town boons: drovers spare ammo, millers pack a kit, ferrymen point out exits, masons grant ward, trappers share tonics, kilnkeepers blunt burn, and elders can point out hidden town addresses
- Town residents now also carry lightweight routine metadata such as `behavior`, `anchor`, `home_name`, and optional `patrol_points`; saves and region snapshots expect these to round-trip through `Resident` serialization
- Town resident rosters are now partly biome-driven in addition to size-driven. If you add new settlement biomes or roles, update `spawn_residents`, inspect text, and any one-shot resident boons together so the role feels coherent instead of decorative-only by accident
- Towns and service interiors now also use decor terrain markers such as paths, flowers, ponds, beds, crates, altars, forges, tables, shelves, pews, and anvils; if you add more, update both the inspect text and `rendering.py` marker drawing together
- Town maps now store richer `town_buildings` metadata for both enterable service sites and non-enterable flavor buildings. Service-building landmarks still come from this table, but non-service entries now matter too for inspect text and resident anchoring, so preserve them in map metadata when touching persistence
- Town decor is now doing more expressive settlement work too: civic markers like `fountain`, `brazier`, `stall`, `hitch_post`, and `notice_board` are generated through the same decor pipeline as paths/flowers/ponds. If you add more town-facing details, update generation, inspect text, and rendering marker support together
- Town buildings can now stamp exterior flavor decor near their doors based on both explicit building kind and name text. If you rename or add building labels in `generate_town`, sanity-check the exterior-decor mapping there so new labels still read sensibly from the street
- Town building metadata now also includes lightweight district labels such as `Town Center`, `Market Square`, `North Works`, or `West Homes`. If you change house assignment heuristics in `generate_town`, keep district naming and inspect output aligned so the clustering remains understandable to players
- First biome combat rules exist: desert boosts ranged pressure, swamp enemies poison, castle enemies are sturdier and deadlier, towns heal on arrival, monster towns inflict burn
- Terrain overlays now exist in some biomes: swamp muck, desert embers, mountain high ground, and town wells
- Overworld biome roster now also includes farmland, badlands, tundra, and volcanic; their current identity is still intentionally lightweight and mostly driven by layout, palette, terrain markers, and enemy mix
- Current special enemies include early archers and shamans in appropriate regions
- The early-game threat curve is intentionally softer now: first-floor overworld regions spawn fewer enemies, and shamans are delayed or nerfed compared with older builds
- Enemy variety now includes lighter biome-flavored variants such as pouncers, boglings, and sentinels in addition to stalkers, archers, shamans, and brutes
- Region danger is now persisted per region: overworld areas snapshot a hybrid of distance-from-origin and player strength on first discovery, and local delves inherit/escalate from their parent region instead of relying only on raw global floor
- Exploration progress should count only tiles reachable from the player start, and completion should use meaningful reachable frontier logic rather than raw "some visible tile exists somewhere" logic
- Connected region types can link at their edges into a persistent world grid; stairs still provide vertical/floor progression inside local delves
- The world map supports clicking discovered regions for stats, and should increasingly surface landmark/site progress
- Settlement size now also feeds into world-map presentation through simple skyline markers for towns and monster towns; if settlement-size tiers change, keep the map visualization and region-detail stats in sync
- The world map also has a local debug preview mode: it can show a radius of nearby generated neighbors around the current region, and previewed regions are cached so later actual entry reuses the same generated state
- Multi-level local delves award a bottom-floor cache and open a return portal back outside
- Town service interiors do not grant exploration rewards, even if fully explored
- Settlements now carry size/context metadata and parent-biome flavor; if you add new town-facing UI, prefer using the display-label helpers rather than recomputing names ad hoc
- Hover inspect should stay informational only for distant entities; actual resident/NPC interaction text belongs to adjacency/interact actions
- Gear is no longer town-only: deeper local delves and some higher-danger overworld regions can place unowned weapons or armor directly on the map, and duplicate non-consumable finds currently salvage into ammo instead of creating redundant inventory stacks

## Smoke-Testing Without a Display
Pygame needs a video driver even headless. Use this pattern for quick verification scripts (no test suite exists yet):
```python
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((100, 100))
import shadowcaster.game as gm
game = gm.Game()
game.start_new_game()
```
From there, set `game.config_world_seed = i`, then `game.start_new_game()` across many seed values to fuzz region generation, and check invariants like "every `game.edge_exits` value is in `game.floor_explorable_tiles`" or "every door tile is in `flood_reachable_tiles(region, plaza.center)`".

## Item Idea Backlog
Beyond the current upgrade-pickup cycle (`light`, `vitality`, `power`, `haste`, `reach`), candidate additions surfaced but not yet built:
- **Ward Potency** - increases tonic ward duration, or grants a passive recurring ward charge independent of tonic consumption
- **Resolve** - shortens the duration of enemy-inflicted status effects (poison/burn) on the player; strong in swamp or monster-town runs
- **Quartermaster** - raises max carried ammo or grants a small passive ammo trickle; pairs with ranged-heavy biomes such as desert or plains archers
- **Medkit Potency** - increases healing per medkit, stacking with the `medkit_heal` tuning value
- **Hushed Step** - shrinks the radius at which enemies notice the player, leaning into the "enemies only act while visible" rule for a stealth-flavored build path
Adding any of these means: extend the cycle in `create_upgrade_pickup`, add tuning keys and tuner schema entries, add a `draw_marker` shape, and add a claim branch in `collect_floor_items`.

## Future Conversation Hints
- If refactoring, keep `shadowcaster_game.py` as a stable wrapper if possible
- If adding new rewards, be careful about generosity and long-term power creep
- If adding new visuals, prioritize shape/marker readability in addition to color
- If expanding world content, prefer stronger region identity and landmark structure before large systemic sprawl
- If choosing between combat-heavy and world-heavy work, prefer features that strengthen route choice, landmarks, settlement growth, recurring residents, rumors, quests, and other expedition-facing hooks
- Future town work should use transition tiles or doors into dedicated interior maps rather than cramming interiors onto the outdoor map
- Next roadmap step under consideration: deepening town interactions beyond one-shot service rooms; generation-side groundwork now includes service rooms, door integrity, biome-aware settlement metadata, non-service building flavor, and simple resident routines/patrols
- Input work is now far enough along that regressions often show up in overlays first; if a modal changes, verify keyboard, mouse, controller, and touch all still have a viable path through it
