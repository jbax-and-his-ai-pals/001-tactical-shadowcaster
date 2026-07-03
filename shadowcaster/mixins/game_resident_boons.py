from __future__ import annotations

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase
from ..systems import heuristic


class ResidentBoonsMixin(GameMixinBase):
    def apply_resident_boon(self, resident):
        if self.region_type != "town":
            return False
        claim_key = f"resident:{resident.kind}"
        if resident.kind == "guide":
            hidden_landmarks = [landmark for landmark in self.landmarks if landmark.position not in self.seen_tiles]
            if claim_key in self.interaction_claims:
                self.message = "The guide says you've already got the best local lead they can offer."
                return True
            if not hidden_landmarks:
                self.message = "The guide smiles. You've already found every notable place nearby."
                return True
            landmark = min(hidden_landmarks, key=lambda item: heuristic(self.player, item.position))
            self.seen_tiles.add(landmark.position)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            self.message = f"The guide marks {landmark.name} on your map."
            return True
        if resident.kind == "scout":
            if claim_key in self.interaction_claims:
                self.message = "The scout has already shared the safest nearby route."
                return True
            revealed = self.reveal_one_adjacent_world_region()
            if not revealed:
                self.message = "The scout shrugs. Every nearby route is already charted."
                return True
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            _, region_name = revealed
            self.message = f"The scout points out a route to {region_name}."
            return True
        if resident.kind == "farmer":
            if claim_key in self.interaction_claims:
                self.message = "The farmer wishes you luck on the road."
                return True
            if self.health >= self.max_health:
                self.message = "The farmer offers a bite to eat, but you're already in good shape."
                return True
            self.health = min(self.max_health, self.health + 1)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            self.message = f"The farmer shares a meal. HP {self.health}/{self.max_health}."
            return True
        if resident.kind == "watch":
            if claim_key in self.interaction_claims:
                self.message = "The watcher says the roads are as clear as they can make them."
                return True
            nearby = []
            for direction in ("north", "south", "west", "east"):
                coord = self.move_coord(self.world_position, direction)
                key = self.region_key(coord)
                state = self.world_regions.get(key)
                if state is None:
                    state = self.create_world_region_state(coord)
                    self.preview_world_regions[key] = state
                danger = state.get("danger_tier", 1)
                nearby.append((danger, coord, state["region_name"]))
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            if not nearby:
                self.message = "The watcher has nothing urgent to report."
                return True
            nearby.sort(key=lambda item: (-item[0], item[2]))
            danger, _, region_name = nearby[0]
            self.message = f"The watcher warns that {region_name} looks dangerous for this stretch of road (tier {danger})."
            return True
        if resident.kind == "vendor":
            if claim_key in self.interaction_claims:
                self.message = "The vendor has already spared what they could."
                return True
            self.interaction_claims.add(claim_key)
            self.ammo += 1
            self.store_current_region()
            self.message = f"The vendor presses a little stock into your hands. Ammo {self.ammo}."
            return True
        if resident.kind == "herbalist":
            if claim_key in self.interaction_claims:
                self.message = "The herbalist has already mixed what they can for today."
                return True
            if "poison" not in self.player_statuses and "burn" not in self.player_statuses:
                self.message = "The herbalist says to come back if the road leaves a worse sting on you."
                return True
            self.clear_player_status("poison")
            self.clear_player_status("burn")
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            self.message = "The herbalist works a quick remedy and eases your afflictions."
            return True
        if resident.kind == "elder":
            if claim_key in self.interaction_claims:
                self.message = "The elder has already pointed you toward what mattered most."
                return True
            building = self.reveal_one_hidden_town_building()
            if building is None:
                self.message = "The elder smiles. There are no hidden corners in this town for you now."
                return True
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            district = building.get("district", "town")
            self.message = f"The elder directs you toward {building['name']} in the {district}."
            return True
        if resident.kind == "drover":
            if claim_key in self.interaction_claims:
                self.message = "The drover has already shared a bit of trail stock."
                return True
            self.interaction_claims.add(claim_key)
            self.ammo += 1
            self.store_current_region()
            self.message = f"The drover presses spare shot into your hand. Ammo {self.ammo}."
            return True
        if resident.kind == "miller":
            if claim_key in self.interaction_claims:
                self.message = "The miller has already packed what they could spare."
                return True
            self.interaction_claims.add(claim_key)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            self.store_current_region()
            self.message = f"The miller hands you a flour-wrapped field kit. Kits {self.inventory_quantity('medkit')}."
            return True
        if resident.kind == "ferryman":
            if claim_key in self.interaction_claims:
                self.message = "The ferryman has already shown you the surest way out."
                return True
            exit_tile = self.reveal_one_town_exit()
            if exit_tile is None:
                self.message = "The ferryman shrugs. Every road out of town is already familiar to you."
                return True
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            direction = next((name for name, tile in self.edge_exits.items() if tile == exit_tile), "out")
            self.message = f"The ferryman points out the {direction}ern way clear of town."
            return True
        if resident.kind == "mason":
            if claim_key in self.interaction_claims:
                self.message = "The mason has already braced you as well as they can."
                return True
            self.interaction_claims.add(claim_key)
            self.add_status(self.player_statuses, "ward", 4)
            self.store_current_region()
            self.message = "The mason steadies your footing and leaves a Ward on you for 4 turns."
            return True
        if resident.kind == "trapper":
            if claim_key in self.interaction_claims:
                self.message = "The trapper has already shared spare trail supplies."
                return True
            self.interaction_claims.add(claim_key)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            self.store_current_region()
            self.message = f"The trapper slips you a tonic for bad country. Tonics {self.inventory_quantity('tonic')}."
            return True
        if resident.kind == "kilnkeeper":
            if claim_key in self.interaction_claims:
                self.message = "The kilnkeeper has already done what they can for your road heat."
                return True
            cleared_burn = "burn" in self.player_statuses
            self.clear_player_status("burn")
            self.add_status(self.player_statuses, "ward", 4)
            self.interaction_claims.add(claim_key)
            self.store_current_region()
            if cleared_burn:
                self.message = "The kilnkeeper banks the heat out of your wounds and leaves you warded for 4 turns."
            else:
                self.message = "The kilnkeeper teaches you how to carry the heat better. Ward 4 turns."
            return True
        return False

    def adjacent_residents(self):
        return [
            resident
            for resident in self.residents
            if max(abs(resident.position[0] - self.player[0]), abs(resident.position[1] - self.player[1])) == 1
        ]

    def choose_adjacent_resident(self):
        adjacent = self.adjacent_residents()
        if not adjacent:
            return None
        adjacent.sort(key=lambda resident: (0 if resident.position in self.visible_tiles else 1, heuristic(self.player, resident.position)))
        return adjacent[0]

    def maybe_interact_with_adjacent_resident(self, previous_adjacent_positions=None):
        resident = self.choose_adjacent_resident()
        if resident is None:
            return False
        if previous_adjacent_positions is not None and resident.position in previous_adjacent_positions:
            return False
        self.talk_to_resident(resident)
        return True
