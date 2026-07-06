"""
Enemy catalog: data-driven enemy definitions.

Each entry is keyed by a slug and defines:
  name          display string used in combat messages
  color         RGB tuple
  marker        rendering marker class ("enemy", "beast", "settler", "archer", "shaman")
  health        base HP (danger-tier bonus is added at spawn)
  damage        base damage per hit
  attack_range  tile range for ranged attack (1 = melee only)
  preferred_range  kiting distance (only relevant when > 1)
  moves_per_turn   extra movement steps per AI tick
  behavior      one of: pursuer | kiter | charger | flanker | tank | ambusher | swarmer
  on_hit_effect optional status string ("poison" | "burn" | "stun")
  traits        list of special trait strings (see game_combat.py dispatch)
  biomes        list of biome slugs where this enemy can spawn (empty = universal filler)
  tier_min      minimum danger_value() for spawning
  tier_max      maximum danger_value() (None = no cap)
  weight        relative spawn weight within its biome pool (default 1)
"""
from __future__ import annotations

import random

_E = (160, 160, 170)   # generic enemy grey
_B = (255, 156, 96)    # beast orange
_G = (138, 188, 112)   # bogling green
_S = (188, 196, 210)   # sentinel blue-grey
_A = (255, 210, 110)   # archer gold
_M = (180, 110, 255)   # shaman purple
_R = (220, 140, 80)    # brute brown-orange
_BK = (100, 110, 130)  # dark tank
_C = (220, 90, 90)     # charger red

def _e(name, color, marker, health, damage, biomes, tier_min=1, tier_max=None, *,
       behavior="pursuer", attack_range=1, preferred_range=1, moves_per_turn=1,
       on_hit_effect=None, traits=(), weight=1, rarity="common"):
    return {
        "name": name, "color": color, "marker": marker,
        "health": health, "damage": damage,
        "behavior": behavior,
        "attack_range": attack_range, "preferred_range": preferred_range,
        "moves_per_turn": moves_per_turn,
        "on_hit_effect": on_hit_effect,
        "traits": list(traits),
        "biomes": biomes,
        "tier_min": tier_min, "tier_max": tier_max,
        "weight": weight,
        "rarity": rarity,
    }

