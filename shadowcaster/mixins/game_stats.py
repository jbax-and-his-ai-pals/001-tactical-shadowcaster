from __future__ import annotations

from ..constants import AUTO_MOVE_INTERVAL_MS
from ..game_typing import GameMixinBase


class StatsMixin(GameMixinBase):

    @property
    def light_radius(self):
        base = self.base_light_radius + self.light_bonus
        weapon = self.equipped_weapon
        armor = self.equipped_armor
        if weapon and weapon.key == "longbow":
            base += 1
        if armor and armor.key == "travel_cloak":
            base += 1
        statuses = getattr(self, "player_statuses", {})
        if "fortify_light" in statuses:
            base += 3
        ability_bonus = self.ability_light_bonus() if hasattr(self, "ability_light_bonus") else 0
        return base + self._trinket_bonus("light") + ability_bonus

    @property
    def autoexplore_interval(self):
        statuses = getattr(self, "player_statuses", {})
        speed_bonus = 30 if "fortify_speed" in statuses else 0
        return max(25, AUTO_MOVE_INTERVAL_MS - self.haste_bonus - speed_bonus)

    @property
    def melee_range(self):
        bonus = 1 if (self.equipped_weapon and self.equipped_weapon.key == "spear") else 0
        return 1 + self.reach_bonus + bonus

    @property
    def equipped_weapon(self):
        return next((item for item in self.inventory if item.category == "weapon" and item.equipped), None)

    @property
    def equipped_armor(self):
        return next((item for item in self.inventory if item.category == "armor" and item.equipped), None)

    @property
    def equipped_trinket(self):
        return next((item for item in self.inventory if item.category == "trinket" and item.equipped), None)

    def _trinket_bonus(self, stat: str) -> int:
        from ..item_catalog import ITEM_CATALOG
        trinket = self.equipped_trinket
        if trinket is None:
            return 0
        spec = ITEM_CATALOG.get(trinket.key, {})
        return spec.get("trinket_bonus", {}).get(stat, 0)

    @property
    def effective_melee_damage(self):
        weapon = self.equipped_weapon
        statuses = getattr(self, "player_statuses", {})
        atk_bonus = 1 if "fortify_attack" in statuses else 0
        return self.melee_damage + (weapon.melee_bonus if weapon else 0) + atk_bonus + self._trinket_bonus("melee")

    @property
    def effective_ranged_damage(self):
        weapon = self.equipped_weapon
        statuses = getattr(self, "player_statuses", {})
        atk_bonus = 1 if "fortify_attack" in statuses else 0
        return self.ranged_damage + (weapon.ranged_bonus if weapon else 0) + atk_bonus + self._trinket_bonus("ranged")

    @property
    def effective_defense(self):
        armor = self.equipped_armor
        statuses = getattr(self, "player_statuses", {})
        def_bonus = 2 if "fortify_defense" in statuses else 0
        return (armor.defense_bonus if armor else 0) + def_bonus + self._trinket_bonus("defense")
