from __future__ import annotations

import random

from ..constants import COLOR_FRIEND, COLOR_FRIEND_ANIMAL
from ..game_typing import GameMixinBase
from ..models import Resident
from ..systems import can_step, heuristic


class ResidentsMixin(GameMixinBase):

    def spawn_residents(self):
        self.residents = []
        if self.region_type in {"inn", "clinic", "supply", "shrine", "smith", "cartographer"}:
            spot = getattr(self.dungeon, "metadata", {}).get("service_spot")
            if spot:
                residents = {
                    "inn": ("innkeeper", COLOR_FRIEND, "inn", "Innkeeper", ("The sheets are fresh and the fire is warm.", "Stay a moment. Even wanderers need rest.")),
                    "clinic": ("medic", COLOR_FRIEND, "clinic", "Medic", ("Hold still. Let me take care of those wounds.", "You're steadier once the bandages are set.")),
                    "supply": ("merchant", COLOR_FRIEND, "supply", "Provisioner", ("Travel light, but never empty.", "If the free bundle is gone, we can still barter.", "A little stock now saves a lot of regret later.")),
                    "shrine": ("caretaker", COLOR_FRIEND, "shrine", "Caretaker", ("Walk gently. Old blessings still answer here.", "The road bites less sharply when you carry a ward.")),
                    "smith": ("smith", COLOR_FRIEND, "smith", "Smith", ("Steel and will both need tending.", "If you're heading back out, go with a steadier hand.")),
                    "cartographer": ("surveyor", COLOR_FRIEND, "cartographer", "Surveyor", ("The frontier opens up once you've charted its edges.", "Roads are easier to trust when you know what lies beyond them.")),
                }
                kind, color, marker, title, dialogue = residents[self.region_type]
                self.residents.append(Resident(spot, kind, color, marker, title, dialogue, "stationary", spot, self.region_name))
            return
        if self.region_type != "town":
            return
        metadata = getattr(self.dungeon, "metadata", {})
        size = metadata.get("settlement_size", "hamlet")
        plaza = metadata.get("town_square", self.player)
        town_paths = set(metadata.get("town_paths", set()))
        parent_biome = metadata.get("town_parent_biome", "plains")
        non_service_buildings = self.town_non_service_buildings()
        building_pool = non_service_buildings[:]
        random.shuffle(building_pool)
        occupied_positions = set()

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

        def take_building(preferred_terms=()):
            if preferred_terms:
                for index, building in enumerate(building_pool):
                    name = building["name"].lower()
                    if any(term in name for term in preferred_terms):
                        return building_pool.pop(index)
            return building_pool.pop(0) if building_pool else None

        def resident_from_building(building, kind, color, marker, title, dialogue, behavior="homebound"):
            anchor = building.get("door") or building.get("center")
            position = claim_resident_tile(anchor)
            return Resident(position, kind, color, marker, title, dialogue, behavior, anchor, building["name"])

        biome_locals = {
            "forest": ("herbalist", "Herbalist", ("The woods cure and poison in equal measure.", "Roots, bark, and leaves can solve more than steel can."), ("shed", "cottage", "house")),
            "plains": ("vendor", "Peddler", ("Road trade keeps a plains town breathing.", "Someone always needs a little powder, rope, or grain."), ("store", "market", "stable")),
            "farmland": ("miller", "Miller", ("Grain, flour, and patience keep a place like this standing.", "A quiet harvest says more than a loud road."), ("granary", "barn", "farm")),
            "desert": ("drover", "Drover", ("A desert town lives by what it can carry.", "Shade, water, and good sense all cost something out here."), ("yard", "depot", "storehouse")),
            "swamp": ("ferryman", "Ferryman", ("In wet country, a sure crossing is worth more than a strong wall.", "Boardwalks and boats make better neighbors than pride."), ("boat", "reed", "hut")),
            "mountain": ("mason", "Mason", ("Stone remembers every bad cut and every good one.", "A mountain settlement survives by what it can brace."), ("stone", "tool", "ore")),
            "badlands": ("vendor", "Trail Trader", ("Badlands folk learn to pack light and sell quick.", "If something breaks out there, you fix it or bury it."), ("store", "shed", "tack")),
            "tundra": ("trapper", "Trapper", ("Cold country teaches you to read silence before tracks.", "A warm room is built long before the snow arrives."), ("smokehouse", "shed", "hut")),
            "volcanic": ("kilnkeeper", "Kilnkeeper", ("Ash and heat still make homes if you know how to work them.", "Even here, people build first and complain after."), ("kiln", "cistern", "ash")),
        }

        patrol_route = [
            point
            for point in (
                plaza,
                self.edge_exits.get("north"),
                self.edge_exits.get("east"),
                self.edge_exits.get("south"),
                self.edge_exits.get("west"),
            )
            if point is not None
        ]

        residents = [
            Resident(
                claim_resident_tile(plaza),
                "guide",
                COLOR_FRIEND,
                "friend",
                "Guide",
                ("The roads connect at the edges out there. Keep your bearings.", "If you clear a whole floor, make sure you claim the boon before moving on."),
                "plaza",
                plaza,
                "Town Square",
            ),
            Resident(
                claim_resident_tile(plaza),
                "scout",
                COLOR_FRIEND,
                "friend",
                "Scout",
                ("If something important comes into view, stop and reassess.", "Open ground favors range. Tight ground favors nerve."),
                "patrol",
                plaza,
                "Town Watch",
                tuple(patrol_route),
            ),
        ]

        farmer_building = take_building(("farm", "granary", "barn"))
        if farmer_building is None:
            farmer_building = take_building()
        if farmer_building is not None:
            residents.append(
                resident_from_building(
                    farmer_building,
                    "farmer",
                    COLOR_FRIEND,
                    "settler",
                    "Farmer",
                    ("Fields are kinder than ruins, but not by much.", "Most places have something worth finding if you look long enough."),
                )
            )

        if size in {"village", "town", "large_town"}:
            watch_building = take_building(("hall", "watch"))
            watch_anchor = (watch_building.get("door") if watch_building else plaza)
            residents.append(
                Resident(
                    claim_resident_tile(watch_anchor),
                    "watch",
                    COLOR_FRIEND,
                    "friend",
                    "Watcher",
                    ("Keep moving if the streets feel too quiet.", "A good town sees the road before the road sees it."),
                    "patrol",
                    watch_anchor,
                    watch_building["name"] if watch_building else "Town Watch",
                    tuple(patrol_route),
                )
            )
        if size in {"town", "large_town"}:
            vendor_building = take_building(("market", "store", "stable"))
            vendor_anchor = vendor_building.get("door") if vendor_building else plaza
            residents.append(
                Resident(
                    claim_resident_tile(vendor_anchor),
                    "vendor",
                    COLOR_FRIEND,
                    "settler",
                    "Street Vendor",
                    ("A busy square keeps a town alive.", "If you keep traveling, keep your pack honest."),
                    "plaza",
                    plaza,
                    vendor_building["name"] if vendor_building else "Market Row",
                )
            )
        local_kind, local_title, local_dialogue, local_terms = biome_locals.get(parent_biome, biome_locals["plains"])
        local_building = take_building(local_terms)
        if local_building is None:
            local_building = take_building()
        if local_building is not None:
            local_behavior = "stationary" if local_kind in {"herbalist", "mason", "kilnkeeper"} else "homebound"
            residents.append(
                resident_from_building(
                    local_building,
                    local_kind,
                    COLOR_FRIEND,
                    "settler",
                    local_title,
                    local_dialogue,
                    local_behavior,
                )
            )
        if size == "large_town":
            elder_building = take_building(("hall", "house", "longhouse"))
            if elder_building is not None:
                residents.append(
                    resident_from_building(
                        elder_building,
                        "elder",
                        COLOR_FRIEND,
                        "settler",
                        "Elder",
                        ("A town lasts by remembering what the road forgets.", "Settlements grow slowly, then all at once."),
                        "stationary",
                    )
                )

        animal_building = take_building(("stable", "barn", "house"))
        if animal_building is not None:
            residents.append(
                resident_from_building(
                    animal_building,
                    "dog",
                    COLOR_FRIEND_ANIMAL,
                    "animal",
                    "Dog",
                    ("The dog circles you once and wags.",),
                    "homebound",
                )
            )
        animal_building = take_building(("house", "cottage", "hut"))
        if animal_building is not None:
            residents.append(
                resident_from_building(
                    animal_building,
                    "cat",
                    COLOR_FRIEND_ANIMAL,
                    "animal",
                    "Cat",
                    ("The cat watches you with perfect indifference.",),
                    "homebound",
                )
            )

        # additional ambient animals on free open tiles
        animal_candidates = [
            tile for tile in self.floor_explorable_tiles
            if tile not in occupied_positions
            and not self.dungeon.is_blocked(*tile)
            and tile != self.player
        ]
        random.shuffle(animal_candidates)
        ambient_pool = []
        if parent_biome in {"farmland", "plains", "forest"}:
            ambient_pool = [
                ("chicken", "Chicken", ("The chicken scratches at the ground.",), "wander"),
                ("chicken", "Chicken", ("The chicken eyes you cautiously.",), "wander"),
            ]
        if parent_biome in {"plains", "desert", "badlands"}:
            ambient_pool.append(("dog", "Dog", ("The dog sniffs at the air nearby.",), "wander"))
        if parent_biome in {"forest", "swamp", "mountain", "tundra"}:
            ambient_pool.append(("cat", "Cat", ("The cat pauses, then looks away.",), "wander"))
        if size in {"town", "large_town"}:
            ambient_pool.append(("cat", "Cat", ("The cat settles on a warm patch of path.",), "wander"))
            ambient_pool.append(("dog", "Dog", ("The dog trots up, tail swinging.",), "wander"))
        for (akind, atitle, adialogue, abehavior), tile in zip(ambient_pool, animal_candidates):
            occupied_positions.add(tile)
            residents.append(Resident(tile, akind, COLOR_FRIEND_ANIMAL, "animal", atitle, adialogue, abehavior, tile, ""))

        self.residents.extend(residents)

    def get_resident_at(self, position):
        return next((resident for resident in self.residents if resident.position == position), None)

    def move_residents(self):
        if not self.residents:
            return
        town_paths = set(getattr(self.dungeon, "metadata", {}).get("town_paths", set())) if self.region_type == "town" else set()
        occupied = {enemy.position for enemy in self.enemies}
        occupied.add(self.player)
        if self.stairs:
            occupied.add(self.stairs)
        if self.upgrade_pickup:
            occupied.add(self.upgrade_pickup.position)
        if self.heal_pickup:
            occupied.add(self.heal_pickup)
        for resident in self.residents:
            occupied.add(resident.position)
        for resident in self.residents:
            if resident.behavior == "stationary":
                continue
            if random.random() < 0.45 and resident.behavior != "patrol":
                continue
            occupied.discard(resident.position)
            options = []
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                next_pos = (resident.position[0] + dx, resident.position[1] + dy)
                if next_pos in occupied:
                    continue
                if can_step(self.dungeon, resident.position, next_pos):
                    if town_paths and resident.behavior in {"plaza", "homebound", "patrol"} and next_pos not in town_paths:
                        continue
                    if resident.behavior == "plaza" and resident.anchor and heuristic(next_pos, resident.anchor) > 4:
                        continue
                    if resident.behavior == "homebound" and resident.anchor and heuristic(next_pos, resident.anchor) > 3:
                        continue
                    options.append(next_pos)
            if resident.behavior == "patrol" and resident.patrol_points:
                if resident.position == resident.patrol_points[resident.patrol_index % len(resident.patrol_points)]:
                    resident.patrol_index = (resident.patrol_index + 1) % len(resident.patrol_points)
                target = resident.patrol_points[resident.patrol_index % len(resident.patrol_points)]
                if options:
                    resident.position = min(options, key=lambda option: (heuristic(option, target), random.random()))
            elif options:
                resident.position = random.choice(options)
            occupied.add(resident.position)
