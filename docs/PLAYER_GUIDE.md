# Tactical Shadowcaster — Player Guide

The game is a world-expedition roguelite. You explore a procedurally generated world, discover named places, decide whether they're worth the risk, and return with something meaningful. The world remembers what you've done.

This guide covers everything needed to play effectively: controls, the world loop, upgrades, gear, enemies, and the four progression tracks.

---

## Controls

| Action | Keyboard / Mouse | Numpad | Controller |
|--------|-----------------|--------|------------|
| Move (cardinal) | Arrows or WASD | 8 / 2 / 4 / 6 | Left Stick or D-pad |
| Move (diagonal) | Q E Z C | 7 9 1 3 | Diagonal on stick or D-pad |
| Hold to walk | Hold any movement key | Hold key | Hold direction |
| Melee / talk | Space | 5 | A / Cross |
| Ranged attack | F | `*` | X / Square |
| Use stairs / portal / exit | Enter or `.` | `.` | A / Cross |
| Medkit | H | `+` | LB / L1 |
| Tonic | G | `-` | RB / R1 |
| Autoexplore | X | 0 | B / Circle (hold) |
| World map | M | `/` | View / Select / Share |
| Inventory | I | — | Pause menu → Inventory |
| Journal | J | — | Pause menu → Journal |
| Message log | L | — | Pause menu → Log |
| Balance tuner | T (during a run) | — | Right Stick click |
| Menu / pause | Esc | — | Menu / Start / Options |
| Back / cancel | Esc | — | B / Circle |

**Mouse:** Click visible creatures, items, exits, and landmarks to inspect. Click seen tiles to path there when no hostile is visible.

### World Map Controls

| Action | Keyboard | Controller |
|--------|----------|------------|
| Open / close | M or Esc | View / Select / Share |
| Pan view | WASD or Arrows | — |
| Move selection cursor | — | D-pad or Left Stick |
| Scroll detail panel up | Page Up | X / Square |
| Scroll detail panel down | Page Down | Y / Triangle |
| Switch map mode | Tab | LB / RB |
| Recenter on player | R or Home | — |

### Touch

Tap the game area to move or interact. Tap on-screen action buttons at the bottom of the screen. Tap overlays (inventory, notice board, world map) to interact with their elements directly.

---

## The World

The overworld is a grid of named regions. You start at `(0, 0)` — always a town. Moving in any direction generates the adjacent region on first visit and stores it permanently. Every world is seeded: the same seed produces the same geography.

### Geography

Each world has several large-scale features generated at the start of a run:

- **Rivers** — 1-2 paths of river tiles flow from distant coords toward the origin. Visible as blue bands on the world map. Biomes along rivers tend toward swamp, farmland, and forest.
- **Coast** — one edge of the world is bounded by a named sea (the Northern Sea, Eastern Sea, etc.). Ocean coords block travel; the world map detail panel notes when you're near the coast.
- **Named zones** — 2-3 named geographic zones (e.g., "the Mire," "the High Pass," "the Verdant Reaches") anchor to distant coords and appear as dim labels on the world map. Each zone has a theme that hints at the biomes you'll find there.
- **Named city** — one city per world (e.g., "Ironhaven," "Duskport") sits a few tiles from the origin. The hub is a large_town with a full service slate; surrounding it are up to 3 district coords (market, civic, temple quarters). The hub is outlined in gold on the world map.

### Biome Distribution

Safer biomes cluster near the origin; harsher ones dominate at distance. Roughly:

| Distance | Likely biomes |
|----------|---------------|
| 1-3 tiles | Plains, farmland, forest |
| 4-6 tiles | Desert, swamp, mountain |
| 7-9 tiles | Badlands, tundra |
| 9+ tiles | Volcanic |

Adjacent biomes also influence each other — forests cluster with swamps and plains, deserts cluster with badlands and volcanic, tundra clusters with mountain. This means the world has geographic continuity rather than pure randomness.

### Region Types

| Type | Notes |
|------|-------|
| Plains, farmland, forest | Safe overworld; farmland has harvestable resources |
| Swamp, desert, mountain | Mid-danger overworld; biome terrain effects active |
| Badlands, tundra, volcanic | High-danger overworld |
| Town | Settlement with services, residents, notice board |
| large_town | Full-service settlement (city hub); broader service slate |
| Dungeon, cave, ruins | Multi-level; deeper floors = higher danger |
| Castle | Multi-level; elaborate multi-zone layout with distinct encounter wings |
| Maze | Single-level; disorienting layout |
| Monster town | Hostile settlement |

