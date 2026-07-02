import random

from .models import RectRoom
from .regions import (
    RegionMap,
    carve_path,
)
from .regions_farmland import generate_farmland


def generate_forest(width, height):
    region = RegionMap(width, height, fill=0)
    clearings = []
    clearing_count = 5 + max(0, (width * height) // 900)
    for _ in range(clearing_count):
        cw = random.randint(6, 12)
        ch = random.randint(5, 10)
        cx = random.randint(2, width - cw - 3)
        cy = random.randint(2, height - ch - 3)
        clearings.append(region.carve_rect(cx, cy, cw, ch))
    for x in range(width):
        region.tiles[x][0] = 1
        region.tiles[x][height - 1] = 1
    for y in range(height):
        region.tiles[0][y] = 1
        region.tiles[width - 1][y] = 1
    for _ in range((width * height) // 8):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if any(room.x <= tx < room.x + room.w and room.y <= ty < room.y + room.h for room in clearings):
            continue
        region.tiles[tx][ty] = 1
    if len(clearings) >= 2:
        for left, right in zip(clearings, clearings[1:]):
            carve_path(region, left.center, right.center, width=2)
    return region


def generate_ruins(width, height):
    region = RegionMap(width, height, fill=1)
    halls = []
    hall_count = 6 + max(0, (width * height) // 1100)
    for _ in range(hall_count):
        rw = random.randint(6, 11)
        rh = random.randint(5, 9)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        halls.append(region.carve_rect(rx, ry, rw, rh))
    for left, right in zip(halls, halls[1:]):
        carve_path(region, left.center, right.center, width=1)
    for room in halls:
        breach_count = random.randint(1, 3)
        for _ in range(breach_count):
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge in ("top", "bottom"):
                bx = random.randint(room.x + 1, room.x + room.w - 2)
                by = room.y if edge == "top" else room.y + room.h - 1
            else:
                bx = room.x if edge == "left" else room.x + room.w - 1
                by = random.randint(room.y + 1, room.y + room.h - 2)
            region.tiles[bx][by] = 0
    return region


def generate_desert(width, height):
    region = RegionMap(width, height, fill=0)
    oases = []
    for x in range(width):
        region.tiles[x][0] = 1
        region.tiles[x][height - 1] = 1
    for y in range(height):
        region.tiles[0][y] = 1
        region.tiles[width - 1][y] = 1
    for _ in range(4 + max(1, width * height // 1200)):
        rw = random.randint(6, 10)
        rh = random.randint(5, 8)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        oases.append(region.carve_rect(rx, ry, rw, rh))
    for _ in range((width * height) // 10):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if any(room.x <= tx < room.x + room.w and room.y <= ty < room.y + room.h for room in oases):
            continue
        if random.random() < 0.55:
            region.tiles[tx][ty] = 1
    for left, right in zip(oases, oases[1:]):
        carve_path(region, left.center, right.center, width=2)
    return region


def generate_mountain(width, height):
    region = RegionMap(width, height, fill=1)
    region.metadata["opaque_tiles"] = set()
    pass_rooms = []
    current_x = 2
    current_y = random.randint(height // 4, height * 3 // 4)
    for _ in range(6):
        rw = random.randint(5, 9)
        rh = random.randint(5, 8)
        rx = min(width - rw - 3, current_x)
        ry = max(2, min(height - rh - 3, current_y - rh // 2))
        room = region.carve_rect(rx, ry, rw, rh)
        pass_rooms.append(room)
        current_x = min(width - 10, rx + random.randint(8, 12))
        current_y = max(4, min(height - 5, current_y + random.randint(-7, 7)))
    for left, right in zip(pass_rooms, pass_rooms[1:]):
        carve_path(region, left.center, right.center, width=1)
    blocked_tiles = [
        (x, y)
        for x in range(1, width - 1)
        for y in range(1, height - 1)
        if region.tiles[x][y] == 1
    ]
    random.shuffle(blocked_tiles)
    opaque_count = max(14, len(blocked_tiles) // 17)
    region.metadata["opaque_tiles"] = set(blocked_tiles[:opaque_count])
    return region


def generate_swamp(width, height):
    region = RegionMap(width, height, fill=1)
    region.metadata["opaque_tiles"] = set()
    islands = []
    island_count = 6 + max(0, width * height // 1200)
    for _ in range(island_count):
        rw = random.randint(5, 9)
        rh = random.randint(4, 7)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        islands.append(region.carve_rect(rx, ry, rw, rh))
    for left, right in zip(islands, islands[1:]):
        carve_path(region, left.center, right.center, width=1)
    for _ in range(width * height // 34):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        region.tiles[tx][ty] = 0 if random.random() < 0.3 else region.tiles[tx][ty]
    blocked_tiles = [
        (x, y)
        for x in range(1, width - 1)
        for y in range(1, height - 1)
        if region.tiles[x][y] == 1
    ]
    random.shuffle(blocked_tiles)
    opaque_count = max(12, len(blocked_tiles) // 18)
    region.metadata["opaque_tiles"] = set(blocked_tiles[:opaque_count])
    return region


def generate_plains(width, height):
    region = RegionMap(width, height, fill=0)
    landmarks = []
    for x in range(width):
        region.tiles[x][0] = 1
        region.tiles[x][height - 1] = 1
    for y in range(height):
        region.tiles[0][y] = 1
        region.tiles[width - 1][y] = 1
    for _ in range(6):
        rw = random.randint(6, 10)
        rh = random.randint(5, 8)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        landmarks.append(region.carve_rect(rx, ry, rw, rh))
    for _ in range(width * height // 14):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if any(room.x <= tx < room.x + room.w and room.y <= ty < room.y + room.h for room in landmarks):
            continue
        if random.random() < 0.28:
            region.tiles[tx][ty] = 1
    for left, right in zip(landmarks, landmarks[1:]):
        carve_path(region, left.center, right.center, width=2)
    return region


def generate_badlands(width, height):
    region = RegionMap(width, height, fill=1)
    region.metadata["opaque_tiles"] = set()
    mesas = []
    current_x = 2
    current_y = random.randint(height // 4, height * 3 // 4)
    for _ in range(7):
        rw = random.randint(5, 10)
        rh = random.randint(5, 8)
        rx = min(width - rw - 3, current_x)
        ry = max(2, min(height - rh - 3, current_y - rh // 2))
        room = region.carve_rect(rx, ry, rw, rh)
        mesas.append(room)
        current_x = min(width - 10, rx + random.randint(7, 11))
        current_y = max(4, min(height - 5, current_y + random.randint(-6, 6)))
    for left, right in zip(mesas, mesas[1:]):
        carve_path(region, left.center, right.center, width=1)
    for _ in range(width * height // 20):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if region.tiles[tx][ty] == 1 and random.random() < 0.1:
            region.tiles[tx][ty] = 0
    blocked_tiles = [
        (x, y)
        for x in range(1, width - 1)
        for y in range(1, height - 1)
        if region.tiles[x][y] == 1
    ]
    random.shuffle(blocked_tiles)
    opaque_count = max(14, len(blocked_tiles) // 16)
    region.metadata["opaque_tiles"] = set(blocked_tiles[:opaque_count])
    return region


def generate_tundra(width, height):
    region = RegionMap(width, height, fill=0)
    clearings = []
    for x in range(width):
        region.tiles[x][0] = 1
        region.tiles[x][height - 1] = 1
    for y in range(height):
        region.tiles[0][y] = 1
        region.tiles[width - 1][y] = 1
    for _ in range(5 + max(0, width * height // 1200)):
        rw = random.randint(6, 11)
        rh = random.randint(5, 9)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        clearings.append(region.carve_rect(rx, ry, rw, rh))
    for left, right in zip(clearings, clearings[1:]):
        carve_path(region, left.center, right.center, width=2)
    for _ in range(width * height // 12):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if any(room.x <= tx < room.x + room.w and room.y <= ty < room.y + room.h for room in clearings):
            continue
        if random.random() < 0.38:
            region.tiles[tx][ty] = 1
    return region


def generate_volcanic(width, height):
    region = RegionMap(width, height, fill=1)
    region.metadata["opaque_tiles"] = set()
    vents = []
    chamber_count = 6 + max(0, width * height // 1200)
    for _ in range(chamber_count):
        rw = random.randint(5, 9)
        rh = random.randint(4, 7)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        vents.append(region.carve_rect(rx, ry, rw, rh))
    for left, right in zip(vents, vents[1:]):
        carve_path(region, left.center, right.center, width=1)
    for _ in range(width * height // 22):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if region.tiles[tx][ty] == 1 and random.random() < 0.14:
            region.tiles[tx][ty] = 0
    blocked_tiles = [
        (x, y)
        for x in range(1, width - 1)
        for y in range(1, height - 1)
        if region.tiles[x][y] == 1
    ]
    random.shuffle(blocked_tiles)
    opaque_count = max(16, len(blocked_tiles) // 14)
    region.metadata["opaque_tiles"] = set(blocked_tiles[:opaque_count])
    return region


def generate_castle(width, height):
    region = RegionMap(width, height, fill=1)
    keep = region.carve_rect(width // 2 - 7, height // 2 - 5, 15, 11)
    wings = [
        region.carve_rect(width // 2 - 4, 3, 9, 7),
        region.carve_rect(width // 2 - 4, height - 10, 9, 7),
        region.carve_rect(3, height // 2 - 3, 8, 7),
        region.carve_rect(width - 11, height // 2 - 3, 8, 7),
    ]
    for room in wings:
        carve_path(region, keep.center, room.center, width=2)
    for room in [keep, *wings]:
        for _ in range(random.randint(1, 3)):
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge in ("top", "bottom"):
                bx = random.randint(room.x + 1, room.x + room.w - 2)
                by = room.y if edge == "top" else room.y + room.h - 1
            else:
                bx = room.x if edge == "left" else room.x + room.w - 1
                by = random.randint(room.y + 1, room.y + room.h - 2)
            region.tiles[bx][by] = 0
    return region


def generate_cave(width, height):
    region = RegionMap(width, height, fill=1)
    chamber = region.carve_rect(width // 2 - 5, height // 2 - 4, 11, 9)
    caves = [chamber]
    for _ in range(8 + max(0, width * height // 1200)):
        rw = random.randint(5, 10)
        rh = random.randint(4, 8)
        rx = random.randint(2, width - rw - 3)
        ry = random.randint(2, height - rh - 3)
        caves.append(region.carve_rect(rx, ry, rw, rh))
    for left, right in zip(caves, caves[1:]):
        carve_path(region, left.center, right.center, width=1)
    for _ in range(width * height // 16):
        tx = random.randint(1, width - 2)
        ty = random.randint(1, height - 2)
        if region.tiles[tx][ty] == 1 and random.random() < 0.22:
            region.tiles[tx][ty] = 0
    return region


def generate_maze(width, height):
    region = RegionMap(width, height, fill=1)
    maze_width = width - 2 if (width - 2) % 2 == 1 else width - 3
    maze_height = height - 2 if (height - 2) % 2 == 1 else height - 3
    start_x = 1
    start_y = 1
    for x in range(start_x, start_x + maze_width, 2):
        for y in range(start_y, start_y + maze_height, 2):
            region.tiles[x][y] = 0
    stack = [(start_x, start_y)]
    visited = {(start_x, start_y)}
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    while stack:
        cx, cy = stack[-1]
        neighbors = []
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if not (1 <= nx < start_x + maze_width and 1 <= ny < start_y + maze_height):
                continue
            if (nx, ny) in visited:
                continue
            neighbors.append((nx, ny, dx, dy))
        if not neighbors:
            stack.pop()
            continue
        nx, ny, dx, dy = neighbors[0]
        region.tiles[cx + dx // 2][cy + dy // 2] = 0
        visited.add((nx, ny))
        stack.append((nx, ny))
    region.rooms.append(RectRoom(1, 1, maze_width, maze_height))
    return region
