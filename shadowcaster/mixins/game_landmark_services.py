from __future__ import annotations

import random

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase

# Per-kind biome flavor lines; biome groups collapse the 12 region types to 4.
_BIOME_GROUP = {
    "desert": "arid", "volcanic": "arid", "badlands": "arid",
    "tundra": "cold", "mountain": "cold",
    "swamp": "wet", "farmland": "wet",
    "forest": "wild", "plains": "wild", "castle": "wild",
    "cave": "wild", "maze": "wild",
}

_SURFACE_BIOME_FLAVOR = {
    "waystone": {
        "arid":  "Carved from heat-cracked sandstone, the inscriptions mark roads across the dust.",
        "cold":  "Frost-split runes, still legible if you know the old forms.",
        "wet":   "Half-sunk in the mud, the waystone tilts — but the directions hold.",
        "wild":  "Weathered but upright, the marker has stood longer than anyone remembers.",
    },
    "barrow": {
        "arid":  "Sun-bleached and dry — the arid air preserved everything.",
        "cold":  "Ice-sealed until recently, the contents are older than any name you know.",
        "wet":   "Moss-swallowed and waterlogged, but the grave goods survived.",
        "wild":  "An earthen mound, root-threaded, undisturbed for long enough to matter.",
    },
    "stone_circle": {
        "arid":  "The stones cast long shadows across the cracked ground.",
        "cold":  "Ice coats the standing stones, but the resonance cuts through.",
        "wet":   "Algae-furred and listing, the ring still holds its shape.",
        "wild":  "Grass grows thick between the uprights as if the ground approves.",
    },
    "oasis": {
        "arid":  "Green impossible against the bleached rock. You smell it before you see it.",
        "cold":  "A warm seep thaws a small hollow out of the frost.",
        "wet":   "Just a deeper pool in the standing water, but clean and still.",
        "wild":  "A spring-fed clearing, quieter than the land around it.",
    },
    "hot_spring": {
        "arid":  "Steam rising from the desert floor — brimstone-scented but welcome.",
        "cold":  "A hot vent in the ice; the warmth is almost violent after the cold.",
        "wet":   "The mud around the spring bubbles. The heat is gentler than it looks.",
        "wild":  "A rocky basin of steaming water, too warm for the season.",
    },
    "watchtower": {
        "arid":  "The top ring commands a view across the dust to every horizon.",
        "cold":  "Wind tears past the open parapet. The view makes it worth it.",
        "wet":   "The wood is rotted on the lower floors. The top still holds.",
        "wild":  "Stone stairs, mossy but sound. From the top the land opens up.",
    },
    "grove": {
        "arid":  "A hollow of scrub trees shading a spring no one mapped.",
        "cold":  "Evergreens packed tight enough to break the wind entirely.",
        "wet":   "The canopy seals out the rain. The air is quiet and heavy.",
        "wild":  "Old growth, cool and dim. Birdsong, nothing else.",
    },
    "necropolis": {
        "arid":  "Tombs cut into the cliff face — the dry air kept everything.",
        "cold":  "Permafrost cracked the seals. The cold preserved what the seals didn't.",
        "wet":   "Sunken crypts, half-flooded. Wealth and rot in equal measure.",
        "wild":  "Overgrown mausoleums in a clearing the forest is slowly reclaiming.",
    },
    "geyser": {
        "arid":  "The vent blows dry steam across the cracked basin.",
        "cold":  "A column of hot water punches through the snowpack every few minutes.",
        "wet":   "Mineral-hot water erupts from the bog floor at odd intervals.",
        "wild":  "A rocky throat that belches steam and heat without warning.",
    },
    "standing_stone": {
        "arid":  "A single slab upright in the open desert, casting the only shadow for miles.",
        "cold":  "Carved from a glacier-dragged boulder, set here before anyone was counting.",
        "wet":   "Granite sunk halfway into the soft ground, still tall enough to read.",
        "wild":  "Old enough that the land has grown up around it like it belongs.",
    },
    "camp": {
        "arid":  "Scorch marks, a lean-to of bleached poles, crates upended for wind cover.",
        "cold":  "A half-collapsed snow shelter and a cache box buried in the frost.",
        "wet":   "A raised platform over the mud, abandoned mid-meal by the look of it.",
        "wild":  "Fire ring, bedroll frame, a hook with nothing on it. Left in a hurry.",
    },
}


