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
| 6 | Economy, Items, and Combat Depth | 🔄 Mostly Complete | ~90% |
| 7 | Leveling, Persistence, and Universal Rarity | ✅ Complete | ~95% |
| 8 | Living World — Towns, Threats, and Growth | 🔲 Planned | 0% |

Overall: roughly **92% of total planned work shipped** (Phases 0-7 complete or near-complete).  
Most complete: world exploration, settlement generation, combat, world-map UX, settlement attachment, world loop, archetype tracks, gather/harvest, social quests, world geography, trade system, composable item effects, enemy catalog (81 types), leveling (L1–L5 with ability system), legendary site gating, city stronghold, persistent world and death system, universal rarity model.  
Remaining frontier: controller/touch audit on new overlays, ability shown in journal overlay, long-term enemy catalog toward 100+ types, Phase 8 (living world).

---

## Current Focus
- Phase 8: Living World — Towns, Threats, and Growth (planned, not yet started)
- Long-term: enemy catalog toward 100+ types

## Player Fantasy
- The game is a **persistent world expedition**, not a roguelite — the world, map discoveries, quests, towns, and character all persist between sessions
- The player fantasy is: discover a place, understand what makes it interesting, decide whether it is worth the risk, return with something meaningful, and see the world respond
- The strongest long-term hook is not raw combat escalation; it is exploration, route choice, light character identity, and visible settlement/world impact
- A dedicated player might spend several hours per level — each level should feel genuinely earned and widen the space of what they can do and face
- Rarity is a first-class design principle: the player should encounter things they have never seen before across dozens of hours of play

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
- Two-column trade overlay: seeded trader gold pool, buy/sell with price display, attitude-scaled stock depth
- Composable item effect system: Potions, Tonics, Tinctures with rarity tiers; Common/Uncommon/Rare/Legendary; never-sold invariant enforced
- 81 data-driven enemies across all biomes: behaviors (pursuer, kiter, charger, tank, flanker, ambusher), traits (pack_bonus, regen, berserks, calls_reinforcements, shields_ally, reflects_damage), named elites gated at Level 2
- Leveling system (L1–L4 active): XP from first-time discoveries, quest milestones, world-distance milestones; level-up modal per level; unlock text
- Level 2: trinket equip slot (equippable accessories with stat bonuses); named elite enemies enter spawn pools
- Level 3: NPCs address player by title at all attitude tiers; Beloved towns at L3+ post a second priority quest; reward bonus +15g
- Level 4: ability selection modal at level-up; 6-ability pool (Bloodthirst, Bulwark, Tactician, Scavenger, Ranger, Iron Nerve); passive effects wired into combat and exploration
- Persistent death system: respawn at shrine/homepoint/origin; carried gold lost; region enemies reset; all other world state preserved
- Universal rarity model: rarity field on enemies, NPCs, items, region types; Ossuary and Mirrorwood as legendary region types (distance-gated, low weight); wandering merchants and lorekeepers seeded once per world

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
Polish and accessibility items that don't require new systems:

1. `XS-S` **Overworld landmark scale language** — towns, cities, castles, and delves should communicate size and importance directly from the world map without requiring the player to open the detail panel
2. `S` **Biome identity deepening — third layer** — settlement/social flavor per biome; add 2-3 biome-specific interior archetypes or resident concerns that only appear in matching biomes
3. `S` **World map accessibility pass** — keyboard-navigable detail panel, colorblind-friendlier tile palette options

---

### Phase 6 — Economy, Items, and Combat Depth `L-XL`

**Goal:** Replace the thin ammo-only economy with a richer, layered system; give items genuine identity through a composable effect model; and dramatically expand enemy variety so the player routinely encounters unfamiliar threats.

**Why this phase now:** Phases 1-5 proved the world loop and social systems. The player now has reasons to travel, towns to care about, and a track identity. The next friction point is that the item landscape is too flat (medkits and tonics are interchangeable utilities), the trade screen is too simple to be interesting, and enemies run out of surprises too quickly.

---

#### 6A — Trade System Overhaul `S`

**Current state:** Provisioner offers a fixed menu of ammo-denominated barters. No player agency over what they sell or what the trader stocks.