### Danger Tiers

Each region has a danger tier computed from its world distance and your player strength at first entry. The tier persists — revisiting a region doesn't reset it. Local regions (dungeon floors, cave levels) inherit their parent site's tier and deepen it with each floor.

Tier is your primary risk signal. A tier 4 castle requires meaningfully more HP and damage than a tier 2 cave.

---

## The Town Loop

Towns are the core of the non-combat loop. Every town tracks:

- **Attitude** — built by completing quests from that town's notice board. Higher attitude improves services.
- **Prosperity** — a secondary score tracking wealth and activity.
- **Supply depth** — increased by completing relief-theme chain quests. Deeper supply means better provisioner stock and larger discounts.

### Services

| Interior | What it does |
|----------|--------------|
| Inn | Heals HP. Amount scales with attitude tier (base 3, up to +3 bonus at high attitude). |
| Clinic | Smaller heal (base 2) + status cleanse. Scales with attitude. |
| Shrine / Chapel | Ward tonic (absorbs one damage hit). Duration scales with attitude. |
| Smith | Sells ammo. |
| Supply / Cartographer | Reveals neighboring world regions on the map. |
| Bathhouse | Full HP restore (rare interior). |
| Armory | Ammo + tonic bundle. |
| Apothecary | Cleanse + potions. |
| Provisioner | Barter for gear, medkits, and crafted items (see below). |

### Provisioner Barter

Ammo is the provisioner's currency. Costs are discounted by supply depth.

| Trade | Default cost |
|-------|--------------|
| Field Kit (1 medkit) | 2 ammo |
| Cleanser (1 tonic) | 3 ammo |
| Sell Tonic | Gives 2 ammo |
| Weapon (varies) | 2–8 ammo |
| Armor (varies) | 2–10 ammo |
| Pack Rations (2 grain → 1 potion) | Requires carried grain |
| Brew Tonic (2 herbs → 1 tonic) | Requires carried herbs |
| Forge Heads (1 ore → +2 ammo) | Requires carried ore |

### Residents

Each town has biome-flavored residents — herbalists, drovers, ferrymen, millers, masons, trappers, kilnkeepers — plus civic roles (watcher, vendor, elder) that appear as your attitude rises. Bump into or inspect a resident to interact.

Many residents offer a **boon** once per town visit: a small heal, route guidance, a marked site, spare ammo, or a ward buff. Return dialogue changes after a boon is given — the resident remembers.

**Town growth:** At attitude tier 1, a vendor appears in the town square. At tier 2, an elder appears. Both offer boons and richer context for the region.

---

## Notice Board Quests

The notice board posts three quest types plus chain quests:

| Kind | Objective | Reward |
|------|-----------|--------|
| Delivery | Carry an item to a named town | Gold |
| Scout | Travel to a region and report back | Gold + map reveal of one adjacent region |
| Bounty | Kill enemies in a named region | Gold |
| Chain | Multi-stage: travel, complete objective, return | Gold + supply depth gain |

**Social quests** are delivery jobs that link specific residents between towns — a letter, a family errand, a rumor follow-up. Completing them advances cross-town story threads and can unlock follow-up jobs.

Completing any quest in a town adds to that town's attitude score and `towns_helped` count, which feed your Warden and Pathfinder track scores.

---

## Upgrades (Floor Pickups)

Colored pickups appear on overworld and delve floors. Each type stacks with itself and with gear.

| Pickup | Effect | Default amount |
|--------|--------|----------------|
| **Power** (orange) | +1 melee damage and +1 ranged damage | +1 per pickup |
| **Vitality** (green) | +2 max HP, heals 2 immediately | +2 HP per pickup |
| **Light** (yellow) | +1 FOV radius (base 10) | +1 radius per pickup |
| **Haste** (cyan) | Autoexplore 8ms faster per pickup | −8ms per pickup |
| **Reach** (purple) | +1 melee attack range | +1 tile per pickup |
| **Heal** (pink) | Small immediate heal | Scales with tuning |

Power pickups are the most combat-impactful and are the primary score driver for the Delver track.

---

## Gear

