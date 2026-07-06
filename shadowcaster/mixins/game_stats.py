from __future__ import annotations

from ..constants import AUTO_MOVE_INTERVAL_MS
from ..game_typing import GameMixinBase


class StatsMixin(GameMixinBase):

    @property
    def effective_max_health(self):
        bonus = sum(getattr(item, "max_hp_bonus", 0) for item in self.inventory if item.equipped)
        skill_bonus = self.skill_max_hp_bonus() if hasattr(self, "skill_max_hp_bonus") else 0
        return self.max_health + bonus + skill_bonus

    @property
    def effective_ranged_penalty(self):
        armor = self.equipped_armor
        return getattr(armor, "ranged_penalty", 0) if armor else 0

    @property
    def effective_fov_penalty(self):
        armor = self.equipped_armor
        return getattr(armor, "fov_penalty", 0) if armor else 0

    @property
    def effective_fov_bonus(self):
        return sum(getattr(item, "fov_bonus", 0) for item in self.inventory if item.equipped)

    @property
    def effective_speed_bonus(self):
        return sum(getattr(item, "speed_bonus", 0) for item in self.inventory if item.equipped)

    @property
    def effective_range_bonus(self):
        return sum(getattr(item, "range_bonus", 0) for item in self.inventory if item.equipped)

    @property
    def light_radius(self):
        base = self.base_light_radius + self.light_bonus
        weapon = self.equipped_weapon
        armor = self.equipped_armor
        bk_weapon = getattr(weapon, "base_key", None) or (weapon.key if weapon else None)
        bk_armor  = getattr(armor,  "base_key", None) or (armor.key  if armor  else None)
        if bk_weapon == "longbow":
            base += 1
        if bk_armor == "travel_cloak":
            base += 1
        statuses = getattr(self, "player_statuses", {})
        if "fortify_light" in statuses:
            base += 3
        ability_bonus = self.ability_light_bonus() if hasattr(self, "ability_light_bonus") else 0
        return base + self._trinket_bonus("light") + ability_bonus + self.effective_fov_bonus + self.effective_fov_penalty

    @property
    def autoexplore_interval(self):
        statuses = getattr(self, "player_statuses", {})
        speed_bonus = 30 if "fortify_speed" in statuses else 0
        haste_bonus = 40 if "haste" in statuses else 0
        equipment_speed = self.effective_speed_bonus * 15
        fieldcraft_speed = self.skill_fieldcraft_speed_bonus() if hasattr(self, "skill_fieldcraft_speed_bonus") else 0
        return max(25, AUTO_MOVE_INTERVAL_MS - self.haste_bonus - speed_bonus - haste_bonus - equipment_speed - fieldcraft_speed)

    @property
    def melee_range(self):
        weapon = self.equipped_weapon
        bk = getattr(weapon, "base_key", None) or (weapon.key if weapon else None)
        bonus = 1 if bk == "spear" else 0
        return 1 + self.reach_bonus + bonus + self.effective_range_bonus

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
        strength_bonus = 3 if "strength" in statuses else 0
        low_hp_bonus = 0
        if weapon and getattr(weapon, "low_hp_melee_bonus", 0) > 0:
            hp_pct = self.health / max(1, self.max_health)
            if hp_pct <= 0.33:
                low_hp_bonus = weapon.low_hp_melee_bonus
        skill_bonus = self.skill_melee_bonus() if hasattr(self, "skill_melee_bonus") else 0
        return self.melee_damage + (weapon.melee_bonus if weapon else 0) + atk_bonus + strength_bonus + self._trinket_bonus("melee") + low_hp_bonus + skill_bonus

    @property
    def effective_ranged_damage(self):
        weapon = self.equipped_weapon
        statuses = getattr(self, "player_statuses", {})
        atk_bonus = 1 if "fortify_attack" in statuses else 0
        ranged_pen = self.effective_ranged_penalty
        skill_bonus = self.skill_ranged_bonus() if hasattr(self, "skill_ranged_bonus") else 0
        return self.ranged_damage + (weapon.ranged_bonus if weapon else 0) + atk_bonus + self._trinket_bonus("ranged") + ranged_pen + skill_bonus

    @property
    def effective_defense(self):
        armor = self.equipped_armor
        statuses = getattr(self, "player_statuses", {})
        def_bonus = 2 if "fortify_defense" in statuses else 0
        return (armor.defense_bonus if armor else 0) + def_bonus + self._trinket_bonus("defense")