**Target:** A two-column trade screen — player inventory on the left, trader inventory on the right. The trader has a named gold pool (fixed per visit, seeded by town and attitude tier). Items move between sides; prices are shown in gold. The player can buy from the trader or sell from their own inventory.

**Currency:** Gold is the single currency for all trade. Ammo has a gold value and can be bought or sold at the trader like any other item — it has no special status as currency. Everything is priced in gold; everything can be sold for gold.

**Trader inventory:** Seeded per town visit. Common items always available; stock depth and uncommon item availability scale with supply depth and attitude tier. Rare and legendary items are never sold — only found.

**Milestones:**
- [x] Two-column trade overlay replacing the current provisioner modal
- [x] Trader gold pool (seeded, finite per visit; replenishes on region re-entry)
- [x] Sell-from-inventory: player can sell any non-equipped item for gold
- [x] Gold as primary consumable currency; ammo scoped to gear/forge only
- [x] Trader stock seeded by town supply depth and attitude tier

---

#### 6B — Item Effect System `M`

**Goal:** Replace flat medkits and tonics with a composable effect model. Every consumable item has one or two effects drawn from a shared pool. Items have names, rarity tiers, and biome affinities that make them feel like discoveries rather than utilities.

**Three item families:**

| Family | Role | Examples |
|--------|------|---------|
| **Potions** | Health restoration | Minor Healing Potion, Regeneration Draught, Elixir of Vitality |
| **Tonics** | Status defense and cleansing | Antidote, Fireward Tonic, Ward Tincture, Panacea |
| **Tinctures** | Active combat and exploration buffs | Attack Tincture, Defender's Draft, Swiftness Vial, Seer's Oil |

**Effect pool (composable — each item has 1-2):**

| Effect | Category | Notes |
|--------|----------|-------|
| Restore Health (minor / moderate / major) | Potion | Replaces medkit |
| Restore Health over Time | Potion | Heals 1 HP/turn for N turns |
| Restore Max Health | Potion | Rare — permanently increases max HP by 1 |
| Cure Poison | Tonic | Replaces tonic's cleanse |
| Cure Burn | Tonic | |
| Cure All | Tonic | Rare |
| Ward | Tonic | Absorbs 1 hit; replaces tonic's ward |
| Resist Poison | Tonic | Reduces duration of next poison by half |
| Resist Fire | Tonic | Reduces duration of next burn by half |
| Fortify Attack | Tincture | +N melee and ranged for M turns |
| Fortify Defense | Tincture | +N defense for M turns |
| Fortify Speed | Tincture | Faster autoexplore for M turns |
| Fortify Light | Tincture | +N FOV radius for M turns |
| Fortify Reach | Tincture | +1 melee range for M turns |
| Reveal | Tincture | Reveals 1 adjacent world region (rare) |

**Rarity tiers:**

| Tier | Availability |
|------|-------------|
| Common | Floor drops anywhere; trader always stocks |
| Uncommon | Biome-matched floor drops; trader stocks at supply depth 1+ |
| Rare | Landmark rewards, deep dungeon caches; never at traders |
| Legendary | Bottom-floor caches, named-site clears only; never at traders |

The provisioner/trader only ever sells Common items. Finding Uncommon through exploration is meaningful. Rare and Legendary are genuine discoveries — the player should remember where they found them.

**Milestones:**
- [x] Effect registry: shared pool of named effects with parameters (amount, duration, cure target)
- [x] Item model extended: each item has 1-2 effects, a rarity tier, and a biome affinity
- [x] Three item families (Potions, Tonics, Tinctures) replacing flat medkit/tonic/ward; Trinkets added as Level 2 equippable family
- [x] Rarity-gated availability: Common in traders, Uncommon gated by supply depth, Rare/Legendary expedition-only
- [x] Inventory display updated to show effect names and rarity tier
- [x] Existing medkit and tonic references migrated to equivalent Common items

**Later (6D):** Crafting — combine gathered materials (herbs, grain, ore) with the effect registry to produce items. Herbs → tonic-family effects, grain → potion-family effects, ore → tincture-family effects. The effect system makes this composable without hardcoded recipes.

---

#### 6C — Enemy Variety Expansion `M-L`

**Current state:** 81 data-driven enemy types across all biomes, with 9 behavioral archetypes and a full trait system. First and second pass complete.

