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
    decor = region.metadata["decor"]
    cx, cy = room.center

    if region_type == "inn":
        # Two side wings with beds; common table; reception counter; barrel
        region.carve_rect(room.x + 1, room.y + 1, 4, room.h - 4)
        region.carve_rect(room.x + room.w - 5, room.y + 1, 4, room.h - 4)
        service_spot = (cx, room.y + 2)
        for y in range(room.y + 2, room.y + room.h - 3, 3):
            decor[(room.x + 2, y)] = "bed"
            decor[(room.x + room.w - 3, y)] = "bed"
        decor[(cx, cy)] = "table"
        decor[(cx, cy + 2)] = "table"
        decor[(cx, room.y + room.h - 4)] = "table"         # reception counter
        decor[(room.x + 2, room.y + room.h - 3)] = "barrel"
        decor[(room.x + room.w - 3, room.y + 2)] = "shelves"

    elif region_type == "clinic":
        # Two wings, multiple beds each; medicine shelves; treatment table at centre
        left_wing = region.carve_rect(room.x + 1, room.y + 2, 4, room.h - 5)
        right_wing = region.carve_rect(room.x + room.w - 5, room.y + 2, 4, room.h - 5)
        carve_path(region, left_wing.center, room.center, width=1)
        carve_path(region, right_wing.center, room.center, width=1)
        service_spot = (cx, cy)
        for y in range(room.y + 3, room.y + room.h - 3, 3):
            decor[(room.x + 2, y)] = "bed"
            decor[(room.x + room.w - 3, y)] = "bed"
        for x in range(cx - 2, cx + 3, 2):
            decor[(x, room.y + 2)] = "shelves"
        decor[(cx, cy)] = "table"                           # treatment table
        decor[(room.x + 2, room.y + 2)] = "crate"
        decor[(room.x + room.w - 3, room.y + 2)] = "crate"

    elif region_type == "supply":
        # Back storage; floor browsing with table + barrels; crate shelves
        region.carve_rect(room.x + 2, room.y + 2, room.w - 4, 2)
        region.carve_rect(room.x + 2, room.y + room.h - 5, room.w - 4, 2)
        service_spot = (cx, room.y + 2)
        for x in range(room.x + 3, room.x + room.w - 3, 3):
            decor[(x, room.y + 2)] = "crate"
            decor[(x, room.y + room.h - 4)] = "crate"
        decor[(cx, cy)] = "table"
        decor[(room.x + 2, cy)] = "barrel"
        decor[(room.x + room.w - 3, cy)] = "barrel"
        decor[(cx - 2, room.y + room.h - 4)] = "barrel"

    elif region_type == "shrine":
        # Wide altar alcove; 3-tile altar; double pew rows; braziers; side alcoves
        altar_alcove = region.carve_rect(cx - 3, room.y + 1, 7, 4)
        carve_path(region, room.center, altar_alcove.center, width=3)
        left_alcove = region.carve_rect(room.x + 1, cy - 3, 3, 6)
        right_alcove = region.carve_rect(room.x + room.w - 4, cy - 3, 3, 6)
        carve_path(region, left_alcove.center, altar_alcove.center, width=1)
        carve_path(region, right_alcove.center, altar_alcove.center, width=1)
        region.carve_rect(room.x + 4, cy - 1, room.w - 8, 3)
        ax, ay = altar_alcove.center
        service_spot = (ax, ay)
        for dx in (-1, 0, 1):
            decor[(ax + dx, ay)] = "altar"
        decor[(ax - 2, ay + 1)] = "brazier"
        decor[(ax + 2, ay + 1)] = "brazier"
        decor[left_alcove.center] = "flowers"
        decor[(left_alcove.center[0], left_alcove.center[1] - 2)] = "brazier"
        decor[right_alcove.center] = "flowers"
        decor[(right_alcove.center[0], right_alcove.center[1] - 2)] = "brazier"
        for x in range(room.x + 5, room.x + room.w - 5, 4):
            decor[(x, cy - 1)] = "pew"
            decor[(x, cy + 1)] = "pew"
        decor[(room.x + 2, room.y + room.h - 4)] = "brazier"
        decor[(room.x + room.w - 3, room.y + room.h - 4)] = "brazier"

    elif region_type == "smith":
        # Forge in back corner; anvil + work bench; brazier glow; material crates
        forge = region.carve_rect(room.x + room.w - 6, room.y + 2, 4, room.h - 5)
        bench = region.carve_rect(room.x + 2, cy - 1, room.w - 10, 3)
        carve_path(region, bench.center, forge.center, width=2)
        service_spot = forge.center
        decor[forge.center] = "forge"
        decor[bench.center] = "anvil"
        decor[(bench.center[0] - 2, bench.center[1])] = "table"
        decor[(room.x + 2, room.y + 2)] = "crate"
        decor[(room.x + 2, room.y + 4)] = "crate"
        decor[(forge.center[0], min(forge.center[1] + 2, room.y + room.h - 3))] = "brazier"
        decor[(room.x + 2, room.y + room.h - 4)] = "barrel"

    elif region_type == "cartographer":
        # Central map table; shelves on three sides; side alcoves; consultation table
        map_table = region.carve_rect(cx - 3, cy - 1, 7, 3)
        shelf_top = region.carve_rect(room.x + 2, room.y + 2, room.w - 4, 2)
        left_shelf = region.carve_rect(room.x + 1, cy - 2, 3, 5)
        right_shelf = region.carve_rect(room.x + room.w - 4, cy - 2, 3, 5)
        carve_path(region, shelf_top.center, map_table.center, width=2)
        carve_path(region, left_shelf.center, map_table.center, width=1)
        carve_path(region, right_shelf.center, map_table.center, width=1)
        service_spot = map_table.center
        decor[map_table.center] = "table"
        for x in range(room.x + 3, room.x + room.w - 3, 4):
            decor[(x, room.y + 2)] = "shelves"
        decor[left_shelf.center] = "shelves"
        decor[right_shelf.center] = "shelves"
        decor[(cx, room.y + room.h - 4)] = "table"
        decor[(cx - 2, room.y + room.h - 4)] = "crate"

    elif region_type == "tavern":
        # Bar counter row one step from north wall, shelves on the wall behind it;
        # side booths; scattered patron tables; barrel cluster; braziers; sign near door
        bar_y = room.y + 3
        for x in range(room.x + 2, room.x + room.w - 2):
            decor[(x, room.y + 1)] = "shelves"     # back-bar shelves on north wall
        for x in range(room.x + 2, room.x + room.w - 2):
            decor[(x, bar_y)] = "table"             # bar counter
        service_spot = (cx, bar_y)
        decor[(room.x + 2, bar_y - 1)] = "barrel"
        decor[(room.x + room.w - 3, bar_y - 1)] = "barrel"
        left_booth = region.carve_rect(room.x + 1, cy - 2, 4, 4)
        right_booth = region.carve_rect(room.x + room.w - 5, cy - 2, 4, 4)
        decor[left_booth.center] = "pew"
        decor[right_booth.center] = "pew"
        for x in range(cx - 3, cx + 4, 4):
            decor[(x, cy + 1)] = "table"
            decor[(x, cy + 3)] = "pew"
        decor[(room.x + 2, room.y + room.h - 4)] = "barrel"
        decor[(room.x + 3, room.y + room.h - 4)] = "barrel"
        decor[(room.x + room.w - 3, room.y + room.h - 4)] = "barrel"
        decor[(room.x + 2, room.y + room.h - 3)] = "brazier"
        decor[(room.x + room.w - 3, room.y + room.h - 3)] = "brazier"
        decor[(cx, room.y + room.h - 4)] = "sign"

    elif region_type == "chapel":
        # Wide pulpit; 3-tile altar; double pew rows; braziers; side alcoves with flowers
        pulpit = region.carve_rect(cx - 3, room.y + 1, 7, 4)
        carve_path(region, room.center, pulpit.center, width=3)
        left_alcove = region.carve_rect(room.x + 1, cy - 2, 3, 5)
        right_alcove = region.carve_rect(room.x + room.w - 4, cy - 2, 3, 5)
        carve_path(region, left_alcove.center, pulpit.center, width=1)
        carve_path(region, right_alcove.center, pulpit.center, width=1)
        region.carve_rect(room.x + 4, cy - 1, room.w - 8, 3)
        px, py = pulpit.center
        service_spot = (px, py)
        for dx in (-1, 0, 1):
            decor[(px + dx, py)] = "altar"
        decor[(px - 2, py + 1)] = "brazier"
        decor[(px + 2, py + 1)] = "brazier"
        decor[left_alcove.center] = "flowers"
        decor[(left_alcove.center[0], left_alcove.center[1] - 1)] = "brazier"
        decor[right_alcove.center] = "flowers"
        decor[(right_alcove.center[0], right_alcove.center[1] - 1)] = "brazier"
        for x in range(room.x + 5, room.x + room.w - 5, 4):
            decor[(x, cy - 1)] = "pew"
            decor[(x, cy + 1)] = "pew"
        decor[(room.x + 2, room.y + room.h - 4)] = "brazier"
        decor[(room.x + room.w - 3, room.y + room.h - 4)] = "brazier"

    elif region_type == "house":
        # Domestic home: beds, hearth, dining table, pantry shelves, flowers
        decor[(room.x + 2, room.y + 1)] = "bed"
        decor[(room.x + 3, room.y + 1)] = "bed"
        decor[(room.x + 2, room.y + 3)] = "brazier"        # hearth
        decor[(room.x + room.w - 3, room.y + 1)] = "shelves"
        decor[(room.x + room.w - 3, room.y + 2)] = "shelves"
        decor[(room.x + room.w - 3, room.y + 3)] = "shelves"
        decor[(cx, cy - 1)] = "table"
        decor[(cx - 1, cy)] = "pew"
        decor[(cx + 1, cy)] = "pew"
        decor[(cx, cy + 1)] = "shelves"
        decor[(room.x + room.w - 4, cy + 1)] = "barrel"
        decor[(room.x + room.w - 3, cy + 1)] = "crate"
        decor[(room.x + 2, room.y + room.h - 4)] = "flowers"
        decor[(room.x + 3, room.y + room.h - 4)] = "flowers"

    elif region_type == "hall":
        # Civic hall: long meeting table, flanking pews, braziers, sign near door
        for x in range(cx - 3, cx + 4):
            decor[(x, cy)] = "table"
        for x in range(cx - 3, cx + 4, 2):
            decor[(x, cy - 2)] = "pew"
            decor[(x, cy + 2)] = "pew"
        decor[(room.x + 2, room.y + 1)] = "brazier"
        decor[(room.x + room.w - 3, room.y + 1)] = "brazier"
        for x in range(cx - 2, cx + 3, 2):
            decor[(x, room.y + 1)] = "shelves"
        decor[(cx, room.y + room.h - 4)] = "sign"
        decor[(room.x + 2, room.y + room.h - 4)] = "pew"
        decor[(room.x + room.w - 3, room.y + room.h - 4)] = "pew"

    elif region_type == "granary":
        # Grain warehouse: dense crate rows, barrel wall, manifest table near door
        for x in range(room.x + 2, room.x + room.w - 4, 3):
            for y in range(room.y + 1, room.y + room.h - 5, 2):
                decor[(x, y)] = "crate"
        for y in range(room.y + 1, room.y + room.h - 5, 2):
            decor[(room.x + room.w - 3, y)] = "barrel"
        decor[(cx - 1, room.y + room.h - 4)] = "barrel"
        decor[(cx, room.y + room.h - 4)] = "table"
        decor[(cx + 1, room.y + room.h - 4)] = "sign"

    elif region_type == "barn":
        # Animal barn: stalls with hay, wide aisle, trough, hitch posts, feed barrels
        stall_h = max(3, (room.h - 4) // 2)
        for ax in (room.x + 1, room.x + room.w - 5):
            sa = region.carve_rect(ax, room.y + 2, 4, stall_h)
            sb = region.carve_rect(ax, room.y + 2 + stall_h + 1, 4, stall_h)
            for stall in (sa, sb):
                decor[stall.center] = "stall"
                hay_y = min(stall.center[1] + 1, stall.y + stall.h - 1)
                decor[(stall.center[0], hay_y)] = "crate"
        decor[(cx - 1, room.y + 2)] = "table"
        decor[(cx, room.y + 2)] = "table"
        decor[(cx + 1, room.y + 2)] = "table"               # trough
        decor[(room.x + 2, room.y + room.h - 3)] = "hitch_post"
        decor[(room.x + room.w - 3, room.y + room.h - 3)] = "hitch_post"
        decor[(cx - 1, room.y + room.h - 3)] = "barrel"
        decor[(cx + 1, room.y + room.h - 3)] = "barrel"

    elif region_type == "workshop":
        # Crafting space: workbench, anvil, shelves on three walls, material crates, braziers
        for x in range(cx - 2, cx + 3):
            decor[(x, room.y + 1)] = "shelves"
        decor[(room.x + 2, room.y + 1)] = "shelves"
        decor[(room.x + room.w - 3, room.y + 1)] = "shelves"
        for y in range(room.y + 1, cy, 2):
            decor[(room.x + 2, y)] = "crate"
            decor[(room.x + room.w - 3, y)] = "crate"
        decor[(cx, cy)] = "table"                           # workbench
        decor[(cx - 1, cy)] = "anvil"
        decor[(cx + 1, cy)] = "crate"
        decor[(room.x + 2, room.y + room.h - 4)] = "brazier"
        decor[(room.x + room.w - 3, room.y + room.h - 4)] = "brazier"
        decor[(cx, room.y + room.h - 4)] = "barrel"

    elif region_type == "smokehouse":
        # Curing house: braziers for smoke, product shelves, preparation table, brine barrels
        for x in range(room.x + 2, room.x + room.w - 2, 3):
            decor[(x, room.y + 1)] = "brazier"
            decor[(x, room.y + 3)] = "shelves"
            decor[(x, cy)] = "shelves"
        decor[(cx, room.y + room.h - 4)] = "table"
        decor[(cx - 1, room.y + room.h - 4)] = "barrel"
        decor[(cx + 1, room.y + room.h - 4)] = "barrel"
        decor[(room.x + 2, room.y + room.h - 3)] = "crate"
        decor[(room.x + room.w - 3, room.y + room.h - 3)] = "crate"

    elif region_type == "storehouse":
        # General warehouse: crate rows on left, barrel rows on right, shelves at back, manifest desk
        for x in range(room.x + 2, cx - 1, 3):
            for y in range(room.y + 1, room.y + room.h - 5, 2):
                decor[(x, y)] = "crate"
        for x in range(cx + 2, room.x + room.w - 2, 3):
            for y in range(room.y + 1, room.y + room.h - 5, 2):
                decor[(x, y)] = "barrel"
        for y in range(room.y + 1, room.y + room.h - 5, 2):
            decor[(cx, y)] = "shelves"
        decor[(cx, room.y + room.h - 4)] = "table"
        decor[(cx - 1, room.y + room.h - 4)] = "sign"
        decor[(cx + 1, room.y + room.h - 4)] = "crate"

    elif region_type == "stable":
        # Four stalls along side walls with hitch posts and hay; central trough aisle; brazier
        stall_h = max(3, (room.h - 4) // 2)
        left_stall_a = region.carve_rect(room.x + 1, room.y + 2, 4, stall_h)
        left_stall_b = region.carve_rect(room.x + 1, room.y + 2 + stall_h + 1, 4, stall_h)
        right_stall_a = region.carve_rect(room.x + room.w - 5, room.y + 2, 4, stall_h)
        right_stall_b = region.carve_rect(room.x + room.w - 5, room.y + 2 + stall_h + 1, 4, stall_h)
        trough = region.carve_rect(cx - 2, room.y + 2, 5, 2)
        carve_path(region, trough.center, room.center, width=2)
        service_spot = trough.center
        for x in range(trough.x, trough.x + trough.w):
            decor[(x, trough.center[1])] = "table"     # water trough
        for stall in (left_stall_a, left_stall_b, right_stall_a, right_stall_b):
            decor[stall.center] = "hitch_post"
            hay_y = min(stall.center[1] + 1, stall.y + stall.h - 1)
            decor[(stall.center[0], hay_y)] = "haystack"
        decor[(room.x + 2, room.y + room.h - 3)] = "hitch_post"
        decor[(room.x + room.w - 3, room.y + room.h - 3)] = "hitch_post"
        decor[(cx - 1, room.y + room.h - 3)] = "barrel"
        decor[(cx + 1, room.y + room.h - 3)] = "barrel"
        decor[(cx, room.y + 1)] = "brazier"

    elif region_type == "cache":
        # Hidden cache: cramped alcove stuffed with crates and barrels, single brazier for light
        region.carve_rect(room.x + 2, room.y + 2, room.w - 4, room.h - 6)
        service_spot = (cx, cy - 1)
        for x in range(room.x + 3, room.x + room.w - 3, 2):
            decor[(x, room.y + 2)] = "crate"
            decor[(x, room.y + 4)] = "crate"
        for x in range(room.x + 3, room.x + room.w - 3, 3):
            decor[(x, room.y + room.h - 7)] = "barrel"
        decor[(room.x + 2, room.y + 3)] = "shelves"
        decor[(room.x + room.w - 3, room.y + 3)] = "shelves"
        decor[(cx, room.y + 2)] = "brazier"
        decor[(cx, cy - 1)] = "crate"                       # the main cache pile

    door_x = foyer.center[0]
    door_y = room.y + room.h - 1
    region.tiles[door_x][door_y] = 0
    region.metadata["interior_exit"] = (door_x, door_y)
    region.metadata["service_spot"] = service_spot
    return region


