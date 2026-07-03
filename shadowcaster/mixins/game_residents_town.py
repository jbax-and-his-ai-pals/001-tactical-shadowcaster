from __future__ import annotations

import random

from ..constants import COLOR_FRIEND, COLOR_FRIEND_ANIMAL
from ..game_typing import GameMixinBase
from ..models import Resident
from ..resident_data import (
    BIOME_LOCALS, BIOME_NAME_POOL, CHILD_OBSERVATIONS,
    WANDERER_DIRECTION_FLAVOR, WANDERER_NAMES, WANDERER_REGION_FLAVOR,
)
from ..systems import can_step, heuristic


class ResidentsTownMixin(GameMixinBase):

    def _resident_name(self, parent_biome):
        pool = BIOME_NAME_POOL.get(parent_biome, BIOME_NAME_POOL["plains"])
        return random.choice(pool)

    def _world_concern_line(self):
        """Return one concern line based on a known adjacent region, or None."""
        for direction in ("north", "south", "east", "west"):
            coord = self.move_coord(self.world_position, direction)
            key = self.region_key(coord)
            state = self.world_regions.get(key)
            if not state:
                continue
            rtype = state.get("region_type", "")
            rname = state.get("region_name", "the area")
            concern_by_type = {
                "dungeon":      f"The roads toward {rname} have been heavier lately. Worth watching.",
                "castle":       f"There's a fortified site at {rname} that's drawing attention.",
                "ruins":        f"Something's been moving through {rname} again. Not sure what.",
                "monster_town": f"The settlement at {rname} is hostile. Avoid if you can.",
                "cave":         f"I've heard strange sounds from the direction of {rname}.",
                "shrine":       f"An old shrine at {rname}. Some of the locals still make offerings.",
                "cache":        f"Travelers have been talking about something hidden near {rname}.",
            }
            line = concern_by_type.get(rtype)
            if line:
                return line
        return None

    def _spawn_town_residents(self, size, plaza, town_paths, parent_biome, occupied_positions):
        def claim_resident_tile(anchor):
            anchor = self.nearest_town_path_tile(anchor, town_paths) if town_paths else anchor
            candidates = [anchor]
            if town_paths:
                candidates.extend(sorted(town_paths, key=lambda tile: heuristic(tile, anchor)))
            for candidate in candidates:
                if candidate is None or candidate in occupied_positions:
                    continue
                if self.dungeon.is_blocked(*candidate):
                    continue
                occupied_positions.add(candidate)
                return candidate
            occupied_positions.add(anchor)
            return anchor

        building_pool = [b for b in self.town_non_service_buildings()]
        random.shuffle(building_pool)

        def take_building(preferred_terms=()):
            if preferred_terms:
                for index, building in enumerate(building_pool):
                    name = building["name"].lower()
                    if any(term in name for term in preferred_terms):
                        return building_pool.pop(index)
            return building_pool.pop(0) if building_pool else None

        def resident_from_building(building, kind, color, marker, title, dialogue, behavior="homebound", name=""):
            anchor = building.get("door") or building.get("center")
            position = claim_resident_tile(anchor)
            return Resident(position, kind, color, marker, title, dialogue, behavior, anchor, building["name"], name)

        patrol_route = [
            point for point in (
                plaza,
                self.edge_exits.get("north"),
                self.edge_exits.get("east"),
                self.edge_exits.get("south"),
                self.edge_exits.get("west"),
            )
            if point is not None
        ]

        concern = self._world_concern_line()
        guide_dialogue = ["The roads connect at the edges out there. Keep your bearings.", "If you clear a whole floor, claim the boon before moving on."]
        if concern:
            guide_dialogue.insert(0, concern)
        scout_dialogue = ["If something important comes into view, stop and reassess.", "Open ground favors range. Tight ground favors nerve."]

        residents = [
            Resident(
                claim_resident_tile(plaza), "guide", COLOR_FRIEND, "friend", "Guide",
                tuple(guide_dialogue), "plaza", plaza, "Town Square",
                self._resident_name(parent_biome),
            ),
            Resident(
                claim_resident_tile(plaza), "scout", COLOR_FRIEND, "friend", "Scout",
                tuple(scout_dialogue), "patrol", plaza, "Town Watch",
                self._resident_name(parent_biome),
                tuple(patrol_route),
            ),
        ]

        farmer_building = take_building(("farm", "granary", "barn")) or take_building()
        if farmer_building is not None:
            residents.append(resident_from_building(
                farmer_building, "farmer", COLOR_FRIEND, "settler", "Farmer",
                ("Fields are kinder than ruins, but not by much.", "Most places have something worth finding if you look long enough."),
                name=self._resident_name(parent_biome),
            ))

        if size in {"village", "town", "large_town"}:
            watch_building = take_building(("hall", "watch"))
            watch_anchor = watch_building.get("door") if watch_building else plaza
            residents.append(Resident(
                claim_resident_tile(watch_anchor), "watch", COLOR_FRIEND, "friend", "Watcher",
                ("Keep moving if the streets feel too quiet.", "A good town sees the road before the road sees it."),
                "patrol", watch_anchor,
                watch_building["name"] if watch_building else "Town Watch",
                self._resident_name(parent_biome),
                tuple(patrol_route),
            ))

        if size in {"town", "large_town"}:
            vendor_building = take_building(("market", "store", "stable"))
            vendor_anchor = vendor_building.get("door") if vendor_building else plaza
            residents.append(Resident(
                claim_resident_tile(vendor_anchor), "vendor", COLOR_FRIEND, "settler", "Street Vendor",
                ("A busy square keeps a town alive.", "If you keep traveling, keep your pack honest."),
                "plaza", plaza,
                vendor_building["name"] if vendor_building else "Market Row",
                self._resident_name(parent_biome),
            ))

        local_kind, local_title, local_dialogue, local_terms = BIOME_LOCALS.get(parent_biome, BIOME_LOCALS["plains"])
        local_building = take_building(local_terms) or take_building()
        if local_building is not None:
            local_behavior = "stationary" if local_kind in {"herbalist", "mason", "kilnkeeper"} else "homebound"
            residents.append(resident_from_building(
                local_building, local_kind, COLOR_FRIEND, "settler", local_title, local_dialogue,
                local_behavior, name=self._resident_name(parent_biome),
            ))

        if size in {"town", "large_town"}:
            second_building = take_building()
            if second_building is not None:
                residents.append(resident_from_building(
                    second_building, local_kind, COLOR_FRIEND, "settler", local_title, local_dialogue,
                    "wander", name=self._resident_name(parent_biome),
                ))

        if size in {"village", "town", "large_town"}:
            extra_farm = take_building(("barn", "granary", "shed", "cottage"))
            if extra_farm is not None:
                residents.append(resident_from_building(
                    extra_farm, "farmer", COLOR_FRIEND, "settler", "Farmer",
                    ("Long days and short nights out here.", "Roots grow where you plant them."),
                    "homebound", name=self._resident_name(parent_biome),
                ))

        if size == "large_town":
            elder_building = take_building(("hall", "house", "longhouse"))
            if elder_building is not None:
                residents.append(resident_from_building(
                    elder_building, "elder", COLOR_FRIEND, "settler", "Elder",
                    ("A town lasts by remembering what the road forgets.", "Settlements grow slowly, then all at once."),
                    "stationary", name=self._resident_name(parent_biome),
                ))

        # Animals
        for terms, kind, title, dialogue in [
            (("stable", "barn", "house"), "dog", "Dog", ("The dog circles you once and wags.",)),
            (("house", "cottage", "hut"), "cat", "Cat", ("The cat watches you with perfect indifference.",)),
        ]:
            b = take_building(terms)
            if b is not None:
                residents.append(resident_from_building(b, kind, COLOR_FRIEND_ANIMAL, "animal", title, dialogue, "homebound"))

        # Wanderer — a passing traveler who knows something about a distant region
        self._spawn_wanderer(size, residents, claim_resident_tile, plaza, occupied_positions)

        # Children — ambient young residents in homes
        self._spawn_children(size, residents, occupied_positions, building_pool)

        # Ambient animals
        animal_candidates = [
            tile for tile in self.floor_explorable_tiles
            if tile not in occupied_positions and not self.dungeon.is_blocked(*tile) and tile != self.player
        ]
        random.shuffle(animal_candidates)
        ambient_pool = []
        if parent_biome in {"farmland", "plains"}:
            ambient_pool = [
                ("chicken", "Chicken", ("The chicken scratches at the ground.",), "wander"),
                ("chicken", "Chicken", ("The chicken eyes you cautiously.",), "wander"),
                ("chicken", "Chicken", ("The chicken pecks at something near the path.",), "wander"),
            ]
        elif parent_biome == "forest":
            ambient_pool = [
                ("chicken", "Chicken", ("The chicken scratches at the ground.",), "wander"),
                ("cat", "Cat", ("The cat watches from a low branch.",), "wander"),
            ]
        if parent_biome in {"plains", "desert", "badlands", "farmland"}:
            ambient_pool += [
                ("dog", "Dog", ("The dog sniffs at the air nearby.",), "wander"),
                ("dog", "Dog", ("The dog circles once, then sits.",), "wander"),
            ]
        if parent_biome in {"swamp", "mountain", "tundra"}:
            ambient_pool.append(("cat", "Cat", ("The cat pauses, then looks away.",), "wander"))
        if parent_biome in {"volcanic", "badlands"}:
            ambient_pool.append(("dog", "Dog", ("The dog eyes you from a distance.",), "wander"))
        if size in {"village", "town", "large_town"}:
            ambient_pool.append(("cat", "Cat", ("The cat settles on a warm patch of path.",), "wander"))
        if size in {"town", "large_town"}:
            ambient_pool += [
                ("dog", "Dog", ("The dog trots up, tail swinging.",), "wander"),
                ("cat", "Cat", ("The cat flicks an ear and keeps walking.",), "wander"),
            ]
        if size == "large_town":
            ambient_pool += [
                ("dog", "Dog", ("The dog barks once, then settles.",), "wander"),
                ("chicken", "Chicken", ("The chicken retreats around a corner.",), "wander"),
            ]
        for (akind, atitle, adialogue, abehavior), tile in zip(ambient_pool, animal_candidates):
            occupied_positions.add(tile)
            residents.append(Resident(tile, akind, COLOR_FRIEND_ANIMAL, "animal", atitle, adialogue, abehavior, tile, ""))

        return residents

    def _spawn_wanderer(self, size, residents, claim_tile_fn, plaza, occupied_positions):
        if size == "hamlet" and random.random() < 0.55:
            return
        if size == "village" and random.random() < 0.35:
            return
        name = random.choice(WANDERER_NAMES)
        # Pick a direction that has a known adjacent region
        directions = list(("north", "south", "east", "west"))
        random.shuffle(directions)
        lead_direction = None
        lead_region = None
        for direction in directions:
            coord = self.move_coord(self.world_position, direction)
            key = self.region_key(coord)
            state = self.world_regions.get(key) or self.preview_world_regions.get(key)
            if state:
                lead_direction = direction
                lead_region = state
                break
        if lead_direction is None:
            # No known adjacent regions yet — still spawn but without a region lead
            direction_flavor = random.choice(["came in from far country", "has been on the road a while", "stopped here for a night"])
        else:
            direction_flavor = random.choice(WANDERER_DIRECTION_FLAVOR.get(lead_direction, ["came in from nearby"]))
        rtype = lead_region.get("region_type", "") if lead_region else ""
        region_flavor = WANDERER_REGION_FLAVOR.get(rtype, "something worth investigating")
        region_name = lead_region.get("region_name", "the area") if lead_region else "the area"
        dialogue = (
            f"I {direction_flavor}. There's {region_flavor} — {region_name}.",
            "The road's been full of surprises. Keep your eyes open.",
            "I don't stay in one place long, but this seemed worth a stop.",
        )
        pos = claim_tile_fn(plaza)
        residents.append(Resident(pos, "wanderer", COLOR_FRIEND, "settler", "Passing Traveler", dialogue, "wander", plaza, "", name))

    def _spawn_children(self, size, residents, occupied_positions, building_pool):
        if size not in {"village", "town", "large_town"}:
            return
        count = 1 if size == "village" else (2 if size == "town" else 3)
        home_tiles = []
        for building in building_pool:
            door = building.get("door")
            if door and not self.dungeon.is_blocked(*door) and door not in occupied_positions:
                home_tiles.append(door)
        random.shuffle(home_tiles)
        candidates = home_tiles[:count]
        for tile in candidates:
            if self.dungeon.is_blocked(*tile):
                continue
            dialogue_line = random.choice(CHILD_OBSERVATIONS)
            occupied_positions.add(tile)
            residents.append(Resident(tile, "child", COLOR_FRIEND, "settler", "Child", (dialogue_line,), "wander", tile, ""))
