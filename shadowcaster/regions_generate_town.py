from .regions import (
    settlement_size_label,
    choose_settlement_size,
)
from .regions_generate_town_helpers import (
    heuristic_city_distance,
    _setup_region_base,
    _place_houses,
)
from .regions_generate_town_civic import (
    _add_decor,
    _add_civic_features,
    _assign_buildings,
)


def town_profile(context, hostile=False):
    parent_biome = context.get("parent_biome", "plains")
    size = context.get("settlement_size") or choose_settlement_size(parent_biome, hostile=hostile)
    profiles = {
        "hamlet": {"plaza_w": 11, "plaza_h": 7, "house_divisor": 380, "min_houses": 8, "service_cap": 3, "ponds": 0},
        "village": {"plaza_w": 13, "plaza_h": 9, "house_divisor": 300, "min_houses": 10, "service_cap": 4, "ponds": 1},
        "town": {"plaza_w": 15, "plaza_h": 9, "house_divisor": 250, "min_houses": 13, "service_cap": 5, "ponds": 1},
        "large_town": {"plaza_w": 17, "plaza_h": 11, "house_divisor": 200, "min_houses": 16, "service_cap": 6, "ponds": 2},
    }
    biome_decor = {
        "forest": {"flowers": 0.18, "water": "pond", "water_bonus": 1, "path_flowers": True},
        "plains": {"flowers": 0.12, "water": "pond", "water_bonus": 0, "path_flowers": True},
        "farmland": {"flowers": 0.08, "water": "pond", "water_bonus": 0, "path_flowers": False},
        "desert": {"flowers": 0.02, "water": "well", "water_bonus": 1, "path_flowers": False},
        "swamp": {"flowers": 0.04, "water": "pond", "water_bonus": 1, "path_flowers": False},
        "mountain": {"flowers": 0.04, "water": "well", "water_bonus": 0, "path_flowers": False},
        "badlands": {"flowers": 0.02, "water": "well", "water_bonus": 0, "path_flowers": False},
        "tundra": {"flowers": 0.03, "water": "well", "water_bonus": 0, "path_flowers": False},
        "volcanic": {"flowers": 0.01, "water": "well", "water_bonus": 0, "path_flowers": False},
    }
    return {
        **profiles[size],
        "parent_biome": parent_biome,
        "settlement_size": size,
        "settlement_label": settlement_size_label(size),
        "decor": biome_decor.get(parent_biome, biome_decor["plains"]),
    }


def generate_town(width, height, context=None):
    context = context or {}
    profile = town_profile(context, hostile=False)
    plaza_w = min(profile["plaza_w"], width - 8)
    plaza_h = min(profile["plaza_h"], height - 8)
    region, plaza, north, south, west, east = _setup_region_base(width, height, profile, plaza_w, plaza_h)
    houses = _place_houses(region, profile, plaza, plaza_w, plaza_h, width, height)
    _add_decor(region, profile, plaza, north, south, west, east, width, height, plaza_w, plaza_h)
    _add_civic_features(region, profile, plaza)
    _assign_buildings(region, profile, plaza, houses)
    return region
