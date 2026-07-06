import random
from dataclasses import dataclass, field

from .constants import INTERIOR_REGION_TYPES
from .dungeon import Dungeon
from .game_typing import RegionMapLike
from .models import RegionPalette
from .regions_map import (  # noqa: F401
    RegionMap, carve_path, feature_footprint_tiles,
    path_tiles, walkable_path_tiles, widen_path_tiles,
)
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


def choose_region_type(floor: int) -> str:
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


def settlement_size_label(size: str) -> str:
    return {
        "hamlet": "Hamlet",
        "village": "Village",
        "town": "Town",
        "large_town": "Large Town",
    }.get(size, size.replace("_", " ").title())


def choose_settlement_size(parent_biome: str, hostile: bool = False) -> str:
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
    if region_type == "stronghold":
        return Region(generate_castle(width, height), region_type, name, palette)
    if region_type in INTERIOR_REGION_TYPES:
        return Region(generate_interior(width, height, region_type), region_type, name, palette)
    return Region(Dungeon(width, height), region_type, name, palette)
