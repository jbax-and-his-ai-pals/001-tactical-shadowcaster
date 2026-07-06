from __future__ import annotations

import random

from ..game_typing import GameMixinBase

LOCKED_CONTAINER_DEFS = {
    "locked_chest":     {"name": "Locked Chest",    "cost": 5,  "color": (190, 160, 100), "min_floor": 1, "drop_chance": 0.07,  "loot_gold": (3, 10),  "loot_item": ("medkit", 0.35), "lock_difficulty": 1},
    "locked_coffer":    {"name": "Locked Coffer",   "cost": 12, "color": (160, 130, 80),  "min_floor": 3, "drop_chance": 0.025, "loot_gold": (8, 22),  "loot_item": ("tonic",  0.40), "lock_difficulty": 3},
    "locked_strongbox": {"name": "Locked Strongbox","cost": 25, "color": (130, 100, 60),  "min_floor": 6, "drop_chance": 0.006, "loot_gold": (18, 45), "loot_item": ("medkit", 0.60), "lock_difficulty": 5},
}


class LocksmithMixin(GameMixinBase):

    def _locksmith_init(self):
        self.locksmith_open = False
        self.locksmith_index = 0

    def open_locksmith(self):
        self.locksmith_open = True
        self.locksmith_index = 0

    def close_locksmith(self):
        self.locksmith_open = False

    def locksmith_items(self):
        return [item for item in self.inventory if item.category == "locked_container"]

    def locksmith_move_selection(self, delta):
        items = self.locksmith_items()
        if not items:
            return
        self.locksmith_index = (self.locksmith_index + delta) % len(items)

    def locksmith_confirm_unlock(self):
        items = self.locksmith_items()
        if not items:
            self.message = "You have no locked containers to open."
            return
        self.locksmith_index = min(self.locksmith_index, len(items) - 1)
        item = items[self.locksmith_index]
        defn = LOCKED_CONTAINER_DEFS.get(item.key, {})
        cost = defn.get("cost", 10)
        if self.gold < cost:
            self.message = f"You need {cost}g to unlock the {item.name}. (You have {self.gold}g.)"
            return
        self.gold -= cost
        item.quantity -= 1
        if item.quantity <= 0:
            self.inventory.remove(item)
            self.locksmith_index = max(0, self.locksmith_index - 1)
        gold_min, gold_max = defn.get("loot_gold", (3, 10))
        found_gold = random.randint(gold_min, gold_max)
        self.gold += found_gold
        msg = f"The locksmith cracks the {item.name}. Inside: {found_gold}g"
        loot_key, loot_chance = defn.get("loot_item", ("medkit", 0))
        if random.random() < loot_chance:
            from ..constants import COLOR_ITEM_CONSUMABLE as COLOR_CONSUMABLE
            loot_defs = {
                "medkit": {"name": "Healing Potion", "description": "Restores 4 HP when used.", "heal_amount": 4},
                "tonic":  {"name": "Ward Tonic",     "description": "Grants 6 turns of ward when used.", "ward_duration": 6},
            }
            ld = loot_defs.get(loot_key, {})
            self.add_item(loot_key, ld["name"], "consumable", COLOR_CONSUMABLE, loot_key,
                          description=ld.get("description", ""), heal_amount=ld.get("heal_amount", 0),
                          ward_duration=ld.get("ward_duration", 0), cleanses=False)
            msg += f" and a {ld['name']}!"
        else:
            msg += "."
        # Small bonus: gem inside higher-tier containers
        gem_chances = {"locked_chest": 0.15, "locked_coffer": 0.35, "locked_strongbox": 0.60}
        if random.random() < gem_chances.get(item.key, 0) and hasattr(self, "random_gem_item"):
            gem = self.random_gem_item()
            self.add_item(gem.key, gem.name, gem.category, gem.color, gem.marker,
                          quantity=1, description=gem.description)
            msg = msg.rstrip(".") + f" and a {gem.name}!"
        self.message = msg
        self.store_current_region()

    def _maybe_drop_locked_container(self, enemy):
        floor = getattr(self, "floor", 1)
        eligible = [k for k, d in LOCKED_CONTAINER_DEFS.items() if floor >= d["min_floor"]]
        if not eligible:
            return
        container_mult = self.skill_container_drop_bonus() if hasattr(self, "skill_container_drop_bonus") else 1.0
        roll = random.random()
        cumulative = 0.0
        chosen = None
        for key in eligible:
            cumulative += LOCKED_CONTAINER_DEFS[key]["drop_chance"] * container_mult
            if roll < cumulative:
                chosen = key
                break
        if chosen is None:
            return
        defn = LOCKED_CONTAINER_DEFS[chosen]
        from ..models import GroundItem, Item
        container = Item(
            key=chosen,
            name=defn["name"],
            category="locked_container",
            color=defn["color"],
            marker="cache",
            quantity=1,
            description=f"Sealed shut. A locksmith can open it for {defn['cost']}g.",
            lock_difficulty=defn.get("lock_difficulty", 1),
        )
        ground = GroundItem(position=enemy.position, item=container)
        self.floor_items.append(ground)
