from __future__ import annotations

import random

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase


class ServiceBoonsMixin(GameMixinBase):

    def _apply_service_boon(self, resident, claim_key):
        if resident.kind == "innkeeper":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            restore = max(2, (self.max_health - self.health) // 2)
            if self.health >= self.max_health:
                self.message = "The innkeeper offers a room, but you're already in full health."
                return True
            self.health = min(self.max_health, self.health + restore)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            self.message = f"The innkeeper gives you a proper rest. HP {self.health}/{self.max_health}."
            return True
        if resident.kind == "healer":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            bad = [s for s in list(self.player_statuses) if s != "ward"]
            if not bad:
                self.message = "The healer finds nothing to treat. Come back if the road changes that."
                return True
            for s in bad:
                self.clear_player_status(s)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            self.message = f"The healer clears your afflictions: {', '.join(bad)}."
            return True
        if resident.kind == "blacksmith":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            self.interaction_claims.add(claim_key)
            self.add_status(self.player_statuses, "ward", 6)
            self.store_current_region()
            self.message = "The blacksmith sets iron bracing on you before you leave. Ward 6 turns."
            return True
        if resident.kind == "barkeep":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            self.interaction_claims.add(claim_key)
            self.add_status(self.player_statuses, "ward", 4)
            self.store_current_region()
            self.message = "The barkeep slips you something bracing for the road. Ward 4 turns."
            return True
        if resident.kind == "priest":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            self.interaction_claims.add(claim_key)
            self.add_status(self.player_statuses, "ward", 8)
            self.store_current_region()
            self.message = "The priest sets a road blessing on you. Ward 8 turns."
            return True
        if resident.kind == "surveyor":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            count = 0
            for _ in range(2):
                if self.reveal_one_adjacent_world_region():
                    count += 1
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            if count == 0:
                self.message = "The surveyor nods. 'Every adjacent route is already charted.'"
            else:
                self.message = f"The surveyor charts {count} nearby route{'s' if count > 1 else ''} on your map."
            return True
        if resident.kind == "armorer":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            self.interaction_claims.add(claim_key)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            self.store_current_region()
            self.message = f"The armorer fits a spare tonic before you leave. Tonics {self.inventory_quantity('tonic')}."
            return True
        if resident.kind == "apothecary":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            self.interaction_claims.add(claim_key)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=2, description="Restores health.")
            self.store_current_region()
            self.message = f"The apothecary presses two potions into your pack. Kits {self.inventory_quantity('medkit')}."
            return True
        if resident.kind == "librarian":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            hidden = [lm for lm in self.landmarks if lm.position not in self.seen_tiles]
            if not hidden:
                self.message = "The librarian looks up. 'You seem to have found everything already.'"
                return True
            for lm in hidden[:2]:
                self.seen_tiles.add(lm.position)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            names = " and ".join(lm.name for lm in hidden[:2])
            self.message = f"The librarian marks {names} on your map."
            return True
        if resident.kind == "watch_captain":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            entries = []
            for direction in ("north", "south", "west", "east"):
                coord = self.move_coord(self.world_position, direction)
                key = self.region_key(coord)
                state = self.world_regions.get(key)
                if state is None:
                    state = self.create_world_region_state(coord)
                    self.preview_world_regions[key] = state
                danger = state.get("danger_tier", 1)
                name = state.get("region_name", "unknown")
                entries.append((danger, name, direction))
            entries.sort(key=lambda e: -e[0])
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            top = entries[0]
            self.message = f"Captain's briefing: {top[1]} ({top[2]}, tier {top[0]}) is highest. All 4 routes assessed."
            return True
        if resident.kind == "mayor":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            count = 0
            for direction in ("north", "south", "west", "east"):
                coord = self.move_coord(self.world_position, direction)
                key = self.region_key(coord)
                if key not in self.world_regions and key not in self.preview_world_regions:
                    self.preview_world_regions[key] = self.create_world_region_state(coord)
                    count += 1
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            if count == 0:
                self.message = "The mayor nods. 'You already know everything I know about these roads.'"
            else:
                self.message = f"The mayor's knowledge fills in {count} blank route{'s' if count > 1 else ''} on your map."
            return True
        if resident.kind == "baker":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            if self.health >= self.max_health:
                self.message = "The baker would spare a loaf, but you look well-fed already."
                return True
            self.health = min(self.max_health, self.health + 2)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            self.message = f"The baker presses a still-warm loaf into your hands. HP {self.health}/{self.max_health}."
            return True
        if resident.kind == "fletcher":
            if claim_key in self.interaction_claims:
                self.message = self._return_line(resident)
                return True
            self.interaction_claims.add(claim_key)
            self.ammo += 2
            self.store_current_region()
            self.message = f"The fletcher counts out two bolts from the rack. Ammo {self.ammo}."
            return True
        if resident.kind in {"laborer", "patron", "townsfolk", "herald"}:
            if resident.dialogue:
                self.message = random.choice(resident.dialogue)
            else:
                self.message = "They glance your way briefly, then go back to what they were doing."
            return True
        return False
