"""Static data tables for procedural equipment generation."""

BASE_WEAPONS = {
    "knife":        {"name": "Knife",           "melee": 1, "ranged": 0, "range_bonus": 0, "base_price": 2},
    "dagger":       {"name": "Dagger",          "melee": 2, "ranged": 0, "range_bonus": 0, "base_price": 3},
    "shortsword":   {"name": "Shortsword",      "melee": 2, "ranged": 0, "range_bonus": 0, "base_price": 4},
    "hand_axe":     {"name": "Hand Axe",        "melee": 2, "ranged": 1, "range_bonus": 0, "base_price": 4},
    "club":         {"name": "Club",            "melee": 2, "ranged": 0, "range_bonus": 0, "base_price": 2},
    "mace":         {"name": "Mace",            "melee": 3, "ranged": 0, "range_bonus": 0, "base_price": 5},
    "longsword":    {"name": "Longsword",       "melee": 3, "ranged": 0, "range_bonus": 0, "base_price": 6},
    "broadsword":   {"name": "Broadsword",      "melee": 3, "ranged": 0, "range_bonus": 0, "base_price": 6},
    "battle_axe":   {"name": "Battle Axe",      "melee": 4, "ranged": 0, "range_bonus": 0, "base_price": 7},
    "warhammer":    {"name": "Warhammer",       "melee": 4, "ranged": 0, "range_bonus": 0, "base_price": 7},
    "spear":        {"name": "Spear",           "melee": 2, "ranged": 2, "range_bonus": 0, "base_price": 5},
    "halberd":      {"name": "Halberd",         "melee": 4, "ranged": 1, "range_bonus": 0, "base_price": 9},
    "glaive":       {"name": "Glaive",          "melee": 3, "ranged": 1, "range_bonus": 0, "base_price": 8},
    "shortbow":     {"name": "Shortbow",        "melee": 0, "ranged": 2, "range_bonus": 0, "base_price": 3},
    "hunting_bow":  {"name": "Hunting Bow",     "melee": 0, "ranged": 3, "range_bonus": 1, "base_price": 5},
    "longbow":      {"name": "Longbow",         "melee": 0, "ranged": 4, "range_bonus": 1, "base_price": 7},
    "crossbow":     {"name": "Crossbow",        "melee": 0, "ranged": 4, "range_bonus": 0, "base_price": 7},
    "sling":        {"name": "Sling",           "melee": 0, "ranged": 2, "range_bonus": 1, "base_price": 2},
    "javelin":      {"name": "Javelin",         "melee": 1, "ranged": 3, "range_bonus": 0, "base_price": 4},
    "throwing_axe": {"name": "Throwing Axe",   "melee": 2, "ranged": 2, "range_bonus": 0, "base_price": 5},
}

BASE_ARMORS = {
    "rags":         {"name": "Rags",            "defense": 0, "ranged_pen": 0, "fov_pen": 0, "base_price": 1},
    "padded_vest":  {"name": "Padded Vest",     "defense": 1, "ranged_pen": 0, "fov_pen": 0, "base_price": 2},
    "travel_cloak": {"name": "Travel Cloak",    "defense": 1, "ranged_pen": 0, "fov_pen": 0, "base_price": 2},
    "leather_armor":{"name": "Leather Armor",   "defense": 2, "ranged_pen": 0, "fov_pen": 0, "base_price": 4},
    "studded_leather":{"name": "Studded Leather","defense": 3, "ranged_pen": 0, "fov_pen": 0, "base_price": 5},
    "hide_armor":   {"name": "Hide Armor",      "defense": 3, "ranged_pen": 0, "fov_pen": 0, "base_price": 5},
    "brigandine":   {"name": "Brigandine",      "defense": 4, "ranged_pen": -1, "fov_pen": 0, "base_price": 7},
    "chain_mail":   {"name": "Chain Mail",      "defense": 4, "ranged_pen": -1, "fov_pen": 0, "base_price": 7},
    "scale_mail":   {"name": "Scale Mail",      "defense": 5, "ranged_pen": -1, "fov_pen": -1, "base_price": 9},
    "plate_coat":   {"name": "Plate Coat",      "defense": 5, "ranged_pen": -2, "fov_pen": -1, "base_price": 10},
    "war_plate":    {"name": "War Plate",       "defense": 6, "ranged_pen": -3, "fov_pen": -2, "base_price": 12},
}

