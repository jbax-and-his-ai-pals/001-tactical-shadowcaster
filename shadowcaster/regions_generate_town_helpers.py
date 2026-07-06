import random

from .models import RectRoom
from .regions_map import RegionMap, carve_path, path_tiles, walkable_path_tiles, widen_path_tiles


def heuristic_city_distance(left, right):
    return max(abs(left[0] - right[0]), abs(left[1] - right[1]))


def _setup_region_base(width, height, profile, plaza_w, plaza_h):
    region = RegionMap(width, height, fill=0)
    region.metadata["town_buildings"] = []
    region.metadata["town_paths"] = set()
    region.metadata["decor"] = {}
    region.metadata["feature_footprints"] = {}
    region.metadata["house_colors"] = {}
    region.metadata["town_parent_biome"] = profile["parent_biome"]
    region.metadata["settlement_size"] = profile["settlement_size"]
    region.metadata["settlement_label"] = profile["settlement_label"]
    region.metadata["hostile_settlement"] = False
    for x in range(width):
        region.tiles[x][0] = 1
        region.tiles[x][height - 1] = 1
    for y in range(height):
        region.tiles[0][y] = 1
        region.tiles[width - 1][y] = 1

    plaza = region.carve_rect(width // 2 - plaza_w // 2, height // 2 - plaza_h // 2, plaza_w, plaza_h)
    region.metadata["town_square"] = plaza.center
    north = region.carve_rect(width // 2 - 4, 3, 9, 7)
    south = region.carve_rect(width // 2 - 4, height - 10, 9, 7)
    west = region.carve_rect(3, height // 2 - 3, 8, 7)
    east = region.carve_rect(width - 11, height // 2 - 3, 8, 7)
    for room in (north, south, west, east):
        carve_path(region, plaza.center, room.center, width=2)
        region.metadata["town_paths"].update(
            {
                (x, y)
                for x, y in path_tiles(plaza.center, room.center, width=2)
                if 0 < x < width - 1 and 0 < y < height - 1
            }
        )
    return region, plaza, north, south, west, east


def _place_houses(region, profile, plaza, plaza_w, plaza_h, width, height):
    # House color palettes — 10 entries per biome, each clearly distinct from the sandy floor (~168,130,86).
    # Contrast achieved via luminosity shift (much darker or much lighter) and hue shift.
    house_color_palettes: dict[str, list[tuple[int, int, int]]] = {
        "forest": [
            (58, 90, 62), (48, 78, 54), (72, 106, 70), (92, 70, 56),
            (50, 68, 82), (84, 96, 64), (110, 80, 58), (64, 82, 96),
            (78, 58, 48), (96, 118, 76),
        ],
        "plains": [
            (72, 58, 44), (88, 68, 50), (104, 80, 56), (56, 72, 96),
            (88, 50, 44), (50, 84, 68), (110, 68, 44), (68, 96, 80),
            (44, 56, 80), (96, 88, 56),
        ],
        "farmland": [
            (96, 62, 40), (112, 72, 44), (80, 54, 36), (60, 80, 56),
            (48, 64, 88), (104, 56, 42), (72, 96, 60), (88, 44, 44),
            (56, 78, 100), (116, 88, 48),
        ],
        "desert": [
            (120, 80, 48), (140, 96, 56), (100, 68, 44), (60, 88, 108),
            (104, 44, 44), (72, 104, 80), (148, 72, 48), (56, 72, 100),
            (132, 112, 60), (80, 56, 40),
        ],
        "swamp": [
            (44, 76, 60), (56, 92, 72), (36, 62, 52), (72, 58, 44),
            (48, 88, 80), (88, 72, 50), (36, 56, 76), (62, 96, 66),
            (80, 50, 42), (44, 70, 92),
        ],
        "mountain": [
            (90, 96, 110), (72, 78, 94), (108, 112, 124), (60, 68, 86),
            (88, 72, 60), (104, 88, 68), (56, 80, 104), (76, 60, 50),
            (120, 104, 80), (64, 92, 108),
        ],
        "badlands": [
            (100, 60, 40), (120, 72, 44), (80, 50, 36), (56, 80, 100),
            (104, 44, 42), (44, 70, 60), (136, 84, 50), (60, 50, 80),
            (88, 56, 36), (50, 88, 70),
        ],
        "tundra": [
            (104, 116, 132), (88, 100, 118), (120, 130, 144), (72, 86, 106),
            (68, 80, 96), (88, 72, 62), (108, 88, 68), (56, 68, 88),
            (136, 120, 96), (76, 60, 50),
        ],
        "volcanic": [
            (72, 50, 44), (88, 62, 52), (56, 42, 38), (104, 72, 56),
            (44, 56, 72), (68, 44, 36), (80, 72, 52), (48, 68, 84),
            (96, 56, 40), (60, 80, 68),
        ],
    }
    color_pool = house_color_palettes.get(profile["parent_biome"], house_color_palettes["plains"])

    def next_house_color() -> tuple[int, int, int]:
        base = random.choice(color_pool)
        r = random.randint(-8, 8)
        return (
            max(30, min(215, base[0] + r)),
            max(30, min(215, base[1] + r)),
            max(30, min(215, base[2] + r)),
        )

    house_count = max(profile["min_houses"], (width * height) // profile["house_divisor"])
    houses = []
    attempts = house_count * 8
    while attempts > 0 and len(houses) < house_count:
        attempts -= 1
        shape = random.choice(["rect", "rect", "rect", "wide", "narrow"])
        if shape == "wide":
            hw = random.randint(7, 10)
            hh = random.randint(3, 4)
        elif shape == "narrow":
            hw = random.randint(3, 4)
            hh = random.randint(6, 9)
        else:
            hw = random.randint(4, 7)
            hh = random.randint(4, 6)
        hx = random.randint(2, width - hw - 3)
        hy = random.randint(2, height - hh - 3)
        if abs((hx + hw // 2) - plaza.center[0]) < plaza_w // 2 + 4 and abs((hy + hh // 2) - plaza.center[1]) < plaza_h // 2 + 3:
            continue
        proposed = RectRoom(hx, hy, hw, hh)
        if any(
            proposed.x < existing["room"].x + existing["room"].w + 2
            and proposed.x + proposed.w + 2 > existing["room"].x
            and proposed.y < existing["room"].y + existing["room"].h + 2
            and proposed.y + proposed.h + 2 > existing["room"].y
            for existing in houses
        ):
            continue
        hcolor = next_house_color()
        for tx in range(hx, hx + hw):
            for ty in range(hy, hy + hh):
                region.tiles[tx][ty] = 1
                region.metadata["house_colors"][(tx, ty)] = hcolor
        # optional L-wing on some houses
        if shape == "rect" and random.random() < 0.28:
            wing_side = random.choice(["left", "right"])
            ww = random.randint(2, max(2, hw // 2))
            wh = random.randint(2, max(2, hh // 2))
            if wing_side == "left":
                wx, wy = hx - ww, hy + random.randint(0, hh - wh)
            else:
                wx, wy = hx + hw, hy + random.randint(0, hh - wh)
            if 2 <= wx and wx + ww <= width - 2 and 2 <= wy and wy + wh <= height - 2:
                if not any(
                    wx < ex["room"].x + ex["room"].w + 1
                    and wx + ww + 1 > ex["room"].x
                    and wy < ex["room"].y + ex["room"].h + 1
                    and wy + wh + 1 > ex["room"].y
                    for ex in houses
                ):
                    for tx in range(wx, wx + ww):
                        for ty in range(wy, wy + wh):
                            region.tiles[tx][ty] = 1
                            region.metadata["house_colors"][(tx, ty)] = hcolor
        door_x = hx + hw // 2
        door_y = hy if plaza.center[1] > hy else hy + hh - 1
        region.tiles[door_x][door_y] = 0
        house = {"room": proposed, "door": (door_x, door_y), "color": hcolor}
        houses.append(house)
        route = walkable_path_tiles(region, plaza.center, house["door"])
        region.metadata["town_paths"].update(
            {
                (x, y)
                for x, y in widen_path_tiles(route or [plaza.center, house["door"]], width=1)
                if 0 < x < width - 1 and 0 < y < height - 1 and region.tiles[x][y] == 0
            }
        )
    return houses