def _biome_flavor(region_type: str, kind: str) -> str:
    group = _BIOME_GROUP.get(region_type, "wild")
    return _SURFACE_BIOME_FLAVOR.get(kind, {}).get(group, "")


class LandmarkServicesMixin(GameMixinBase):

    def _world_danger_bonus(self) -> int:
        """0–3: world distance tier + 1 when region danger_tier >= 3."""
        wx, wy = self.world_position
        dist = max(abs(wx), abs(wy))
        dist_tier = min(2, dist // 2)
        danger_bump = 1 if self.danger_value() >= 3 else 0
        return min(3, dist_tier + danger_bump)

    def apply_surface_landmark(self, landmark):
        if landmark.key in self.claimed_surface_landmark_keys:
            self.message = f"{landmark.name} — already visited."
            return
        title = ""
        lines = []
        kind = landmark.kind
        bonus = self._world_danger_bonus()

        flavor = _biome_flavor(self.region_type, kind)
        if flavor:
            lines.append(flavor)

        if kind == "waystone":
            title = "Waystone — Routes Traced"
            revealed = self.reveal_one_adjacent_world_region()
            if revealed:
                _, name = revealed
                lines.append(f"One route marked: {name}.")
                if bonus >= 1:
                    extra = self.reveal_one_adjacent_world_region()
                    if extra:
                        _, extra_name = extra
                        lines.append(f"A second inscription: {extra_name}.")
                if bonus >= 3:
                    third = self.reveal_one_adjacent_world_region()
                    if third:
                        _, third_name = third
                        lines.append(f"A faint third mark — worn but readable: {third_name}.")
            else:
                lines.append("The markings describe only roads you already know.")
                ammo_gain = 1 + bonus
                self.ammo += ammo_gain
                lines.append(f"+{ammo_gain} ammo from a hidden niche. Ammo: {self.ammo}.")

        elif kind == "barrow":
            title = "Barrow — Ancient Grave"
            gold_gain = random.randint(2 + bonus, 4 + bonus * 2)
            self.gold += gold_gain
            medkits = 1 + (1 if bonus >= 2 else 0)
            tonics = 1 if bonus >= 3 else 0
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=medkits, description="Restores health.")
            if tonics:
                self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                              quantity=tonics, description="Clears statuses and grants ward.")
            lines.append("Burial goods left undisturbed — mostly. You take only what the dead no longer need.")
            tonic_note = f", +{tonics} tonic" if tonics else ""
            lines.append(f"+{gold_gain} gold, +{medkits} healing potion{'s' if medkits > 1 else ''}{tonic_note}.")
            if bonus >= 1:
                lead = self.reveal_one_adjacent_world_region()
                if lead:
                    _, lead_name = lead
                    lines.append(f"A carved stone near the entrance names a place: {lead_name}.")

        elif kind == "stone_circle":
            title = "Stone Circle — Old Power"
            ward_turns = 8 + bonus * 2
            self.add_status(self.player_statuses, "ward", ward_turns)
            lines.append("Stepping inside the ring, a low hum settles into your bones.")
            lines.append(f"Ward for {ward_turns} turns.")
            if bonus >= 2:
                lead = self.reveal_one_adjacent_world_region()
                if lead:
                    _, lead_name = lead
                    lines.append(f"The alignment of the stones points toward {lead_name}.")

        elif kind == "oasis":
            title = "Oasis — Water and Shade"
            heal = self.max_health - self.health
            if heal > 0:
                self.health = self.max_health
                lines.append(f"You drink deep and rest. Restored {heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            else:
                lines.append("You are already at full health.")
            ammo_gain = 2 + bonus
            self.ammo += ammo_gain
            lines.append(f"+{ammo_gain} ammo from dry reeds. Ammo: {self.ammo}.")
            # Oases are waypoints — reveal a route
            lead = self.reveal_one_adjacent_world_region()
            if lead:
                _, lead_name = lead
                lines.append(f"A trail marker points toward {lead_name}.")

        elif kind == "hot_spring":
            title = "Hot Spring — Deep Warmth"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = self.max_health - self.health
            if heal > 0:
                self.health = self.max_health
            if statuses_cleared:
                lines.append(f"The heat draws out the {' and '.join(statuses_cleared)}.")
            if heal > 0:
                lines.append(f"Fully restored. Health: {self.health} / {self.max_health}")
            if not statuses_cleared and not heal:
                lines.append("Already in good health, the soak is pure luxury.")
            # Bonus: at danger bonus 1+, grant short ward (mineral effects)
            if bonus >= 1:
                ward = bonus
                self.add_status(self.player_statuses, "ward", ward)
                lines.append(f"The minerals leave a {ward}-turn ward.")
            lines.append("You feel ready for whatever is next.")

        elif kind == "watchtower":
            title = "Watchtower — Clear Sightlines"
            revealed = self.reveal_adjacent_world_regions()
            if revealed:
                preview = ", ".join(name for _, name in revealed[:3])
                extra = f" and {len(revealed) - 3} more" if len(revealed) > 3 else ""
                lines.append(f"From the top you can see: {preview}{extra}.")
            else:
                lines.append("You can see for miles. Every route you already know.")
                ammo_gain = 2 + bonus
                self.ammo += ammo_gain
                lines.append(f"+{ammo_gain} ammo from a supply box. Ammo: {self.ammo}.")

        elif kind == "grove":
            title = "Grove — Still Air"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = min(self.max_health - self.health, max(2, self.max_health // 4) + bonus)
            if heal > 0:
                self.health += heal
                lines.append(f"The quiet here mends you. +{heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            if statuses_cleared:
                lines.append(f"Cleared: {', '.join(statuses_cleared)}.")
            if not heal and not statuses_cleared:
                lines.append("A stillness in the canopy. You are already well.")
            # Bonus: at danger 1+, the grove also imparts a short ward
            if bonus >= 1:
                ward = bonus
                self.add_status(self.player_statuses, "ward", ward)
                lines.append(f"Something in the air settles over you. Ward {ward} turns.")

        elif kind == "necropolis":
            title = "Necropolis — Looted Tombs"
            gold_gain = random.randint(3 + bonus, 6 + bonus * 2)
            self.gold += gold_gain
            medkits = 2 + (1 if bonus >= 3 else 0)
            tonics = 1 + (1 if bonus >= 2 else 0)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=medkits, description="Restores health.")
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=tonics, description="Clears statuses and grants ward.")
            lines.append("Generations of forgotten wealth. You cannot carry it all.")
            lines.append(f"+{gold_gain} gold, +{medkits} healing potions, +{tonics} ward tonic{'s' if tonics > 1 else ''}.")
            if bonus >= 2:
                lead = self.reveal_one_adjacent_world_region()
                if lead:
                    _, lead_name = lead
                    lines.append(f"Tomb markings reference another place: {lead_name}.")

        elif kind == "geyser":
            title = "Geyser — Scalding Find"
            ammo_gain = 2 + bonus
            self.ammo += ammo_gain
            tonics = 1 + (1 if bonus >= 2 else 0)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=tonics, description="Clears statuses and grants ward.")
            lines.append("A kit left by a previous traveler near the vent — still dry.")
            lines.append(f"+{ammo_gain} ammo, +{tonics} ward tonic{'s' if tonics > 1 else ''}.")
            if bonus >= 1:
                lead = self.reveal_one_adjacent_world_region()
                if lead:
                    _, lead_name = lead
                    lines.append(f"Trail marks scratched into a nearby rock point toward {lead_name}.")

        elif kind == "standing_stone":
            title = "Standing Stone — Old Directions"
            revealed = self.reveal_one_adjacent_world_region()
            if revealed:
                _, name = revealed
                lines.append(f"Scratched into the face: an old name. {name}.")
                # Follow-up: at bonus 2, the stone also names a second place
                if bonus >= 2:
                    extra = self.reveal_one_adjacent_world_region()
                    if extra:
                        _, extra_name = extra
                        lines.append(f"Lower down, a second inscription: {extra_name}.")
            else:
                lines.append("The stone names only places you already know.")
            lines.append("You copy the markings and move on.")

        elif kind == "camp":
            title = "Abandoned Camp — Trail Stores"
            ammo_gain = 2 + bonus
            self.ammo += ammo_gain
            medkits = 1 + (1 if bonus >= 2 else 0)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=medkits, description="Restores health.")
            lines.append("Someone left in a hurry. Their loss.")
            lines.append(f"+{ammo_gain} ammo, +{medkits} healing potion{'s' if medkits > 1 else ''}.")
            if bonus >= 1:
                lead = self.reveal_one_adjacent_world_region()
                if lead:
                    _, lead_name = lead
                    lines.append(f"A map scrap in the supplies shows a route toward {lead_name}.")

        if not title:
            return
        self.claimed_surface_landmark_keys.add(landmark.key)
        self.service_modal_title = title
        self.service_modal_lines = lines
        self.service_modal_open = True
        self.store_current_region()
