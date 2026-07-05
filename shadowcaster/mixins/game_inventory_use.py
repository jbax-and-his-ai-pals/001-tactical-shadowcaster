from __future__ import annotations

from ..item_catalog import ITEM_CATALOG
from ..game_typing import GameMixinBase


class InventoryUseMixin(GameMixinBase):

    def add_catalog_item(self, key, quantity=1):
        spec = ITEM_CATALOG.get(key)
        if spec is None:
            return None
        return self.add_item(
            key, spec["name"], "consumable",
            spec["color"], spec["marker"],
            quantity=quantity,
            rarity=spec["rarity"],
            description=spec["description"],
        )

    def equip_item(self, key):
        item = self.inventory_item(key)
        if item is None or item.category not in ("weapon", "armor", "trinket"):
            return
        if item.category == "trinket" and getattr(self, "player_level", 1) < 2:
            self.message = "The trinket slot unlocks at level 2 (Seasoned)."
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
        spec = ITEM_CATALOG.get(key)
        if spec:
            parts = self._apply_item_effects(spec["effects"])
            if not parts:
                self.message = f"The {item.name} has no effect right now."
                return
        else:
            # Legacy fallback for items not yet in catalog
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

    def _apply_item_effects(self, effects):
        parts = []
        for eff in effects:
            etype = eff["type"]
            if etype == "restore_health":
                amount = self.tuning.get("medkit_heal", eff.get("amount", 4)) if eff.get("amount", 0) <= 4 else eff["amount"]
                before = self.health
                self.health = min(self.max_health, self.health + amount)
                gained = self.health - before
                if gained > 0:
                    parts.append(f"Recovered {gained} HP.")
            elif etype == "restore_max_health":
                self.max_health += eff.get("amount", 1)
                self.health = self.max_health
                parts.append(f"Max HP increases to {self.max_health}. Fully restored.")
            elif etype == "cure_all":
                if self.player_statuses:
                    cleared = ", ".join(sorted(self.player_statuses))
                    self.player_statuses.clear()
                    self.player_status_sources.clear()
                    parts.append(f"Cleared {cleared}.")
                else:
                    parts.append("No statuses to clear.")
            elif etype == "cure_poison":
                if "poison" in self.player_statuses:
                    self.clear_player_status("poison")
                    parts.append("Poison cleared.")
                else:
                    parts.append("No poison to cure.")
            elif etype == "cure_burn":
                if "burn" in self.player_statuses:
                    self.clear_player_status("burn")
                    parts.append("Burn cleared.")
                else:
                    parts.append("No burn to cure.")
            elif etype == "ward":
                duration = eff.get("duration", 4)
                self.add_status(self.player_statuses, "ward", duration)
                parts.append(f"Ward for {duration} turns.")
            elif etype == "regen":
                turns = eff.get("turns", 3)
                self.add_status(self.player_statuses, "regen", turns)
                parts.append(f"Regeneration for {turns} turns.")
            elif etype in ("resist_poison", "resist_fire"):
                turns = eff.get("turns", 6)
                self.add_status(self.player_statuses, etype, turns)
                label = "Poison" if etype == "resist_poison" else "Fire"
                parts.append(f"{label} resistance for {turns} turns.")
            elif etype == "fortify_attack":
                turns = eff.get("turns", 8)
                self.add_status(self.player_statuses, "fortify_attack", turns)
                parts.append(f"Attack fortified for {turns} turns.")
            elif etype == "fortify_defense":
                turns = eff.get("turns", 6)
                self.add_status(self.player_statuses, "fortify_defense", turns)
                parts.append(f"Defense fortified for {turns} turns.")
            elif etype == "fortify_speed":
                turns = eff.get("turns", 10)
                self.add_status(self.player_statuses, "fortify_speed", turns)
                parts.append(f"Speed fortified for {turns} turns.")
            elif etype == "fortify_light":
                turns = eff.get("turns", 8)
                self.add_status(self.player_statuses, "fortify_light", turns)
                self.update_visibility()
                parts.append(f"Sight extended for {turns} turns.")
        return parts

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
