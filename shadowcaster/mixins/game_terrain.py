from __future__ import annotations

import random

from ..constants import (
    COLOR_TERRAIN_CROP,
    COLOR_TERRAIN_DEADBRUSH,
    COLOR_TERRAIN_DUNE,
    COLOR_TERRAIN_FALLOW,
    COLOR_TERRAIN_FENCE,
    COLOR_TERRAIN_FLOWERS,
    COLOR_TERRAIN_FROST,
    COLOR_TERRAIN_HAYSTACK,
    COLOR_TERRAIN_NOTICE,
    COLOR_TERRAIN_SHRUB,
    COLOR_TERRAIN_TREE,
    COLOR_TERRAIN_WHEAT,
)
from ..game_typing import GameMixinBase


class TerrainMixin(GameMixinBase):

    def terrain_candidates(self):
        blocked = self.reserved_special_tiles(include_units=False)
        return [tile for tile in self.floor_explorable_tiles if tile not in blocked]

    def sync_vision_transparency(self):
        self.dungeon.transparent_tiles = {
            position
            for position, kind in getattr(self, "terrain_features", {}).items()
            if kind.startswith(("bog", "mesa", "lavafield", "cliff")) or kind == "pond"
        }

    def generate_terrain_features(self):
        features = dict(getattr(self.dungeon, "metadata", {}).get("decor", {}))
        for tile in getattr(self.dungeon, "metadata", {}).get("town_paths", set()):
            if self.dungeon.tiles[tile[0]][tile[1]] == 0 and tile not in features:
                features[tile] = "path"
        if self.region_type == "swamp":
            opaque_tiles = set(getattr(self.dungeon, "metadata", {}).get("opaque_tiles", set()))
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 1:
                        continue
                    if (x, y) in opaque_tiles:
                        continue
                    roll = random.random()
                    if roll < 0.12:
                        features[(x, y)] = "bog_cypress"
                    elif roll < 0.38:
                        features[(x, y)] = "bog_reeds"
                    else:
                        features[(x, y)] = "bog"
        elif self.region_type == "mountain":
            opaque_tiles = set(getattr(self.dungeon, "metadata", {}).get("opaque_tiles", set()))
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 1:
                        continue
                    if (x, y) in opaque_tiles:
                        continue
                    features[(x, y)] = "cliff_pine" if random.random() < 0.22 else "cliff"
        elif self.region_type == "badlands":
            opaque_tiles = set(getattr(self.dungeon, "metadata", {}).get("opaque_tiles", set()))
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 1:
                        continue
                    if (x, y) in opaque_tiles:
                        continue
                    features[(x, y)] = "mesa_scrub" if random.random() < 0.3 else "mesa"
        elif self.region_type == "volcanic":
            opaque_tiles = set(getattr(self.dungeon, "metadata", {}).get("opaque_tiles", set()))
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 1:
                        continue
                    if (x, y) in opaque_tiles:
                        continue
                    features[(x, y)] = "lavafield_obsidian" if random.random() < 0.24 else "lavafield"
        elif self.region_type == "plains":
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 0:
                        continue
                    roll = random.random()
                    if roll < 0.04:
                        features[(x, y)] = "shrub"
                    elif roll < 0.07:
                        features[(x, y)] = "flowers"
        elif self.region_type == "desert":
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 1:
                        continue
                    roll = random.random()
                    if roll < 0.25:
                        features[(x, y)] = "deadbrush"
                    elif roll < 0.55:
                        features[(x, y)] = "dune"
        elif self.region_type == "tundra":
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    if self.dungeon.tiles[x][y] != 1:
                        continue
                    features[(x, y)] = "frost" if random.random() < 0.45 else features.get((x, y), "frost")
        elif self.region_type == "forest":
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    tile = self.dungeon.tiles[x][y]
                    roll = random.random()
                    if tile == 1:
                        features[(x, y)] = "tree" if roll < 0.6 else "shrub"
                    elif tile == 0 and roll < 0.05:
                        features[(x, y)] = "flowers"
                    elif tile == 0 and roll < 0.09:
                        features[(x, y)] = "shrub"
        elif self.region_type == "ruins":
            for x in range(1, self.dungeon.width - 1):
                for y in range(1, self.dungeon.height - 1):
                    tile = self.dungeon.tiles[x][y]
                    roll = random.random()
                    if tile == 1 and roll < 0.18:
                        features[(x, y)] = "deadbrush" if roll < 0.10 else "shrub"
                    elif tile == 0 and roll < 0.04:
                        features[(x, y)] = "shrub"
        candidates = self.terrain_candidates()
        if not candidates:
            return features
        random.shuffle(candidates)
        feature_count = min(12, max(3, len(candidates) // 120))
        feature_type = None
        if self.region_type == "swamp":
            feature_type = "muck"
        elif self.region_type in {"desert", "volcanic"}:
            feature_type = "embers"
        elif self.region_type in {"mountain", "badlands", "tundra"}:
            feature_type = "high_ground"
        elif self.region_type == "town":
            feature_type = "well"
        if feature_type:
            for tile in candidates[:feature_count]:
                features[tile] = feature_type
        return features
