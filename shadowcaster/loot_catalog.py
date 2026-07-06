"""
Gem and curio definitions — loot items with no combat role, sold for gold.

Gems  : category="gem"   — precious stones, tiered by rarity
Curios: category="curio" — metallic everyday objects, tiered by metal value
"""

# ── Gems ──────────────────────────────────────────────────────────────────────
# tier: common / uncommon / rare / legendary
# sell: gold value at market

GEMS: dict[str, dict] = {
    # Common — found everywhere, low value
    "gem_quartz":      {"name": "Quartz",          "tier": "common",    "sell": 3,  "color": (218, 214, 232)},
    "gem_onyx":        {"name": "Onyx",             "tier": "common",    "sell": 4,  "color": (68,  60,  78)},
    "gem_jasper":      {"name": "Jasper",           "tier": "common",    "sell": 4,  "color": (188, 104, 80)},
    "gem_carnelian":   {"name": "Carnelian",        "tier": "common",    "sell": 5,  "color": (214, 90,  58)},
    "gem_agate":       {"name": "Agate",            "tier": "common",    "sell": 5,  "color": (158, 138, 182)},

    # Uncommon — floor 3+, moderate value
    "gem_amethyst":    {"name": "Amethyst",         "tier": "uncommon",  "sell": 10, "color": (148, 80,  200)},
    "gem_garnet":      {"name": "Garnet",           "tier": "uncommon",  "sell": 10, "color": (178, 28,  52)},
    "gem_topaz":       {"name": "Topaz",            "tier": "uncommon",  "sell": 12, "color": (222, 182, 58)},
    "gem_tourmaline":  {"name": "Tourmaline",       "tier": "uncommon",  "sell": 12, "color": (58,  162, 102)},
    "gem_jade":        {"name": "Jade",             "tier": "uncommon",  "sell": 14, "color": (78,  182, 122)},
    "gem_moonstone":   {"name": "Moonstone",        "tier": "uncommon",  "sell": 14, "color": (198, 210, 232)},

    # Rare — floor 5+, high value
    "gem_sapphire":    {"name": "Sapphire",         "tier": "rare",      "sell": 25, "color": (58,  98,  222)},
    "gem_ruby":        {"name": "Ruby",             "tier": "rare",      "sell": 28, "color": (222, 28,  58)},
    "gem_emerald":     {"name": "Emerald",          "tier": "rare",      "sell": 30, "color": (28,  202, 82)},

    # Legendary — deep delves only, very high value
    "gem_diamond":     {"name": "Diamond",          "tier": "legendary", "sell": 60, "color": (228, 240, 255)},
    "gem_bloodstone":  {"name": "Bloodstone",       "tier": "legendary", "sell": 55, "color": (38,  118, 62)},
}

# Gems available by minimum floor depth
GEMS_BY_FLOOR: list[tuple[int, str]] = [
    # (min_floor, key)  — listed most restricted first for drop logic
    (8, "gem_diamond"),
    (8, "gem_bloodstone"),
    (5, "gem_sapphire"),
    (5, "gem_ruby"),
    (5, "gem_emerald"),
    (3, "gem_amethyst"),
    (3, "gem_garnet"),
    (3, "gem_topaz"),
    (3, "gem_tourmaline"),
    (3, "gem_jade"),
    (3, "gem_moonstone"),
    (1, "gem_quartz"),
    (1, "gem_onyx"),
    (1, "gem_jasper"),
    (1, "gem_carnelian"),
    (1, "gem_agate"),
]

# Weight by tier for random selection (higher = more likely)
GEM_TIER_WEIGHT = {"common": 55, "uncommon": 30, "rare": 12, "legendary": 3}


# ── Curios ────────────────────────────────────────────────────────────────────
# Metallic household objects — flavor loot worth a few coins each.
# sell: base gold value (no combat use)

_CU  = (178, 98,  58)   # copper
_BR  = (158, 112, 58)   # bronze
_PW  = (138, 138, 148)  # pewter
_SI  = (198, 202, 222)  # silver
_BS  = (202, 172, 78)   # brass
_GO  = (232, 192, 58)   # gold
_IR  = (120, 118, 114)  # iron

