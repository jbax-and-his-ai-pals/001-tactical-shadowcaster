"""Skill registry and progression helpers."""

SKILL_REGISTRY = {
    # ── Combat ──────────────────────────────────────────────────────────────
    "swordsmanship": {
        "name": "Swordsmanship",
        "description": "Increases melee damage. At rank 4, grants a chance to parry incoming blows.",
        "max_rank": 5,
        "color": (220, 140, 100),
        "group": "Combat",
    },
    "archery": {
        "name": "Archery",
        "description": "Increases ranged damage. At rank 3, every fifth shot costs no ammo.",
        "max_rank": 5,
        "color": (160, 220, 140),
        "group": "Combat",
    },
    "toughness": {
        "name": "Toughness",
        "description": "Increases max HP by 3 per rank. At rank 3 and 5, reduces incoming damage by 1.",
        "max_rank": 5,
        "color": (200, 100, 100),
        "group": "Combat",
    },
    "stealth": {
        "name": "Stealth",
        "description": "First strike in each region deals bonus damage equal to your rank. At rank 5, autoexplore occasionally avoids triggering nearby enemies.",
        "max_rank": 5,
        "color": (120, 120, 180),
        "group": "Combat",
    },
    # ── Economy ─────────────────────────────────────────────────────────────
    "bartering": {
        "name": "Bartering",
        "description": "Reduces buy prices and increases sell prices. At rank 4+, unlocks higher-quality shop stock regardless of town attitude.",
        "max_rank": 5,
        "color": (220, 190, 80),
        "group": "Economy",
    },
    "diplomacy": {
        "name": "Diplomacy",
        "description": "Earn 10% more quest gold per rank. At rank 3+, attitude with towns builds faster.",
        "max_rank": 5,
        "color": (140, 200, 220),
        "group": "Economy",
    },
    "scavenging": {
        "name": "Scavenging",
        "description": "Enemies drop +1 gold per rank. Gem and curio drop rates improve. At rank 5, locked container drops are more common.",
        "max_rank": 5,
        "color": (180, 160, 120),
        "group": "Economy",
    },
    # ── Knowledge ───────────────────────────────────────────────────────────
    "lockpicking": {
        "name": "Lockpicking",
        "description": "Attempt to pick locks without a locksmith. Higher ranks open harder containers.",
        "max_rank": 5,
        "color": (190, 170, 120),
        "group": "Knowledge",
    },
    "herbalism": {
        "name": "Herbalism",
        "description": "Improved harvest yields and recognition of rare plants.",
        "max_rank": 5,
        "color": (120, 200, 140),
        "group": "Knowledge",
    },
    "alchemy": {
        "name": "Alchemy",
        "description": "Brew potions from herbs without a trader. Higher ranks improve yields and unlock advanced brews.",
        "max_rank": 5,
        "color": (180, 140, 220),
        "group": "Knowledge",
    },
    "arcana": {
        "name": "Arcana",
        "description": "Identifies item quality and affixes. At rank 5, grants bonuses in mystical regions and reveals hidden caches on the map.",
        "max_rank": 5,
        "color": (160, 180, 240),
        "group": "Knowledge",
    },
    "fieldcraft": {
        "name": "Fieldcraft",
        "description": "Better cache-finding, faster autoexplore, and awareness of hidden paths.",
        "max_rank": 5,
        "color": (140, 190, 220),
        "group": "Knowledge",
    },
}

SKILL_ORDER = [
    "swordsmanship", "archery", "toughness", "stealth",
    "bartering", "diplomacy", "scavenging",
    "lockpicking", "herbalism", "alchemy", "arcana", "fieldcraft",
]

SKILL_GROUPS = ["Combat", "Economy", "Knowledge"]


def rank_cost(target_rank: int) -> int:
    return target_rank


def total_cost_to_rank(target_rank: int) -> int:
    return sum(rank_cost(r) for r in range(1, target_rank + 1))


def skill_rank(player_skills: dict, skill_key: str) -> int:
    return player_skills.get(skill_key, 0)


def can_afford_next_rank(player_skills: dict, skill_points: int, skill_key: str) -> bool:
    current = skill_rank(player_skills, skill_key)
    spec = SKILL_REGISTRY.get(skill_key, {})
    max_rank = spec.get("max_rank", 5)
    if current >= max_rank:
        return False
    return skill_points >= rank_cost(current + 1)


def upgrade_skill(player_skills: dict, skill_key: str) -> tuple[int, int]:
    """Return (new_rank, cost). Caller must subtract cost from skill_points."""
    current = player_skills.get(skill_key, 0)
    next_rank = current + 1
    cost = rank_cost(next_rank)
    player_skills[skill_key] = next_rank
    return next_rank, cost
