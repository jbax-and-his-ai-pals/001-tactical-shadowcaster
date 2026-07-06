from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..models import Landmark
from ..regions import RegionChoice, random_region_name
from ..systems import heuristic


class TownsMixin(GameMixinBase):
    def resident_role_summary(self, resident):
        summaries = {
            "guide":       "Can mark one local site",
            "scout":       "Can reveal one nearby route",
            "farmer":      "May share a meal",
            "watch":       "Can warn you about nearby danger",
            "vendor":      "May spare a little trail stock",
            "herbalist":   "May soothe poison or burn",
            "elder":       "Can point out a hidden address",
            "drover":      "May spare trail ammunition",
            "miller":      "May share a field kit",
            "ferryman":    "Can point out the town's way out",
            "mason":       "Can brace you with a ward",
            "trapper":     "May spare a tonic",
            "kilnkeeper":  "Can bank the heat into a ward",
            "wanderer":    "Can tip you off about a distant region",
            "child":       "Has nothing much to say, but means it",
            "innkeeper":   "May restore your health with a proper rest",
            "healer":      "Can clear road ailments and afflictions",
            "blacksmith":  "May fortify you before the road",
            "barkeep":     "Can brace you with something steadying",
            "priest":      "May bless you with a ward for the journey",
            "surveyor":    "Can chart nearby routes on your map",
            "armorer":     "May set a ward to weather what's ahead",
            "apothecary":  "Can treat wounds and spare a remedy",
            "librarian":   "Can mark hidden sites from the records",
            "watch_captain":"Briefs on every known danger nearby",
            "mayor":       "May reveal all routes surrounding the town",
            "baker":       "May spare a loaf to ease the road",
            "fletcher":    "May press spare arrows into your hands",
            "locksmith":   "Opens locked containers for a fee",
            "laborer":     "Just getting on with the work",
            "patron":      "Enjoying a moment off the road",
            "townsfolk":   "Keeping to their own business",
            "herald":      "Keeps track of what moves on the roads",
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
            "tavern": ("tavern", (208, 164, 96)),
            "chapel": ("chapel", (196, 188, 240)),
            "stable": ("stable", (172, 148, 108)),
            "bathhouse": ("bathhouse", (164, 208, 228)),
            "armory": ("armory", (200, 172, 140)),
            "apothecary": ("apothecary", (168, 220, 188)),
            "library": ("library", (172, 196, 228)),
            "guardhouse": ("guardhouse", (188, 176, 148)),
            "town_hall": ("town_hall", (208, 196, 168)),
            "bakery": ("bakery", (216, 184, 136)),
            "fletcher": ("fletcher", (180, 168, 140)),
            "locksmith": ("locksmith", (160, 150, 120)),
            "house": ("home", (210, 196, 168)),
            "hall": ("civic", (200, 192, 236)),
            "granary": ("work", (196, 176, 128)),
            "barn": ("work", (172, 152, 112)),
            "workshop": ("work", (172, 168, 160)),
            "smokehouse": ("work", (180, 160, 140)),
            "storehouse": ("work", (176, 170, 152)),
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

    def town_service_buildings(self):
        return [b for b in self.town_building_data() if b.get("role") == "service"]

    def town_non_service_buildings(self):
        return [b for b in self.town_building_data() if b.get("role") != "service"]

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

    def surface_landmark_kinds(self):
        return {"waystone", "barrow", "stone_circle", "oasis", "hot_spring", "watchtower", "grove", "necropolis", "geyser", "standing_stone", "camp"}

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
            "forest":   ["town", "cave", "ruins", "shrine", "cache", "grove", "stone_circle", "barrow", "watchtower", "standing_stone"],
            "plains":   ["town", "castle", "cave", "ruins", "shrine", "waystone", "barrow", "watchtower", "standing_stone", "camp"],
            "farmland": ["town", "town", "castle", "shrine", "cache", "watchtower", "grove", "camp"],
            "desert":   ["ruins", "cave", "dungeon", "cache", "oasis", "standing_stone", "necropolis", "camp"],
            "swamp":    ["ruins", "cave", "dungeon", "cache", "stone_circle", "grove", "standing_stone", "camp"],
            "mountain": ["castle", "dungeon", "cave", "shrine", "cache", "hot_spring", "barrow", "watchtower", "stone_circle", "geyser"],
            "badlands": ["ruins", "castle", "cave", "dungeon", "cache", "necropolis", "standing_stone", "camp"],
            "tundra":   ["cave", "ruins", "castle", "shrine", "cache", "hot_spring", "barrow", "necropolis", "waystone"],
            "volcanic": ["dungeon", "cave", "ruins", "monster_town", "cache", "geyser", "hot_spring", "standing_stone"],
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
                "cave":          ("cave",          (172, 144, 116)),
                "dungeon":       ("dungeon",        (154, 164, 182)),
                "town":          ("town",           (210, 182, 120)),
                "castle":        ("castle",         (196, 188, 220)),
                "ruins":         ("ruins",          (184, 148, 108)),
                "monster_town":  ("monster_town",   (220, 96,  120)),
                "shrine":        ("shrine",         (212, 196, 248)),
                "cache":         ("cache",          (188, 164, 112)),
                "waystone":      ("waystone",       (168, 210, 200)),
                "barrow":        ("barrow",         (160, 148, 132)),
                "stone_circle":  ("stone_circle",   (186, 172, 220)),
                "oasis":         ("oasis",          (120, 196, 164)),
                "hot_spring":    ("hot_spring",     (220, 168, 140)),
                "watchtower":    ("watchtower",     (180, 196, 164)),
                "grove":         ("grove",          (140, 188, 128)),
                "necropolis":    ("necropolis",     (148, 140, 164)),
                "geyser":        ("geyser",         (200, 180, 148)),
                "standing_stone":("standing_stone", (172, 164, 148)),
                "camp":          ("camp",           (180, 160, 120)),
            }.get(kind, ("town", (210, 182, 120)))
            landmarks.append(Landmark(f"poi_{index}_{kind}", available_tiles[index], kind, random_region_name(kind), color, marker))
        is_start_region = self.world_position == (0, 0) and not self.in_local_region()
        if is_start_region and not any(lm.kind == "town" for lm in landmarks):
            used_tiles = {lm.position for lm in landmarks}
            fallback_tiles = [t for t in available_tiles if t not in used_tiles]
            if fallback_tiles:
                tile = fallback_tiles[0]
                landmarks.insert(0, Landmark("poi_start_town", tile, "town", random_region_name("town"), (210, 182, 120), "town"))
        return landmarks

    def enter_landmark(self, landmark):
        if landmark.kind in self.surface_landmark_kinds():
            self.apply_surface_landmark(landmark)
            return
        self.player = landmark.position
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
            interior_kind = landmark.kind
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
        self.message = f"You enter {landmark.name}."

    def talk_to_resident(self, resident):
        if resident is None:
            return
        if resident.kind == "merchant" and self.region_type == "supply" and self.service_claimed and not self.trade_open and not self.has_pending_choice():
            self.open_trade()
            return
        if self.apply_resident_boon(resident):
            self.message = self.with_town_attitude_dialogue(self.message, resident)
            social_msg = self.maybe_offer_social_quest(resident) if hasattr(self, "maybe_offer_social_quest") else None
            if social_msg:
                self.message = f"{self.message} {social_msg}"
            return
        social_msg = self.maybe_offer_social_quest(resident) if hasattr(self, "maybe_offer_social_quest") else None
        if social_msg:
            self.message = self.with_town_attitude_dialogue(social_msg, resident)
            return
        if resident.dialogue:
            base = random.choice(resident.dialogue)
            response = self.resident_town_response_line(resident)
            self.message = self.with_town_attitude_dialogue(f"{base} {response}".strip(), resident)
            return
        name = resident.name or f"the {resident.kind}"
        plain = f"{name.capitalize()} nods to you." if resident.name else f"The {resident.kind} nods to you."
        self.message = self.with_town_attitude_dialogue(plain, resident)