**Target:** 80+ authored types as a second milestone; long-term goal of 100+ types deep enough that players encounter unfamiliar enemies across many sessions.

**Design model:** Each enemy is defined by a combination of:

| Dimension | Options |
|-----------|---------|
| **Behavioral archetype** | Pursuer, kiter, flanker, charger, tank, support, ambusher, swarmer, burrower |
| **Attack type** | Melee, ranged, ranged-status, melee-status, terrain-modifier, aoe |
| **Biome affiliation** | One or more biomes where it naturally spawns |
| **Tier range** | Minimum and maximum danger tier for spawning |
| **Special trait** | Pack bonus, shields ally, reflects damage, splits on death, berserks at low HP, drains HP, blinds player (reduces FOV), phases through walls, regenerates, calls reinforcements |

**First authored catalog (50 types across biomes):**

| Biome | Early (tier 1-2) | Mid (tier 3-4) | Late (tier 5+) |
|-------|-----------------|----------------|----------------|
| Forest | Pouncer, Thornling, Bark Golem | Pack Hunter, Grove Warden, Spore Shaman | Ancient Treant, Shadow Stalker |
| Swamp | Bogling, Mud Crawler, Leech | Bog Shaman, Swamp Brute, Mire Lurker | Swamp Behemoth, Plague Caller |
| Plains / Farmland | Archer, Raider, Scarecrow | Siege Archer, Pack Raider, Field Hexer | Warlord, Artillery Mage |
| Desert | Dust Crawler, Sand Ambusher | Hexer, Dune Sentinel, Mirage Kiter | Sand Titan, Venom Shaman |
| Mountain / Tundra | Sentinel, Ice Shard | Stone Golem, Frost Shaman, Avalanche Caller | Glacier Brute, Mountain Warden |
| Cave / Dungeon | Bogling, Lurker | Nest Guard, Crystal Shaman, Cave Brute | Dungeon Warden, Lair Sentinel |
| Badlands / Volcanic | Ash Crawler, Ember Sprite | Shaman, Slag Brute, Hexer | Magma Titan, Ash Warden |
| Castle / Ruins | Stalker, Sentinel | Armored Lurker, Ruins Shaman, Knight | Castle Warden, Lich |
| Monster Town | Raider, Pack Bogling | Orc Shaman, Siege Brute | War Chief, Plague Lord |

**Milestones:**
- [x] Data-driven enemy definition model (`enemy_catalog.py`): behavior archetype, biome list, tier range, special traits, stat scaling
- [x] Behavior dispatch system routes each archetype to the correct AI logic (pursuer, kiter, flanker, charger, tank, ambusher, swarmer) — `game_combat_ai.py`
- [x] Special trait system: pack_bonus, shields_ally, berserks, regen, drains_hp, blinds_player, calls_reinforcements, reflects_damage implemented
- [x] First pass catalog: 55+ named types authored and spawning correctly by biome and tier (now 81 total)
- [x] Biome spawn tables updated to draw from catalog rather than hard-coded type lists
- [x] Second pass catalog: 81 total types shipped
- [ ] Long-term target: 100+ types (ongoing, not blocking exit)

---

### Phase 7 — Leveling, Persistence, and Universal Rarity `L-XL`

**Goal:** Give the player a coherent journey across dozens of hours through a meaningful level progression, a truly persistent world, a death system with real stakes, and a rarity model that extends to every content type — so that something rare can be any kind of thing: a region, an enemy, an NPC, a potion, a biome, a region type never seen in 50 hours.

---

#### 7A — Persistent World and Death System `S-M`

**Current state:** The game already saves and loads, but the mental model is closer to roguelite than a persistent world — the player expects reset. The death screen returns to the main menu without a built-in respawn path.

**Target:** The world persists fully across sessions. Death is a setback, not a wipe. The player respawns at a shrine and loses only their carried gold.

**Death rules:**
- On death: carried gold is lost; inventory (gear, consumables), map discoveries, quest state, and character stats are preserved
- Enemies in the region where the player died respawn (that specific region is "reset")
- All other regions remain as left

**Respawn priority:**
1. Homepoint shrine — a shrine the player has explicitly set as their respawn anchor
2. Nearest discovered shrine — any shrine the player has visited, closest by world distance
3. Coordinate `(0, 0)` — the starting town, always a fallback

