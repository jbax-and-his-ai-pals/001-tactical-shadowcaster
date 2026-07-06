import random

from .regions_generate_town_helpers import heuristic_city_distance
from .regions import feature_footprint_tiles


def _add_decor(region, profile, plaza, north, south, west, east, width, height, plaza_w, plaza_h):
    decor_profile = profile["decor"]
    water_count = profile["ponds"] + decor_profile["water_bonus"]
    is_well_biome = decor_profile["water"] == "well"
    well_count = 0
    max_wells = 1
    for _ in range(water_count):
        if not is_well_biome:
            pond_w = random.randint(4, 6)
            pond_h = random.randint(3, 5)
            px = random.choice([2, width - pond_w - 3])
            py = random.choice([2, height - pond_h - 3])
            for tx in range(px, px + pond_w):
                for ty in range(py, py + pond_h):
                    if abs(tx - plaza.center[0]) < plaza_w // 2 + 2 and abs(ty - plaza.center[1]) < plaza_h // 2 + 2:
                        continue
                    if (tx, ty) in region.metadata["town_paths"]:
                        continue
                    region.tiles[tx][ty] = 1
                    region.metadata["decor"][(tx, ty)] = "pond"
        elif well_count < max_wells:
            well_candidates = [tile for tile in region.metadata["town_paths"] if heuristic_city_distance(tile, plaza.center) > 2]
            if well_candidates:
                region.metadata["decor"][random.choice(well_candidates)] = "well"
                well_count += 1
    if not is_well_biome and random.random() < 0.35:
        well_candidates = [tile for tile in region.metadata["town_paths"] if heuristic_city_distance(tile, plaza.center) > 3 and tile not in region.metadata["decor"]]
        if well_candidates:
            region.metadata["decor"][random.choice(well_candidates)] = "well"

    flower_candidates = [tile for tile in region.metadata["town_paths"] if tile not in {plaza.center, north.center, south.center, west.center, east.center}]
    random.shuffle(flower_candidates)
    flower_count = max(3, int(len(flower_candidates) * decor_profile["flowers"]))
    for tile in flower_candidates[: flower_count]:
        region.metadata["decor"][tile] = "flowers"
    if profile["parent_biome"] == "farmland":
        for tile in flower_candidates[flower_count : flower_count + max(4, len(flower_candidates) // 14)]:
            region.metadata["decor"][tile] = "crate"

    plant_kind = "tree" if profile["parent_biome"] in {"forest", "swamp", "mountain", "tundra"} else "shrub"
    plant_candidates = [
        (x, y)
        for x in range(2, width - 2)
        for y in range(2, height - 2)
        if region.tiles[x][y] == 0
        and (x, y) not in region.metadata["town_paths"]
        and (x, y) not in region.metadata["decor"]
        and heuristic_city_distance((x, y), plaza.center) > plaza_w // 2 + 2
    ]
    random.shuffle(plant_candidates)
    plant_count = max(4, len(plant_candidates) // 10)
    for tile in plant_candidates[:plant_count]:
        region.metadata["decor"][tile] = plant_kind
    if profile["parent_biome"] == "farmland":
        garden_candidates = [t for t in plant_candidates[plant_count:] if t not in region.metadata["decor"]]
        for tile in garden_candidates[: max(2, len(garden_candidates) // 12)]:
            region.metadata["decor"][tile] = "garden"


def _add_civic_features(region, profile, plaza):
    region.metadata["town_paths"] = {
        tile
        for tile in region.metadata["town_paths"]
        if region.tiles[tile[0]][tile[1]] == 0
    }
    region.metadata["decor"] = {
        tile: kind
        for tile, kind in region.metadata["decor"].items()
        if kind != "path" or region.tiles[tile[0]][tile[1]] == 0
    }

    civic_candidates = [tile for tile in region.metadata["town_paths"] if heuristic_city_distance(tile, plaza.center) <= 3]
    outer_path_candidates = [tile for tile in region.metadata["town_paths"] if heuristic_city_distance(tile, plaza.center) >= 4]
    center_feature_by_biome = {
        "forest": "fountain",
        "plains": "notice_board",
        "farmland": "notice_board",
        "desert": "well",
        "swamp": "fountain",
        "mountain": "brazier",
        "badlands": "brazier",
        "tundra": "brazier",
        "volcanic": "brazier",
    }
    center_feature = center_feature_by_biome.get(profile["parent_biome"], "notice_board")
    center_tile = plaza.center if plaza.center in region.metadata["town_paths"] else min(civic_candidates or region.metadata["town_paths"], key=lambda tile: heuristic_city_distance(tile, plaza.center), default=plaza.center)
    region.metadata["decor"][center_tile] = center_feature
    if center_feature == "notice_board":
        region.metadata["feature_footprints"][center_tile] = feature_footprint_tiles(
            region,
            center_tile,
            center_feature,
            preferred_tiles=region.metadata["town_paths"],
        )
    occupied_center_tiles = set(region.metadata["feature_footprints"].get(center_tile, {center_tile}))
    if profile["settlement_size"] in {"town", "large_town"}:
        stall_tiles = [tile for tile in civic_candidates if tile not in occupied_center_tiles]
        random.shuffle(stall_tiles)
        for tile in stall_tiles[: min(4, 2 + (1 if profile["settlement_size"] == "large_town" else 0))]:
            if tile not in region.metadata["decor"]:
                region.metadata["decor"][tile] = "stall"
    if profile["parent_biome"] in {"plains", "farmland", "desert", "badlands"}:
        hitch_tiles = [tile for tile in outer_path_candidates if tile not in region.metadata["decor"] and tile not in occupied_center_tiles]
        random.shuffle(hitch_tiles)
        for tile in hitch_tiles[:2]:
            region.metadata["decor"][tile] = "hitch_post"


def _assign_buildings(region, profile, plaza, houses):
    services = [
        ("inn", "Traveler's Inn"),
        ("clinic", "Town Clinic"),
        ("supply", "Provisioner"),
        ("shrine", "Wayside Shrine"),
        ("smith", "Old Forge"),
        ("cartographer", "Surveyor's Office"),
        ("tavern", "The Dusty Road Tavern"),
        ("chapel", "Town Chapel"),
        ("stable", "Town Stable"),
        ("bathhouse", "Public Bathhouse"),
        ("armory", "Town Armory"),
        ("apothecary", "Apothecary"),
        ("library", "Town Library"),
        ("guardhouse", "Guardhouse"),
        ("town_hall", "Town Hall"),
        ("bakery", "Town Bakery"),
        ("fletcher", "Fletcher's Workshop"),
    ]
    flavor_buildings = {
        "forest": [
            ("home", "Woodcutter's Cottage"), ("home", "Trapper's Lodge"), ("home", "Miller's House"),
            ("home", "Ranger's Dwelling"), ("home", "Charcoal Burner's Hut"), ("home", "Logger's House"),
            ("home", "Cooper's Cottage"), ("home", "Tanner's House"),
            ("work", "Herbal Shed"), ("work", "Lumber Store"), ("work", "Drying Rack"), ("work", "Hunter's Cache"),
            ("work", "Tanning Works"), ("work", "Cooper's Yard"), ("work", "Pitch House"),
            ("work", "Wood Store"), ("work", "Bark Press"), ("work", "Charcoal Pit"),
            ("civic", "Gathering Hall"), ("civic", "Foresters' Lodge"), ("civic", "Woodland Chapter"),
        ],
        "plains": [
            ("home", "Roadside Cottage"), ("home", "Farmer's House"), ("home", "Drover's House"),
            ("home", "Shepherd's Cottage"), ("home", "Carter's House"), ("home", "Plowman's Dwelling"),
            ("home", "Miller's House"), ("home", "Dairymaid's Cottage"),
            ("work", "Granary"), ("work", "Stable"), ("work", "Storehouse"), ("work", "Feed Barn"),
            ("work", "Dairy Shed"), ("work", "Threshing Floor"), ("work", "Hay Loft"),
            ("work", "Cart Yard"), ("work", "Wool Store"), ("work", "Tallow Works"),
            ("civic", "Meeting Hall"), ("civic", "Commons Hall"), ("civic", "Parish Room"),
        ],
        "farmland": [
            ("home", "Farmhouse"), ("home", "Miller's House"), ("home", "Shepherd's Cottage"),
            ("home", "Plowman's House"), ("home", "Dairyman's Cottage"), ("home", "Yeoman's House"),
            ("home", "Thatcher's Dwelling"), ("home", "Reeve's House"),
            ("work", "Barn"), ("work", "Granary"), ("work", "Stable"), ("work", "Root Cellar"),
            ("work", "Hay Loft"), ("work", "Dairy Shed"), ("work", "Threshing Floor"),
            ("work", "Sheep Pen"), ("work", "Cider Press"), ("work", "Wool Loft"),
            ("civic", "Market Shed"), ("civic", "Parish Room"), ("civic", "Common House"),
        ],
        "desert": [
            ("home", "Adobe House"), ("home", "Mudbrick House"), ("home", "Sand Lodge"),
            ("home", "Dyer's House"), ("home", "Trader's House"), ("home", "Caravaneer's Lodge"),
            ("home", "Weavers' Dwelling"), ("home", "Potter's House"),
            ("work", "Camel Yard"), ("work", "Storehouse"), ("work", "Water Depot"), ("work", "Dye House"),
            ("work", "Weaving Shed"), ("work", "Salt Store"), ("work", "Date Loft"),
            ("work", "Oil Press"), ("work", "Pottery Works"), ("work", "Tanning Yard"),
            ("civic", "Shade Court"), ("civic", "Merchant's Hall"), ("civic", "Council Tent"),
        ],
        "swamp": [
            ("home", "Raised Hut"), ("home", "Stilt House"), ("home", "Reed Dwelling"),
            ("home", "Fisher's Hut"), ("home", "Net Mender's House"), ("home", "Trapper's Shack"),
            ("home", "Dye Maker's Dwelling"), ("home", "Peat Cutter's Hut"),
            ("work", "Net Shed"), ("work", "Reed Loft"), ("work", "Boat House"), ("work", "Smoke Hut"),
            ("work", "Peat Store"), ("work", "Fish Rack"), ("work", "Rush Dryer"),
            ("work", "Tar House"), ("work", "Dye Shed"), ("work", "Eel Trap Store"),
            ("civic", "Boardwalk Hall"), ("civic", "Fishers' Lodge"), ("civic", "Common Dock"),
        ],
        "mountain": [
            ("home", "Stone House"), ("home", "Quarrier's Lodge"), ("home", "Herder's Hut"),
            ("home", "Miner's Cottage"), ("home", "Goatherd's House"), ("home", "Charcoal Burner's Hut"),
            ("home", "Prospector's Lodge"), ("home", "Mason's Dwelling"),
            ("work", "Goat Pen"), ("work", "Tool Shed"), ("work", "Ore Store"), ("work", "Charcoal Pit"),
            ("work", "Smelting Shed"), ("work", "Crushing Mill"), ("work", "Rope Walk"),
            ("work", "Ice Store"), ("work", "Quarry Yard"), ("work", "Bellows House"),
            ("civic", "Watch Hall"), ("civic", "Miners' Lodge"), ("civic", "Stonecutters' Hall"),
        ],
        "badlands": [
            ("home", "Dust House"), ("home", "Drifter's Lodge"), ("home", "Clay Hut"),
            ("home", "Scout's Den"), ("home", "Outrider's House"), ("home", "Scrapper's Shack"),
            ("home", "Bounty Hunter's Lodge"), ("home", "Trailbreaker's Hut"),
            ("work", "Tack Shed"), ("work", "Storehouse"), ("work", "Feed Loft"), ("work", "Scrap Yard"),
            ("work", "Salt Flat Store"), ("work", "Clay Works"), ("work", "Rendering Yard"),
            ("work", "Bone Shed"), ("work", "Wagon Repair"), ("work", "Hide Stretch"),
            ("civic", "Outpost Hall"), ("civic", "Bounty Board"), ("civic", "Drifters' Rest"),
        ],
        "tundra": [
            ("home", "Warm Hut"), ("home", "Longhouse Annex"), ("home", "Fur Trader's Lodge"),
            ("home", "Hunter's Hut"), ("home", "Fisherman's Dwelling"), ("home", "Trapper's Cabin"),
            ("home", "Ice Fisher's Hut"), ("home", "Herder's Lodge"),
            ("work", "Smokehouse"), ("work", "Supply Shed"), ("work", "Kennel"), ("work", "Ice Store"),
            ("work", "Pelt Dryer"), ("work", "Bone Works"), ("work", "Blubber Store"),
            ("work", "Fish Rack"), ("work", "Antler Shed"), ("work", "Fat Rendering"),
            ("civic", "Longhouse"), ("civic", "Hunters' Hall"), ("civic", "Elders' Hearth"),
        ],
        "volcanic": [
            ("home", "Ash House"), ("home", "Cinder Lodge"), ("home", "Soot Cottage"),
            ("home", "Fumarole Keeper's House"), ("home", "Miner's Dwelling"), ("home", "Smelter's Lodge"),
            ("home", "Glassblower's House"), ("home", "Sulphur Miner's Hut"),
            ("work", "Coal Shed"), ("work", "Kiln Store"), ("work", "Water Cistern"), ("work", "Slag Pile"),
            ("work", "Ash Pit"), ("work", "Smelting Works"), ("work", "Glass Furnace"),
            ("work", "Sulphur Store"), ("work", "Obsidian Yard"), ("work", "Bellows House"),
            ("civic", "Stone Hall"), ("civic", "Fire Wardens' Lodge"), ("civic", "Ash Court"),
        ],
    }

    def house_distance(house):
        return heuristic_city_distance(house["door"], plaza.center)

    def house_side_label(house):
        dx = house["door"][0] - plaza.center[0]
        dy = house["door"][1] - plaza.center[1]
        if abs(dx) >= abs(dy):
            return "east" if dx >= 0 else "west"
        return "south" if dy >= 0 else "north"

    def district_label(role, house, kind=None):
        side = house_side_label(house).title()
        if role == "service":
            if kind in {"supply", "cartographer", "inn", "tavern", "bakery", "apothecary"}:
                return "Market Quarter"
            if kind in {"clinic", "shrine", "chapel", "library", "town_hall", "bathhouse"}:
                return "Civic Quarter"
            if kind in {"smith", "stable", "armory", "guardhouse", "fletcher"}:
                return f"{side} Works"
            return "Town Center"
        if role == "civic":
            return "Town Center"
        if role == "work":
            return f"{side} Works"
        return f"{side} Homes"

    houses_by_distance = sorted(houses, key=lambda house: (house_distance(house), random.random()))
    random.shuffle(services)
    service_cap = min(profile["service_cap"], len(services), len(houses))
    service_houses = houses_by_distance[:service_cap]
    service_house_ids = {id(house) for house in service_houses}
    for house, (kind, label) in zip(service_houses, services[:service_cap]):
        room = house["room"]
        region.metadata["town_buildings"].append(
            {
                "kind": kind,
                "name": label,
                "door": house["door"],
                "center": room.center,
                "room": {"x": room.x, "y": room.y, "w": room.w, "h": room.h},
                "role": "service",
                "enterable": True,
                "district": district_label("service", house, kind),
            }
        )
    flavor_pool = flavor_buildings.get(profile["parent_biome"], flavor_buildings["plains"])[:]
    random.shuffle(flavor_pool)
    remaining_houses = [house for house in houses_by_distance if id(house) not in service_house_ids]

    def choose_house_for_role(role):
        if not remaining_houses:
            return None
        if role == "civic":
            return remaining_houses.pop(0)
        if role == "work":
            return remaining_houses.pop(-1)
        return remaining_houses.pop(len(remaining_houses) // 2)

    def flavor_interior_kind(role, name):
        if role == "home":
            return "house"
        if role == "civic":
            return "hall"
        lowered = name.lower()
        if any(k in lowered for k in ("barn", "feed", "goat", "camel", "kennel")):
            return "barn"
        if any(k in lowered for k in ("granary", "grain", "cellar", "root", "ice store")):
            return "granary"
        if any(k in lowered for k in ("smokehouse", "smoke", "drying", "charcoal")):
            return "smokehouse"
        if any(k in lowered for k in ("shed", "tool", "lumber", "ore", "slag", "tack", "scrap", "coal", "kiln", "dye")):
            return "workshop"
        return "storehouse"

    for role, label in flavor_pool:
        house = choose_house_for_role(role)
        if house is None:
            break
        room = house["room"]
        interior_kind = flavor_interior_kind(role, label)
        region.metadata["town_buildings"].append(
            {
                "kind": interior_kind,
                "name": label,
                "door": house["door"],
                "center": room.center,
                "room": {"x": room.x, "y": room.y, "w": room.w, "h": room.h},
                "role": role,
                "enterable": True,
                "district": district_label(role, house),
            }
        )
    region.metadata["town_buildings"].sort(key=lambda building: (0 if building["enterable"] else 1, building["name"]))

    def nearby_path_slots(anchor, limit=2):
        candidates = sorted(
            (
                tile
                for tile in region.metadata["town_paths"]
                if tile not in region.metadata["decor"] and heuristic_city_distance(tile, anchor) <= 2
            ),
            key=lambda tile: (heuristic_city_distance(tile, anchor), tile[1], tile[0]),
        )
        return candidates[:limit]

    exterior_decor = {
        "inn": ["pew", "table", "barrel"],
        "clinic": ["flowers", "pew", "flowers"],
        "supply": ["crate", "crate", "barrel"],
        "shrine": ["flowers", "pew", "flowers"],
        "smith": ["anvil", "crate", "barrel"],
        "cartographer": ["table", "crate", "sign"],
        "tavern": ["barrel", "barrel", "sign", "pew"],
        "chapel": ["flowers", "pew", "flowers"],
        "stable": ["hitch_post", "hitch_post", "crate", "barrel"],
        "library": ["pew", "sign"],
        "guardhouse": ["brazier", "brazier"],
        "town_hall": ["pew", "pew", "sign"],
        "bakery": ["crate", "barrel"],
        "fletcher": ["crate", "sign"],
        "home": ["flowers"],
        "work": ["crate"],
        "civic": ["pew"],
    }
    name_decor = {
        "barn": ["crate", "hitch_post", "barrel"],
        "stable": ["hitch_post", "crate", "barrel"],
        "granary": ["crate", "crate", "barrel"],
        "market": ["stall", "crate", "sign"],
        "boat": ["crate", "hitch_post"],
        "reed": ["flowers", "crate"],
        "watch": ["brazier", "crate"],
        "hall": ["pew"],
        "kiln": ["brazier", "crate"],
        "water": ["crate", "crate"],
        "camel": ["hitch_post", "crate"],
        "ore": ["crate", "anvil"],
        "tool": ["anvil", "crate"],
        "smokehouse": ["brazier", "crate", "barrel"],
        "kennel": ["hitch_post"],
        "tavern": ["barrel", "sign"],
        "chapel": ["flowers", "pew"],
        "lodge": ["crate", "barrel"],
        "shed": ["crate"],
        "cellar": ["barrel", "crate"],
        "pit": ["crate", "brazier"],
        "slag": ["crate", "anvil"],
    }
    for building in region.metadata["town_buildings"]:
        anchor = building["door"]
        decor_list = exterior_decor.get(building["kind"], []) + exterior_decor.get(building.get("role"), [])
        lowered_name = building["name"].lower()
        for key, decor in name_decor.items():
            if key in lowered_name:
                decor_list.extend(decor)
        slots = nearby_path_slots(anchor, limit=min(4, len(decor_list)))
        for tile, decor_kind in zip(slots, decor_list):
            if tile not in region.metadata["decor"]:
                region.metadata["decor"][tile] = decor_kind
