import random
from dataclasses import dataclass, field
from collections import deque

from .constants import INTERIOR_REGION_TYPES
from .dungeon import Dungeon
from .game_typing import RegionMapLike
from .models import RectRoom, RegionPalette
from .regions_metadata import palette_for_region, random_region_name, region_summary  # noqa: F401


@dataclass
class Region:
    map_data: RegionMapLike
    region_type: str
    name: str
    palette: RegionPalette


@dataclass
class RegionChoice:
    region_type: str
    name: str
    summary: str
    context: dict = field(default_factory=dict)


class RegionMap:
    def __init__(self, width, height, fill=1):
        self.width: int = width
        self.height: int = height
        self.tiles: list[list[int]] = [[fill for _ in range(height)] for _ in range(width)]
        self.rooms: list[RectRoom] = []
        self.metadata: dict = {}
        self.transparent_tiles: set[tuple[int, int]] = set()

    def carve_rect(self, x, y, w, h):
        room = RectRoom(x, y, w, h)
        self.rooms.append(room)
        for tx in range(x, x + w):
            for ty in range(y, y + h):
                self.tiles[tx][ty] = 0
        return room

    def is_blocked(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or self.tiles[x][y] == 1


def path_tiles(start, end, width=1):
    tiles = set()
    x1, y1 = start
    x2, y2 = end
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            tiles.add((x, y1 + offset))
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            tiles.add((x2 + offset, y))
    return tiles


def walkable_path_tiles(region_map, start, end):
    if start == end:
        return [start]
    frontier = deque([start])
    came_from = {start: None}
    while frontier:
        current = frontier.popleft()
        if current == end:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in came_from:
                continue
            if not (0 < neighbor[0] < region_map.width - 1 and 0 < neighbor[1] < region_map.height - 1):
                continue
            if region_map.is_blocked(*neighbor) and neighbor != end:
                continue
            came_from[neighbor] = current
            frontier.append(neighbor)
    if end not in came_from:
        return []
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def widen_path_tiles(tiles, width=1):
    widened = set()
    for x, y in tiles:
        for offset_x in range(-(width // 2), width - (width // 2)):
            for offset_y in range(-(width // 2), width - (width // 2)):
                widened.add((x + offset_x, y + offset_y))
    return widened


def feature_footprint_tiles(region_map, anchor, kind, preferred_tiles=None):
    if kind != "notice_board":
        return {anchor}
    preferred_tiles = set(preferred_tiles or set())
    candidates = [
        [(0, 0), (1, 0), (0, -1), (1, -1)],
        [(-1, 0), (0, 0), (-1, -1), (0, -1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(-1, 0), (0, 0), (-1, 1), (0, 1)],
    ]
    best_tiles = {anchor}
    best_score = (-1, -1)
    for offsets in candidates:
        tiles = []
        valid = True
        for dx, dy in offsets:
            tile = (anchor[0] + dx, anchor[1] + dy)
            if not (1 <= tile[0] < region_map.width - 1 and 1 <= tile[1] < region_map.height - 1):
                valid = False
                break
            if region_map.tiles[tile[0]][tile[1]] != 0:
                valid = False
                break
            tiles.append(tile)
        if not valid:
            continue
        preferred_count = sum(1 for tile in tiles if tile in preferred_tiles)
        score = (preferred_count, len(tiles))
        if score > best_score:
            best_score = score
            best_tiles = set(tiles)
    return best_tiles


def choose_region_type(floor):
    if floor == 1:
        return "dungeon"
    options = ["dungeon", "forest", "ruins"]
    weights = [4, 3, 2]
    if floor >= 2:
        options.extend(["plains", "farmland", "cave"])
        weights.extend([2, 2, 2])
    if floor >= 3:
        options.extend(["desert", "swamp", "badlands", "town"])
        weights.extend([2, 2, 2, 2])
    if floor >= 4:
        options.extend(["mountain", "tundra", "castle"])
        weights.extend([2, 2, 1])
    if floor >= 5:
        options.extend(["volcanic", "monster_town", "maze"])
        weights.extend([1, 1, 1])
    return random.choices(options, weights=weights, k=1)[0]


def settlement_size_label(size):
    return {
        "hamlet": "Hamlet",
        "village": "Village",
        "town": "Town",
        "large_town": "Large Town",
    }.get(size, size.replace("_", " ").title())


def choose_settlement_size(parent_biome, hostile=False):
    weights = {
        "forest": [3, 5, 3, 1],
        "plains": [2, 4, 4, 2],
        "farmland": [1, 3, 4, 3],
        "desert": [4, 4, 2, 1],
        "swamp": [4, 4, 2, 0],
        "mountain": [4, 4, 2, 1],
        "badlands": [5, 3, 1, 0],
        "tundra": [4, 4, 2, 0],
        "volcanic": [5, 3, 1, 0],
    }
    options = ["hamlet", "village", "town", "large_town"]
    biome_weights = weights.get(parent_biome, [3, 4, 3, 1])[:]
    if hostile:
        biome_weights = [max(1, biome_weights[0] + 1), biome_weights[1], max(1, biome_weights[2] - 1), max(0, biome_weights[3] - 1)]
    return random.choices(options, weights=biome_weights, k=1)[0]


def carve_path(region_map, start, end, width=1):
    x1, y1 = start
    x2, y2 = end
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            py = max(1, min(region_map.height - 2, y1 + offset))
            region_map.tiles[x][py] = 0
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for offset in range(-(width // 2), width - (width // 2)):
            px = max(1, min(region_map.width - 2, x2 + offset))
            region_map.tiles[px][y] = 0




# Generators are imported after the core definitions to avoid circular imports.
from .regions_generators import (  # noqa: E402
    generate_forest, generate_ruins, generate_desert, generate_mountain,
    generate_swamp, generate_plains, generate_farmland,
    generate_badlands, generate_tundra, generate_volcanic, generate_castle,
    generate_cave, generate_maze,
)
def generate_region(floor, width, height, region_type=None, name=None, context=None):
    from .regions_town import generate_interior, generate_monster_town, generate_town
    region_type = region_type or choose_region_type(floor)
    name = name or random_region_name(region_type)
    palette = palette_for_region(region_type)
    context = context or {}
    if region_type == "forest":
        return Region(generate_forest(width, height), region_type, name, palette)
    if region_type == "ruins":
        return Region(generate_ruins(width, height), region_type, name, palette)
    if region_type == "desert":
        return Region(generate_desert(width, height), region_type, name, palette)
    if region_type == "mountain":
        return Region(generate_mountain(width, height), region_type, name, palette)
    if region_type == "swamp":
        return Region(generate_swamp(width, height), region_type, name, palette)
    if region_type == "plains":
        return Region(generate_plains(width, height), region_type, name, palette)
    if region_type == "farmland":
        return Region(generate_farmland(width, height), region_type, name, palette)
    if region_type == "badlands":
        return Region(generate_badlands(width, height), region_type, name, palette)
    if region_type == "tundra":
        return Region(generate_tundra(width, height), region_type, name, palette)
    if region_type == "volcanic":
        return Region(generate_volcanic(width, height), region_type, name, palette)
    if region_type == "castle":
        return Region(generate_castle(width, height), region_type, name, palette)
    if region_type == "cave":
        return Region(generate_cave(width, height), region_type, name, palette)
    if region_type == "maze":
        return Region(generate_maze(width, height), region_type, name, palette)
    if region_type == "town":
        return Region(generate_town(width, height, context=context), region_type, name, palette)
    if region_type == "monster_town":
        return Region(generate_monster_town(width, height, context=context), region_type, name, palette)
    if region_type == "ossuary":
        return Region(generate_ruins(width, height), region_type, name, palette)
    if region_type == "mirrorwood":
        return Region(generate_forest(width, height), region_type, name, palette)
    if region_type in INTERIOR_REGION_TYPES:
        return Region(generate_interior(width, height, region_type), region_type, name, palette)
    return Region(Dungeon(width, height), region_type, name, palette)
