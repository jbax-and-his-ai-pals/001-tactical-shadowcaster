from __future__ import annotations

import pygame

from ..constants import COLOR_ACCENT, COLOR_HEAL, SCREEN_HEIGHT, SCREEN_WIDTH
from ..game_typing import GameMixinBase


class RewardsUIMixin(GameMixinBase):

    def exploration_reward_options(self):
        return [
            ("Vitality", f"+{self.tuning['full_explore_vitality_bonus']} max HP"),
            ("Power", f"+{self.tuning['full_explore_power_bonus']} attack"),
            (
                "Recovery",
                f"+{self.tuning['full_explore_recovery_medkits']} kit, +{self.tuning['full_explore_recovery_tonics']} tonic",
            ),
        ]

    def delve_reward_options(self):
        return [
            ("Vitality", f"+{self.tuning['delve_reward_vitality_bonus']} max HP"),
            ("Power", f"+{self.tuning['delve_reward_power_bonus']} attack, +1 ammo"),
            (
                "Recovery",
                f"+{self.tuning['bottom_reward_ammo']} ammo, +{self.tuning['bottom_reward_medkits']} kit, +{self.tuning['delve_reward_recovery_tonics']} tonic",
            ),
        ]

    def has_pending_reward(self):
        return self.exploration_reward_pending is not None or self.delve_reward_pending

    def has_pending_choice(self):
        return self.has_pending_reward() or self.town_choice_pending is not None

    def current_choice_title_subtitle(self):
        if self.town_choice_pending == "provisioner_trade":
            return "Provisioner", "Choose a barter"
        if self.delve_reward_pending:
            return "Delve Cleared", "Choose your delve reward"
        return "100% Explored", "Choose your floor-clear reward"

    def current_reward_options(self):
        return self.delve_reward_options() if self.delve_reward_pending else self.exploration_reward_options()

    def provisioner_trade_options(self):
        weapon = self.WEAPON_CATALOG[self.provisioner_weapon_offer]
        armor = self.ARMOR_CATALOG[self.provisioner_armor_offer]
        weapon_stat = f"+{weapon['melee_bonus']} melee" if weapon["melee_bonus"] else f"+{weapon['ranged_bonus']} ranged"
        return [
            ("Field Kit", "Spend 2 ammo for 1 medkit"),
            ("Cleanser", "Spend 3 ammo for 1 tonic"),
            ("Sell Tonic", "Trade 1 tonic for 2 ammo"),
            (f"Buy {weapon['name']}", f"Spend {weapon['cost']} ammo for {weapon_stat}"),
            (f"Buy {armor['name']}", f"Spend {armor['cost']} ammo for +{armor['defense_bonus']} defense"),
            ("Leave", "Step back from the counter"),
        ]

    def current_choice_options(self):
        if self.town_choice_pending == "provisioner_trade":
            return self.provisioner_trade_options()
        return self.current_reward_options()

    def apply_reward_choice(self):
        if self.delve_reward_pending:
            self.apply_delve_reward_choice()
        else:
            self.apply_exploration_reward_choice()

    def open_provisioner_trade(self):
        self.stop_auto_movement()
        self.town_choice_pending = "provisioner_trade"
        self.exploration_choice_index = 0
        weapon_preferences, armor_preferences = self.region_gear_preferences()
        self.provisioner_weapon_offer = self.choose_catalog_offer("weapon", preferred=weapon_preferences)
        self.provisioner_armor_offer = self.choose_catalog_offer("armor", preferred=armor_preferences)
        self.message = "The provisioner lays out a few practical trades."

    def apply_current_choice(self):
        if self.town_choice_pending == "provisioner_trade":
            self.apply_provisioner_trade_choice()
            return
        self.apply_reward_choice()

    def apply_provisioner_trade_choice(self):
        if self.town_choice_pending != "provisioner_trade":
            return
        choice = self.exploration_choice_index
        self.town_choice_pending = None
        if choice == 0:
            if self.ammo < 2:
                self.message = "You need 2 ammo for that trade."
                return
            self.ammo -= 2
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            self.message = f"You trade for a field kit. Ammo {self.ammo}, kits {self.inventory_quantity('medkit')}."
            return
        if choice == 1:
            if self.ammo < 3:
                self.message = "You need 3 ammo for that trade."
                return
            self.ammo -= 3
            from ..constants import COLOR_ACCENT
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            self.message = f"You trade for a tonic. Ammo {self.ammo}, tonics {self.inventory_quantity('tonic')}."
            return
        if choice == 2:
            if self.inventory_quantity("tonic") < 1:
                self.message = "You do not have a tonic to spare."
                return
            tonic_item = self.inventory_item("tonic")
            if tonic_item is not None:
                tonic_item.quantity -= 1
            self.ammo += 2
            self.message = f"You trade a tonic for ammunition. Ammo {self.ammo}, tonics {self.inventory_quantity('tonic')}."
            return
        if choice == 3:
            key = self.provisioner_weapon_offer
            catalog = self.WEAPON_CATALOG[key]
            if self.owns_item(key):
                self.message = f"You already own {catalog['name']}."
                return
            if self.ammo < catalog["cost"]:
                self.message = f"You need {catalog['cost']} ammo for that trade."
                return
            self.ammo -= catalog["cost"]
            self.add_item(
                key,
                catalog["name"],
                "weapon",
                catalog["color"],
                "weapon",
                melee_bonus=catalog["melee_bonus"],
                ranged_bonus=catalog["ranged_bonus"],
                description=catalog.get("description", ""),
            )
            self.message = f"You buy a {catalog['name']}. Open your inventory to equip it."
            return
        if choice == 4:
            key = self.provisioner_armor_offer
            catalog = self.ARMOR_CATALOG[key]
            if self.owns_item(key):
                self.message = f"You already own {catalog['name']}."
                return
            if self.ammo < catalog["cost"]:
                self.message = f"You need {catalog['cost']} ammo for that trade."
                return
            self.ammo -= catalog["cost"]
            self.add_item(
                key,
                catalog["name"],
                "armor",
                catalog["color"],
                "armor",
                defense_bonus=catalog["defense_bonus"],
                description=catalog.get("description", ""),
            )
            self.message = f"You buy {catalog['name']}. Open your inventory to equip it."
            return
        self.message = "You step away from the provisioner."

    def apply_delve_reward_choice(self):
        if not self.delve_reward_pending:
            return
        self.stop_auto_movement()
        self.delve_reward_pending = False
        self.bottom_reward_claimed = True
        if self.exploration_choice_index == 0:
            amount = self.tuning["delve_reward_vitality_bonus"]
            self.max_health += amount
            self.health = min(self.max_health, self.health + amount)
            self.trigger_completion_modal(f"+{amount} max HP for clearing the delve")
            self.message = f"Delve reward claimed: +{amount} max HP. HP {self.health}/{self.max_health}. A return portal hums to life."
        elif self.exploration_choice_index == 1:
            amount = self.tuning["delve_reward_power_bonus"]
            self.melee_damage += amount
            self.ranged_damage += amount
            self.ammo += 1
            self.trigger_completion_modal(f"+{amount} attack for clearing the delve")
            self.message = f"Delve reward claimed: attack rises to {self.melee_damage}/{self.ranged_damage}. A return portal hums to life."
        else:
            ammo = self.tuning["bottom_reward_ammo"]
            medkits = self.tuning["bottom_reward_medkits"]
            tonics = self.tuning["delve_reward_recovery_tonics"]
            self.ammo += ammo
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=medkits, description="Restores health.")
            from ..constants import COLOR_ACCENT
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=tonics, description="Clears statuses and grants ward.")
            self.trigger_completion_modal(f"+{ammo} ammo, +{medkits} kit, +{tonics} tonic for clearing the delve")
            self.message = f"Delve reward claimed: +{ammo} ammo, +{medkits} medkits, +{tonics} tonics. A return portal hums to life."

    def apply_exploration_reward_choice(self):
        milestone = self.exploration_reward_pending
        if milestone is None:
            return
        self.stop_auto_movement()
        self.exploration_reward_pending = None
        self.claimed_exploration_rewards.add(milestone)
        self.full_clears += 1
        if self.exploration_choice_index == 0:
            amount = self.tuning["full_explore_vitality_bonus"]
            self.max_health += amount
            self.health = min(self.max_health, self.health + amount)
            self.trigger_completion_modal(f"+{amount} max HP for full exploration")
            self.message = f"Floor fully explored: +{amount} max HP. HP {self.health}/{self.max_health}."
        elif self.exploration_choice_index == 1:
            amount = self.tuning["full_explore_power_bonus"]
            self.melee_damage += amount
            self.ranged_damage += amount
            self.trigger_completion_modal(f"+{amount} attack for full exploration")
            self.message = f"Floor fully explored: attack rises to {self.melee_damage}/{self.ranged_damage}."
        else:
            medkits = self.tuning["full_explore_recovery_medkits"]
            tonics = self.tuning["full_explore_recovery_tonics"]
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=medkits, description="Restores health.")
            from ..constants import COLOR_ACCENT
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=tonics, description="Clears statuses and grants ward.")
            self.trigger_completion_modal(f"+{medkits} kit, +{tonics} tonic for full exploration")
            self.message = f"Floor fully explored: +{medkits} medkits, +{tonics} tonics."

    def adjust_choice_index(self, delta):
        option_count = len(self.current_choice_options())
        self.exploration_choice_index = (self.exploration_choice_index + delta) % option_count

    def reward_choice_from_screen(self, screen_x, screen_y):
        option_count = len(self.current_choice_options())
        box_width = 200
        box_height = 96
        gap = 20
        total_width = box_width * option_count + gap * max(0, option_count - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        top = (SCREEN_HEIGHT - box_height) // 2 + 30
        for index in range(option_count):
            left = start_x + index * (box_width + gap)
            if pygame.Rect(left, top, box_width, box_height).collidepoint(screen_x, screen_y):
                return index
        return None