**Shrine interactions (new):**
- Approach a shrine tile → prompt to "Set as homepoint" (replaces prior homepoint)
- Shrine UI shows current homepoint status
- Shrines are already landmark types; this adds homepoint bookkeeping to them

**Milestones:**
- [x] Death flow: on death, log gold loss, clear region enemies, then respawn at shrine/homepoint/0,0 via Respawn button
- [x] Homepoint state: `homepoint_coord`, `discovered_shrines` list saved to world state and persisted
- [x] Shrine interaction: "H to set homepoint" prompt in shrine service modal; shrine visits recorded
- [x] Death screen updated: shows respawn location, gold lost; Respawn + Main Menu buttons; Enter=Respawn, Esc=Main Menu

---

#### 7B — Leveling System `M`

**Philosophy:** Maximum level 5. Each level is a milestone, not a grind reward. XP is earned from first-time discoveries, quest milestones, and world achievements — not from killing or revisiting. Regions and enemies do **not** scale with player level; a high-level player can still be killed by a well-rolled dangerous region.

**Level descriptions:**

| Level | Title | What Opens |
|-------|-------|-----------|
| 1 | Wanderer | Starting state. All core mechanics available. |
| 2 | Seasoned | Accessory / trinket slot unlocked. Named enemies (rare elites) begin appearing in the world. |
| 3 | Experienced | World reputation: NPCs across the world react to you by name. Track-appropriate notice board jobs begin to appear (harder, better reward). |
| 4 | Veteran | One active combat ability chosen at level-up from a short list (matched to track or open choice). |
| 5 | Master | Legendary sites become enterable. The named city's stronghold opens. Track mastery tier unlocks. |

**XP is earned from:**

| Source | Notes |
|--------|-------|
| First visit to each distinct region type | One-time; exploring the biome roster |
| First bottom floor of each delve family | One-time per family (dungeon, cave, ruins, castle…) |
| Quest milestones | First chain quest complete, first cross-town social quest, etc. (diminishing returns per type) |
| World distance milestones | First region at distance 5, 8, 10 from origin |
| Attitude milestones | First town reaching attitude tier 1, 2 |
| Named / rare discoveries | First named enemy killed, first legendary item found, first rare region type entered |

**XP is NOT earned from:**
- Kills
- Revisiting already-explored regions
- Repeating the same quest type for the same town

**Experience arc (rough hours):**

| Hours | Arc |
|-------|-----|
| 1–5 | Level 1. Learning systems, mapping nearby biomes, first towns, first notice board chains. |
| 5–10 | Approaching Level 2. Deeper biomes, first delve bottoms, first city. Named enemies start appearing. |
| 10–20 | Level 2–3. World feels familiar but new region types still surface. Reputation growing. Track identity clear. |
| 20–35 | Level 3–4. The player knows the world but still encounters genuinely rare content. Combat ability adds a new dimension. |
| 35+ | Approaching Level 5. Legendary sites, city stronghold, track mastery. The player has seen most of the world but not everything. |

**Milestones:**
- [x] XP state: `player_xp`, `player_level` (1–5) in world state; XP thresholds per level
- [x] XP sources wired: first-visit flags, first-delve-bottom flags, quest milestone flags
- [x] Level-up modal: shows new title, what opened, what the next level requires
- [x] Level 2: accessory slot in inventory; named enemy spawn logic (elites gated at level 2+ ✓, trinket slot ✓)
- [x] Level 3: NPC greeting lines pull player name/title; harder board jobs at high-attitude towns
- [x] Level 4: ability selection modal at level-up; 6-ability pool with passive combat effects wired; click/touch card selection
- [x] Level 5: legendary site entry gating (ossuary/mirrorwood/stronghold blocked below L5); city stronghold district added as 3-floor castle-class region with elite danger tier
- [x] Character journal tab: level, title, XP progress, active ability, dominant track
- [x] Controller/touch audit for all new overlays complete; levelup ability cards clickable/tappable

---

#### 7C — Universal Rarity Model `M`

**Philosophy:** Rarity is not just an item property. It applies to every content type. The player should, after 50 hours, encounter a region type, NPC type, enemy, or potion they have never seen before. Some things are designed to be seen once per many worlds — or never at all for most players.

