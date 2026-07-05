"""
Item catalog: all consumable item definitions.

Each entry defines a consumable's name, family, rarity, effects, flavor description,
biome affinities (for drop weighting), and gold prices.

Effects are a list of dicts:
  {"type": "restore_health",         "amount": N}
  {"type": "restore_max_health",     "amount": N}
  {"type": "regen",                  "turns": N}
  {"type": "cure_all"}
  {"type": "cure_poison"}
  {"type": "cure_burn"}
  {"type": "ward",                   "duration": N}
  {"type": "resist_poison",          "turns": N}
  {"type": "resist_fire",            "turns": N}
  {"type": "fortify_attack",         "amount": N, "turns": N}
  {"type": "fortify_defense",        "amount": N, "turns": N}
  {"type": "fortify_speed",          "amount": N, "turns": N}   # haste reduction in ms per turn
  {"type": "fortify_light",          "amount": N, "turns": N}

Rarity:
  common    — floor drops anywhere; trader always stocks
  uncommon  — biome-matched floor drops; trader stocks at supply depth 1+
  rare      — landmark rewards, deep dungeon caches; never at traders
  legendary — bottom-floor caches, named-site clears only; never at traders
"""

_HEAL  = (200, 100, 120)
_TONIC = (100, 160, 220)
_TINC  = (160, 130, 220)
_TRNK  = (220, 190, 110)

