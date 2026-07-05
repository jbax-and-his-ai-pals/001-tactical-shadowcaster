# ROADMAP

## Roadmap Format
- `XS`: 0.5-1 session, low risk, mostly additive polish
- `S`: 1-2 sessions, focused feature slice, low-to-moderate risk
- `M`: 3-5 sessions, multiple touch points, moderate risk
- `L`: 1-2 weeks of intermittent work, broad integration risk
- `XL`: major initiative; should be split before implementation

---

## Progress at a Glance

| Phase | Name | Status | ~Done |
|-------|------|--------|-------|
| 0 | Foundation Tightening | ✅ Complete | 95% |
| 1 | Purposeful World Loop | ✅ Complete | 95% |
| 2 | Settlement Attachment | ✅ Complete | 95% |
| 3 | Build Identity | ✅ Complete | 95% |
| 3.5 | Expedition Systems | ✅ Complete | 95% |
| 4 | Regional Pressure & Encounter Variety | ✅ Complete | 95% |
| 5 | Larger Social & World Structures | ✅ Complete | 95% |

Overall: roughly **90% of planned work shipped**.  
Most complete: world exploration, settlement generation, combat, world-map UX, settlement attachment, purposeful world loop, archetype tracks, gather/harvest, social quests, enemy variety, world geography (rivers, coast, zones, cities).  
Remaining frontier: accessibility polish (ongoing), overworld landmark scale language, and the "Much Later" large-scope experiments.

---

## Current Focus
- Stabilize the current world-region loop and tighten UX polish
- Make overworld exploration feel more purposeful through landmarks and map feedback
- Turn towns into a more expressive non-combat hub through interiors, services, and biome-specific identity
- Grow the player's meaningful verbs through place-based activities such as survey, delivery, recovery, gathering, and light transformation
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

## Content Strategy
- Scale the game through authored content atoms plus procedural composition, not through endless generic random variation
- Favor reusable templates with strong identity: landmark families, town concerns, resident archetypes, quest situations, and biome motifs
- Let places gain meaning through persistence: remembered discoveries, local consequences, recurring residents, and visible changes in service quality or opportunities
- Expand player expression by adding verbs before adding bulk: observe, gather, deliver, restore, transform, choose, and report
- Keep each new system narrow and world-facing; if it does not make a place more memorable or a decision more interesting, it is probably not worth the cost

## Implemented
- BSP dungeon generation
- Region framework with random named region types
- Expanded region roster: desert, mountain, swamp, plains, farmland, badlands, tundra, volcanic, castle, cave, maze, large_town
- Lightweight world-travel layer with named route choices between regions
- Persistent world-grid connections between overworld biome regions
- Overworld biome selection ramps from safer regions near `(0, 0)` toward harsher biomes as world distance increases
- Biome adjacency coherence: neighbors influence each other's selection weights so forests cluster with swamps/plains, deserts with badlands/volcanic, tundra with mountain
- River system: 1-2 seeded river paths per world; visible as blue bands on the world map; bias swamp/farmland/forest near their route
- Coast system: seeded sea direction and threshold per world; ocean coords block travel with flavor message; coastal biome weight bonuses
- Named world zones: 2-3 seeded geographic zones per world ("the Mire," "the High Pass," etc.) with dim labels on the world map
- Named city: one seeded multi-tile city per world with hub (large_town) and up to 3 district coords (market, civic, temple); gold-bordered on world map
- Castle multi-zone layouts: 4 corner towers, throne hall, garrison barracks, armory, north watchtower, south gatehouse, wide courtyard corridors, battlement openings
- Recursive shadowcasting FOV
- Grid movement with direct diagonal traversal; held movement and click-to-move on seen tiles
- Scrolling camera and multi-screen floors
- Melee and ranged combat with auto-targeting; A* enemy pursuit gated by player visibility
- Multi-turn combat with scaled health, damage, and basic status effects
- Enemy roster: pouncer, boggling, sentinel, shaman, brute, plus 2-3 high-signal archetypes with biome-specific pools
- Biome terrain effects (muck → poison, embers → burn, high ground, well heal)
- Hybrid regional danger scaling: world distance + first-entry player strength baseline
- Upgrade pickup cycle: light, vitality, power, haste, reach
- Lightweight archetype progression tracks: Scout, Delver, Warden, Hunter
- Inventory and equipment layer: weapons, armor, medkits, tonics; purchasable from provisioner, floor drops in deeper regions; `I` overlay; effective stat readout
- Gear catalog: reach weapons, light vs heavy armor, identity-aligned reward choices
- 100% exploration reward modal; delve-clearing reward choice (Vitality/Power/Recovery)
- Bottom-floor reward cache plus return portal for multilevel delves
- Overworld landmark variety: 11 surface-modal site kinds + 6 enterable kinds, biome-specific pools, first-visit reward modal
- World-map region detail: marked/open/cleared progress, landmark summaries, route-choice hints, risk/reward clarity
- Notice board quest chains: staged delivery/scout/bounty chains with direction hints and full-completion loops
- Survey/report payoff: completions reveal adjacent map intel, supply depth, or goodwill
- Cross-town social quests: letters, relatives, favors, and rumor follow-ups that link residents across towns
- Gather/harvest loop: farmland resource pick and town turn-in; simple cooking/transformation layer
- Town attitude system: score and bonus tier from quest history, feeding into service quality and social tone
- Biome-flavored resident roster: herbalists, drovers, ferrymen, millers, masons, trappers, kilnkeepers, watchers, vendors, elders
- Resident boons: once-per-town functional help (heals, cleansing, ward, ammo, medkit)
- Resident behavior routines: stationary posts, plaza loops, homebound wandering, path patrols
- Recurring resident hooks: return dialogue prefers boon-referencing lines after prior visit
- Town building interiors: inn, shrine, smith, cartographer, bathhouse, armory, apothecary
- Cartographer reveals neighboring overworld regions; town-growth response adds residents as attitude rises
- Town district clustering: town center, market square, works, homes; exterior building signatures in streets
- Civic decor: fountains, braziers, notice boards, stalls, hitching posts; biome and size influenced
- World map UX: recenter, right-panel scroll, wheel zoom, correct render order, click vs drag disambiguated, local debug mode
- World map controller support: D-pad and analog stick navigate selection; X/Y scroll detail panel; LB/RB switch mode
- Touch support: gameplay taps, on-screen action buttons, modal/menu/notice-board interactions
- Controller support: analog-stick movement, menus, reward dialogs, world map, tuner, death screen
- Controls UI: Keyboard/Mouse and Controller tabs with scrolling help content
- Main menu, multi-save/load shell, global world seed, death modal with stat tabs