CURIOS: dict[str, dict] = {
    # Copper (cheapest)
    "curio_copper_cup":         {"name": "Copper Cup",          "sell": 2,  "color": _CU},
    "curio_copper_plate":       {"name": "Copper Plate",        "sell": 2,  "color": _CU},
    "curio_copper_fork":        {"name": "Copper Fork",         "sell": 1,  "color": _CU},
    "curio_copper_spoon":       {"name": "Copper Spoon",        "sell": 1,  "color": _CU},
    "curio_copper_bowl":        {"name": "Copper Bowl",         "sell": 2,  "color": _CU},

    # Iron
    "curio_iron_mug":           {"name": "Iron Mug",            "sell": 2,  "color": _IR},
    "curio_iron_clasp":         {"name": "Iron Clasp",          "sell": 1,  "color": _IR},
    "curio_iron_buckle":        {"name": "Iron Buckle",         "sell": 2,  "color": _IR},

    # Bronze
    "curio_bronze_flask":       {"name": "Bronze Flask",        "sell": 3,  "color": _BR},
    "curio_bronze_bowl":        {"name": "Bronze Bowl",         "sell": 3,  "color": _BR},
    "curio_bronze_clasp":       {"name": "Bronze Clasp",        "sell": 2,  "color": _BR},
    "curio_bronze_buckle":      {"name": "Bronze Buckle",       "sell": 2,  "color": _BR},
    "curio_bronze_candlestick": {"name": "Bronze Candlestick",  "sell": 4,  "color": _BR},

    # Pewter
    "curio_pewter_mug":         {"name": "Pewter Mug",          "sell": 3,  "color": _PW},
    "curio_pewter_plate":       {"name": "Pewter Plate",        "sell": 4,  "color": _PW},
    "curio_pewter_bowl":        {"name": "Pewter Bowl",         "sell": 3,  "color": _PW},
    "curio_pewter_cup":         {"name": "Pewter Cup",          "sell": 3,  "color": _PW},
    "curio_pewter_candlestick": {"name": "Pewter Candlestick",  "sell": 5,  "color": _PW},

    # Brass
    "curio_brass_candlestick":  {"name": "Brass Candlestick",   "sell": 6,  "color": _BS},
    "curio_brass_buckle":       {"name": "Brass Buckle",        "sell": 4,  "color": _BS},
    "curio_brass_clasp":        {"name": "Brass Clasp",         "sell": 4,  "color": _BS},
    "curio_brass_goblet":       {"name": "Brass Goblet",        "sell": 6,  "color": _BS},
    "curio_brass_flask":        {"name": "Brass Flask",         "sell": 5,  "color": _BS},

    # Silver
    "curio_silver_cup":         {"name": "Silver Cup",          "sell": 8,  "color": _SI},
    "curio_silver_flask":       {"name": "Silver Flask",        "sell": 8,  "color": _SI},
    "curio_silver_plate":       {"name": "Silver Plate",        "sell": 10, "color": _SI},
    "curio_silver_spoon":       {"name": "Silver Spoon",        "sell": 6,  "color": _SI},
    "curio_silver_fork":        {"name": "Silver Fork",         "sell": 6,  "color": _SI},
    "curio_silver_pin":         {"name": "Silver Pin",          "sell": 5,  "color": _SI},
    "curio_silver_ring":        {"name": "Silver Ring",         "sell": 7,  "color": _SI},
    "curio_silver_bell":        {"name": "Silver Bell",         "sell": 8,  "color": _SI},
    "curio_silver_goblet":      {"name": "Silver Goblet",       "sell": 10, "color": _SI},

    # Gold (most valuable)
    "curio_gold_cup":           {"name": "Gold Cup",            "sell": 20, "color": _GO},
    "curio_gold_ring":          {"name": "Gold Ring",           "sell": 15, "color": _GO},
    "curio_gold_pin":           {"name": "Gold Pin",            "sell": 12, "color": _GO},
    "curio_gold_fork":          {"name": "Gold Fork",           "sell": 14, "color": _GO},
    "curio_gold_goblet":        {"name": "Gold Goblet",         "sell": 25, "color": _GO},
    "curio_gold_spoon":         {"name": "Gold Spoon",          "sell": 12, "color": _GO},
    "curio_gold_plate":         {"name": "Gold Plate",          "sell": 18, "color": _GO},
}

# Curio pools by drop weight (common metals appear more often)
CURIO_POOL_COMMON = [k for k in CURIOS if k.startswith(("curio_copper_", "curio_iron_", "curio_bronze_", "curio_pewter_"))]
CURIO_POOL_UNCOMMON = [k for k in CURIOS if k.startswith("curio_brass_")]
CURIO_POOL_SILVER = [k for k in CURIOS if k.startswith("curio_silver_")]
CURIO_POOL_GOLD = [k for k in CURIOS if k.startswith("curio_gold_")]