ENEMY_CATALOG: dict[str, dict] = {

    # ── Universal fillers ────────────────────────────────────────────────────
    "stalker": _e("stalker",  _E, "enemy",   3, 1, [], 1),
    "brute":   _e("brute",    _R, "enemy",   5, 2, [], 3, behavior="tank"),
    "warden":  _e("warden",   _BK,"enemy",   7, 1, [], 4, traits=["shields_ally"]),

    # ── Forest ───────────────────────────────────────────────────────────────
    "pouncer":      _e("pouncer",     _B,  "beast",   2, 1, ["forest"],            1, 3, behavior="charger", weight=3),
    "thornling":    _e("thornling",   (120,180,80),"beast", 3, 1, ["forest"],      1, 2, traits=["reflects_damage"], weight=2),
    "bark_golem":   _e("bark golem",  (100,140,90),"enemy", 6, 1, ["forest"],      2, 3, behavior="tank", traits=["regen"]),
    "pack_hunter":  _e("pack hunter", _B,  "beast",   3, 1, ["forest"],            3, 4, behavior="swarmer", traits=["pack_bonus"], weight=2),
    "grove_warden": _e("grove warden",(80,160,100),"enemy", 5, 1, ["forest"],      3, 4, traits=["shields_ally"]),
    "spore_shaman": _e("spore shaman",_M,  "shaman",  3, 1, ["forest"],            3, 5,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "shadow_stalker":_e("shadow stalker",(60,60,90),"enemy", 4, 2, ["forest"],     5, None, behavior="ambusher", moves_per_turn=2),
    "ancient_treant":_e("ancient treant",(60,100,60),"enemy",10, 2, ["forest"],    5, None, behavior="tank", traits=["regen", "shields_ally"]),

    # ── Swamp ────────────────────────────────────────────────────────────────
    "bogling":      _e("bogling",     _G,  "beast",   2, 1, ["swamp","cave","maze"], 1, 3, weight=3),
    "mud_crawler":  _e("mud crawler", (110,150,90),"beast", 3, 1, ["swamp"],       1, 2, on_hit_effect="poison", weight=2),
    "leech":        _e("leech",       (100,130,80),"beast", 2, 1, ["swamp"],       1, 2, traits=["drains_hp"]),
    "bog_shaman":   _e("bog shaman",  _M,  "shaman",  3, 1, ["swamp"],             2, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "swamp_brute":  _e("swamp brute", _R,  "enemy",   6, 2, ["swamp"],             3, 4, behavior="tank"),
    "mire_lurker":  _e("mire lurker", (80,110,70),"enemy",  3, 2, ["swamp"],       3, 5, behavior="ambusher", moves_per_turn=2),
    "swamp_behemoth":_e("swamp behemoth",(70,100,60),"enemy",10, 2, ["swamp"],     5, None, behavior="tank", on_hit_effect="poison"),
    "plague_caller":_e("plague caller",_M, "shaman",  4, 1, ["swamp"],             5, None,
                       attack_range=5, preferred_range=4, behavior="kiter",
                       on_hit_effect="poison", traits=["calls_reinforcements"]),

    # ── Plains / Farmland ────────────────────────────────────────────────────
    "archer":       _e("archer",      _A,  "archer",  3, 1, ["plains","farmland","desert","badlands"], 1,
                       attack_range=6, preferred_range=3, behavior="kiter", weight=2),
    "raider":       _e("raider",      _C,  "settler", 3, 1, ["plains","farmland"], 1, 3, behavior="charger", weight=2),
    "scarecrow":    _e("scarecrow",   (200,180,120),"enemy", 2, 1, ["farmland"],   1, 2, traits=["blinds_player"]),
    "siege_archer": _e("siege archer",_A,  "archer",  4, 2, ["plains","farmland"], 3, 4,
                       attack_range=7, preferred_range=4, behavior="kiter"),
    "pack_raider":  _e("pack raider", _C,  "settler", 3, 1, ["plains","farmland"], 3, 4,
                       behavior="swarmer", traits=["pack_bonus"]),
    "field_hexer":  _e("field hexer", _M,  "shaman",  3, 1, ["plains","farmland"], 3, 5,
                       attack_range=5, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "warlord":      _e("warlord",     _C,  "settler", 7, 2, ["plains","farmland"], 5, None,
                       behavior="tank", traits=["berserks", "shields_ally"]),

    # ── Desert ───────────────────────────────────────────────────────────────
    "dust_crawler": _e("dust crawler",(210,190,140),"beast", 2, 1, ["desert"],     1, 2, behavior="charger", weight=2),
    "sand_ambusher":_e("sand ambusher",(200,170,100),"beast",3, 1, ["desert"],     2, 3, behavior="ambusher", moves_per_turn=2),
    "dune_sentinel":_e("dune sentinel",_S, "settler", 4, 1, ["desert"],            2, 4, behavior="tank"),
    "hexer":        _e("hexer",       (220,160,80),"shaman",  2, 1, ["desert","volcanic","badlands"], 2,
                       attack_range=5, preferred_range=4, behavior="kiter", on_hit_effect="poison"),
    "venom_shaman": _e("venom shaman",_M,  "shaman",  3, 1, ["desert"],            4, 5,
                       attack_range=5, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "sand_titan":   _e("sand titan",  (180,160,110),"enemy",10, 2, ["desert"],     5, None,
                       behavior="tank", traits=["berserks"]),

    # ── Mountain / Tundra ────────────────────────────────────────────────────
    "sentinel":     _e("sentinel",    _S,  "settler", 4, 1, ["mountain","tundra","ruins","castle"], 1, weight=2),
    "cliff_hound":  _e("cliff hound", _B,  "beast",   3, 1, ["mountain"],          1, 3, behavior="charger", weight=2),
    "ice_shard":    _e("ice shard",   (180,220,255),"beast", 2, 1, ["tundra"],     1, 2,
                       attack_range=4, preferred_range=3, behavior="kiter"),
    "frost_wraith": _e("frost wraith",(140,190,240),"enemy", 3, 2, ["tundra"],     2, 4, behavior="ambusher",
                       moves_per_turn=2, on_hit_effect="stun"),
    "stone_golem":  _e("stone golem", (130,130,140),"enemy", 7, 2, ["mountain"],   2, 4,
                       behavior="tank", traits=["reflects_damage"]),
    "ridge_shaman": _e("ridge shaman",(160,170,200),"shaman",3, 1, ["mountain"],   2, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="stun"),
    "frost_shaman": _e("frost shaman",(160,210,255),"shaman",3, 1, ["tundra"],     3, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="stun"),
    "ice_golem":    _e("ice golem",   (160,210,240),"enemy", 8, 2, ["tundra"],     3, 5,
                       behavior="tank", on_hit_effect="stun", traits=["reflects_damage"]),
    "avalanche_caller":_e("avalanche caller",(200,210,220),"shaman",3,1,["mountain"],3,5,
                       attack_range=5, preferred_range=4, behavior="kiter",
                       traits=["calls_reinforcements"]),
    "glacier_brute":_e("glacier brute",(140,180,200),"enemy",8, 2, ["tundra"],     5, None,
                       behavior="tank", on_hit_effect="stun"),
    "mountain_warden":_e("mountain warden",_BK,"enemy",7,1,["mountain"],           5, None,
                       behavior="tank", traits=["shields_ally", "regen"]),

    # ── Cave / Dungeon / Maze ────────────────────────────────────────────────
    "trap_springer":_e("trap springer",_B, "beast",   2, 1, ["dungeon","cave"],    1, 2, behavior="charger", weight=2),
    "lurker":       _e("lurker",      (160,100,220),"enemy", 2, 2, ["cave","dungeon","maze","ruins"], 2,
                       behavior="ambusher", moves_per_turn=2, weight=2, on_hit_effect="cripple"),
    "nest_guard":   _e("nest guard",  _G,  "beast",   4, 1, ["cave","dungeon"],    2, 4,
                       behavior="swarmer", traits=["pack_bonus"]),
    "cave_shaman":  _e("cave shaman", _M,  "shaman",  3, 1, ["cave"],              2, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "crystal_shaman":_e("crystal shaman",(160,220,255),"shaman",3,1,["cave"],      3, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="stun"),
    "cave_brute":   _e("cave brute",  _R,  "enemy",   6, 2, ["cave","dungeon"],    3, 5, behavior="tank", on_hit_effect="cripple"),
    "bone_golem":   _e("bone golem",  (180,170,160),"enemy", 7, 1, ["dungeon","ruins"], 3, 5,
                       behavior="tank", traits=["regen"]),
    "maze_specter": _e("maze specter",(120,80,200),"enemy",  3, 2, ["maze"],       3, 5,
                       behavior="ambusher", moves_per_turn=2, on_hit_effect="stun"),
    "dungeon_warden":_e("dungeon warden",_BK,"enemy",  7, 1, ["dungeon"],          4, None,
                       traits=["shields_ally"]),
    "lair_sentinel":_e("lair sentinel",_S, "enemy",   5, 2, ["cave"],              4, None,
                       behavior="tank", traits=["berserks"]),

    # ── Badlands / Volcanic ──────────────────────────────────────────────────
    "ash_crawler":  _e("ash crawler", (160,140,120),"beast", 2, 1, ["volcanic","badlands"], 1, 2,
                       behavior="charger", weight=2),
    "scorched_raider":_e("scorched raider",_C,"settler",3, 1, ["badlands"],        1, 3, behavior="charger", weight=2),
    "ember_sprite": _e("ember sprite",(255,120,60),"beast",  2, 1, ["volcanic"],   1, 2,
                       on_hit_effect="burn", weight=2),
    "cinder_hound": _e("cinder hound",_B,  "beast",   4, 2, ["volcanic"],         2, 4,
                       behavior="charger", on_hit_effect="burn"),
    "dust_wraith":  _e("dust wraith", (160,150,130),"enemy", 3, 2, ["badlands"],   2, 4,
                       behavior="ambusher", moves_per_turn=2),
    "slag_brute":   _e("slag brute",  _R,  "enemy",   6, 2, ["volcanic","badlands"],3, 5,
                       behavior="tank", on_hit_effect="burn"),
    "magma_titan":  _e("magma titan", (200,80,50), "enemy", 10, 2, ["volcanic"],   5, None,
                       behavior="tank", on_hit_effect="burn", traits=["berserks"]),
    "ash_warden":   _e("ash warden",  _BK, "enemy",   7, 1, ["badlands"],          5, None,
                       behavior="tank", traits=["shields_ally"]),

    # ── Castle / Ruins ───────────────────────────────────────────────────────
    "grave_crawler":_e("grave crawler",_G, "beast",   2, 1, ["ruins"],             1, 2, behavior="charger", weight=2),
    "armored_lurker":_e("armored lurker",(140,130,120),"enemy",4,2,["castle","ruins"],3,4,
                       behavior="ambusher", moves_per_turn=2),
    "crossbowman":  _e("crossbowman", _A,  "archer",  3, 1, ["castle"],            2, 4,
                       attack_range=6, preferred_range=4, behavior="kiter"),
    "herald":       _e("herald",      _S,  "settler", 4, 1, ["castle"],            2, 4,
                       traits=["shields_ally"]),
    "ruins_shaman": _e("ruins shaman", _M, "shaman",  3, 1, ["ruins"],             3, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "knight":       _e("knight",      (200,200,220),"settler",5, 2, ["castle"],     3, 5,
                       behavior="charger", traits=["berserks"]),
    "castle_warden":_e("castle warden",_BK,"enemy",   8, 2, ["castle"],            5, None,
                       behavior="tank", traits=["shields_ally", "regen"]),
    "lich":         _e("lich",        (200,180,255),"shaman", 5, 1, ["ruins"],      5, None,
                       attack_range=5, preferred_range=4, behavior="kiter",
                       on_hit_effect="poison", traits=["regen", "calls_reinforcements"]),

    # ── Monster Town ─────────────────────────────────────────────────────────
    "goblin":       _e("goblin",      _G,  "beast",   2, 1, ["monster_town"],      1, 3,
                       behavior="swarmer", traits=["pack_bonus"], weight=3),
    "troll":        _e("troll",       (100,160,100),"enemy", 5, 2, ["monster_town"],2, 4,
                       behavior="tank", traits=["regen"]),
    "orc_shaman":   _e("orc shaman",  _M,  "shaman",  3, 1, ["monster_town"],      2, 4,
                       attack_range=4, preferred_range=3, behavior="kiter", on_hit_effect="poison"),
    "siege_brute":  _e("siege brute", _R,  "enemy",   6, 2, ["monster_town"],      3, 5, behavior="tank"),
    "war_chief":    _e("war chief",   _C,  "settler", 7, 2, ["monster_town"],      5, None,
                       behavior="tank", traits=["berserks", "shields_ally"]),
    "plague_lord":  _e("plague lord", _M,  "shaman",  6, 1, ["monster_town"],      5, None,
                       attack_range=5, preferred_range=4, behavior="kiter",
                       on_hit_effect="poison", traits=["calls_reinforcements", "regen"]),

    # ── Named Elites (rarity="elite" — spawn only at player level 2+) ────────
    "the_iron_warden":  _e("the Iron Warden",  _BK, "enemy",  12, 2, ["dungeon","castle"],     5, None,
                           behavior="tank", traits=["shields_ally", "regen", "berserks"],
                           rarity="elite"),
    "vex_the_flayer":   _e("Vex the Flayer",   _C,  "settler", 9, 3, ["plains","badlands"],    4, None,
                           behavior="charger", traits=["berserks", "pack_bonus"],
                           moves_per_turn=2, rarity="elite"),
    "thornmother":      _e("the Thornmother",  (80,160,80),"beast",11,2,["forest","swamp"],     4, None,
                           behavior="tank", traits=["regen", "calls_reinforcements"],
                           on_hit_effect="poison", rarity="elite"),
    "ashcaller":        _e("Ashcaller",        (220,100,60),"shaman",7,2,["volcanic","desert"], 4, None,
                           attack_range=6, preferred_range=5, behavior="kiter",
                           on_hit_effect="burn", traits=["calls_reinforcements"],
                           rarity="elite"),
    "gravetide":        _e("Gravetide",        (140,110,200),"shaman",8,1,["ruins","cave"],     4, None,
                           attack_range=5, preferred_range=4, behavior="kiter",
                           on_hit_effect="poison", traits=["regen","calls_reinforcements"],
                           rarity="elite"),
    "coldfang":         _e("Coldfang",         (160,220,255),"beast",10,2,["tundra","mountain"],4, None,
                           behavior="charger", on_hit_effect="stun",
                           traits=["berserks"], moves_per_turn=2, rarity="elite"),
}


_BIOME_ALIASES = {
    "ossuary": "ruins",
    "mirrorwood": "forest",
    "stronghold": "castle",
}


def biome_pool(biome: str, tier: int, player_level: int = 1) -> list[str]:
    """Return list of catalog keys valid for this biome, tier, and player level."""
    biome = _BIOME_ALIASES.get(biome, biome)
    return [
        key for key, spec in ENEMY_CATALOG.items()
        if spec.get("rarity", "common") != "elite"
        and (not spec["biomes"] or biome in spec["biomes"])
        and spec["tier_min"] <= tier
        and (spec["tier_max"] is None or spec["tier_max"] >= tier)
    ] if player_level < 2 else [
        key for key, spec in ENEMY_CATALOG.items()
        if (not spec["biomes"] or biome in spec["biomes"])
        and spec["tier_min"] <= tier
        and (spec["tier_max"] is None or spec["tier_max"] >= tier)
    ]


def weighted_choice(rng: "random.Random", keys: list[str]) -> str:
    weights = [ENEMY_CATALOG[k]["weight"] for k in keys]
    total = sum(weights)
    r = rng.random() * total
    cumulative = 0
    for key, w in zip(keys, weights):
        cumulative += w
        if r < cumulative:
            return key
    return keys[-1]
