from __future__ import annotations

import random

from ..constants import COLOR_ACCENT, COLOR_HEAL
from ..game_typing import GameMixinBase
from ..models import Landmark
from ..regions import RegionChoice, random_region_name
from ..systems import heuristic


class TownsMixin(GameMixinBase):
    def resident_role_summary(self, resident):
        summaries = {
            "guide": "Can mark one local site",
            "scout": "Can reveal one nearby route",
            "farmer": "May share a meal",
            "watch": "Can warn you about nearby danger",
            "vendor": "May spare a little trail stock",
            "herbalist": "May soothe poison or burn",
            "elder": "Can point out a hidden address",
            "drover": "May spare trail ammunition",
            "miller": "May share a field kit",
            "ferryman": "Can point out the town's way out",
            "mason": "Can brace you with a ward",
            "trapper": "May spare a tonic",
            "kilnkeeper": "Can bank the heat into a ward",
        }
        return summaries.get(resident.kind)

    def resident_routine_summary(self, resident):
        routine_labels = {
            "stationary": "Keeps to one post",
            "plaza": "Circles the square",
            "homebound": "Stays near home",
            "patrol": "Walks a regular patrol",
            "wander": "Wanders the streets",
        }
        return routine_labels.get(resident.behavior)

    def town_building_landmarks(self):
        building_data = getattr(self.dungeon, "metadata", {}).get("town_buildings", [])
        palette = {
            "inn": ("inn", (222, 188, 128)),
            "clinic": ("clinic", (188, 232, 244)),
            "supply": ("supply", (220, 198, 126)),
            "shrine": ("shrine", (212, 196, 248)),
            "smith": ("smith", (228, 160, 92)),
            "cartographer": ("cartographer", (156, 214, 236)),
        }
        landmarks = []
        for index, building in enumerate(building_data):
            if not building.get("enterable"):
                continue
            marker, color = palette.get(building["kind"], ("town", (210, 182, 120)))
            landmarks.append(Landmark(f"building_{index}_{building['kind']}", building["door"], building["kind"], building["name"], color, marker))
        return landmarks

    def town_building_data(self):
        return getattr(self.dungeon, "metadata", {}).get("town_buildings", [])

    def town_non_service_buildings(self):
        return [building for building in self.town_building_data() if not building.get("enterable")]

    def feature_footprints(self):
        return getattr(self.dungeon, "metadata", {}).get("feature_footprints", {})

    def feature_tiles(self, anchor):
        return set(self.feature_footprints().get(anchor, {anchor}))

    def feature_anchor_at(self, position):
        for anchor, tiles in self.feature_footprints().items():
            if position in tiles:
                return anchor
        if position in getattr(self, "terrain_features", {}):
            return position
        return None

    def terrain_kind_at(self, position):
        anchor = self.feature_anchor_at(position) or position
        return getattr(self, "terrain_features", {}).get(anchor)

    def nearest_town_path_tile(self, origin, candidates=None):
        path_tiles = list(candidates if candidates is not None else getattr(self.dungeon, "metadata", {}).get("town_paths", set()))
        if not path_tiles:
            return origin
        return min(path_tiles, key=lambda tile: heuristic(tile, origin))

    def generate_landmarks(self):
        if self.region_type == "town":
            return self.town_building_landmarks()
        if not self.is_overworld_region():
            return []
        candidates = [tile for tile in self.floor_explorable_tiles if tile not in self.reserved_special_tiles(include_units=True)]
        room_centers = [room.center for room in self.dungeon.rooms if room.center in candidates]
        available_tiles = room_centers or candidates
        if not available_tiles:
            return []
        count_weights = {
            "forest": [1, 5, 3],
            "plains": [1, 4, 4],
            "farmland": [1, 4, 4],
            "desert": [2, 5, 2],
            "swamp": [2, 5, 2],
            "mountain": [2, 6, 1],
            "badlands": [2, 5, 2],
            "tundra": [2, 5, 2],
            "volcanic": [2, 6, 1],
        }
        count = random.choices([0, 1, 2], weights=count_weights.get(self.region_type, [2, 5, 2]), k=1)[0]
        landmark_pool = {
            "forest": ["town", "cave", "ruins", "dungeon", "town"],
            "plains": ["town", "castle", "cave", "ruins", "town"],
            "farmland": ["town", "town", "castle", "ruins", "cave"],
            "desert": ["ruins", "cave", "dungeon", "town", "ruins"],
            "swamp": ["ruins", "cave", "dungeon", "ruins", "town"],
            "mountain": ["castle", "dungeon", "cave", "ruins", "cave"],
            "badlands": ["ruins", "castle", "cave", "dungeon", "ruins"],
            "tundra": ["cave", "ruins", "town", "castle", "dungeon"],
            "volcanic": ["dungeon", "cave", "ruins", "monster_town", "dungeon"],
        }.get(self.region_type, ["cave", "dungeon", "town", "castle", "ruins"])
        random.shuffle(available_tiles)
        random.shuffle(landmark_pool)
        landmarks = []
        chosen_kinds = []
        for kind in landmark_pool:
            if kind not in chosen_kinds:
                chosen_kinds.append(kind)
        if self.floor >= 4 and "monster_town" not in chosen_kinds and self.region_type in {"swamp", "mountain", "desert", "badlands", "volcanic"}:
            insert_at = random.randint(0, len(chosen_kinds))
            chosen_kinds.insert(insert_at, "monster_town")
        for index in range(min(count, len(available_tiles), len(chosen_kinds))):
            kind = chosen_kinds[index]
            marker, color = {
                "cave": ("cave", (172, 144, 116)),
                "dungeon": ("dungeon", (154, 164, 182)),
                "town": ("town", (210, 182, 120)),
                "castle": ("castle", (196, 188, 220)),
                "ruins": ("ruins", (184, 148, 108)),
                "monster_town": ("monster_town", (220, 96, 120)),
            }[kind]
            landmarks.append(Landmark(f"poi_{index}_{kind}", available_tiles[index], kind, random_region_name(kind), color, marker))
        return landmarks

    def enter_landmark(self, landmark):
        self.store_current_region()
        if self.in_local_region():
            context_base = self.local_region_base_key()
        else:
            context_base = self.region_key(self.world_position)
        local_base_key = f"{context_base}::{landmark.key}"
        local_key = self.local_region_depth_key(local_base_key, 1)
        legacy_key = local_base_key
        if local_key not in self.local_regions and legacy_key in self.local_regions:
            self.local_regions[local_key] = self.local_regions[legacy_key]
        parent_tier = self.danger_tier
        if local_key not in self.local_regions:
            interior_kind = landmark.kind if landmark.kind in {"inn", "clinic", "supply", "shrine", "smith", "cartographer"} else landmark.kind
            chosen = RegionChoice(region_type=interior_kind, name=landmark.name, summary="", context=self.town_context_for_landmark(landmark))
            self.current_local_region = local_key
            with self.seed_scope("build_floor", ("local", local_key), self.floor):
                self.build_floor(chosen_region=chosen, delve_depth=1, parent_danger_tier=parent_tier)
            self.player = self.initial_local_entry_tile()
            self.seen_tiles = set()
            self.update_visibility()
            self.last_interest_tiles = self.visible_interest_tiles()
            self.update_camera()
            self.store_current_region()
        self.current_local_region = local_key
        self.load_region_state(self.local_regions[local_key])
        self.player = self.safe_arrival_tile(self.initial_local_entry_tile())
        self.update_visibility()
        self.last_interest_tiles = self.visible_interest_tiles()
        self.update_camera()
        self.message = ""
        self.apply_town_service()
        if not self.message:
            self.message = f"You enter {landmark.name}."

    def apply_town_service(self):
        if self.service_claimed or self.region_type not in {"inn", "clinic", "supply", "shrine", "smith", "cartographer"}:
            return
        if self.region_type == "inn":
            heal = min(self.max_health - self.health, 3)
            self.health += heal
            self.service_claimed = True
            self.message = f"You rest at the inn. HP {self.health}/{self.max_health}."
        elif self.region_type == "clinic":
            cleared = ", ".join(sorted(self.player_statuses)) if self.player_statuses else "nothing"
            self.clear_player_status("poison")
            self.clear_player_status("burn")
            self.health = min(self.max_health, self.health + 2)
            self.service_claimed = True
            self.message = f"The clinic patches you up and clears {cleared}. HP {self.health}/{self.max_health}."
        elif self.region_type == "supply":
            self.ammo += 1
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality", quantity=1, description="Restores health.")
            self.service_claimed = True
            self.message = f"You resupply for the road. Ammo {self.ammo}, kits {self.inventory_quantity('medkit')}."
        elif self.region_type == "shrine":
            cleared = ", ".join(sorted(status for status in self.player_statuses if status in {"poison", "burn"})) or "nothing"
            self.clear_player_status("poison")
            self.clear_player_status("burn")
            self.add_status(self.player_statuses, "ward", 8)
            self.service_claimed = True
            self.message = f"A quiet blessing settles over you. It clears {cleared} and grants Ward 8t."
        elif self.region_type == "smith":
            self.ammo += 1
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power", quantity=1, description="Clears statuses and grants ward.")
            self.service_claimed = True
            self.message = f"The smith outfits you for the trail. Ammo {self.ammo}, tonics {self.inventory_quantity('tonic')}."
        elif self.region_type == "cartographer":
            revealed = self.reveal_adjacent_world_regions()
            self.service_claimed = True
            if revealed:
                preview = ", ".join(name for _, name in revealed[:3])
                extra = f" and {len(revealed) - 3} more" if len(revealed) > 3 else ""
                self.message = f"New routes are marked on your map: {preview}{extra}."
            else:
                self.message = "The survey maps are already up to date."
        self.store_current_region()

    def talk_to_resident(self, resident):
        if resident is None:
            return
        if resident.kind == "merchant" and self.region_type == "supply" and self.service_claimed and not self.has_pending_choice():
            self.open_provisioner_trade()
            return
        if self.apply_resident_boon(resident):
            return
        if resident.dialogue:
            self.message = random.choice(resident.dialogue)
            return
        self.message = f"The {resident.kind} nods to you."

    def reveal_one_adjacent_world_region(self):
        candidates = []
        for direction in ("north", "south", "west", "east"):
            coord = self.move_coord(self.world_position, direction)
            key = self.region_key(coord)
            if key in self.world_regions:
                continue
            candidates.append(coord)
        if not candidates:
            return None
        with self.seed_scope("scout_reveal", self.world_position, tuple(sorted(candidates))):
            coord = random.choice(candidates)
        state = self.create_world_region_state(coord)
        self.world_regions[self.region_key(coord)] = state
        return coord, state["region_name"]

    def reveal_one_hidden_town_building(self):
        hidden_buildings = [
            building
            for building in self.town_building_data()
            if building.get("door") not in self.seen_tiles
        ]
        if not hidden_buildings:
            return None
        building = min(
            hidden_buildings,
            key=lambda entry: heuristic(self.player, entry.get("door") or entry.get("center") or self.player),
        )
        door = building.get("door")
        center = building.get("center")
        if door is not None:
            self.seen_tiles.add(door)
        if center is not None:
            self.seen_tiles.add(center)
        return building

    def reveal_one_town_exit(self):
        hidden_exits = [tile for tile in self.edge_exits.values() if tile is not None and tile not in self.seen_tiles]
        if not hidden_exits:
            return None
        exit_tile = min(hidden_exits, key=lambda tile: heuristic(self.player, tile))
        self.seen_tiles.add(exit_tile)
        return exit_tile

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