**Rarity tiers (universal):**

| Tier | Meaning | Rough frequency |
|------|---------|----------------|
| Common | Appears routinely | Every few sessions |
| Uncommon | Seen across a long play session | Every several hours |
| Rare | Requires specific conditions or distance | Once per world or fewer |
| Legendary | May not appear in a given world at all | Designed for discovery, not expectation |

**Rarity by content type:**

| Content | Rare examples | Legendary examples |
|---------|--------------|-------------------|
| **Region types** | Monster town, maze | A region type that appears in <5% of worlds (e.g., Sunken Citadel, Ossuary, Mirrorwood) |
| **Biome combinations** | Volcanic adjacent to farmland | Truly anomalous geography — frozen volcanic, island lake |
| **NPC types** | Elder at high attitude tier | Wandering merchant with unique inventory; lorekeeper with world secrets |
| **Enemy types** | Named elite (appears at level 2+) | Boss-tier named enemy seeded into one deep delve per world |
| **Items (potions/tonics/tinctures)** | Uncommon: only in biome-matched drops | Legendary: never sold, found only in bottom-floor caches or named-site clears |
| **Landmarks** | Already: 11+ kinds | A landmark that only appears once per world and rewards a unique item on first visit |
| **Quest types** | Cross-town social chains | A quest that triggers only after meeting specific world conditions |

**Never-sold items:** Rare and Legendary items are expedition-only. No trader, provisioner, or resident ever sells them. The player must explore to find them. Some items exist that no player may ever buy — only discover.

**Always-rare things should feel rare:** Legendary content should not be telegraphed or listed in a guide. The goal is that finding a legendary region or item is genuinely surprising and memorable.

**Milestones:**
- [x] Rarity field on all content types: region types, NPC archetypes, enemy types, item definitions
- [x] Region rarity: rare/legendary region types have very low spawn weight and may require minimum world distance
- [x] NPC rarity: rare NPC archetypes (wandering merchant, lorekeeper) seeded once per world or per-world-condition
- [x] Enemy rarity: named elites spawn at level 2+; boss-tier enemies seeded to one deep region per world
- [x] Item rarity: Rare/Legendary never sold (enforced via `NEVER_SOLD` set); Uncommon biome-gated in drops; `DROPPABLE` excludes trinkets from generic cache pool
- [x] At least 2 legendary region types authored (Ossuary, Mirrorwood — both distance-gated, very low weight)
- [x] At least 1 legendary item authored: Mirrorleaf trinket (legendary rarity, mirrorwood-only cache drop, buy_price=0, never sold)

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
- Biome identity should deepen through three layers: palette/markers, traversal/combat behavior, and settlement/social flavor
- Favor "world expedition" features over generic roguelite bulk such as large crafting trees, loot floods, or huge enemy catalogs with tiny differences
- Narrow place-based systems are good; sprawling generic economy systems are not
- Item rarity should be legible at a glance; rare items should feel like discoveries, not just stat upgrades
- Enemy variety should emerge from behavioral combinatorics, not stat inflation — a new enemy type earns its place by asking a question the player hasn't seen before
- The effect system for items should remain composable and data-driven so crafting can be layered on without rewriting the item model
- Input support is now multi-surface (keyboard/mouse, controller, touch), so UX changes should be checked across all active overlays
- Settlement visuals should scale with importance: small towns stay one tile, larger towns and cities occupy multiple overworld tiles with district variation
- The game is a persistent world, not a roguelite — resist any design that implies a full reset. Death should be a setback that the player can recover from, not a wipe.
- Rarity applies to every content type, not just items. Region types, NPC archetypes, enemy types, landmarks, and quest conditions can all be rare or legendary. Legendary content should not be listed in the player guide — finding it should be a genuine surprise.
- Never-sold content is a design invariant: Rare and Legendary items, potions, and encounters are found through expedition only. No economy system should ever surface them for purchase.
- The leveling system is deliberately narrow (max 5). Each level must add a genuinely new dimension — not a stat increment. If a new level doesn't change what the player can access or how they play, it's not worth a level.
- XP sources should be first-time achievements, not grinding. Kill counts and revisit counts should not be XP sources.
- Regions and enemies do not scale with player level. A high-level player in a distant volcanic region is still in danger. The player grows; the world does not shrink.

