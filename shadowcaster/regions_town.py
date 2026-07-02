import random

from .regions import RegionMap, carve_path
from .regions_generate_town import generate_town, town_profile, heuristic_city_distance


def generate_monster_town(width, height, context=None):
    region = generate_town(width, height, context=context)
    region.metadata["hostile_settlement"] = True
    plaza = region.rooms[0]
    door_tiles = {building["door"] for building in region.metadata.get("town_buildings", [])}
    for _ in range((width * height) // 18):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if plaza.x <= tx < plaza.x + plaza.w and plaza.y <= ty < plaza.y + plaza.h:
            continue
        if (tx, ty) in door_tiles:
            continue
        if region.tiles[tx][ty] == 0 and random.random() < 0.45:
            region.tiles[tx][ty] = 1
    for door_x, door_y in door_tiles:
        region.tiles[door_x][door_y] = 0
        carve_path(region, plaza.center, (door_x, door_y), width=1)
    for room in region.rooms[1:]:
        carve_path(region, plaza.center, room.center, width=1)
    return region


def generate_interior(width, height, region_type):
    region = RegionMap(width, height, fill=1)
    region.metadata["decor"] = {}
    room_width = max(12, min(18, width - 6))
    room_height = max(10, min(14, height - 8))
    left = (width - room_width) // 2
    top = (height - room_height) // 2
    room = region.carve_rect(left, top, room_width, room_height)
    foyer = region.carve_rect(room.center[0] - 1, room.y + room.h - 3, 3, 2)
    carve_path(region, foyer.center, room.center, width=2)
    service_spot = room.center
    if region_type == "inn":
        region.carve_rect(room.x + 1, room.y + 1, 4, room.h - 4)
        region.carve_rect(room.x + room.w - 5, room.y + 1, 4, room.h - 4)
        service_spot = (room.center[0], room.y + 2)
        for y in range(room.y + 2, room.y + room.h - 3, 3):
            region.metadata["decor"][(room.x + 2, y)] = "bed"
            region.metadata["decor"][(room.x + room.w - 3, y)] = "bed"
        region.metadata["decor"][(room.center[0], room.center[1] + 1)] = "table"
    elif region_type == "clinic":
        left_wing = region.carve_rect(room.x + 1, room.y + 2, 4, room.h - 5)
        right_wing = region.carve_rect(room.x + room.w - 5, room.y + 2, 4, room.h - 5)
        carve_path(region, left_wing.center, room.center, width=1)
        carve_path(region, right_wing.center, room.center, width=1)
        region.metadata["decor"][(left_wing.center[0], left_wing.center[1])] = "bed"
        region.metadata["decor"][(right_wing.center[0], right_wing.center[1])] = "bed"
        region.metadata["decor"][(room.center[0], room.y + 2)] = "shelves"
    elif region_type == "supply":
        region.carve_rect(room.x + 2, room.y + 2, room.w - 4, 2)
        region.carve_rect(room.x + 2, room.y + room.h - 5, room.w - 4, 2)
        service_spot = (room.center[0], room.y + 2)
        for x in range(room.x + 3, room.x + room.w - 3, 3):
            region.metadata["decor"][(x, room.y + 2)] = "crate"
            region.metadata["decor"][(x, room.y + room.h - 4)] = "crate"
    elif region_type == "shrine":
        altar = region.carve_rect(room.center[0] - 2, room.y + 1, 5, 3)
        carve_path(region, room.center, altar.center, width=2)
        region.carve_rect(room.x + 2, room.center[1] - 1, room.w - 4, 3)
        service_spot = altar.center
        region.metadata["decor"][altar.center] = "altar"
        for x in range(room.x + 4, room.x + room.w - 4, 4):
            region.metadata["decor"][(x, room.center[1] + 1)] = "pew"
    elif region_type == "smith":
        forge = region.carve_rect(room.x + room.w - 6, room.y + 2, 4, room.h - 5)
        bench = region.carve_rect(room.x + 2, room.center[1] - 1, room.w - 10, 3)
        carve_path(region, bench.center, forge.center, width=2)
        service_spot = forge.center
        region.metadata["decor"][forge.center] = "forge"
        region.metadata["decor"][bench.center] = "anvil"
    elif region_type == "cartographer":
        map_table = region.carve_rect(room.center[0] - 3, room.center[1] - 1, 7, 3)
        shelf = region.carve_rect(room.x + 2, room.y + 2, room.w - 4, 2)
        carve_path(region, shelf.center, map_table.center, width=2)
        service_spot = map_table.center
        region.metadata["decor"][map_table.center] = "table"
        for x in range(room.x + 3, room.x + room.w - 3, 4):
            region.metadata["decor"][(x, room.y + 2)] = "shelves"
    door_x = foyer.center[0]
    door_y = room.y + room.h - 1
    region.tiles[door_x][door_y] = 0
    region.metadata["interior_exit"] = (door_x, door_y)
    region.metadata["service_spot"] = service_spot
    return region


