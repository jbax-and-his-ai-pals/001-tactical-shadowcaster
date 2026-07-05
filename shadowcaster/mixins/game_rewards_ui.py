from __future__ import annotations

import pygame

from ..constants import COLOR_ACCENT, COLOR_HEAL, SCREEN_HEIGHT, SCREEN_WIDTH
from ..game_typing import GameMixinBase


class RewardsUIMixin(GameMixinBase):

    def _track_reward_spec(self, delve=False):
        track = self.dominant_track() if hasattr(self, "dominant_track") else None
        if not track:
            return None
        name, tier = track
        mul = 2 if tier >= 2 else 1
        if name == "Scout":
            reveals = 1 + (1 if tier >= 2 else 0)
            tonic = 1
            label = "Scout"
            desc = f"Reveal {reveals} world region{'s' if reveals > 1 else ''}, +{tonic} tonic"
        elif name == "Delver":
            power = mul
            ammo = 2 + mul
            label = "Delver"
            desc = f"+{power} attack, +{ammo} ammo"
        elif name == "Warden":
            gold = 35 if tier >= 2 else 20
            label = "Warden"
            desc = f"+{gold}g, full HP restore"
        else:  # Pathfinder
            medkits = 1 + mul
            reveals = mul
            label = "Pathfinder"
            desc = f"+{medkits} kit, +1 tonic, reveal {reveals} region{'s' if reveals > 1 else ''}"
        if delve:
            desc = desc + " (delve)"
        return (label, desc)

    def exploration_reward_options(self):
        opts = [
            ("Vitality", f"+{self.tuning['full_explore_vitality_bonus']} max HP"),
            ("Power", f"+{self.tuning['full_explore_power_bonus']} attack"),
            (
                "Recovery",
                f"+{self.tuning['full_explore_recovery_medkits']} kit, +{self.tuning['full_explore_recovery_tonics']} tonic",
            ),
        ]
        track_opt = self._track_reward_spec(delve=False)
        if track_opt:
            opts.append(track_opt)
        return opts

    def delve_reward_options(self):
        opts = [
            ("Vitality", f"+{self.tuning['delve_reward_vitality_bonus']} max HP"),
            ("Power", f"+{self.tuning['delve_reward_power_bonus']} attack, +1 ammo"),
            (
                "Recovery",
                f"+{self.tuning['bottom_reward_ammo']} ammo, +{self.tuning['bottom_reward_medkits']} kit, +{self.tuning['delve_reward_recovery_tonics']} tonic",
            ),
        ]
        track_opt = self._track_reward_spec(delve=True)
        if track_opt:
            opts.append(track_opt)
        return opts

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

    def _provisioner_action_list(self):
        """Ordered list of action tags for the current provisioner menu."""
        actions = ["field_kit", "cleanser", "sell_tonic", "buy_weapon", "buy_armor"]
        if self.inventory_quantity("grain") >= 2:
            actions.append("craft_rations")
        if self.inventory_quantity("herbs") >= 2:
            actions.append("craft_tonic")
        if self.inventory_quantity("ore") >= 1:
            actions.append("craft_ammo")
        actions.append("leave")
        return actions

    def provisioner_trade_options(self):
        weapon = self.WEAPON_CATALOG[self.provisioner_weapon_offer]
        armor = self.ARMOR_CATALOG[self.provisioner_armor_offer]
        weapon_stat = f"+{weapon['melee_bonus']} melee" if weapon["melee_bonus"] else f"+{weapon['ranged_bonus']} ranged"
        discount = self.provisioner_ammo_discount()
        w_cost = max(1, weapon["cost"] - discount)
        a_cost = max(1, armor["cost"] - discount)
        w_label = f"Spend {w_cost} ammo for {weapon_stat}" + (f" (was {weapon['cost']})" if discount else "")
        a_label = f"Spend {a_cost} ammo for +{armor['defense_bonus']} defense" + (f" (was {armor['cost']})" if discount else "")
        base = [
            ("Field Kit", "Spend 2 ammo for 1 medkit"),
            ("Cleanser", "Spend 3 ammo for 1 tonic"),
            ("Sell Tonic", "Trade 1 tonic for 2 ammo"),
            (f"Buy {weapon['name']}", w_label),
            (f"Buy {armor['name']}", a_label),
        ]
        craft = []
        grain = self.inventory_quantity("grain")
        herbs = self.inventory_quantity("herbs")
        ore = self.inventory_quantity("ore")
        if grain >= 2:
            craft.append(("Pack Rations", f"2 grain ({grain} carried) → 1 healing potion"))
        if herbs >= 2:
            craft.append(("Brew Tonic", f"2 herbs ({herbs} carried) → 1 ward tonic"))
        if ore >= 1:
            craft.append(("Forge Heads", f"1 ore ({ore} carried) → +2 ammo"))
        return base + craft + [("Leave", "Step back from the counter")]

    def current_choice_options(self):
        if self.town_choice_pending == "provisioner_trade":
            return self.provisioner_trade_options()
        return self.current_reward_options()

    def apply_reward_choice(self):
        if self.delve_reward_pending:
            self.apply_delve_reward_choice()
        else:
            self.apply_exploration_reward_choice()

    def provisioner_ammo_discount(self):
        depth = getattr(self, "_supply_depth", 0)
        if depth >= 3:
            return 2
        if depth >= 1:
            return 1
        return 0

    def open_provisioner_trade(self):
        self.stop_auto_movement()
        self.town_choice_pending = "provisioner_trade"
        self.exploration_choice_index = 0
        weapon_preferences, armor_preferences = self.region_gear_preferences()
        self.provisioner_weapon_offer = self.choose_catalog_offer("weapon", preferred=weapon_preferences)
        self.provisioner_armor_offer = self.choose_catalog_offer("armor", preferred=armor_preferences)
        depth = getattr(self, "_supply_depth", 0)
        if depth >= 1:
            discount = self.provisioner_ammo_discount()
            self.message = f"The provisioner lays out a few practical trades. Supply reputation: -{discount} ammo on gear."
        else:
            self.message = "The provisioner lays out a few practical trades."

    def apply_current_choice(self):
        if self.town_choice_pending == "provisioner_trade":
            self.apply_provisioner_trade_choice()
            return
        self.apply_reward_choice()

    def apply_provisioner_trade_choice(self):
        if self.town_choice_pending != "provisioner_trade":
            return
        actions = self._provisioner_action_list()
        idx = self.exploration_choice_index
        action = actions[idx] if idx < len(actions) else "leave"
        self.town_choice_pending = None

        if action == "field_kit":
            if self.ammo < 2:
                self.message = "You need 2 ammo for that trade."
                return
            self.ammo -= 2
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            self.message = f"You trade for a field kit. Ammo {self.ammo}, kits {self.inventory_quantity('medkit')}."
            return
        if action == "cleanser":
            if self.ammo < 3:
                self.message = "You need 3 ammo for that trade."
                return
            self.ammo -= 3
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            self.message = f"You trade for a tonic. Ammo {self.ammo}, tonics {self.inventory_quantity('tonic')}."
            return
        if action == "sell_tonic":
            if self.inventory_quantity("tonic") < 1:
                self.message = "You do not have a tonic to spare."
                return
            tonic_item = self.inventory_item("tonic")
            if tonic_item is not None:
                tonic_item.quantity -= 1
                if tonic_item.quantity <= 0:
                    self.inventory.remove(tonic_item)
            self.ammo += 2
            self.message = f"You trade a tonic for ammunition. Ammo {self.ammo}."
            return
        if action == "buy_weapon":
            key = self.provisioner_weapon_offer
            catalog = self.WEAPON_CATALOG[key]
            if self.owns_item(key):
                self.message = f"You already own {catalog['name']}."
                return
            cost = max(1, catalog["cost"] - self.provisioner_ammo_discount())
            if self.ammo < cost:
                self.message = f"You need {cost} ammo for that trade."
                return
            self.ammo -= cost
            self.add_item(key, catalog["name"], "weapon", catalog["color"], "weapon",
                          melee_bonus=catalog["melee_bonus"], ranged_bonus=catalog["ranged_bonus"],
                          description=catalog.get("description", ""))
            self.message = f"You buy a {catalog['name']}. Open your inventory to equip it."
            return
        if action == "buy_armor":
            key = self.provisioner_armor_offer
            catalog = self.ARMOR_CATALOG[key]
            if self.owns_item(key):
                self.message = f"You already own {catalog['name']}."
                return
            cost = max(1, catalog["cost"] - self.provisioner_ammo_discount())
            if self.ammo < cost:
                self.message = f"You need {cost} ammo for that trade."
                return
            self.ammo -= cost
            self.add_item(key, catalog["name"], "armor", catalog["color"], "armor",
                          defense_bonus=catalog["defense_bonus"], description=catalog.get("description", ""))
            self.message = f"You buy {catalog['name']}. Open your inventory to equip it."
            return
        if action == "craft_rations":
            grain = self.inventory_item("grain")
            if grain is None or grain.quantity < 2:
                self.message = "You need 2 grain to pack rations."
                return
            grain.quantity -= 2
            if grain.quantity <= 0:
                self.inventory.remove(grain)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            self.message = f"You pack field rations from your grain. +1 healing potion (kits: {self.inventory_quantity('medkit')})."
            return
        if action == "craft_tonic":
            herbs = self.inventory_item("herbs")
            if herbs is None or herbs.quantity < 2:
                self.message = "You need 2 herbs to brew a tonic."
                return
            herbs.quantity -= 2
            if herbs.quantity <= 0:
                self.inventory.remove(herbs)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            self.message = f"You brew a ward tonic from the herbs. +1 tonic (tonics: {self.inventory_quantity('tonic')})."
            return
        if action == "craft_ammo":
            ore = self.inventory_item("ore")
            if ore is None or ore.quantity < 1:
                self.message = "You need ore to forge arrowheads."
                return
            ore.quantity -= 1
            if ore.quantity <= 0:
                self.inventory.remove(ore)
            self.ammo += 2
            self.message = f"You forge broadheads from raw ore. +2 ammo (ammo: {self.ammo})."
            return
        self.message = "You step away from the provisioner."

    def _apply_track_reward(self, delve=False):
        track = self.dominant_track() if hasattr(self, "dominant_track") else None
        if not track:
            return "No track reward available."
        name, tier = track
        mul = 2 if tier >= 2 else 1
        parts = []
        if name == "Scout":
            reveals = 1 + (1 if tier >= 2 else 0)
            revealed = []
            for _ in range(reveals):
                r = self.reveal_one_adjacent_world_region_from(self.world_position) if hasattr(self, "reveal_one_adjacent_world_region_from") else None
                if r:
                    revealed.append(r[1])
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            parts.append(f"+1 tonic")
            if revealed:
                parts.append(f"routes to {', '.join(revealed[:2])}")
            else:
                parts.append("no new routes found")
        elif name == "Delver":
            power = mul
            ammo = 2 + mul
            self.melee_damage += power
            self.ranged_damage += power
            self.ammo += ammo
            parts.append(f"+{power} attack (now {self.melee_damage}/{self.ranged_damage}), +{ammo} ammo")
        elif name == "Warden":
            gold = 35 if tier >= 2 else 20
            self.gold += gold
            self.health = self.max_health
            parts.append(f"+{gold}g, HP restored to {self.max_health}")
        else:  # Pathfinder
            medkits = 1 + mul
            reveals = mul
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=medkits, description="Restores health.")
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            parts.append(f"+{medkits} medkits, +1 tonic")
            revealed = []
            for _ in range(reveals):
                r = self.reveal_one_adjacent_world_region_from(self.world_position) if hasattr(self, "reveal_one_adjacent_world_region_from") else None
                if r:
                    revealed.append(r[1])
            if revealed:
                parts.append(f"routes to {', '.join(revealed[:2])}")
        return f"{name} reward: {'; '.join(parts)}."

    def apply_delve_reward_choice(self):
        if not self.delve_reward_pending:
            return
        self.stop_auto_movement()
        self.delve_reward_pending = False
        self.bottom_reward_claimed = True
        if hasattr(self, "xp_check_delve_bottom"):
            self.xp_check_delve_bottom()
        if self.exploration_choice_index == 3:
            msg = self._apply_track_reward(delve=True)
            self.trigger_completion_modal(msg)
            self.message = f"Delve reward claimed: {msg} A return portal hums to life."
            return
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
        if self.exploration_choice_index == 3:
            msg = self._apply_track_reward(delve=False)
            self.trigger_completion_modal(msg)
            self.message = f"Floor fully explored: {msg}"
            return
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