---

## Sequential Roadmap

### Phase 0 — Foundation Tightening ✅ ~95% complete
**Goal:** Make the current game loop dependable and readable before adding broader content hooks.

**Milestones:**
- [x] World-state stability pass (connectivity, door/exit guarantees, FOV, save corruption)
- [x] Controller, mouse, and touch support across all overlays
- [x] World-map UX (zoom, scroll, recenter, correct render order)
- [x] Death screen, main menu, multi-save shell
- [x] Journal, inventory, and inspect overlays coherent

**Remaining:** Minor UX polish and edge cases as they surface.

---

### Phase 1 — Purposeful World Loop ✅ ~95% complete
**Goal:** Make exploration feel like following leads through a world, not just clearing disconnected maps.

**Milestones:**
- [x] Surface landmark rewards (11 kinds, biome-specific pools, first-visit modal)
- [x] Notice board quest chains: staged delivery/scout chains with stage-based direction hints
- [x] World-map site-state display: marked/open/cleared progress, landmark summaries
- [x] **Landmark identity by kind on the world map** — distinct icons per site kind
- [x] **Survey/report payoff** — scout/bounty/delivery completions reveal adjacent map intel
- [x] **Non-combat site rewards by biome** — biome flavor lines + danger-tier-scaled rewards
- [x] **Quest direction clarity** — descriptions include landmark-kind intel and danger-tier warnings
- [x] **Hidden cache discoveries** — consumable stashes seeded into overworld and shallow dungeon regions

---

### Phase 2 — Settlement Attachment ✅ ~95% complete
**Goal:** Turn towns from service stops into places the player remembers, helps, and revisits on purpose.

**Milestones:**
- [x] Biome-flavored resident roster (herbalist, drover, ferryman, miller, mason, trapper, kilnkeeper, etc.)
- [x] Resident boons (once-per-town functional help: heals, cleansing, ward, ammo, medkit)
- [x] Town attitude system: score and bonus tier computed from per-town quest history
- [x] Building exteriors with biome-specific district structure
- [x] Interior variety: shrine, smith, cartographer (reveals neighbors)
- [x] **Town attitude feeding into service quality** — bonus tier improves inn heal, supply stock depth, chapel ward duration, etc.
- [x] **Deeper resident roles and authored concerns** — named residents with local region concerns and boon-referencing return dialogue
- [x] **More interior archetypes** — bathhouse (full restore), armory (ammo+tonic), apothecary (cleanse+potions)
- [x] **Town-growth response** — new residents appear in the square as attitude tier rises
- [x] **Recurring resident hooks** — return dialogue prefers boon-referencing lines after a boon was given

---

### Phase 3 — Build Identity ✅ ~95% complete
**Goal:** Give the player a lightweight but meaningful sense of who they are becoming.

**Milestones:**
- [x] Upgrade cycle (vitality, power, haste, reach, light) with distinct mechanical effects
- [x] Inventory and equipment layer (weapons, armor, provisioner barter)
- [x] Effective stat readout (effective_melee_damage, effective_ranged_damage, effective_defense)
- [x] **Lightweight progression tracks** — Scout, Delver, Warden, Hunter: paths that make runs feel distinct
- [x] **Identity-aligned reward choices** — some delve/exploration rewards lean into a path
- [x] **Gear catalog expansion** — reach weapon, light armor vs heavy, clearer niches
- [x] **Loadout identity** — equipped kit meaningfully changes play approach

---

### Phase 3.5 — Expedition Systems ✅ ~95% complete
**Goal:** Add tightly scoped non-combat systems that make the world feel more lived in.