---

### Phase 8 — Living World: Towns, Threats, and Growth `XL`

**Goal:** Make the world feel alive between player visits. Towns grow in directions shaped by their geography and by what the player has done. Threats have origins and apply real pressure. The player's sustained attention to a place changes what it becomes.

**Design principles:**
- Towns grow; they do not stage. There is no stage 1 → stage 2 progression. Instead, towns have tracked dimensions (security, prosperity, knowledge, connections) that rise and fall based on quests, threats, and player activity. Physical changes reflect dimension scores, not a fixed checklist.
- Archetype is derived, then self-reinforcing. A town with a dominant dimension develops archetype momentum: new residents, notice board priorities, and organic quest generation all compound that direction. Archetype is never explicitly named to the player — they read it from what's there.
- Expansion is directional. Towns expand only toward viable biomes. Hostile biome borders (badlands, swamp, volcanic, etc.) are hard stops in that direction. The town's shape is determined by its geography.
- Hemmed-in towns improve inward. A town that cannot expand still develops — through interior upgrades, wall hardening, and reputation rather than new districts or satellites.
- Threats have origins and leak. A monster town or hostile camp two regions away is a source, not just a destination. It generates patrol pressure on roads, notice board entries, and eventually raid events if left unaddressed.

---

#### 8A — Town Dimension Tracking `S`

**Current state:** Towns have an attitude score and a supply depth. There is no tracking of what a town has been doing or what kind of place it is becoming.

**Target:** Each town tracks four dimensions as integer scores: `security`, `prosperity`, `knowledge`, `connections`. These rise when the player completes relevant quests and fall when threats go unaddressed or supply routes break. The dominant dimension at any time determines the town's **derived archetype** (used internally to drive NPC behavior, notice board priorities, and building generation).

**Dimension sources:**

| Dimension | Rises from | Falls from |
|-----------|-----------|-----------|
| Security | Bounty/threat-clearance quests, escort completions | Nearby hostile camp unresolved, raid event |
| Prosperity | Trade/delivery quests, supply route established | Supply route broken, long absence |
| Knowledge | Investigation/survey quests, Chronicler work | — (knowledge does not decay) |
| Connections | Cross-town social quests, letter chains | — (connections do not decay) |

**Derived archetypes:**

| Dominant dimension | Archetype label (internal) | What it drives |
|-------------------|--------------------------|----------------|
| Security | `frontier_post` | Watch captain prominence, heavy-wall aesthetics, threat-response notice board weighting |
| Prosperity | `trade_hub` | Merchant NPC, caravan activity, market district growth, best shop stock |
| Knowledge | `learning_seat` | Archive building, trainer hall, expanded NPC knowledge, lorekeeper attraction |
| Connections | `social_anchor` | Cross-town NPC visitors, diplomat resident, richer attitude bonuses to neighboring towns |
| Balanced / low | `survivor` | Default; no dominant identity; notice board is pure survival quests |

**Milestones:**
- [ ] `town_dimensions` dict per town in world state (`security`, `prosperity`, `knowledge`, `connections`)
- [ ] Quest completion hooks increment the appropriate dimension
- [ ] `town_archetype(town_coord)` derived from dominant dimension; returns archetype key
- [ ] Archetype threshold: archetype is `survivor` until any dimension reaches threshold value (e.g., 3); above threshold, self-reinforcement begins (see 8B)

---

#### 8B — Archetype Self-Reinforcement `S-M`

**Current state:** Town contents are fixed at generation time. Revisiting a town changes nothing except attitude tier and stock depth.

**Target:** Past the archetype threshold, a town starts generating its own momentum. A `trade_hub` town attracts a permanent merchant NPC, generates trade quests organically, and eventually spawns a market district building if space allows. A `frontier_post` generates patrol quests on its own and eventually hardens its wall appearance. The player doesn't trigger these changes — they happen between visits and are discoverable on return.

**Self-reinforcement by archetype:**

