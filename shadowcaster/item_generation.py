"""Procedural equipment generation (Diablo-style)."""

from __future__ import annotations

import random
import uuid

from .item_generation_data import (
    AFFIX_CHANCE_TABLE,
    BASE_ARMORS,
    BASE_WEAPONS,
    PREFIX_MIN_ILVL,
    PREFIXES,
    QUALITY_MULT,
    QUALITY_STAT_RANGE,
    QUALITY_TIERS,
    QUALITY_WEIGHTS,
    SUFFIX_MIN_ILVL,
    SUFFIXES,
)

# ── Color constants ──────────────────────────────────────────────────────────
COLOR_WEAPON = (200, 180, 100)
COLOR_ARMOR  = (120, 160, 200)

# Quality label colors for UI display
QUALITY_COLORS = {
    "damaged":    (130, 110, 90),
    "normal":     (200, 200, 200),
    "superior":   (140, 210, 140),
    "quality":    (100, 160, 240),
    "masterwork": (220, 160, 50),
}


def compute_item_level(danger_tier: int, region_depth: int = 1) -> int:
    """iLvl = danger_tier (primary) + small bonus for deep dungeons."""
    depth_bonus = max(0, region_depth - 1)
    return min(15, danger_tier + depth_bonus)


def _roll_scaled(rng: random.Random, low: int, high: int, ilvl: int) -> int:
    """Biased roll: most results cluster near low end; high values only at high iLvl."""
    if low >= high:
        return low
    reach = low + int((high - low) * (ilvl / 15.0))
    reach = max(low, min(high, reach))
    return min(rng.randint(low, reach), rng.randint(low, reach))


def _pick_quality_tier(rng: random.Random, ilvl: int) -> str:
    weights = QUALITY_WEIGHTS[-1][1]
    for max_ilvl, w in QUALITY_WEIGHTS:
        if ilvl <= max_ilvl:
            weights = w
            break
    total = sum(weights)
    roll = rng.randint(0, total - 1)
    cumulative = 0
    for tier, w in zip(QUALITY_TIERS, weights):
        cumulative += w
        if roll < cumulative:
            return tier
    return "normal"


def _lookup_affix_chances(ilvl: int):
    for max_ilvl, p_chance, s_chance in AFFIX_CHANCE_TABLE:
        if ilvl <= max_ilvl:
            return p_chance, s_chance
    return AFFIX_CHANCE_TABLE[-1][1], AFFIX_CHANCE_TABLE[-1][2]


def _pick_prefix(rng: random.Random, ilvl: int):
    eligible = [k for k, min_il in PREFIX_MIN_ILVL.items() if ilvl >= min_il]
    return rng.choice(eligible) if eligible else None


def _pick_suffix(rng: random.Random, ilvl: int):
    eligible = [k for k, min_il in SUFFIX_MIN_ILVL.items() if ilvl >= min_il]
    return rng.choice(eligible) if eligible else None


def _apply_mods(mods: dict, rng: random.Random, ilvl: int) -> dict:
    """Convert affix mod spec into concrete rolled values."""
    result = {}
    for k, v in mods.items():
        if isinstance(v, tuple) and len(v) == 2:
            lo, hi = v
            result[k] = _roll_scaled(rng, lo, hi, ilvl)
        elif isinstance(v, bool):
            result[k] = v
    return result


def _build_item_mods(prefix_key, suffix_key, rng, ilvl) -> dict:
    combined: dict = {}
    for key, source in [(prefix_key, PREFIXES), (suffix_key, SUFFIXES)]:
        if key is None:
            continue
        raw = source.get(key, {})
        rolled = _apply_mods(raw, rng, ilvl)
        for k, v in rolled.items():
            if k == "name":
                continue
            if isinstance(v, int) and k in combined and isinstance(combined[k], int):
                combined[k] = combined[k] + v
            else:
                combined[k] = v
    return combined


def _build_display_name(base_name: str, quality: str, prefix_key, suffix_key) -> str:
    parts = []
    if prefix_key:
        parts.append(PREFIXES[prefix_key]["name"])
    parts.append(base_name)
    if quality != "normal":
        parts.append(f"[{quality.capitalize()}]")
    if suffix_key:
        parts.append(SUFFIXES[suffix_key]["name"])
    return " ".join(parts)


def _compute_sell_price(base_price: int, quality: str, mods: dict) -> int:
    mult = QUALITY_MULT.get(quality, 1.0)
    stat_value = sum(v for v in mods.values() if isinstance(v, int) and v > 0)
    return max(1, int(base_price * mult) + stat_value)


def _unique_key(base_key: str) -> str:
    return f"{base_key}_{uuid.uuid4().hex[:6]}"


