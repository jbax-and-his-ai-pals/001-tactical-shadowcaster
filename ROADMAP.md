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
| 3 | Build Identity | 🟡 Started | 20% |
| 3.5 | Expedition Systems | ⬜ Not started | 5% |
| 4 | Regional Pressure & Encounter Variety | 🟡 Started | 30% |
| 5 | Larger Social & World Structures | ⬜ Not started | 0% |

Overall: roughly **52% of planned work shipped**.  
Most complete: world exploration skeleton, settlement generation, combat basics, world-map UX, settlement attachment loop, purposeful world loop.  
Weakest: progression identity, expedition verbs, cross-town social threads, enemy variety.

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
- First place-based lead chains now exist on town notice boards: staged quests can send the player to a nearby region, require a site search or survey there, then route them back home for gold plus supplies
- Town attitude system exists: `town_attitude_label`, `town_attitude_score`, `town_prosperity_score`, and `town_service_bonus_tier` are computed from completed quest history per town coordinate, feeding into service quality and social tone

---

## Sequential Roadmap

### Phase 0 — Foundation Tightening ✅ 95% complete
**Goal:** Make the current game loop dependable and readable before adding broader content hooks.

**Why this phase first:** Every later system depends on stable map flow, understandable UI, and consistent world-state behavior.

**Estimated cost:** `S-M`

**Milestones:**
- [x] World-state stability pass (connectivity, door/exit guarantees, FOV, save corruption)
- [x] Controller, mouse, and touch support across all overlays
- [x] World-map UX (zoom, scroll, recenter, correct render order)
- [x] Death screen, main menu, multi-save shell
- [x] Journal, inventory, and inspect overlays coherent

**Remaining:** Minor UX polish and edge cases as they surface. No blocking work.

---

### Phase 1 — Purposeful World Loop 🔶 ~45% complete
**Goal:** Make exploration feel like following leads through a world, not just clearing disconnected maps.

**Why this phase:** Cheapest path to a stronger expedition identity and directly supports the core player fantasy.

**Estimated cost:** `M`

**Milestones:**
- [x] Surface landmark rewards (11 kinds, biome-specific pools, first-visit modal)
- [x] Notice board quest chains: staged delivery/scout chains with stage-based direction hints
- [x] World-map site-state display: marked/open/cleared progress, landmark summaries
- [x] **Landmark identity by kind on the world map** — distinct icons per site kind (waystone, barrow, grove, necropolis, camp, etc.)
- [x] **Survey/report payoff** — scout/bounty/delivery completions reveal adjacent map intel; waystone/oasis/barrow give follow-up leads
- [x] **Non-combat site rewards by biome** — biome flavor lines + danger-tier-scaled rewards for all 11 surface landmark kinds
- [x] **Quest direction clarity** — scout/bounty/delivery descriptions now include landmark-kind intel and danger-tier warnings
- [x] **Shortcut and hidden cache discoveries** — consumable stashes (medkit/tonic) seeded into overworld and shallow dungeon regions; distinctive discovery messages

**Exit criteria:**
- The player has concrete reasons to visit specific places besides combat and exits
- Towns, landmarks, and neighboring regions can point to one another in a way the player can follow

---

### Phase 2 — Settlement Attachment 🔶 ~35% complete
**Goal:** Turn towns from service stops into places the player remembers, helps, and revisits on purpose.

**Why this phase:** Once the world loop is purposeful, the next emotional hook is settlement attachment and visible consequence.

**Estimated cost:** `M-L`

**Milestones:**
- [x] Biome-flavored resident roster (herbalist, drover, fermyman, miller, mason, trapper, kilnkeeper, etc.)
- [x] Resident boons (once-per-town functional help: heals, cleansing, ward, ammo, medkit)
- [x] Town attitude system: score and bonus tier computed from per-town quest history
- [x] Building exteriors with biome-specific district structure
- [x] Interior variety: shrine, smith, cartographer (reveals neighbors)
- [x] **Town attitude feeding into service quality** — bonus tier improves inn heal, supply stock depth, chapel ward duration, etc.
- [x] **Deeper resident roles and authored concerns** — named residents with local region concerns and boon-referencing return dialogue
- [x] **More interior archetypes** — bathhouse (full restore), armory (ammo+tonic), apothecary (cleanse+potions)
- [x] **Town-growth response** — new residents appear in the square as attitude tier rises (vendor at tier 1, elder at tier 2)
- [x] **Recurring resident hooks** — return dialogue now prefers boon-referencing lines when a boon was given on a prior visit

**Exit criteria:**
- Returning to a settlement can feel different because of what the player did there
- Towns are remembered for more than one-shot utility rooms

---

### Phase 3 — Build Identity 🟡 ~20% complete
**Goal:** Give the player a lightweight but meaningful sense of who they are becoming.

**Why this phase:** Identity choices are most interesting once the world already offers multiple kinds of opportunities.

**Estimated cost:** `M`

**Milestones:**
- [x] Upgrade cycle (vitality, power, haste, reach, light) with distinct mechanical effects
- [x] Inventory and equipment layer (weapons, armor, provisioner barter)
- [x] Effective stat readout (effective_melee_damage, effective_ranged_damage, effective_defense)
- [x] **Lightweight progression tracks** — Scout, Delver, Warden, Hunter (or equivalent): 3-4 paths that make runs feel distinct
- [x] **Identity-aligned reward choices** — some delve/exploration rewards should lean into a path rather than always being generic
- [x] **Gear catalog expansion** — a few more weapon/armor options with clearer niches (reach weapon, light armor vs heavy, etc.)
- [x] **Loadout identity** — the equipped kit should meaningfully change play approach, not just tweak numbers