Weapons and armor are purchased from the provisioner using ammo. You can own one weapon and one armor at a time; equipping a new one replaces the old.

### Weapons

| Weapon | Melee bonus | Ranged bonus | Cost | Notes |
|--------|-------------|--------------|------|-------|
| Dagger | +1 | — | 3 | Cheap entry weapon |
| Shortbow | — | +1 | 2 | Cheapest ranged option |
| Longbow | — | +2 | 4 | Best pure ranged value |
| Warhammer | +2 | — | 5 | Best pure melee value |
| Spear | +1 | +1 | 5 | Also grants +1 melee range (stacks with Reach upgrades) |
| Halberd | +2 | +1 | 8 | Best overall; expensive |

The **Spear** is broadly efficient. Its +1 melee range bonus is in addition to any Reach upgrade pickups, making it the best weapon for reach-focused builds. The **Halberd** is the Delver endgame weapon when you can afford it.

### Armor

| Armor | Defense bonus | Cost | Notes |
|-------|---------------|------|-------|
| Travel Cloak | +1 | 2 | Cheapest; minimal ammo investment |
| Leather Armor | +2 | 4 | Good early value |
| Chain Mail | +3 | 6 | Mid-tier standard |
| Plate Coat | +4 | 8 | Heavy; for committed Delver builds |
| War Plate | +5 | 10 | Maximum defense; serious ammo cost |

Armor defense is applied before damage on every hit: `damage taken = max(1, incoming − defense − reduction)`. Even +1 defense meaningfully extends survival across a long run.

---

## Enemies

Enemies spawn based on region type and danger tier. At the end of a group, a stronger bookend may appear.

| Enemy | Marker | Notes |
|-------|--------|-------|
| **Stalker** | Enemy | Standard pursuer; A* pathfinding to player. Baseline threat. |
| **Pouncer** | Beast | Low HP, fast. Forest signature. Dies quickly but moves before you can react if you're not watching flanks. |
| **Bogling** | Beast | Cave/swamp signature. Tough for early danger tiers; packs hit hard. |
| **Sentinel** | Settler | High HP (4). Mountain/tundra/ruins/castle. Slow but absorbs many hits. |
| **Archer** | Archer | Ranged attacker (range 6, prefers distance 3). Plains/desert/farmland. Kites backward; close the distance before engaging. |
| **Shaman** | Shaman | Ranged, applies **poison** or **burn** (by biome). Range 4, prefers distance 2. Swamp, cave, volcanic. Kill first — status effects compound over turns. |
| **Hexer** | Shaman | Ranged status applier (range 5, prefers distance 4). Desert/volcanic/badlands at threat 3+. Longer range than shaman; dangerous from across the room. |
| **Lurker** | Enemy | Moves **2 tiles per turn**. Cave/maze at threat 3+. The most dangerous melee enemy in the game because it closes distance instantly. |
| **Brute** | Enemy | High HP (5), +2 damage. Bookend at threat 3+ in most regions. Respect the damage — don't tank hits from a brute without armor. |
| **Warden** | Enemy | High HP (7). Bookend in castle/dungeon at threat 4+. The strongest enemy; plan your resources before the final room. |

### Terrain Effects

| Terrain | Effect |
|---------|--------|
| Muck (swamp) | Walking through applies **poison** (damage over turns) |
| Embers (volcanic/desert) | Walking through applies **burn** |
| High ground | Tactical positioning; visibility advantage |
| Well | Steps onto well tile restore 1 HP or cleanse a status |

Tonics cleanse both poison and burn. In swamp and volcanic regions, carry at least one tonic before descending.

---

## Progression Tracks

Tracks are not chosen upfront. They emerge from what you do during a run. Your dominant track (the highest-scoring one that has reached tier 1) appears in the journal stats tab. Reaching tier 1 (8+ points) adds a **fourth reward option** to every exploration and delve reward modal — the track-specific bonus. Reaching tier 2 (20+ points) upgrades that bonus.

### Track Matrix

