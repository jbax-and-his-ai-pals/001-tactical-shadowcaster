from __future__ import annotations

import random

from ..constants import COLOR_HEAL
from ..models import GroundItem, Item
from ..game_typing import GameMixinBase

# region_type → (item_key, display_name, sell_value_per_unit)
_HARVEST_SPECS = {
    "farmland": ("grain",    "Grain Bundle",   12),
    "plains":   ("grain",    "Grain Bundle",   12),
    "forest":   ("herbs",    "Wild Herbs",     10),
    "swamp":    ("herbs",    "Wild Herbs",     10),
    "mountain": ("ore",      "Raw Ore",        14),
    "tundra":   ("herbs",    "Wild Herbs",     10),
}

_HARVEST_COLOR = (200, 230, 160)
_HARVEST_MAX_STACK = 4

_HARVEST_GATHER_MESSAGES = {
    "grain": "You gather a bundle of grain.",
    "herbs": "You pick a handful of wild herbs.",
    "ore":   "You chip loose a chunk of raw ore.",
}

_HARVEST_SELL_MESSAGES = {
    "grain": "The market takes your grain",
    "herbs": "An apothecary buys your herbs",
    "ore":   "A smith pays for your ore",
}


class HarvestMixin(GameMixinBase):

    def harvest_spec(self):
        return _HARVEST_SPECS.get(self.region_type)

    def is_harvest_eligible(self):
        if self.in_local_region():
            return False
        if self.region_type in {"town", "monster_town"}:
            return False
        spec = self.harvest_spec()
        if not spec:
            return False
        danger = getattr(self, "danger_tier", 1)
        return danger <= 2

    def generate_harvest_nodes(self):
        if not self.is_harvest_eligible():
            return []
        spec = self.harvest_spec()
        if not spec:
            return []
        key, name, _ = spec
        exclude = {
            self.player,
            getattr(self, "stairs", None),
            getattr(self, "up_stairs", None),
            getattr(self, "delve_goal", None),
            getattr(self, "return_portal", None),
        }
        exclude.discard(None)
        fieldcraft_extra = self.skill_fieldcraft_node_bonus() if hasattr(self, "skill_fieldcraft_node_bonus") else 0
        count = (2 if self.region_type in {"farmland", "plains"} else 1) + fieldcraft_extra
        nodes = []
        for _ in range(count):
            position = self.place_feature(exclude=exclude | {n.position for n in nodes})
            if position is None:
                break
            item = Item(
                key=key,
                name=name,
                category="harvest",
                color=_HARVEST_COLOR,
                marker="harvest",
                description=f"A field resource. Sell it at any town market for gold.",
            )
            nodes.append(GroundItem(position=position, item=item))
        return nodes

    def harvest_item_message(self, item_key):
        return _HARVEST_GATHER_MESSAGES.get(item_key, "You gather a resource.")

    def can_carry_harvest(self, item_key):
        existing = self.inventory_item(item_key)
        if existing is None:
            return True
        return existing.quantity < _HARVEST_MAX_STACK

    def sell_harvest_goods(self):
        harvest_items = [item for item in self.inventory if item.category == "harvest"]
        if not harvest_items:
            return None
        parts = []
        total_gold = 0
        herb_bonus = self.skill_herbalism_sell_bonus() if hasattr(self, "skill_herbalism_sell_bonus") else 0
        for item in harvest_items:
            spec = _HARVEST_SPECS.get(item.key)
            if not spec:
                continue
            _, _, value = spec
            bonus = herb_bonus if item.key == "herbs" else 0
            earned = item.quantity * (value + bonus)
            total_gold += earned
            label = _HARVEST_SELL_MESSAGES.get(item.key, f"You sell {item.name}")
            qty_str = f"{item.quantity}" if item.quantity > 1 else ""
            parts.append(f"{label} ({qty_str}x{value}g)")
            self.inventory.remove(item)
        if total_gold:
            self.gold += total_gold
            joined = "; ".join(parts)
            return f"Town market: {joined}. +{total_gold}g. Total: {self.gold}g."
        return None