def generate_weapon(rng: random.Random, ilvl: int, base_key: str | None = None) -> dict:
    """Return a dict describing a generated weapon item (pass to add_item as **kwargs)."""
    if base_key is None:
        base_key = rng.choice(list(BASE_WEAPONS.keys()))
    base = BASE_WEAPONS[base_key]
    quality = _pick_quality_tier(rng, ilvl)
    q_stat_lo, q_stat_hi = QUALITY_STAT_RANGE[quality]
    q_bonus = _roll_scaled(rng, q_stat_lo, q_stat_hi, ilvl)

    p_chance, s_chance = _lookup_affix_chances(ilvl)
    prefix_key = _pick_prefix(rng, ilvl) if rng.random() < p_chance else None
    suffix_key = _pick_suffix(rng, ilvl) if rng.random() < s_chance else None

    mods = _build_item_mods(prefix_key, suffix_key, rng, ilvl)

    melee_bonus  = base["melee"]  + q_bonus + mods.pop("melee_bonus", 0)
    ranged_bonus = base["ranged"] + q_bonus + mods.pop("ranged_bonus", 0)
    range_bonus  = base["range_bonus"] + mods.pop("range_bonus", 0)

    name      = _build_display_name(base["name"], quality, prefix_key, suffix_key)
    sell      = _compute_sell_price(base["base_price"], quality, mods)
    item_key  = _unique_key(base_key)

    return {
        "key": item_key,
        "name": name,
        "category": "weapon",
        "color": COLOR_WEAPON,
        "marker": "weapon",
        "description": f"{quality.capitalize()} {base['name']}.",
        "melee_bonus": melee_bonus,
        "ranged_bonus": ranged_bonus,
        "range_bonus": range_bonus,
        "max_hp_bonus": mods.pop("max_hp_bonus", 0),
        "fov_bonus": mods.pop("fov_bonus", 0),
        "speed_bonus": mods.pop("speed_bonus", 0),
        "on_kill_heal": mods.pop("on_kill_heal", 0),
        "low_hp_melee_bonus": mods.pop("low_hp_melee_bonus", 0),
        "on_hit_effect": {k: v for k, v in mods.items() if k.startswith("on_hit_")},
        "passive_effects": {k: v for k, v in mods.items() if k.startswith("on_enter_")},
        "sell_price": sell,
        "quality": quality,
        "prefix_key": prefix_key,
        "suffix_key": suffix_key,
        "base_key": base_key,
        "item_level": ilvl,
    }


def generate_armor(rng: random.Random, ilvl: int, base_key: str | None = None) -> dict:
    """Return a dict describing a generated armor item."""
    if base_key is None:
        base_key = rng.choice(list(BASE_ARMORS.keys()))
    base = BASE_ARMORS[base_key]
    quality = _pick_quality_tier(rng, ilvl)
    q_stat_lo, q_stat_hi = QUALITY_STAT_RANGE[quality]
    q_bonus = _roll_scaled(rng, q_stat_lo, q_stat_hi, ilvl)

    p_chance, s_chance = _lookup_affix_chances(ilvl)
    prefix_key = _pick_prefix(rng, ilvl) if rng.random() < p_chance else None
    suffix_key = _pick_suffix(rng, ilvl) if rng.random() < s_chance else None

    mods = _build_item_mods(prefix_key, suffix_key, rng, ilvl)

    defense_bonus  = base["defense"]    + q_bonus + mods.pop("defense_bonus", 0)
    ranged_penalty = base["ranged_pen"] + mods.pop("ranged_penalty", 0)
    fov_penalty    = base["fov_pen"]    + mods.pop("fov_penalty", 0)

    name     = _build_display_name(base["name"], quality, prefix_key, suffix_key)
    sell     = _compute_sell_price(base["base_price"], quality, mods)
    item_key = _unique_key(base_key)

    return {
        "key": item_key,
        "name": name,
        "category": "armor",
        "color": COLOR_ARMOR,
        "marker": "armor",
        "description": f"{quality.capitalize()} {base['name']}.",
        "defense_bonus": defense_bonus,
        "ranged_penalty": ranged_penalty,
        "fov_penalty": fov_penalty,
        "max_hp_bonus": mods.pop("max_hp_bonus", 0),
        "fov_bonus": mods.pop("fov_bonus", 0),
        "speed_bonus": mods.pop("speed_bonus", 0),
        "on_kill_heal": mods.pop("on_kill_heal", 0),
        "low_hp_melee_bonus": mods.pop("low_hp_melee_bonus", 0),
        "on_hit_effect": {k: v for k, v in mods.items() if k.startswith("on_hit_")},
        "passive_effects": {k: v for k, v in mods.items() if k.startswith("on_enter_")},
        "sell_price": sell,
        "quality": quality,
        "prefix_key": prefix_key,
        "suffix_key": suffix_key,
        "base_key": base_key,
        "item_level": ilvl,
    }