QUALITY_TIERS = ["damaged", "normal", "superior", "quality", "masterwork"]

# Multiplier applied to base stats and price
QUALITY_MULT = {
    "damaged":    0.7,
    "normal":     1.0,
    "superior":   1.2,
    "quality":    1.5,
    "masterwork": 2.0,
}

# Stat bonus range per quality tier — (min_bonus, max_bonus) added on top of base
QUALITY_STAT_RANGE = {
    "damaged":    (0, 0),
    "normal":     (0, 0),
    "superior":   (0, 1),
    "quality":    (1, 2),
    "masterwork": (2, 3),
}

# Weight tables for quality selection — indexed by iLvl breakpoints
# Format: {max_ilvl_inclusive: [damaged, normal, superior, quality, masterwork]}
QUALITY_WEIGHTS = [
    (3,  [50, 40, 8,  2,  0]),
    (6,  [30, 45, 17, 7,  1]),
    (9,  [15, 42, 28, 13, 2]),
    (13, [8,  35, 32, 20, 5]),
    (99, [4,  28, 33, 26, 9]),
]

PREFIXES = {
    "keen":        {"name": "Keen",        "melee_bonus": (1, 3),  "ranged_bonus": (0, 0)},
    "brutal":      {"name": "Brutal",      "melee_bonus": (2, 5),  "ranged_bonus": (0, 0)},
    "serrated":    {"name": "Serrated",    "melee_bonus": (1, 4),  "on_hit_bleed": True},
    "savage":      {"name": "Savage",      "melee_bonus": (2, 6),  "ranged_bonus": (0, 0)},
    "true":        {"name": "True",        "melee_bonus": (1, 2),  "ranged_bonus": (1, 2)},
    "longshot":    {"name": "Longshot",    "ranged_bonus": (1, 3), "range_bonus": (1, 2)},
    "accurate":    {"name": "Accurate",    "ranged_bonus": (2, 5), "ranged_bonus2": (0, 0)},
    "balanced":    {"name": "Balanced",    "melee_bonus": (1, 2),  "ranged_bonus": (1, 2)},
    "weighted":    {"name": "Weighted",    "melee_bonus": (2, 4),  "ranged_bonus": (0, 0)},
    "stalwart":    {"name": "Stalwart",    "defense_bonus": (1, 3)},
    "fortified":   {"name": "Fortified",   "defense_bonus": (2, 5)},
    "resilient":   {"name": "Resilient",   "defense_bonus": (1, 4), "max_hp_bonus": (1, 3)},
    "illuminating":{"name": "Illuminating","fov_bonus": (1, 2)},
    "longreach":   {"name": "Longreach",   "range_bonus": (1, 3)},
    "swift":       {"name": "Swift",       "speed_bonus": (1, 2)},
    "nimble":      {"name": "Nimble",      "speed_bonus": (1, 3),  "fov_bonus": (1, 1)},
    "venomous":    {"name": "Venomous",    "on_hit_poison": True},
    "flaming":     {"name": "Flaming",     "on_hit_fire": True,    "melee_bonus": (1, 2)},
    "disrupting":  {"name": "Disrupting",  "melee_bonus": (1, 3)},
    "sapping":     {"name": "Sapping",     "ranged_bonus": (1, 2), "on_hit_slow": True},
    "hungering":   {"name": "Hungering",   "on_kill_heal": (1, 3)},
    "warding":     {"name": "Warding",     "defense_bonus": (1, 2), "max_hp_bonus": (2, 5)},
    "mending":     {"name": "Mending",     "max_hp_bonus": (3, 8)},
    "invigorating":{"name": "Invigorating","max_hp_bonus": (2, 6),  "speed_bonus": (1, 1)},
}