ITEM_CATALOG: dict[str, dict] = {

    # ── Potions ────────────────────────────────────────────────────────────
    "medkit": {
        "name": "Healing Potion",
        "family": "potion",
        "rarity": "common",
        "effects": [{"type": "restore_health", "amount": 4}],
        "color": _HEAL,
        "marker": "vitality",
        "description": "Restores 4 health.",
        "biomes": [],
        "buy_price": 10,
        "sell_price": 5,
    },
    "healing_draught": {
        "name": "Healing Draught",
        "family": "potion",
        "rarity": "uncommon",
        "effects": [{"type": "restore_health", "amount": 8}, {"type": "regen", "turns": 4}],
        "color": _HEAL,
        "marker": "vitality",
        "description": "Restores 8 health and regenerates 1 HP per turn for 4 turns.",
        "biomes": ["forest", "farmland", "plains"],
        "buy_price": 0,
        "sell_price": 12,
    },
    "elixir_of_vitality": {
        "name": "Elixir of Vitality",
        "family": "potion",
        "rarity": "rare",
        "effects": [{"type": "restore_max_health", "amount": 1}, {"type": "restore_health", "amount": 999}],
        "color": _HEAL,
        "marker": "vitality",
        "description": "Permanently increases max HP by 1 and fully restores health.",
        "biomes": [],
        "buy_price": 0,
        "sell_price": 0,
    },

    # ── Tonics ─────────────────────────────────────────────────────────────
    "tonic": {
        "name": "Ward Tonic",
        "family": "tonic",
        "rarity": "common",
        "effects": [{"type": "ward", "duration": 4}, {"type": "cure_all"}],
        "color": _TONIC,
        "marker": "power",
        "description": "Clears all statuses and grants 4 turns of ward.",
        "biomes": [],
        "buy_price": 15,
        "sell_price": 7,
    },
    "antidote": {
        "name": "Antidote",
        "family": "tonic",
        "rarity": "common",
        "effects": [{"type": "cure_poison"}],
        "color": _TONIC,
        "marker": "power",
        "description": "Immediately cures poison.",
        "biomes": ["swamp", "forest", "cave"],
        "buy_price": 8,
        "sell_price": 4,
    },
    "fireward_tonic": {
        "name": "Fireward Tonic",
        "family": "tonic",
        "rarity": "uncommon",
        "effects": [{"type": "cure_burn"}, {"type": "resist_fire", "turns": 6}],
        "color": _TONIC,
        "marker": "power",
        "description": "Cures burn and grants 6 turns of fire resistance.",
        "biomes": ["volcanic", "desert", "badlands"],
        "buy_price": 0,
        "sell_price": 10,
    },
    "panacea": {
        "name": "Panacea",
        "family": "tonic",
        "rarity": "rare",
        "effects": [
            {"type": "cure_all"},
            {"type": "ward", "duration": 6},
            {"type": "resist_poison", "turns": 8},
            {"type": "resist_fire", "turns": 8},
        ],
        "color": _TONIC,
        "marker": "power",
        "description": "Clears all statuses, grants ward, and provides 8 turns of dual resistance.",
        "biomes": [],
        "buy_price": 0,
        "sell_price": 0,
    },

    # ── Tinctures ──────────────────────────────────────────────────────────
    "attack_tincture": {
        "name": "Attack Tincture",
        "family": "tincture",
        "rarity": "uncommon",
        "effects": [{"type": "fortify_attack", "amount": 1, "turns": 8}],
        "color": _TINC,
        "marker": "power",
        "description": "Fortifies attack by 1 for 8 turns.",
        "biomes": ["castle", "dungeon", "ruins", "badlands"],
        "buy_price": 0,
        "sell_price": 10,
    },
    "defender_draft": {
        "name": "Defender's Draft",
        "family": "tincture",
        "rarity": "uncommon",
        "effects": [{"type": "fortify_defense", "amount": 2, "turns": 6}],
        "color": _TINC,
        "marker": "power",
        "description": "Fortifies defense by 2 for 6 turns.",
        "biomes": ["dungeon", "cave", "mountain", "tundra"],
        "buy_price": 0,
        "sell_price": 10,
    },
    "swiftness_vial": {
        "name": "Swiftness Vial",
        "family": "tincture",
        "rarity": "uncommon",
        "effects": [{"type": "fortify_speed", "amount": 30, "turns": 10}],
        "color": _TINC,
        "marker": "power",
        "description": "Increases autoexplore speed for 10 turns.",
        "biomes": ["plains", "farmland", "desert"],
        "buy_price": 0,
        "sell_price": 10,
    },
    "seer_oil": {
        "name": "Seer's Oil",
        "family": "tincture",
        "rarity": "rare",
        "effects": [{"type": "fortify_light", "amount": 3, "turns": 8}],
        "color": _TINC,
        "marker": "power",
        "description": "Extends your field of view by 3 tiles for 8 turns.",
        "biomes": [],
        "buy_price": 0,
        "sell_price": 0,
    },

    # ── Trinkets (equippable — Level 2 unlock) ────────────────────────────────
    "lucky_charm": {
        "name": "Lucky Charm",
        "family": "trinket",
        "rarity": "uncommon",
        "effects": [],
        "trinket_bonus": {"melee": 1},
        "color": _TRNK,
        "marker": "power",
        "description": "A worn charm. +1 melee damage while equipped.",
        "biomes": ["plains", "farmland", "forest"],
        "buy_price": 0,
        "sell_price": 15,
    },
    "shard_of_warding": {
        "name": "Shard of Warding",
        "family": "trinket",
        "rarity": "uncommon",
        "effects": [],
        "trinket_bonus": {"defense": 1},
        "color": _TRNK,
        "marker": "power",
        "description": "A protective shard. +1 defense while equipped.",
        "biomes": ["ruins", "dungeon", "cave"],
        "buy_price": 0,
        "sell_price": 15,
    },
    "lantern_lens": {
        "name": "Lantern Lens",
        "family": "trinket",
        "rarity": "uncommon",
        "effects": [],
        "trinket_bonus": {"light": 2},
        "color": _TRNK,
        "marker": "power",
        "description": "A focusing lens. +2 FOV radius while equipped.",
        "biomes": ["cave", "dungeon", "maze"],
        "buy_price": 0,
        "sell_price": 15,
    },
    "bone_sigil": {
        "name": "Bone Sigil",
        "family": "trinket",
        "rarity": "rare",
        "effects": [],
        "trinket_bonus": {"melee": 1, "defense": 1},
        "color": _TRNK,
        "marker": "power",
        "description": "An ancient bone carving. +1 melee and +1 defense while equipped.",
        "biomes": ["ossuary", "ruins"],
        "buy_price": 0,
        "sell_price": 0,
    },
    "mirrorleaf": {
        "name": "Mirrorleaf",
        "family": "trinket",
        "rarity": "legendary",
        "effects": [],
        "trinket_bonus": {"light": 3, "defense": 1},
        "color": (180, 230, 200),
        "marker": "power",
        "description": "A leaf that never wilts, from a wood no map shows. +3 FOV and +1 defense.",
        "biomes": ["mirrorwood"],
        "buy_price": 0,
        "sell_price": 0,
    },
}

# Items that traders never sell (Rare and Legendary)
NEVER_SOLD = {key for key, v in ITEM_CATALOG.items() if v["rarity"] in ("rare", "legendary")}

# Common items always available at traders
TRADER_COMMON = [key for key, v in ITEM_CATALOG.items() if v["rarity"] == "common"]

# Uncommon items available at traders with supply depth 1+
TRADER_UNCOMMON = [key for key, v in ITEM_CATALOG.items() if v["rarity"] == "uncommon"]

# Items that can drop in biome-appropriate caches (common + uncommon)
DROPPABLE = [key for key, v in ITEM_CATALOG.items() if v["rarity"] in ("common", "uncommon")]
