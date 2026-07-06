from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..loot_catalog import (
    GEMS, GEMS_BY_FLOOR, GEM_TIER_WEIGHT,
    CURIOS, CURIO_POOL_COMMON, CURIO_POOL_UNCOMMON, CURIO_POOL_SILVER, CURIO_POOL_GOLD,
)


def _pick_gem(floor: int) -> str | None:
    eligible = [key for min_f, key in GEMS_BY_FLOOR if floor >= min_f]
    if not eligible:
        return None
    weights = [GEM_TIER_WEIGHT[GEMS[k]["tier"]] for k in eligible]
    return random.choices(eligible, weights=weights, k=1)[0]


def _pick_curio(floor: int) -> str:
    if floor >= 7 and random.random() < 0.12:
        return random.choice(CURIO_POOL_GOLD)
    if floor >= 4 and random.random() < 0.25:
        return random.choice(CURIO_POOL_SILVER)
    if floor >= 2 and random.random() < 0.30:
        return random.choice(CURIO_POOL_UNCOMMON)
    return random.choice(CURIO_POOL_COMMON)


class LootMixin(GameMixinBase):

    def _drop_gem_at(self, position):
        floor = getattr(self, "floor", 1)
        key = _pick_gem(floor)
        if key is None:
            return
        defn = GEMS[key]
        from ..models import GroundItem, Item
        item = Item(key=key, name=defn["name"], category="gem",
                    color=defn["color"], marker="gem", quantity=1,
                    description=f"A polished {defn['name'].lower()}. Worth {defn['sell']}g at market.")
        self.floor_items.append(GroundItem(position=position, item=item))

    def _drop_curio_at(self, position):
        floor = getattr(self, "floor", 1)
        key = _pick_curio(floor)
        defn = CURIOS[key]
        from ..models import GroundItem, Item
        item = Item(key=key, name=defn["name"], category="curio",
                    color=defn["color"], marker="curio", quantity=1,
                    description=f"Worth {defn['sell']}g at market.")
        self.floor_items.append(GroundItem(position=position, item=item))

    def _maybe_drop_gem(self, enemy):
        bonus = self.skill_gem_drop_bonus() if hasattr(self, "skill_gem_drop_bonus") else 0.0
        if random.random() >= 0.05 + bonus:
            return
        self._drop_gem_at(enemy.position)

    def _maybe_drop_curio(self, enemy):
        bonus = self.skill_gem_drop_bonus() if hasattr(self, "skill_gem_drop_bonus") else 0.0
        if random.random() >= 0.08 + bonus:
            return
        self._drop_curio_at(enemy.position)

    def random_gem_item(self, floor: int | None = None):
        """Return a random gem Item for embedding in locked container loot etc."""
        f = floor if floor is not None else getattr(self, "floor", 1)
        key = _pick_gem(f) or "gem_quartz"
        defn = GEMS[key]
        from ..models import Item
        return Item(key=key, name=defn["name"], category="gem",
                    color=defn["color"], marker="gem", quantity=1,
                    description=f"A polished {defn['name'].lower()}. Worth {defn['sell']}g at market.")

    def random_curio_item(self, floor: int | None = None):
        """Return a random curio Item for embedding in locked container loot etc."""
        f = floor if floor is not None else getattr(self, "floor", 1)
        key = _pick_curio(f)
        defn = CURIOS[key]
        from ..models import Item
        return Item(key=key, name=defn["name"], category="curio",
                    color=defn["color"], marker="curio", quantity=1,
                    description=f"Worth {defn['sell']}g at market.")
