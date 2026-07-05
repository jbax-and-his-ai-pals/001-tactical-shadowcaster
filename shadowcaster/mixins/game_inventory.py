from __future__ import annotations
import random
from ..constants import COLOR_ACCENT, COLOR_HEAL, COLOR_ITEM_ARMOR, COLOR_ITEM_WEAPON
from ..item_catalog import ITEM_CATALOG
from ..models import GroundItem, Item, UpgradePickup
from ..game_typing import GameMixinBase


class InventoryMixin(GameMixinBase):
    def add_starting_items(self):
        self.add_catalog_item("medkit", quantity=1)
        self.add_catalog_item("tonic", quantity=1)

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
            "desert":   ["longbow", "shortbow", "spear"],
            "plains":   ["longbow", "spear", "shortbow"],
            "farmland": ["spear", "dagger", "shortbow"],
            "swamp":    ["spear", "dagger", "shortbow"],
            "mountain": ["warhammer", "halberd", "spear"],
            "tundra":   ["spear", "warhammer", "halberd"],
            "volcanic": ["warhammer", "halberd", "dagger"],
            "castle":   ["halberd", "warhammer", "longbow"],
            "dungeon":  ["warhammer", "halberd", "dagger"],
            "cave":     ["warhammer", "spear", "dagger"],
            "ruins":    ["dagger", "spear", "shortbow"],
            "badlands": ["longbow", "warhammer", "halberd"],
            "forest":   ["shortbow", "dagger", "spear"],
        }
        armor_preferences = {
            "desert":   ["travel_cloak", "leather_armor"],
            "plains":   ["travel_cloak", "leather_armor"],
            "farmland": ["travel_cloak", "leather_armor"],
            "swamp":    ["leather_armor", "chain_mail"],
            "mountain": ["chain_mail", "plate_coat"],
            "tundra":   ["chain_mail", "leather_armor"],
            "volcanic": ["plate_coat", "chain_mail"],
            "castle":   ["plate_coat", "war_plate"],
            "dungeon":  ["plate_coat", "war_plate"],
            "cave":     ["leather_armor", "chain_mail"],
            "ruins":    ["leather_armor", "chain_mail"],
            "badlands": ["chain_mail", "travel_cloak"],
            "forest":   ["travel_cloak", "leather_armor"],
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
        if item.category == "harvest":
            if hasattr(self, "can_carry_harvest") and not self.can_carry_harvest(item.key):
                return f"You're already carrying as much {item.name} as you can manage."
        if existing is not None and existing.category not in ("consumable", "harvest"):
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
            cache_finds = {
                "medkit": "You find a stashed healing potion — left here by someone who didn't come back for it.",
                "tonic":  "You find a ward tonic wedged out of sight. Someone hid it well.",
            }
            return cache_finds.get(item.key, f"You tuck away {item.name}.")
        if item.category == "harvest":
            if hasattr(self, "harvest_item_message"):
                return self.harvest_item_message(item.key) + " Sell it at a town market."
            return f"You gather {item.name}. Sell it at a town."
        return f"You pick up {item.name}. Open your inventory to equip it."

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

    def create_hidden_cache_item(self, exclude=None):
        """A consumable stash hidden in exploration terrain."""
        exclude = exclude or set()
        position = self.place_feature(exclude=exclude)
        if position is None:
            return None
        danger = self._world_danger_bonus() if hasattr(self, "_world_danger_bonus") else min(2, self.danger_tier // 2)
        biome = self.region_type
        # Legendary region: chance of a rare/legendary trinket
        if biome in ("ossuary", "mirrorwood") and random.random() < 0.30:
            candidates = [
                key for key, spec in ITEM_CATALOG.items()
                if spec["family"] == "trinket"
                and (not spec["biomes"] or biome in spec["biomes"])
            ]
            if candidates:
                key = random.choice(candidates)
                spec = ITEM_CATALOG[key]
                item = Item(key, spec["name"], "trinket", spec["color"], spec["marker"],
                            rarity=spec["rarity"], description=spec["description"])
                return GroundItem(position=position, item=item)
        # 20% chance of a biome-matched uncommon item in dangerous areas
        if danger >= 2 and random.random() < 0.20:
            candidates = [
                key for key, spec in ITEM_CATALOG.items()
                if spec["rarity"] == "uncommon" and spec["family"] != "trinket"
                and (not spec["biomes"] or biome in spec["biomes"])
            ]
            if candidates:
                key = random.choice(candidates)
                spec = ITEM_CATALOG[key]
                item = Item(key, spec["name"], "consumable", spec["color"], spec["marker"],
                            rarity=spec["rarity"], description=spec["description"])
                return GroundItem(position=position, item=item)
        # Default: tonic in dangerous areas, medkit elsewhere
        if danger >= 2 and random.random() < 0.5:
            spec = ITEM_CATALOG["tonic"]
            item = Item("tonic", spec["name"], "consumable", spec["color"], spec["marker"],
                        description=spec["description"])
        else:
            spec = ITEM_CATALOG["medkit"]
            item = Item("medkit", spec["name"], "consumable", spec["color"], spec["marker"],
                        description=spec["description"])
        return GroundItem(position=position, item=item)

    def generate_floor_items(self, pickups_enabled):
        if not pickups_enabled or self.region_type in {"town", "monster_town"}:
            return []
        items = []
        exclude = {self.player, self.stairs, self.up_stairs, self.delve_goal, self.return_portal}

        # Gear drops in deep local regions
        if self.in_local_region() and self.region_depth >= 2 and not self.is_bottom_floor():
            ground_item = self.create_floor_item(exclude=exclude | {item.position for item in items})
            if ground_item is not None:
                items.append(ground_item)

        # Gear drops in high-danger world regions (existing behaviour)
        elif not self.in_local_region() and self.danger_tier >= 4 and random.random() < 0.4:
            ground_item = self.create_floor_item(exclude=exclude | {item.position for item in items})
            if ground_item is not None:
                items.append(ground_item)

        # Hidden caches: consumable stashes in exploration terrain
        track = self.dominant_track() if hasattr(self, "dominant_track") else None
        cache_chance = 0.0
        if not self.in_local_region() and self.region_type not in {"town", "monster_town"}:
            base = 0.45 if self.region_type in {"forest", "swamp", "tundra", "mountain", "cave"} else 0.3
            if track and track[0] == "Pathfinder":
                base += 0.25 if track[1] >= 2 else 0.15
            cache_chance = min(0.85, base)
        elif self.in_local_region() and self.region_depth == 1 and self.region_type in {"dungeon", "cave", "ruins"}:
            base = 0.25
            if track and track[0] == "Delver":
                base += 0.3 if track[1] >= 2 else 0.15
            cache_chance = min(0.75, base)

        if cache_chance and random.random() < cache_chance:
            cache = self.create_hidden_cache_item(exclude=exclude | {item.position for item in items})
            if cache is not None:
                items.append(cache)
                if hasattr(self, "ability_cache_double_chance") and self.ability_cache_double_chance():
                    bonus = self.create_hidden_cache_item(exclude=exclude | {item.position for item in items})
                    if bonus is not None:
                        items.append(bonus)

        if hasattr(self, "generate_harvest_nodes"):
            items.extend(self.generate_harvest_nodes())

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
