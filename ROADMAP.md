# ROADMAP

## Roadmap Format
- `XS`: 0.5-1 session, low risk, mostly additive polish
- `S`: 1-2 sessions, focused feature slice, low-to-moderate risk
- `M`: 3-5 sessions, multiple touch points, moderate risk
- `L`: 1-2 weeks of intermittent work, broad integration risk
- `XL`: major initiative; should be split before implementation

## Current Focus
- Stabilize the current world-region loop and tighten UX polish
- Make overworld exploration feel more purposeful through landmarks and map feedback
- Turn towns into a more expressive non-combat hub through interiors, services, and biome-specific identity
- Keep progression readable, rewarding, and resistant to power creep
- Bias the overworld toward safer biomes near the origin and let harsher regions become more common farther out

## Player Fantasy
- The game should feel like a world-expedition roguelite, not just a floor-clearing dungeon crawler
- The player fantasy is: discover a place, understand what makes it interesting, decide whether it is worth the risk, return with something meaningful, and see the world respond
- The strongest long-term hook is not raw combat escalation; it is exploration, route choice, light character identity, and visible settlement/world impact

## Player Fun Pillars
- Exploration should reward curiosity with rumors, landmarks, shortcuts, hidden caches, and distinct regional stories instead of only exits and enemies
- Route choice should matter: the player should often choose between pushing deeper, detouring to a town, chasing a rumor, scouting a risky landmark, or returning to cash in progress
- Character growth should create identity rather than stat clutter; small specialization paths should change how the player approaches regions
- Settlements should become places the player cares about through recurring residents, better services, town growth, and consequences from completed work
- Non-combat discoveries should be exciting in their own right so the world does not feel like filler between fights

## Implemented
- BSP dungeon generation
- Region framework with random named region types
- Early non-dungeon generation for forest and ruins regions
- Settlement generation for town and monster-town regions
- Expanded region roster: desert, mountain, swamp, plains, farmland, badlands, tundra, volcanic, castle, cave, maze
- Lightweight world-travel layer with named route choices between regions
- Persistent world-grid connections between overworld biome regions
- Overworld biome selection now ramps from safer regions near `(0, 0)` toward harsher biomes as world distance increases
- Recursive shadowcasting FOV
- Grid movement with direct diagonal traversal
- Held movement and click-to-move on seen tiles
- Scrolling camera and multi-screen floors
- Melee and ranged combat with auto-targeting
- A* enemy pursuit gated by player visibility
- Multi-turn combat with scaled health, damage, and basic status effects
- Consumable recovery tools, ranged enemy archetypes, and first terrain-driven biome effects
- Multiple enemies and brute variant
- Early-region difficulty pass: starting HP increased, first-floor overworlds spawn fewer enemies, shamans arrive later and hit softer, and the enemy roster now includes pouncers, boglings, and sentinels
- Hybrid regional danger scaling: overworld regions now snapshot a danger baseline from world distance plus first-entry player strength, while local regions inherit and deepen that danger from their parent site
- Upgrade pickup cycle: light, vitality, power, haste, and reach
- 100% exploration reward modal
- Delve-clearing reward is now a choice modal (Vitality/Power/Recovery) reusing the 100%-exploration UI, generalized behind `has_pending_reward()`, `current_reward_options()`, and `apply_reward_choice()`
- Exploration completion now resolves "visible but effectively unreachable" frontier edge cases instead of relying only on raw seen-tile counts
- World-map inspection for discovered regions
- World map now also has a local debug preview mode for the current region and nearby generated neighbors
- World-map region detail now tracks notable-site state more clearly, including marked/open/cleared site progress, richer landmark summaries, and stronger route-choice hints
- Landmark-based local regions embedded into overworld maps
- Bottom-floor reward cache plus return portal for multilevel delves
- Main menu plus multi-save/load shell
- Global world seed support for deterministic new runs, previews, and saved-world regeneration
- Death modal with stat tabs and mouse support
- Controller support now includes analog-stick movement plus analog navigation across menus, reward dialogs, the world map, the tuner, and the death screen
- Controls UI now uses dedicated `Keyboard/Mouse` and `Controller` tabs with scrolling support for longer help content
- First-pass touch support now exists for gameplay taps, on-screen action buttons, and modal/menu interactions
- Region-specific terrain palettes and clearer actor silhouettes
- First town building interiors with lightweight service rooms
- Expanded town interior variety with shrine, smith, and cartographer buildings
- Cartographer town interior reveals neighboring overworld regions
- Contextual resident interaction through inspect and bump-to-talk messages
- Town residents now provide lightweight functional help: guides can mark one local site, scouts can reveal one nearby route, and farmers can share a small heal
- Town provisioners can now offer lightweight barter using existing resources
- Settlements now carry biome-aware size/context metadata, clearer display labels, and parent-biome-informed palette treatment
- Towns and service interiors now carry more authored environmental detail through roads, ponds, flowers, and room-specific decor markers
- World-map site-mix details for clearer notable-site identity
- Stability pass: guaranteed region edge-exit/door connectivity for all region types, fixed bottom-floor terminus FOV visibility, deduplicated combat/interest-tile logic, graceful corrupted-save handling
- Lightweight inventory and equipment layer: medkits and tonics are now `Item` entries instead of bare counters, plus purchasable weapons (melee/ranged bonus) and armor (flat damage reduction) bought from the provisioner and equipped via a new `I` inventory overlay; status panel shows equipped weapon/armor and effective attack
- Inventory is now starting to feed back into the world loop: deeper delves and some harsher overworld regions can spawn gear pickups directly on the floor, and the pause menu now exposes inventory for controller-first play
- Settlements now have richer per-building metadata even for non-enterable structures, letting towns carry homes, work buildings, and civic spaces in addition to service interiors
- Town residents now use lightweight behavior routines such as stationary posts, plaza loops, homebound wandering, and simple path patrols, with inspect text surfacing where they belong and how they move
- The world map now shows simple skyline-style markers for towns and monster towns, scaled by settlement size so larger settlements read more clearly at a glance
- Larger settlements now also field a broader social cast, with biome-flavored locals such as herbalists, drovers, ferrymen, millers, masons, trappers, and kilnkeepers alongside civic roles like watchers, vendors, and elders
- Several of those biome-flavored locals now also provide lightweight once-per-town help, such as spare supplies, route guidance, cleansing, or short warding buffs, so settlement roles matter in play instead of reading as pure scenery
- Town squares and streets now carry lightweight civic decor such as fountains, braziers, notice boards, stalls, and hitching posts, with placement influenced by biome and settlement size
- Individual town buildings now also project small exterior signatures into nearby streets, so barns, stores, shrines, clinics, forges, and halls read more distinctly from the outside
- Town buildings are now loosely clustered into district-like bands such as town center, market square, works, and homes, giving larger settlements more legible internal structure
- World map UX tightened: recenter button, right-panel scroll, chip vertical centering, wheel zoom (18% per step from center), prominent selected-region border drawn above preview tiles, three-pass render for correct depth order, local debug map preserves mode/pan/expanded state across close/reopen, click vs drag correctly disambiguated for all tile types
- Overworld landmark variety expanded: 11 surface-modal site kinds (waystone, barrow, stone_circle, oasis, hot_spring, watchtower, grove, necropolis, geyser, standing_stone, camp) now generate alongside the 6 enterable kinds, with biome-specific pools; surface sites fire a reward modal on first visit without entering a local region, tracked in `claimed_surface_landmark_keys`

