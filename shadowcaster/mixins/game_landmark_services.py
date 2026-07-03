from __future__ import annotations

import random

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase


class LandmarkServicesMixin(GameMixinBase):

    def apply_surface_landmark(self, landmark):
        if landmark.key in self.claimed_surface_landmark_keys:
            self.message = f"{landmark.name} — already visited."
            return
        title = ""
        lines = []
        kind = landmark.kind
        if kind == "waystone":
            title = "Waystone — Routes Traced"
            revealed = self.reveal_one_adjacent_world_region()
            if revealed:
                _, name = revealed
                lines.append(f"Faded carvings point toward {name}.")
            else:
                lines.append("The markings describe only roads you already know.")
                self.ammo += 1
                lines.append(f"+1 ammo from a hidden niche. Ammo: {self.ammo}.")
        elif kind == "barrow":
            title = "Barrow — Ancient Grave"
            self.gold += random.randint(2, 4)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            lines.append("Burial goods left undisturbed — mostly. You take only what the dead no longer need.")
            lines.append(f"+{self.gold} gold, +1 healing potion.")
        elif kind == "stone_circle":
            title = "Stone Circle — Old Power"
            ward_turns = 8
            self.add_status(self.player_statuses, "ward", ward_turns)
            lines.append("Stepping inside the ring, a low hum settles into your bones.")
            lines.append(f"Ward for {ward_turns} turns.")
        elif kind == "oasis":
            title = "Oasis — Water and Shade"
            heal = self.max_health - self.health
            if heal > 0:
                self.health = self.max_health
                lines.append(f"You drink deep and rest. Restored {heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            else:
                lines.append("You are already at full health.")
            self.ammo += 2
            lines.append(f"+2 ammo from dry reeds. Ammo: {self.ammo}.")
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
            if not lines:
                lines.append("You are already at full health with no ailments.")
            lines.append("A long soak. You feel ready.")
        elif kind == "watchtower":
            title = "Watchtower — Clear Sightlines"
            revealed = self.reveal_adjacent_world_regions()
            if revealed:
                preview = ", ".join(name for _, name in revealed[:3])
                extra = f" and {len(revealed) - 3} more" if len(revealed) > 3 else ""
                lines.append(f"From the top you can see: {preview}{extra}.")
            else:
                lines.append("You can see for miles. Every route you already know.")
                self.ammo += 2
                lines.append(f"+2 ammo from a supply box. Ammo: {self.ammo}.")
        elif kind == "grove":
            title = "Grove — Still Air"
            statuses_cleared = [s for s in ("poison", "burn") if s in self.player_statuses]
            for s in statuses_cleared:
                self.clear_player_status(s)
            heal = min(self.max_health - self.health, max(2, self.max_health // 4))
            if heal > 0:
                self.health += heal
                lines.append(f"The quiet here mends you. +{heal} HP.")
                lines.append(f"Health: {self.health} / {self.max_health}")
            if statuses_cleared:
                lines.append(f"Cleared: {', '.join(statuses_cleared)}.")
            if not lines:
                lines.append("A stillness in the canopy. You are already well.")
        elif kind == "necropolis":
            title = "Necropolis — Looted Tombs"
            self.gold += random.randint(3, 6)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=2, description="Restores health.")
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            lines.append("Generations of forgotten wealth. You cannot carry it all.")
            lines.append(f"+{self.gold} gold, +2 healing potions, +1 ward tonic.")
        elif kind == "geyser":
            title = "Geyser — Scalding Find"
            self.ammo += 2
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            lines.append("A kit left by a previous traveler near the vent — still dry.")
            lines.append(f"+2 ammo, +1 ward tonic.")
        elif kind == "standing_stone":
            title = "Standing Stone — Old Directions"
            revealed = self.reveal_one_adjacent_world_region()
            if revealed:
                _, name = revealed
                lines.append(f"Scratched into the face: an old name. {name}.")
            else:
                lines.append("The stone names only places you already know.")
            lines.append("You copy the markings and move on.")
        elif kind == "camp":
            title = "Abandoned Camp — Trail Stores"
            self.ammo += 2
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            lines.append("Someone left in a hurry. Their loss.")
            lines.append(f"+2 ammo, +1 healing potion.")
        if not title:
            return
        self.claimed_surface_landmark_keys.add(landmark.key)
        self.service_modal_title = title
        self.service_modal_lines = lines
        self.service_modal_open = True
        self.store_current_region()