**Exit criteria:**
- Two runs can feel meaningfully different because the player leaned into different priorities
- Progression remains compact and readable rather than turning into stat soup

---

### Phase 3.5 — Expedition Systems ⬜ ~5% complete
**Goal:** Add a few tightly scoped non-combat systems that make the world feel more lived in and give towns practical needs.

**Why this phase here:** By this point the player should already care about places; now we can add light verbs that deepen those places without exploding complexity.

**Estimated cost:** `M-L`

**Milestones:**
- [x] Provisioner barter (lightweight trade using existing resources) — framework exists
- [x] **Gather/harvest loop** — farmland or low-danger region has a pickable resource; turn it in to a town for small reward
- [x] **Simple transformation layer** — cooking or packing provisions from gathered materials (very small input/output set)
- [x] **Cross-town social quests** — letters, relatives, favors, or rumor follow-ups that link residents across towns
- [x] **Survey and relief consequence tracking** — completions unlock map intel, supply depth, or goodwill in specific towns

**Exit criteria:**
- The player has at least a few meaningful things to do besides fight, loot, and descend
- Towns begin to feel connected to surrounding regions through practical needs and stories

---

### Phase 4 — Regional Pressure and Encounter Variety 🟡 ~30% complete
**Goal:** Make regions and dangerous sites feel more strategically distinct without drowning the game in enemy bloat.

**Why this phase here:** Once the player has better reasons to travel and better identity tools, encounter variety can sharpen those choices.

**Estimated cost:** `S-M`

**Milestones:**
- [x] Biome terrain effects (muck → poison, embers → burn, high ground, well heal)
- [x] Enemy roster: pouncer, boggling, sentinel, shaman, brute
- [x] Hybrid danger scaling by world distance + player strength at first entry
- [x] **2-3 new high-signal enemy archetypes** with clear tactical roles (e.g., blocker, ambusher, support)
- [x] **Stronger biome-combat interplay** — enemy type pools should vary more meaningfully by biome
- [x] **Risk/reward clarity** — regions should communicate expected danger vs. expected reward before entry

**Exit criteria:**
- Regions feel different because they ask different questions of the player
- Enemy variety adds decision-making, not just volume

---

### Phase 5 — Larger Social and World Structures ⬜ 0% complete
**Goal:** Push the world from a collection of good regions into a more convincing frontier with larger settlements and stronger continuity.

**Why this phase later:** More expensive; benefits from proven town, quest, and world-map patterns first.

**Estimated cost:** `L-XL`

**Milestones:**
- [ ] Larger cities with multi-tile footprints and district diversity
- [ ] More elaborate castle structures with courtyards and encounter identity
- [ ] Higher-level world continuity (rivers, regional relationships, coast logic)

**Exit criteria:**
- The world feels like a place with structure, not only a grid of interesting cells
- Large features justify their extra implementation cost through clearer player goals and memory

---

## Near-Term Queue
Ordered candidates for the next several slices:

1. ~~`XS` **[Phase 1]** Deepen per-kind landmark identity on the world map — distinct icons, clearer site-state display in right panel~~ ✓
2. ~~`M` **[Phase 1]** Expand place-based quest chains — stronger direction hints, better stage variety, bounty full-completion loop~~ ✓
3. ~~`S` **[Phase 1]** *(surface reward kinds landed)* Deepen non-combat landmark rewards: flavor text variety per biome, scaled rewards by danger tier, stronger follow-up leads~~ ✓
4. ~~`S-M` **[Phase 1/2]** Survey and relief completions materially affect map knowledge, town services, or later quest quality~~ ✓
5. ~~`S` **[Phase 2]** Town attitude bonus tier feeds visibly into service quality (inn heal, supply depth, board quality)~~ ✓
6. `M` **[Phase 2]** Deepen resident roles: named concerns, authored local context, recurring hooks
7. `M` **[Phase 2]** Add more building interior variety and dedicated local map pieces
8. `S-M` **[Phase 2]** Early town-growth response to completed local work
9. `S-M` **[Phase 3.5]** Gather-and-turn-in loop tied to farmland or low-danger overworld regions
10. `S` **[Phase 3.5]** Simple cooking/provisioning loop with tiny scope
11. `M` **[Phase 3.5]** Cross-town social threads and recurring resident connections
12. `M` **[Phase 3]** Lightweight player archetype progression (Scout, Delver, Warden, Hunter)
13. `S` **[Phase 3]** Expand gear/loadout identity and reward-economy items
14. `S-M` **[Phase 4]** 2-3 high-signal enemy archetypes with stronger biome interplay
15. `XS-S` **[ongoing]** Controller, touch, and accessibility polish alongside every phase

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
- Settlement visuals should scale with importance: small towns can stay one tile, while larger towns and cities should eventually occupy multiple overworld tiles with visible district and house-pattern variation
- Biome identity should deepen through three layers: palette/markers, traversal/combat behavior, and settlement/social flavor
- Favor "world expedition" features over generic roguelite bulk such as large crafting trees, loot floods, or huge enemy catalogs with tiny differences
- Narrow place-based systems are good; sprawling generic economy systems are not
- Survey, relief, and social follow-up work should pay off through clearer routes, better services, stronger town attitude, and more interesting opportunities rather than abstract "safety" stats
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