## Sequential Roadmap
### Phase 0 - Foundation Tightening
Goal:
Make the current game loop dependable and readable before adding broader content hooks.

Why this phase first:
Every later system depends on stable map flow, understandable UI, and consistent world-state behavior.

Estimated cost:
`S-M`

Status:
`In progress`

Primary deliverables:
- Continue UX polish across keyboard, mouse, controller, and touch
- Keep world-map, journal, inspect, and settlement presentation coherent
- Tighten remaining world-state, rendering, and generation edge cases

Exit criteria:
- The player can reliably explore, fight, inspect, travel, save/load, and understand what happened
- Landmark and town presentation is readable enough to support more authored content

### Phase 1 - Purposeful World Loop
Goal:
Make exploration feel like following leads through a world, not just clearing disconnected maps.

Why this phase first:
This is the cheapest path to a stronger identity and directly supports the expedition fantasy.

Estimated cost:
`M`

Primary deliverables:
- Small place-based quest chains connecting towns, landmarks, and nearby regions
- Better landmark identity by biome
- Better world-map and journal progress for notable sites
- Optional non-combat discoveries such as surveys, caches, shrine boons, shortcuts, and special finds

Suggested sequence:
1. Expand landmark metadata and world-map progress display
2. Add first multi-step place-based quest chain templates
3. Add non-combat site rewards that feed future route choice

Exit criteria:
- The player has concrete reasons to visit specific places besides combat and exits
- Towns, landmarks, and neighboring regions can point to one another in a way the player can follow

### Phase 2 - Settlement Attachment
Goal:
Turn towns from service stops into places the player remembers, helps, and revisits on purpose.

Why this phase second:
Once the world loop is purposeful, the next big emotional hook is settlement attachment and visible consequence.

Estimated cost:
`M-L`

Primary deliverables:
- Stronger resident roles, named local concerns, and recurring social hooks
- More building interior variety and dedicated local map pieces
- Town and city representation upgrades on the overworld/world map
- Early town-growth or town-state response to player help

Suggested sequence:
1. Deepen resident roles, homes, and authored points of interest
2. Add a few more interior archetypes with clearer local flavor
3. Let completed local work improve stock, safety, staffing, or available leads

Exit criteria:
- Returning to a settlement can feel different because of what the player did there
- Towns are remembered for more than one-shot utility rooms

### Phase 3 - Build Identity
Goal:
Give the player a lightweight but meaningful sense of who they are becoming.

Why this phase third:
Identity choices are most interesting once the world already offers multiple kinds of opportunities.

Estimated cost:
`M`

Primary deliverables:
- Lightweight archetype/progression tracks such as Scout, Delver, Warden, and Hunter
- Upgrade, gear, and reward choices that support information, mobility, survival, and route control as much as raw damage
- Cleaner weapon/loadout identity and a slightly broader gear catalog