| Archetype | What compounds automatically |
|-----------|----------------------------|
| `frontier_post` | Watch captain becomes most prominent NPC; notice board weights threat-response quests; wall aesthetics harden (timber → stone appearance); patrol buffer zone appears at hostile border |
| `trade_hub` | Wandering merchant sets up permanently; caravan NPC appears on roads; market stall count increases; shop stock depth increases beyond attitude tier alone |
| `learning_seat` | Archive building appears; trainer hall appears (if not already); lorekeeper NPC attracted; NPC dialogue depth increases |
| `social_anchor` | Cross-town visitors appear as temporary residents; diplomat NPC appears; attitude bonuses extend to neighboring towns the player has connected |

**Milestones:**
- [ ] `town_reinforcement_tick(town_coord)` called on each town visit (not on every game tick — only when player enters the region)
- [ ] Reinforcement checks archetype and dimension score; applies the next appropriate change if threshold met and change not yet applied
- [ ] Change log per town: tracks which reinforcements have fired so they don't repeat
- [ ] Permanent merchant NPC seeded into `trade_hub` towns above threshold
- [ ] Archive building added to `learning_seat` towns above threshold (if footprint allows)
- [ ] Notice board quest weighting reads archetype key to bias quest type selection

---

#### 8C — Endemic Threat System `M`

**Current state:** Threats exist in specific regions and stay there. Clearing a region ends its threat permanently. Roads between towns have no safety state.

**Target:** Hostile camps and monster towns are **sources** that apply continuous pressure to nearby areas. Road safety between towns is a tracked variable. Raid events can damage towns that go unattended. Wildlife acts as weather — environmental pressure without faction intent.

**Road safety:**
- Each road connection between towns has a `road_safety` state: `safe`, `watched`, or `contested`
- `safe`: caravans move freely; NPC trader stock replenishes faster; attitude between connected towns is warmer
- `watched`: player-cleared recently; patrols present; caravans move cautiously
- `contested`: nearby hostile source unresolved; caravans stop; town isolation sets in (stock depth drops, attitude between towns cools)
- Road safety visible on world map as subtle color coding on road lines; NPC dialogue references it

**Threat origins:**
- Monster towns and hostile camps are tagged as `threat_source` at world generation
- Each source has a `pressure_radius` (in world-grid steps) and a `patrol_interval`
- On each world-time tick (triggered by player region transitions), sources emit patrol pressure onto roads within radius
- Pressure degrades road safety for roads in radius; clearing the source ends the pressure permanently

**Raid events:**
- A town that has had `contested` road safety for too long (tracked by world-time ticks) may receive a raid event
- Raid events are discovered on the next visit: a quest appears ("three days ago they hit the outer district"), one NPC may be absent, one building may be closed temporarily, attitude takes a small hit
- Completing the follow-up quest (bounty or relief) restores the affected building and NPC; repeated raids without response can make an NPC permanently leave

**Wildlife pressure:**
- Certain biome adjacencies generate wildlife pressure: boar migrations through farmland, wolf packs in forest borders, ember sprites drifting from volcanic
- Wildlife pressure is seasonal (tied to world-time counter) rather than source-based
- Towns with sufficient security dimension already have counter-measures in place; low-security towns generate wildlife quests organically

**Milestones:**
- [ ] `road_safety` state tracked per town-pair connection in world state
- [ ] Threat source tags at world generation for monster towns and hostile camps
- [ ] Pressure propagation on world-time tick; roads in radius degrade toward `contested` if source unresolved
- [ ] Clearing a source permanently removes its pressure; road safety recovers over subsequent ticks
- [ ] World map road color indicates safety state (subtle; readable without being loud)
- [ ] Raid event generation for long-contested towns; discoverable on next visit with quest hook
- [ ] Wildlife pressure by biome adjacency; seasonal cycle tied to world-time counter
- [ ] NPC dialogue references road safety and threat situation naturally

---

#### 8D — Directional Town Expansion `M`

**Current state:** Towns occupy a single world-grid tile. Their footprint never changes.

**Target:** Towns with sufficient dimension scores and available adjacent viable tiles can expand: first to an outer district (features outside the main settlement cluster in the same tile), then to satellite hamlets (a new world-grid tile), then to road infrastructure between connected towns. Expansion direction is determined by adjacent biome viability.

**Expansion tiers:**

