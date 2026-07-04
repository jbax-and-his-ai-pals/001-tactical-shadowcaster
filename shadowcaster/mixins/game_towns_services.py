from __future__ import annotations

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase

_SERVICE_REGION_TYPES = {
    "inn", "clinic", "supply", "shrine", "smith", "cartographer", "tavern",
    "chapel", "stable", "bathhouse", "armory", "apothecary",
    "cave", "dungeon", "castle", "ruins", "cache",
}


class TownsServicesMixin(GameMixinBase):

    def apply_town_service(self):
        if self.service_claimed or self.region_type not in _SERVICE_REGION_TYPES:
            return
        title = ""
        lines = []
        service_bonus = self.town_service_bonus_tier()
        if self.region_type == "inn":
            title = "Inn — Rest"
            heal = min(self.max_health - self.health, 3 + service_bonus)
            if heal > 0:
                self.health += heal
                lines.append(f"You rest and recover {heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            else:
                lines.append("You are already at full health.")
                lines.append("Rest is still welcome.")
            if service_bonus:
                lines.append("The innkeeper remembers your help and puts a little extra care into your stay.")
        elif self.region_type == "clinic":
            title = "Clinic — Treatment"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = min(self.max_health - self.health, 2 + service_bonus)
            if heal > 0:
                self.health = min(self.max_health, self.health + heal)
            if statuses_cleared:
                lines.append(f"Cleared: {', '.join(statuses_cleared)}.")
            if heal > 0:
                lines.append(f"Wounds dressed — recovered {heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            elif not statuses_cleared:
                lines.append("You are in good health.")
                lines.append("Nothing to treat.")
            else:
                lines.append("You are already at full health.")
            if service_bonus:
                lines.append("The healer takes extra care — your reputation here is well earned.")
        elif self.region_type == "supply":
            title = "Provisioner — Resupply"
            ammo_gain = 1 + service_bonus
            medkit_gain = 1 + (1 if service_bonus >= 2 else 0)
            self.ammo += ammo_gain
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=medkit_gain, description="Restores health.")
            lines.append("Stocked up for the road.")
            lines.append(f"+{ammo_gain} ammo (now {self.ammo}), +{medkit_gain} healing potion{'s' if medkit_gain != 1 else ''}.")
            if service_bonus:
                lines.append("Your reputation here opens the back shelf.")
        elif self.region_type == "shrine":
            title = "Shrine — Blessing"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = min(self.max_health - self.health, self.max_health)
            if heal > 0:
                self.health = min(self.max_health, self.health + heal)
            if statuses_cleared:
                lines.append(f"A quiet light clears {', '.join(statuses_cleared)}.")
            if heal > 0:
                lines.append(f"Wounds fade — restored {heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            elif not statuses_cleared:
                lines.append("You are already at full health.")
            if not lines:
                lines.append("A stillness settles over you.")
        elif self.region_type == "smith":
            title = "Smithy — Outfitted"
            ammo_gain = 1 + service_bonus
            tonic_gain = 1 + (1 if service_bonus >= 2 else 0)
            self.ammo += ammo_gain
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=tonic_gain, description="Clears statuses and grants ward.")
            lines.append("The smith sets you up for the trail.")
            lines.append(f"+{ammo_gain} ammo (now {self.ammo}), +{tonic_gain} ward tonic{'s' if tonic_gain != 1 else ''}.")
            if service_bonus:
                lines.append("They throw in a little extra — word travels fast in a small town.")
        elif self.region_type == "cartographer":
            title = "Survey Office — Routes Mapped"
            revealed = self.reveal_adjacent_world_regions()
            if revealed:
                preview = ", ".join(name for _, name in revealed[:3])
                extra = f" and {len(revealed) - 3} more" if len(revealed) > 3 else ""
                lines.append(f"New routes marked: {preview}{extra}.")
            else:
                lines.append("Survey maps are already up to date.")
                lines.append("No new routes to chart.")
        elif self.region_type == "tavern":
            title = "Tavern — Road Rumors"
            revealed = []
            result = self.reveal_one_adjacent_world_region()
            if result:
                revealed.append(result)
            if service_bonus >= 2:
                result = self.reveal_one_adjacent_world_region()
                if result:
                    revealed.append(result)
            if revealed:
                names = " and ".join(name for _, name in revealed)
                lines.append(f"A traveler at the bar tips you off about {names}.")
            else:
                lines.append("The bar's talk has dried up — every route you know already.")
            gold_gain = 2 + service_bonus
            self.gold += gold_gain
            lines.append(f"+{gold_gain} gold from a small trade. Gold: {self.gold}.")
            if service_bonus:
                lines.append("A regular face gets a fair cut.")
        elif self.region_type == "chapel":
            title = "Chapel — Road Blessing"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            ward_turns = (6 if statuses_cleared else 3) + service_bonus
            self.add_status(self.player_statuses, "ward", ward_turns)
            if statuses_cleared:
                lines.append(f"Afflictions cleared: {', '.join(statuses_cleared)}.")
            lines.append(f"A ward settles over you for {ward_turns} turns.")
            if service_bonus:
                lines.append("The blessing holds a little longer for a friend of this town.")
        elif self.region_type == "stable":
            title = "Stable — Back-Country Routes"
            revealed = []
            for _ in range(2):
                result = self.reveal_one_adjacent_world_region()
                if result:
                    revealed.append(result)
            if revealed:
                names = " and ".join(name for _, name in revealed)
                lines.append(f"The stable hand knows the back roads: {names}.")
            else:
                self.ammo += 2
                lines.append("All nearby routes are already mapped.")
                lines.append(f"+2 ammo from trail supplies (now {self.ammo}).")
        elif self.region_type == "bathhouse":
            title = "Bathhouse — Full Restore"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = self.max_health - self.health
            if heal > 0:
                self.health = self.max_health
            if statuses_cleared:
                lines.append(f"The heat draws out the {' and '.join(statuses_cleared)}.")
            if heal > 0:
                lines.append(f"You soak until fully recovered. +{heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            elif not statuses_cleared:
                lines.append("You are already in full health. The soak is welcome rest.")
            if service_bonus:
                ward = service_bonus
                self.add_status(self.player_statuses, "ward", ward)
                lines.append(f"A regular visitor gets the mineral treatment. Ward {ward} turns.")
        elif self.region_type == "armory":
            title = "Armory — Outfitted"
            ammo_gain = 2 + service_bonus
            tonic_gain = 1 + (1 if service_bonus >= 2 else 0)
            self.ammo += ammo_gain
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=tonic_gain, description="Clears statuses and grants ward.")
            lines.append("The quartermaster sets you up from the reserve stock.")
            lines.append(f"+{ammo_gain} ammo (now {self.ammo}), +{tonic_gain} ward tonic{'s' if tonic_gain != 1 else ''}.")
            if service_bonus:
                lines.append("Known allies get access to the better shelf.")
        elif self.region_type == "apothecary":
            title = "Apothecary — Treatment"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = min(self.max_health - self.health, 1 + service_bonus)
            if heal > 0:
                self.health = min(self.max_health, self.health + heal)
            tonic_gain = 1 + (1 if service_bonus >= 1 else 0)
            medkit_gain = 1 + (1 if service_bonus >= 2 else 0)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=tonic_gain, description="Clears statuses and grants ward.")
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=medkit_gain, description="Restores health.")
            if statuses_cleared:
                lines.append(f"The apothecary clears {', '.join(statuses_cleared)}.")
            if heal > 0:
                lines.append(f"A quick treatment. +{heal} HP.")
            lines.append(f"+{tonic_gain} ward tonic{'s' if tonic_gain != 1 else ''}, +{medkit_gain} healing potion{'s' if medkit_gain != 1 else ''}.")
            if service_bonus:
                lines.append("A trusted customer gets the full compounding service.")
        elif self.region_type == "cave":
            title = "Cache Found"
            self.ammo += 2
            lines.append("A stash of arrows near the entrance.")
            lines.append(f"+2 ammo (now {self.ammo}).")
        elif self.region_type in {"dungeon", "castle"}:
            title = "Kit Found" if self.region_type == "dungeon" else "Ward Cached"
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=1, description="Clears statuses and grants ward.")
            if self.region_type == "dungeon":
                lines.append("An adventurer's pack left near the gate.")
            else:
                lines.append("A ward tonic remains from a previous expedition.")
            lines.append("+1 ward tonic.")
        elif self.region_type == "ruins":
            title = "Salvage Found"
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=1, description="Restores health.")
            lines.append("You salvage a healing potion from the debris.")
            lines.append("+1 healing potion.")
        elif self.region_type == "cache":
            title = "Cache Opened"
            self.ammo += 3
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=2, description="Restores health.")
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=1, description="Clears statuses and grants ward.")
            lines.append("Someone packed this carefully. You take everything.")
            lines.append(f"+3 ammo (now {self.ammo}), +2 healing potions, +1 ward tonic.")
        self.service_claimed = True
        self.service_modal_title = title
        self.service_modal_lines = lines
        self.service_modal_open = True
        self.store_current_region()
