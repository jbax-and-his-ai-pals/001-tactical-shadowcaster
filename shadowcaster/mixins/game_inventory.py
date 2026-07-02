from __future__ import annotations
import random
from ..constants import COLOR_ACCENT, COLOR_HEAL, COLOR_ITEM_ARMOR, COLOR_ITEM_WEAPON
from ..models import GroundItem, Item, UpgradePickup
from ..game_typing import GameMixinBase


class InventoryMixin(GameMixinBase):
    def add_starting_items(self):
        self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
        self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")

    def owns_item(self, key):
        return self.inventory_item(key) is not None

    def unowned_catalog_keys(self, category):
        catalog = self.WEAPON_CATALOG if category == "weapon" else self.ARMOR_CATALOG
        return [key for key in catalog if not self.owns_item(key)]

    def item_from_catalog(self, category, key):
        catalog = self.WEAPON_CATALOG if category == "weapon" else self.ARMOR_CATALOG
        data = catalog[key]
        return Item(
            key=key,
            name=data["name"],
            category=category,
            color=data["color"],
            marker=category,
            description=data.get("description", ""),
            melee_bonus=data.get("melee_bonus", 0),
            ranged_bonus=data.get("ranged_bonus", 0),
            defense_bonus=data.get("defense_bonus", 0),
        )

    def choose_catalog_offer(self, category, preferred=None):
        catalog = self.WEAPON_CATALOG if category == "weapon" else self.ARMOR_CATALOG
        preferred = preferred or []
        available = [key for key in preferred if key in catalog and not self.owns_item(key)]
        if not available:
            available = self.unowned_catalog_keys(category)
        if not available:
            available = [key for key in preferred if key in catalog] or list(catalog)
        return random.choice(available)

    def region_gear_preferences(self):
        weapon_preferences = {
            "desert": ["longbow", "spear"],
            "plains": ["longbow", "spear"],
            "farmland": ["spear", "dagger"],
            "swamp": ["spear", "dagger"],
            "mountain": ["warhammer", "spear"],
            "tundra": ["spear", "warhammer"],
            "volcanic": ["warhammer", "dagger"],
            "castle": ["warhammer", "longbow"],
            "dungeon": ["warhammer", "dagger"],
            "cave": ["warhammer", "spear"],
            "ruins": ["dagger", "spear"],
            "badlands": ["longbow", "warhammer"],
        }
        armor_preferences = {
            "desert": ["travel_cloak", "leather_armor"],
            "plains": ["travel_cloak", "leather_armor"],
            "farmland": ["travel_cloak", "leather_armor"],
            "swamp": ["leather_armor", "chain_mail"],
            "mountain": ["chain_mail", "plate_coat"],
            "tundra": ["chain_mail", "travel_cloak"],
            "volcanic": ["chain_mail", "plate_coat"],
            "castle": ["plate_coat", "chain_mail"],
            "dungeon": ["chain_mail", "plate_coat"],
            "cave": ["leather_armor", "chain_mail"],
            "ruins": ["leather_armor", "chain_mail"],
            "badlands": ["travel_cloak", "chain_mail"],
        }
        return weapon_preferences.get(self.region_type, []), armor_preferences.get(self.region_type, [])

    def inventory_item(self, key):
        return next((item for item in self.inventory if item.key == key), None)

    def inventory_quantity(self, key):
        item = self.inventory_item(key)
        return item.quantity if item else 0

    def add_item(self, key, name, category, color, marker, quantity=1, **stats):
        existing = self.inventory_item(key)
        if existing is not None:
            if existing.category == "consumable":
                existing.quantity += quantity
            return existing
        item = Item(key=key, name=name, category=category, color=color, marker=marker, quantity=quantity, **stats)
        self.inventory.append(item)
        return item

    def add_ground_item_to_inventory(self, ground_item):
        item = ground_item.item
        existing = self.inventory_item(item.key)
        if existing is not None and existing.category != "consumable":
            self.ammo += 1
            return f"You already know this gear. You salvage the spare for 1 ammo."
        self.add_item(
            item.key,
            item.name,
            item.category,
            item.color,
            item.marker,
            quantity=item.quantity,
            description=item.description,
            melee_bonus=item.melee_bonus,
            ranged_bonus=item.ranged_bonus,
            defense_bonus=item.defense_bonus,
            heal_amount=item.heal_amount,
            cleanses=item.cleanses,
            ward_duration=item.ward_duration,
        )
        if item.category == "consumable":
            return f"You tuck away {item.name}."
        return f"You pick up {item.name}. Open your inventory to equip it."

    def equip_item(self, key):
        item = self.inventory_item(key)
        if item is None or item.category not in ("weapon", "armor"):
            return
        if item.equipped:
            item.equipped = False
            self.message = f"You unequip the {item.name}."
            return
        for other in self.inventory:
            if other.category == item.category:
                other.equipped = False
        item.equipped = True
        self.message = f"You equip the {item.name}."

    def use_item(self, key):
        item = self.inventory_item(key)
        if item is None or item.quantity <= 0:
            self.message = "You don't have that."
            return
        heal_amount = self.tuning["medkit_heal"] if item.key == "medkit" else item.heal_amount
        ward_duration = 4 if item.key == "tonic" else item.ward_duration
        cleanses = True if item.key == "tonic" else item.cleanses
        if heal_amount and self.health >= self.max_health and not cleanses:
            self.message = "You are already at full health."
            return
        parts = []
        if heal_amount:
            before = self.health
            self.health = min(self.max_health, self.health + heal_amount)
            if self.health > before:
                parts.append(f"You recover {self.health - before} HP.")
        if cleanses:
            cleared = ", ".join(sorted(self.player_statuses)) if self.player_statuses else "nothing"
            self.player_statuses.clear()
            self.player_status_sources.clear()
            parts.append(f"You clear {cleared}.")
        if ward_duration:
            self.add_status(self.player_statuses, "ward", ward_duration)
            parts.append("Ward takes hold.")
        item.quantity -= 1
        if item.key == "medkit":
            self.medkits_used += 1
        elif item.key == "tonic":
            self.tonics_used += 1
        if item.quantity <= 0:
            self.inventory.remove(item)
        self.after_player_turn(player_acted=False, base_message=f"You use the {item.name}. " + " ".join(parts))

    def consume_medkit(self):
        if self.inventory_quantity("medkit") <= 0:
            self.message = "You are out of medkits."
            return
        self.use_item("medkit")

    def consume_tonic(self):
        if self.inventory_quantity("tonic") <= 0:
            self.message = "You are out of tonics."
            return
        self.use_item("tonic")

    def floor_item_at(self, position):
        return next((ground_item for ground_item in getattr(self, "floor_items", []) if ground_item.position == position), None)

    def create_floor_item(self, exclude=None):
        weapon_preferences, armor_preferences = self.region_gear_preferences()
        category_order = ["weapon", "armor"] if self.region_type in {"desert", "plains", "farmland"} else ["armor", "weapon"]
        if random.random() < 0.5:
            category_order.reverse()
        for category in category_order:
            preferred = weapon_preferences if category == "weapon" else armor_preferences
            available = [key for key in preferred if key in (self.WEAPON_CATALOG if category == "weapon" else self.ARMOR_CATALOG) and not self.owns_item(key)]
            if not available:
                available = self.unowned_catalog_keys(category)
            if not available:
                continue
            key = random.choice(available)
            position = self.place_feature(exclude=exclude or set())
            return GroundItem(position=position, item=self.item_from_catalog(category, key))
        return None

    def generate_floor_items(self, pickups_enabled):
        if not pickups_enabled or self.region_type in {"town", "monster_town"}:
            return []
        item_count = 0
        if self.in_local_region():
            if self.region_depth >= 2 and not self.is_bottom_floor():
                item_count = 1
        elif self.danger_tier >= 4 and random.random() < 0.4:
            item_count = 1
        items = []
        exclude = {self.player, self.stairs, self.up_stairs, self.delve_goal, self.return_portal}
        for _ in range(item_count):
            ground_item = self.create_floor_item(exclude=exclude | {item.position for item in items})
            if ground_item is not None:
                items.append(ground_item)
        return items

    def create_upgrade_pickup(self, exclude=None):
        position = self.place_feature(exclude=exclude or set())
        if self.region_type == "forest":
            cycle = [
                ("vitality", (255, 90, 170), (100, 38, 70)),
                ("light", (255, 210, 80), (96, 72, 30)),
                ("haste", (110, 224, 255), (38, 84, 96)),
                ("power", (130, 255, 120), (48, 96, 44)),
                ("reach", (240, 150, 230), (94, 50, 90)),
            ]
        elif self.region_type == "ruins":
            cycle = [
                ("power", (130, 255, 120), (48, 96, 44)),
                ("light", (255, 210, 80), (96, 72, 30)),
                ("haste", (110, 224, 255), (38, 84, 96)),
                ("vitality", (255, 90, 170), (100, 38, 70)),
                ("reach", (240, 150, 230), (94, 50, 90)),
            ]
        else:
            cycle = [
                ("light", (255, 210, 80), (96, 72, 30)),
                ("vitality", (255, 90, 170), (100, 38, 70)),
                ("haste", (110, 224, 255), (38, 84, 96)),
                ("power", (130, 255, 120), (48, 96, 44)),
                ("reach", (240, 150, 230), (94, 50, 90)),
            ]
        kind, color, memory_color = cycle[(self.floor - 1) % len(cycle)]
        return UpgradePickup(position=position, kind=kind, color=color, memory_color=memory_color)

    def collect_floor_items(self):
        starting_light = self.light_radius
        messages = []
        if self.delve_goal and self.player == self.delve_goal and not self.bottom_reward_claimed and not self.delve_reward_pending:
            self.delve_reward_pending = True
            self.exploration_choice_index = 0
            messages.append("The delve terminus stirs. Choose your reward.")
        if self.upgrade_pickup and self.player == self.upgrade_pickup.position:
            if self.upgrade_pickup.kind == "light":
                self.light_bonus += self.tuning["light_upgrade_amount"]
                self.powerups_collected["light"] += 1
                messages.append(f"You claim a sight upgrade. Light radius is now {self.light_radius}.")
            elif self.upgrade_pickup.kind == "vitality":
                self.max_health += self.tuning["vitality_upgrade_amount"]
                self.health = min(self.max_health, self.health + self.tuning["vitality_upgrade_amount"])
                self.powerups_collected["vitality"] += 1
                messages.append(f"You claim a vitality upgrade. HP {self.health}/{self.max_health}.")
            elif self.upgrade_pickup.kind == "haste":
                self.haste_bonus += self.tuning["haste_upgrade_amount"]
                self.powerups_collected["haste"] += 1
                messages.append("You claim a haste upgrade. Autoexplore moves faster.")
            elif self.upgrade_pickup.kind == "reach":
                self.reach_bonus += self.tuning["reach_upgrade_amount"]
                self.powerups_collected["reach"] += 1
                messages.append(f"You claim a reach upgrade. Melee range is now {self.melee_range}.")
            else:
                self.melee_damage += self.tuning["power_upgrade_amount"]
                self.ranged_damage += self.tuning["power_upgrade_amount"]
                self.ammo += 1
                self.powerups_collected["power"] += 1
                messages.append(f"You claim a power upgrade. Attack rises to {self.melee_damage}/{self.ranged_damage}.")
            self.upgrade_pickup = None
        if self.heal_pickup and self.player == self.heal_pickup:
            self.heal_pickup = None
            self.powerups_collected["heal"] += 1
            if self.health < self.max_health:
                restored = min(self.tuning["heal_pickup_restore"], self.max_health - self.health)
                self.health += restored
                messages.append(f"You recover {restored} health. HP {self.health}/{self.max_health}.")
            else:
                messages.append("You find medicine, but you are already at full health.")
        floor_item = self.floor_item_at(self.player)
        if floor_item is not None:
            self.floor_items = [item for item in self.floor_items if item.position != self.player]
            messages.append(self.add_ground_item_to_inventory(floor_item))
        reward_message = self.check_exploration_rewards()
        if reward_message:
            messages.append(reward_message)
        if self.light_radius != starting_light:
            self.update_visibility()
        return " ".join(messages) if messages else None