| Tier | What appears | Requires |
|------|-------------|---------|
| Outer district | Specific tiles outside the building cluster: tannery, stable, open-air market stall, guard post | Any dimension score ≥ 4; at least one viable adjacent direction |
| Satellite hamlet | New world-grid tile appears 1 step from parent town; 2-3 NPCs, no full services, fragile | Dominant dimension ≥ 6; viable adjacent tile |
| Road infrastructure | Waystation or bridge appears on a long road between two connected towns | Both towns have `connections` ≥ 3; road is `safe` or `watched` |
| District town | Multiple distinct clusters within the same tile footprint; specialized quarters | Dominant dimension ≥ 10; multiple dimensions ≥ 4 |

**Biome viability for expansion:**
- Viable: plains, farmland, forest, mountain (slow), tundra (slow)
- Blocked: badlands, swamp, volcanic, desert (without specific quest unlock), cave, dungeon
- Hostile border tiles become buffer zones rather than expansion targets: a cleared perimeter the town patrols, not settled

**Buffer zones:**
- A town adjacent to a hostile biome maintains a buffer zone at that border
- The buffer zone is a cleared strip: no hostile cover, patrolled by town watch
- Buffer zone can shrink if the town's security dimension falls; player quests can restore it
- The buffer zone is the first place a raid event manifests — visible as disturbed terrain on the next visit

**Hemmed-in towns (no viable expansion directions):**
- Cannot expand outward; can still improve inward
- Interior improvements: wall upgrade (timber → stone appearance), second building in footprint, well deepening, skilled watch NPC
- Hemmed-in towns develop `survivor` or `frontier_post` archetypes almost exclusively
- Reputation track: a fully improved hemmed-in town becomes known as a tough waypoint; passing NPCs mention it; the town's notice board has its own distinct character

**Satellite hamlet:**
- Fragile: can be abandoned if threat pressure exceeds the hamlet's small security score
- If abandoned, the world-grid tile reverts to its biome type; the parent town takes a prosperity hit
- Protecting the hamlet is a distinct quest structure — smaller scale, more personal — compared to town-level quests

**Milestones:**
- [ ] `viable_expansion_directions(town_coord)` computed from adjacent biome types at world generation
- [ ] Outer district generation: when dimension threshold met, scatter 2-3 specific feature tiles outside the building cluster
- [ ] Satellite hamlet: new world-grid entry seeded as `hamlet` type, connected to parent; own NPC set; own quest hooks
- [ ] Hamlet fragility: security score tracked; abandoned if pressure sustained without player response
- [ ] Buffer zone: flagged on hostile-border tiles; shrinks/grows with security dimension; raid events manifest here first
- [ ] Road infrastructure: waystation or bridge tile seeded on long roads between sufficiently connected towns
- [ ] District town: multiple spatial clusters in one tile when dimension thresholds reached; district labels on world map

---

#### 8E — World Improvement Visibility `S`

**Goal:** The player should be able to read the world's history from what's there — not from a stats screen. Changes made by the town growth system should be discoverable through observation, NPC dialogue, and world map details.

**Milestones:**
- [ ] World map road coloring reflects safety state without requiring the detail panel
- [ ] Town world-map tile reflects development stage: a trade hub looks busier, a frontier post looks fortified (via icon or tile overlay)
- [ ] NPC dialogue references town history: "used to be rougher here before the patrols started" / "caravan stopped coming through last season"
- [ ] Notice board quest text reflects archetype: frontier post boards use military register, trade hub boards use merchant language, learning seat boards have scholarly tone
- [ ] Journal tab: "World Notes" section that records significant changes the player has witnessed or caused (raid repelled, satellite founded, road secured)

---

## Much Later
- Experiment with a giant seamless overworld driven by a stable world seed and coordinate-based procedural generation
- Add overworld landmark scale language at the full-detail level: authored tile art, animated beacons, or layered glyph overlays
- Explore a theme-pack architecture for alternate content skins (modern setting, sci-fi, etc.)
- Expand multi-region water systems: river sources and mouths, lake regions, flood-plain farmland bonuses
- Item crafting system: combine gathered materials with the effect registry to produce consumables (herbs → tonics, grain → potions, ore → tinctures); the effect model makes this composable without hardcoded recipes
- Hundreds of enemy types: once the data-driven catalog is in place, adding types is cheap — the long-term target is a roster deep enough that players encounter unfamiliar enemies across many sessions