**Milestones:**
- [x] Provisioner barter (lightweight trade using existing resources)
- [x] **Gather/harvest loop** — farmland resource pick; turn in to a town for small reward
- [x] **Simple transformation layer** — cooking or packing provisions from gathered materials
- [x] **Cross-town social quests** — letters, relatives, favors, rumor follow-ups linking residents across towns
- [x] **Survey and relief consequence tracking** — completions unlock map intel, supply depth, or goodwill

---

### Phase 4 — Regional Pressure and Encounter Variety ✅ ~95% complete
**Goal:** Make regions and dangerous sites feel more strategically distinct.

**Milestones:**
- [x] Biome terrain effects (muck → poison, embers → burn, high ground, well heal)
- [x] Enemy roster: pouncer, boggling, sentinel, shaman, brute
- [x] Hybrid danger scaling by world distance + player strength at first entry
- [x] **2-3 new high-signal enemy archetypes** with clear tactical roles (blocker, ambusher, support)
- [x] **Stronger biome-combat interplay** — enemy type pools vary more meaningfully by biome
- [x] **Risk/reward clarity** — regions communicate expected danger vs. expected reward before entry

---

### Phase 5 — Larger Social and World Structures ✅ ~95% complete
**Goal:** Push the world from a collection of good regions into a more convincing frontier with larger settlements and stronger continuity.

**Milestones:**
- [x] **Larger cities with multi-tile footprints and district diversity** — one named city per world (`world_city`) with hub coord (large_town) and up to 3 district coords (market, civic, temple quarters); gold border on world map; city name label above hub tile
- [x] **More elaborate castle structures with courtyards and encounter identity** — corner towers, throne hall, garrison barracks, armory wing, north watchtower, south gatehouse, battlement breaches, wide courtyard corridors
- [x] **Biome adjacency coherence** — `overworld_region_weight` multiplies by affinity factors from known neighbors
- [x] **River paths** — 1-2 seeded river paths per world; blue water band on world map; biome weight bonuses for swamp/farmland/forest
- [x] **Named world zones** — 2-3 seeded geographic zones per world with dim labels on the world map anchor tile
- [x] **Coast logic** — seeded sea direction and threshold; ocean coords block travel; coastal panel notes and biome bonuses

**Exit criteria met:** The world has geographic structure (zones, rivers, coast, city) that gives the player routes and named places to remember, not just a grid of interesting cells.

---

## Near-Term Queue
All 14 planned queue items shipped. Item 15 is ongoing:

15. `XS-S` **[ongoing]** Controller, touch, and accessibility polish alongside every phase
    - ✓ D-pad world map navigation (step selection, matching analog stick)
    - ✓ Touch notice-board interaction
    - ✓ Controller world map detail-panel scroll (X/Y buttons)
    - Remaining: audit new overlays as they arrive; watch for regressions on touch

---

## Next Candidates
These are the most impactful remaining slices, roughly ordered by value/cost:

1. `XS-S` **Overworld landmark scale language** — towns, cities, castles, and delves should communicate size and importance directly from the world map (icon size variation, a city crown glyph, castle battlements marker, etc.) without requiring the player to open the detail panel
2. `S` **Biome identity deepening — third layer** — settlement/social flavor per biome is thinner than palette/markers and traversal/combat; add 2-3 biome-specific interior archetypes or resident concerns that only appear in matching biomes
3. `S` **World map accessibility pass** — keyboard-navigable detail panel (Tab to focus, arrow keys through entries), screen-reader-friendly region name announcements, and colorblind-friendlier tile palette options
4. `XS` **Stale ROADMAP housekeeping** — "Much Later" items that have now shipped (cities, castles, rivers, coast) should be moved to Implemented or removed

---

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
- Biome identity should deepen through three layers: palette/markers, traversal/combat behavior, and settlement/social flavor
- Favor "world expedition" features over generic roguelite bulk such as large crafting trees, loot floods, or huge enemy catalogs with tiny differences
- Narrow place-based systems are good; sprawling generic economy systems are not
- Survey, relief, and social follow-up work should pay off through clearer routes, better services, stronger town attitude, and more interesting opportunities rather than abstract "safety" stats
- Input support is now multi-surface (keyboard/mouse, controller, touch), so UX changes should be checked across all active overlays rather than assuming keyboard-only focus
- Settlement visuals should scale with importance: small towns can stay one tile, while larger towns and cities should eventually occupy multiple overworld tiles with visible district and house-pattern variation

## Much Later
- Experiment with a giant seamless overworld driven by a stable world seed and coordinate-based procedural generation, potentially extending infinitely without hard exit-to-exit region transitions
- Add overworld landmark scale language at the full-detail level: authored tile art, animated beacons, or layered glyph overlays that convey settlement size and site importance without needing the detail panel
- Explore a theme-pack architecture that could support alternate content skins such as a modern setting with offices, modern equipment, firearms, and contemporary NPC behaviors
- Expand multi-region water systems: river sources and mouths that persist across the world map with influence on nearby terrain and settlement layout; lake regions; flood-plain farmland bonuses