Suggested sequence:
1. Define 3-4 small progression identities
2. Reframe some existing reward/upgrade choices to reinforce those identities
3. Add a few gear pieces and reward-economy items that deepen choice without adding clutter

Exit criteria:
- Two runs can feel meaningfully different because the player leaned into different priorities
- Progression remains compact and readable rather than turning into stat soup

### Phase 4 - Regional Pressure and Encounter Variety
Goal:
Make regions and dangerous sites feel more strategically distinct without drowning the game in enemy bloat.

Why this phase here:
Once the player has better reasons to travel and better identity tools, encounter variety can sharpen those choices.

Estimated cost:
`S-M`

Primary deliverables:
- A small set of new enemy archetypes with clear roles
- Stronger biome-combat interplay
- More interesting risk/reward contrast between safe routes, harsh regions, and optional danger sites

Suggested sequence:
1. Add only a few high-signal enemy roles
2. Tie them to biome behavior, not just biome color
3. Rebalance regional pressure around player identity choices

Exit criteria:
- Regions feel different because they ask different questions of the player
- Enemy variety adds decision-making, not just volume

### Phase 5 - Larger Social and World Structures
Goal:
Push the world from a collection of good regions into a more convincing frontier with larger settlements and stronger continuity.

Why this phase later:
This work is more expensive and benefits from proven town, quest, and world-map patterns first.

Estimated cost:
`L-XL`

Primary deliverables:
- Larger cities and more legible settlement scale
- More elaborate castle and landmark structures
- Higher-level world continuity systems such as rivers and other regional relationships

Exit criteria:
- The world feels like a place with structure, not only a grid of interesting cells
- Large features justify their extra implementation cost through clearer player goals and memory

## Near-Term Queue
Ordered candidates for the next several slices:

1. `XS` *(in progress)* Deepen per-kind landmark identity on the world map (distinct icons, clearer site-state display in the right panel)
2. `M` Add small place-based quest chains
3. `S` *(partially done — surface reward kinds landed)* Deepen non-combat landmark rewards: flavor text variety per biome, scaled rewards by danger tier
4. `M` Deepen resident roles, homes, and recurring town hooks
5. `M` Add more building interior variety and dedicated local map pieces
6. `S-M` Add early town-growth responses to completed local work
7. `M` Define lightweight player archetype progression
8. `S` Expand gear/loadout identity and reward-economy items
9. `S-M` Add a few high-signal enemy archetypes with stronger biome interplay
10. `XS-S` Continue controller, touch, and accessibility polish alongside every phase

## Design Notes
- Keep systems small and composable rather than sprawling
- Exploration should feel rewarding but not mandatory overpowered
- Visibility, movement, and positioning are the game's identity
- Special tiles should be distinguishable by both color and shape
- Ask of each new feature: "Does this give the player a better reason to care where they go next?"
- Grow outward through connected region archetypes before attempting a seamless world
- Towns should eventually support ZZT-like building transitions into interior maps
- Prefer world-structure improvements that make regions memorable over adding lots of one-off mechanics
- Larger regions are likely viable in moderation, but they should probably arrive alongside render/path/FOV profiling instead of as a blanket size increase everywhere
- Settlement visuals should scale with importance: small towns can stay one tile, while larger towns and cities should eventually occupy multiple overworld tiles with visible district and house-pattern variation
- Biome identity should deepen through three layers: palette/markers, traversal/combat behavior, and settlement/social flavor
- Favor "world expedition" features over generic roguelite bulk such as crafting trees, loot floods, or huge enemy catalogs with tiny differences
- The current cheapest high-value world-loop work is still site-driven: landmarks should tell the player what kind of opportunity remains there before we add larger social/economy systems
- A reusable engine/content split makes sense eventually, but only after more fantasy systems are proven; the likely seam is engine systems underneath data-driven biome/theme content packs
- When coasts, rivers, and larger water systems arrive, biome placement should stop being fully independent: coast orientation, river flow, and adjacent-region continuity should come from a higher-level world layout rather than per-region randomness
- Input support is now multi-surface (keyboard/mouse, controller, touch), so UX changes should be checked across all active overlays rather than assuming keyboard-only focus

## Much Later
- Experiment with a giant seamless overworld driven by a stable world seed and coordinate-based procedural generation, potentially extending infinitely without hard exit-to-exit region transitions
- Explore multi-region rivers with sources and mouths that persist across the world map and influence nearby terrain and settlement layout
- Add coastlines only after there is a world-scale water model capable of expressing which side of a region borders sea or lake, so we avoid nonsense continuity like inland-facing coasts against dry plains
- Build large city generation with multi-tile settlement footprints, district diversity, biome-specific architecture, and variable fauna/NPC mixes
- Expand castles into more elaborate authored-feeling structures with courtyards, wings, service spaces, and stronger encounter identity
- Add overworld landmark scale language so towns, cities, castles, and delves communicate size and importance directly from the map
- Explore a theme-pack architecture that could support alternate content skins such as a modern setting with offices, modern equipment, firearms, and contemporary NPC behaviors