SUFFIXES = {
    "of_the_bear":    {"name": "of the Bear",    "max_hp_bonus": (4, 10)},
    "of_vigor":       {"name": "of Vigor",       "max_hp_bonus": (2, 6)},
    "of_endurance":   {"name": "of Endurance",   "max_hp_bonus": (3, 8),  "defense_bonus": (1, 2)},
    "of_the_wolf":    {"name": "of the Wolf",    "speed_bonus": (1, 3)},
    "of_the_warrior": {"name": "of the Warrior", "melee_bonus": (2, 5)},
    "of_the_hawk":    {"name": "of the Hawk",    "ranged_bonus": (2, 5),  "fov_bonus": (1, 2)},
    "of_the_hunt":    {"name": "of the Hunt",    "ranged_bonus": (1, 4),  "range_bonus": (1, 2)},
    "of_defense":     {"name": "of Defense",     "defense_bonus": (2, 4)},
    "of_fortification":{"name": "of Fortification","defense_bonus": (3, 6)},
    "of_protection":  {"name": "of Protection",  "defense_bonus": (1, 3),  "max_hp_bonus": (2, 5)},
    "of_the_fox":     {"name": "of the Fox",     "speed_bonus": (2, 4),   "fov_bonus": (1, 2)},
    "of_light":       {"name": "of Light",       "fov_bonus": (2, 4)},
    "of_brilliance":  {"name": "of Brilliance",  "fov_bonus": (3, 5)},
    "of_swiftness":   {"name": "of Swiftness",   "speed_bonus": (1, 2)},
    "of_haste":       {"name": "of Haste",       "speed_bonus": (2, 4)},
    "of_reach":       {"name": "of Reach",       "range_bonus": (2, 4)},
    "of_the_shadow":  {"name": "of the Shadow",  "speed_bonus": (1, 2),   "fov_bonus": (1, 1)},
    "of_the_stalker": {"name": "of the Stalker", "ranged_bonus": (1, 3),  "range_bonus": (1, 2)},
    "of_warding":     {"name": "of Warding",     "on_enter_ward": True},
    "of_vengeance":   {"name": "of Vengeance",   "low_hp_melee_bonus": (2, 5)},
    "of_recovery":    {"name": "of Recovery",    "on_enter_heal": (1, 2)},
    "of_resistance":  {"name": "of Resistance",  "defense_bonus": (1, 2)},
    "of_absorption":  {"name": "of Absorption",  "defense_bonus": (2, 5),  "max_hp_bonus": (1, 3)},
    "of_the_deep":    {"name": "of the Deep",    "melee_bonus": (1, 3),   "ranged_bonus": (1, 3)},
}

# iLvl threshold above which each affix key becomes eligible
PREFIX_MIN_ILVL = {
    "keen": 1, "brutal": 5, "serrated": 3, "savage": 7, "true": 4,
    "longshot": 2, "accurate": 3, "balanced": 1, "weighted": 2, "stalwart": 1,
    "fortified": 4, "resilient": 4, "illuminating": 1, "longreach": 2, "swift": 1,
    "nimble": 3, "venomous": 5, "flaming": 6, "disrupting": 3, "sapping": 4,
    "hungering": 6, "warding": 5, "mending": 4, "invigorating": 5,
}

SUFFIX_MIN_ILVL = {
    "of_the_bear": 5, "of_vigor": 2, "of_endurance": 4, "of_the_wolf": 3,
    "of_the_warrior": 4, "of_the_hawk": 3, "of_the_hunt": 3, "of_defense": 1,
    "of_fortification": 5, "of_protection": 3, "of_the_fox": 4, "of_light": 1,
    "of_brilliance": 5, "of_swiftness": 1, "of_haste": 4, "of_reach": 3,
    "of_the_shadow": 3, "of_the_stalker": 5, "of_warding": 6, "of_vengeance": 6,
    "of_recovery": 5, "of_resistance": 2, "of_absorption": 6, "of_the_deep": 7,
}

# Chance that a prefix/suffix is added; increases with iLvl but stays low
# Format: (max_ilvl, prefix_chance, suffix_chance)
AFFIX_CHANCE_TABLE = [
    (3,  0.10, 0.05),
    (6,  0.18, 0.10),
    (9,  0.25, 0.15),
    (13, 0.32, 0.22),
    (99, 0.40, 0.30),
]
