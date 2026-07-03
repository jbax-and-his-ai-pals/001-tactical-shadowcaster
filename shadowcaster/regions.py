import random
from dataclasses import dataclass, field
from collections import deque

from .dungeon import Dungeon
from .game_typing import RegionMapLike
from .models import RectRoom, RegionPalette


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
        options.extend(["desert", "swamp", "badlands"])
        weights.extend([2, 2, 2])
    if floor >= 4:
        options.extend(["mountain", "tundra", "castle"])
        weights.extend([2, 2, 1])
    if floor >= 5:
        options.append("volcanic")
        weights.append(1)
    if floor >= 3:
        options.append("town")
        weights.append(2)
    if floor >= 5:
        options.extend(["monster_town", "maze"])
        weights.extend([1, 1])
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


def random_region_name(region_type):
    tables = {
        "dungeon": (
            ["Ashen", "Gloam", "Hollow", "Iron", "Silent", "Black", "Sunken"],
            ["Catacombs", "Vault", "Keep", "Depths", "Warrens", "Crypt", "Halls"],
        ),
        "forest": (
            ["Whispering", "Moss", "Amber", "Moon", "Thorn", "Green", "Cedar"],
            ["Grove", "Wilds", "Wood", "Glade", "Canopy", "Thicket", "Copse"],
        ),
        "ruins": (
            ["Broken", "Fallen", "Old", "Shattered", "Weathered", "Lost", "Sable"],
            ["Sanctum", "Stones", "Court", "Ruins", "Pillars", "Watch", "Forum"],
        ),
        "desert": (
            ["Amber", "Burning", "Dune", "Saffron", "Glass", "Sun", "Red"],
            ["Expanse", "Waste", "Reach", "Sea", "Hollows", "Oasis", "Steppe"],
        ),
        "mountain": (
            ["High", "Granite", "Storm", "Snow", "Iron", "Eagle", "Frost"],
            ["Pass", "Spine", "Ridge", "Climb", "Heights", "Steps", "Crown"],
        ),
        "swamp": (
            ["Black", "Mire", "Sour", "Fog", "Drowned", "Bog", "Reed"],
            ["Fen", "Marsh", "Bog", "Lowland", "Mire", "Hollow", "Waters"],
        ),
        "plains": (
            ["Golden", "Wide", "Sun", "High", "Long", "Breeze", "Open"],
            ["Field", "Plains", "Plateau", "Reach", "Grass", "Steppe", "Downs"],
        ),
        "farmland": (
            ["Amber", "Harvest", "Miller's", "Green", "Orchard", "Barley", "Sun"],
            ["Fields", "Farm", "Croft", "Acres", "Pasture", "Hold", "Meadow"],
        ),
        "badlands": (
            ["Red", "Broken", "Dust", "Shale", "Riven", "Dry", "Rust"],
            ["Badlands", "Cuts", "Canyon", "Reach", "Barrens", "Gulch", "Flats"],
        ),
        "tundra": (
            ["White", "Frost", "Pale", "Winter", "North", "Snow", "Icewind"],
            ["Tundra", "Waste", "Reach", "Expanse", "Fields", "Hollows", "Drift"],
        ),
        "volcanic": (
            ["Ash", "Cinder", "Ember", "Magma", "Fire", "Black", "Smoldering"],
            ["Caldera", "Crags", "Wastes", "Spine", "Fields", "Fissure", "Flow"],
        ),
        "castle": (
            ["Ivory", "Ashen", "Black", "Silent", "Red", "Kings", "Fallen"],
            ["Keep", "Castle", "Bastion", "Hall", "Rampart", "Court", "Citadel"],
        ),
        "cave": (
            ["Deep", "Echo", "Moon", "Hollow", "Stone", "Cold", "Twilight"],
            ["Cavern", "Grotto", "Cave", "Hollow", "Tunnels", "Sink", "Den"],
        ),
        "maze": (
            ["Crooked", "Mirror", "Lost", "Twisted", "Hedge", "Silent", "Winding"],
            ["Maze", "Labyrinth", "Ways", "Passages", "Turns", "Loops", "Grid"],
        ),
        "town": (
            ["Oak", "Lantern", "Still", "River", "Market", "Sun", "Crossing"],
            ["Hollow", "Cross", "Square", "Village", "Commons", "Rest", "Ford"],
        ),
        "monster_town": (
            ["Blight", "Grim", "Howling", "Rotted", "Ash", "Blood", "Crooked"],
            ["Borough", "Hamlet", "Row", "Hearth", "Square", "Stead", "Market"],
        ),
        "inn": (["Traveler's"], ["Inn"]),
        "clinic": (["Town"], ["Clinic"]),
        "supply": (["Old"], ["Provisioner"]),
        "shrine": (["Wayside", "Quiet", "Sun", "Pilgrim's", "Stone"], ["Shrine", "Sanctum", "Chapel"]),
        "smith": (["Old", "Iron", "Ember", "Hammer", "Anvil"], ["Forge", "Smithy", "Works"]),
        "cartographer": (["Surveyor's", "Wayfinder's", "Lantern", "Road", "Atlas"], ["Office", "Charts", "Maps"]),
    }
    first, second = tables[region_type]
    return f"{random.choice(first)} {random.choice(second)}"


