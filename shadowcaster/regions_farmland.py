import random

from .models import RectRoom
from .regions import (
    RegionMap,
    carve_path,
    path_tiles,
)


def _place_building(region, bx, by, bw, bh, door_side="south"):
    """Stamp a walled building with a single door gap. Returns the interior room."""
    for tx in range(bx, bx + bw):
        for ty in range(by, by + bh):
            region.tiles[tx][ty] = 1
    interior = RectRoom(bx + 1, by + 1, bw - 2, bh - 2)
    for tx in range(interior.x, interior.x + interior.w):
        for ty in range(interior.y, interior.y + interior.h):
            region.tiles[tx][ty] = 0
    dx = (bx + bw // 2)
    dy = (by + bh // 2)
    if door_side == "south":
        region.tiles[dx][by + bh - 1] = 0
    elif door_side == "north":
        region.tiles[dx][by] = 0
    elif door_side == "west":
        region.tiles[bx][dy] = 0
    elif door_side == "east":
        region.tiles[bx + bw - 1][dy] = 0
    region.rooms.append(interior)
    return interior


def generate_farmland(width, height):
    region = RegionMap(width, height, fill=0)
    region.metadata["decor"] = {}

    for x in range(width):
        region.tiles[x][0] = 1
        region.tiles[x][height - 1] = 1
    for y in range(height):
        region.tiles[0][y] = 1
        region.tiles[width - 1][y] = 1

    buildings = []

    # farmhouse — smallish, near one corner quadrant
    fh_w, fh_h = random.randint(6, 8), random.randint(5, 7)
    fh_x = random.randint(3, width // 3)
    fh_y = random.randint(3, height // 3)
    farmhouse = _place_building(region, fh_x, fh_y, fh_w, fh_h, door_side="south")
    buildings.append(farmhouse)
    well_x = fh_x + fh_w // 2
    well_y = fh_y + fh_h + 1
    if 1 < well_x < width - 2 and 1 < well_y < height - 2:
        region.metadata["decor"][(well_x, well_y)] = "well"

    # barn — wider and taller, placed elsewhere
    barn_w, barn_h = random.randint(8, 11), random.randint(6, 8)
    barn_x = random.randint(width * 2 // 3 - barn_w, width - barn_w - 4)
    barn_y = random.randint(3, height - barn_h - 4)
    barn = _place_building(region, barn_x, barn_y, barn_w, barn_h, door_side="west")
    buildings.append(barn)
    # haystacks near barn entrance
    for hoff in (-1, 1):
        hx = barn_x - 2
        hy = barn_y + barn_h // 2 + hoff * 2
        if 1 < hx < width - 2 and 1 < hy < height - 2 and region.tiles[hx][hy] == 0:
            region.metadata["decor"][(hx, hy)] = "haystack"

    # optional second outbuilding (shed/storage)
    if random.random() < 0.65:
        shed_w, shed_h = random.randint(4, 6), random.randint(3, 5)
        shed_x = random.randint(3, width - shed_w - 4)
        shed_y = random.randint(height // 2, height - shed_h - 4)
        overlaps = any(
            sx <= shed_x + shed_w and shed_x <= sx + sw and
            sy <= shed_y + shed_h and shed_y <= sy + sh
            for sx, sy, sw, sh in [
                (fh_x - 1, fh_y - 1, fh_w + 2, fh_h + 2),
                (barn_x - 1, barn_y - 1, barn_w + 2, barn_h + 2),
            ]
        )
        if not overlaps:
            shed = _place_building(region, shed_x, shed_y, shed_w, shed_h,
                                   door_side=random.choice(["north", "south", "east", "west"]))
            buildings.append(shed)

    # crop plots of varying sizes and types
    plot_types = ["wheat", "wheat", "crop_row", "crop_row", "fallow"]
    plots = []
    plot_attempts = 10 + width * height // 400
    for _ in range(plot_attempts):
        pw = random.randint(6, 14)
        ph = random.randint(5, 10)
        px = random.randint(2, width - pw - 3)
        py = random.randint(2, height - ph - 3)
        # reject if overlaps any building footprint (with 1-tile margin)
        if any(
            bx - 1 <= px + pw and px <= bx + bw + 1 and
            by - 1 <= py + ph and py <= by + bh + 1
            for bx, by, bw, bh in [
                (fh_x, fh_y, fh_w, fh_h),
                (barn_x, barn_y, barn_w, barn_h),
            ]
        ):
            continue
        # reject if overlaps an existing plot (1-tile buffer)
        if any(
            px2 - 1 <= px + pw and px <= px2 + pw2 + 1 and
            py2 - 1 <= py + ph and py <= py2 + ph2 + 1
            for px2, py2, pw2, ph2 in plots
        ):
            continue
        plots.append((px, py, pw, ph))

    for px, py, pw, ph in plots:
        crop = random.choice(plot_types)
        for tx in range(px, px + pw):
            for ty in range(py, py + ph):
                if region.tiles[tx][ty] != 0:
                    continue
                if crop == "wheat":
                    region.metadata["decor"][(tx, ty)] = "wheat"
                elif crop == "crop_row":
                    # alternate rows
                    region.metadata["decor"][(tx, ty)] = "crop_row" if (ty - py) % 2 == 0 else "fallow"
                else:
                    region.metadata["decor"][(tx, ty)] = "fallow"
        # fence along one or two edges of each plot
        fence_edges = random.sample(["top", "bottom", "left", "right"], k=random.randint(1, 3))
        for edge in fence_edges:
            if edge == "top":
                for tx in range(px, px + pw):
                    if region.tiles[tx][py] == 0:
                        region.metadata["decor"][(tx, py)] = "fence"
            elif edge == "bottom":
                for tx in range(px, px + pw):
                    if region.tiles[tx][py + ph - 1] == 0:
                        region.metadata["decor"][(tx, py + ph - 1)] = "fence"
            elif edge == "left":
                for ty in range(py, py + ph):
                    if region.tiles[px][ty] == 0:
                        region.metadata["decor"][(px, ty)] = "fence"
            elif edge == "right":
                for ty in range(py, py + ph):
                    if region.tiles[px + pw - 1][ty] == 0:
                        region.metadata["decor"][(px + pw - 1, ty)] = "fence"

    # dirt paths connecting buildings to each other and to plots
    waypoints = [farmhouse.center, barn.center]
    if len(buildings) > 2:
        waypoints.append(buildings[2].center)
    for plot in plots[:4]:
        px, py, pw, ph = plot
        waypoints.append((px + pw // 2, py + ph // 2))
    random.shuffle(waypoints[2:])
    for a, b in zip(waypoints, waypoints[1:]):
        carve_path(region, a, b, width=2)
        for tile in path_tiles(a, b, width=2):
            tx, ty = tile
            if 1 < tx < width - 2 and 1 < ty < height - 2 and region.tiles[tx][ty] == 0:
                if region.metadata["decor"].get(tile) not in {"fence", "haystack", "well"}:
                    region.metadata["decor"][tile] = "path"

    # scatter a few extra haystacks and flowers in open areas
    open_tiles = [
        (x, y) for x in range(2, width - 2) for y in range(2, height - 2)
        if region.tiles[x][y] == 0 and (x, y) not in region.metadata["decor"]
    ]
    random.shuffle(open_tiles)
    for tile in open_tiles[: max(2, len(open_tiles) // 80)]:
        region.metadata["decor"][tile] = "haystack"
    for tile in open_tiles[len(open_tiles) // 80 : len(open_tiles) // 80 + max(4, len(open_tiles) // 40)]:
        region.metadata["decor"][tile] = "flowers"

    return region