| | **Scout** | **Delver** | **Warden** | **Pathfinder** |
|---|---|---|---|---|
| **Scores from** | Scout quests ×4, surface landmarks ×2 | Kills ÷5, Power pickups ×4, Vitality ×3, full clears ×5 | Bounty quests ×4, towns helped ×3, chain quests ×3 | Regions seen ×1, surface landmarks ×3, delivery quests ×2 |
| **Tier 1 reward** | Reveal 1 region + 1 tonic | +1 attack + 3 ammo | +20g + full HP restore | +2 medkits + 1 tonic + 1 reveal |
| **Master reward** | Reveal 2 regions + 1 tonic | +2 attack + 4 ammo | +35g + full HP restore | +3 medkits + 1 tonic + 2 reveals |
| **Best regions** | Overworld, surface sites | Dungeon, cave, castle | Town networks | Wide overworld traversal |
| **Preferred weapon** | Spear | Warhammer → Halberd | Spear → Halberd | Shortbow → Longbow |
| **Preferred armor** | Travel Cloak or none | Chain Mail → Plate Coat | Leather → Chain Mail | Travel Cloak |
| **Upgrade priority** | Light → Vitality | Power → Vitality → Reach | Vitality → Reach | Light → Haste → Vitality |
| **Skip** | Heavy armor, Reach | Haste, Light | — | Reach, Power |
| **Quest focus** | Scout board jobs | — (combat-driven) | Bounty + chain board jobs | Delivery board jobs |
| **Town role** | Cartographer for map reveals | City hub as gear base | Build attitude in 2-3 towns | Delivery endpoints; attitude bonus |
| **Special bonus** | Scout reward compounds: reveals → more sites | +15-30% dungeon cache chance | Gold reward funds gear economy | +15-25% overworld cache chance |
| **Playstyle** | Wide, shallow, fast | Deep, slow, thorough | Town-anchored, quest-driven | Horizontal, many tiles, cheap |

### Notes per Track

**Scout** — Use the Cartographer to pre-reveal neighbors, then visit them for the landmark bonus before moving on. Every Scout tier 1 reveal gives you new sites to chain into more points. Light upgrades extend your FOV so you spot surface sites without walking every tile.

**Delver** — Full clears are the biggest score driver (5 points each). Heavy armor is what makes full clears survivable at high danger tiers — the ammo cost of Plate Coat or War Plate pays for itself in completed floors. Power pickups both score points and directly increase your damage output.

**Warden** — Every completed quest in any town scores `towns_helped` (3 points each). Cross-town social quests chain between towns you've already helped, compounding attitude and score simultaneously. The gold reward is unique — no other track gives currency, and gold feeds directly into ammo purchases for gear upgrades.

**Pathfinder** — Delivery jobs are the core engine: each one is a region visit, delivery points, and attitude in two towns at once. The named city hub plus its 3 district tiles is 4 region visits in a tight cluster. River corridors are natural highways — biomes along them are hospitable and give you orientation for planning multi-tile routes.

---

## Reward Modals

Two events trigger a reward choice:

1. **100% exploration** of a floor — choose Vitality (+1 max HP), Power (+1 attack), Recovery (+1 medkit, +1 tonic), or your track reward if unlocked.
2. **Delve clear** (reaching the bottom floor of a multilevel region) — choose Vitality (+3 max HP), Power (+1 attack, +1 ammo), Recovery (+2 ammo, +2 medkits, +1 tonic), or your track reward.

**Rule of thumb:** Take the track reward if you're above half HP and not critically low on consumables. It's almost always the best value once you've reached tier 1, and it compounds across the run.

---

## General Tips

- **Tonics cleanse status effects** — always carry one before entering swamp or volcanic regions.
- **Retreat is a real option** — leaving a region preserves your HP and consumables. Failed attempts give you scouting intel for the next visit.
- **Town attitude compounds** — every quest you complete in a town pays off in better heals and cheaper gear on every future visit. Anchor to 2-3 towns early.
- **The provisioner discount** from supply depth applies to all gear purchases. Completing relief-theme chain quests (medkit/ammo deliveries) doubles the supply depth gain.
- **Shamans and hexers first** — their ranged status attacks apply poison or burn that ticks for multiple turns. Kill them before engaging the melee pack.
- **Lurkers move twice per turn** — do not assume a lurker is far enough away. It can close the full room length in one turn.
- **The Spear's range bonus stacks** — a Spear + two Reach pickups gives melee range 4. That covers most rooms and lets you attack around corners.
- **Full clears on first floors** — the first floor of a dungeon or cave is the easiest to fully explore. Doing so scores track points and generates a cache chance that scales with your Delver or Pathfinder tier.