def region_summary(region_type, floor):
    summaries = {
        "dungeon": "Dense corridors, tighter fights, reliable cover.",
        "forest": "Open paths, broken sightlines, vitality-friendly growth.",
        "ruins": "Shattered halls, mixed cover, stronger salvage.",
        "desert": "Open sands, jagged cover, and long sightlines between oases.",
        "mountain": "Narrow passes, sudden bends, and strong positional choke points.",
        "swamp": "Broken islands of footing with murky, awkward approaches.",
        "plains": "Broad space, sparse cover, and clean lines for ranged pressure.",
        "farmland": "Cultivated lanes, hedges, and open working ground around settlements.",
        "badlands": "Riven rock, hard bends, and broken canyon approaches.",
        "tundra": "Cold open stretches with wind-cut cover and bright sightlines.",
        "volcanic": "Ash-choked chambers, hard rock, and constant heat hazards.",
        "castle": "Structured wings, central keeps, and disciplined room fights.",
        "cave": "Jagged chambers and tunnels with irregular visibility pockets.",
        "maze": "Tight turns, deliberate scouting, and disorienting navigation.",
        "town": "Peaceful streets, townsfolk, and room to recover bearings.",
        "monster_town": "A settlement gone wrong, full of hostile residents and beasts.",
        "inn": "A quiet room and a chance to rest.",
        "clinic": "A clean stop for patching wounds.",
        "supply": "A stocked room for expedition essentials.",
        "shrine": "A still place where protective rites linger.",
        "smith": "A forge for tuning gear before the road ahead.",
        "cartographer": "A map room for charting the nearby frontier.",
    }
    suffix = f" Floor {floor + 1} route."
    return summaries[region_type] + suffix


def palette_for_region(region_type):
    palettes = {
        "dungeon": RegionPalette((96, 100, 112), (42, 42, 52), (46, 50, 60), (20, 20, 28), (18, 24, 36), (120, 154, 188), (245, 244, 232)),
        "forest": RegionPalette((48, 108, 62), (34, 52, 38), (24, 62, 34), (18, 28, 20), (16, 32, 22), (94, 156, 112), (236, 248, 228)),
        "ruins": RegionPalette((116, 90, 62), (54, 46, 40), (68, 50, 34), (26, 22, 20), (34, 24, 18), (176, 132, 94), (250, 238, 220)),
        "desert": RegionPalette((168, 132, 72), (92, 76, 44), (102, 72, 28), (40, 30, 18), (42, 28, 12), (228, 184, 92), (255, 244, 214)),
        "mountain": RegionPalette((108, 120, 126), (56, 64, 70), (62, 70, 76), (26, 28, 32), (24, 28, 36), (168, 184, 196), (244, 248, 252)),
        "swamp": RegionPalette((64, 86, 52), (44, 58, 40), (34, 48, 26), (20, 28, 18), (20, 26, 18), (124, 166, 96), (232, 246, 222)),
        "plains": RegionPalette((132, 156, 86), (74, 92, 54), (68, 88, 42), (28, 34, 20), (28, 32, 16), (206, 216, 126), (248, 250, 224)),
        "farmland": RegionPalette((156, 150, 92), (84, 88, 54), (92, 94, 48), (32, 34, 20), (34, 34, 18), (224, 206, 118), (250, 246, 214)),
        "badlands": RegionPalette((144, 96, 72), (76, 52, 42), (92, 58, 36), (30, 22, 18), (34, 22, 14), (220, 154, 104), (252, 236, 214)),
        "tundra": RegionPalette((176, 186, 194), (92, 102, 112), (110, 122, 132), (36, 40, 46), (34, 40, 48), (220, 236, 244), (252, 252, 255)),
        "volcanic": RegionPalette((110, 88, 84), (62, 48, 46), (84, 52, 42), (26, 20, 20), (34, 18, 18), (232, 126, 84), (255, 236, 226)),
        "castle": RegionPalette((124, 124, 138), (62, 58, 72), (68, 68, 84), (26, 24, 30), (26, 22, 34), (180, 168, 214), (246, 240, 255)),
        "cave": RegionPalette((92, 84, 74), (48, 42, 36), (54, 44, 34), (22, 18, 16), (22, 18, 14), (172, 144, 116), (246, 234, 220)),
        "maze": RegionPalette((84, 112, 86), (40, 54, 42), (34, 68, 36), (18, 26, 18), (18, 30, 20), (154, 210, 156), (236, 250, 236)),
        "town": RegionPalette((160, 126, 88), (82, 78, 70), (88, 68, 48), (34, 30, 28), (38, 28, 22), (198, 160, 112), (252, 242, 220)),
        "monster_town": RegionPalette((120, 54, 54), (54, 40, 40), (62, 26, 26), (24, 18, 18), (34, 14, 18), (210, 92, 112), (255, 232, 236)),
        "inn": RegionPalette((132, 102, 70), (70, 58, 46), (76, 58, 40), (28, 24, 20), (34, 26, 20), (208, 170, 120), (255, 244, 222)),
        "clinic": RegionPalette((122, 132, 144), (62, 72, 84), (70, 80, 92), (24, 28, 34), (22, 28, 32), (180, 214, 226), (240, 250, 255)),
        "supply": RegionPalette((132, 118, 84), (72, 64, 48), (80, 70, 50), (28, 24, 18), (32, 28, 22), (214, 192, 132), (255, 246, 224)),
        "shrine": RegionPalette((126, 126, 152), (62, 58, 78), (72, 68, 90), (24, 22, 32), (26, 22, 38), (196, 186, 234), (248, 242, 255)),
        "smith": RegionPalette((146, 104, 74), (72, 52, 40), (82, 58, 42), (28, 20, 18), (34, 22, 18), (226, 164, 96), (255, 240, 220)),
        "cartographer": RegionPalette((96, 120, 138), (50, 64, 74), (56, 74, 88), (20, 26, 30), (22, 28, 34), (154, 204, 224), (240, 248, 252)),
    }
    return palettes[region_type]


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
    if region_type in {"inn", "clinic", "supply", "shrine", "smith", "cartographer", "tavern", "chapel", "stable"}:
        return Region(generate_interior(width, height, region_type), region_type, name, palette)
    return Region(Dungeon(width, height), region_type, name, palette)
