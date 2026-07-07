from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..models import RegionPalette
from ..regions import palette_for_region, settlement_size_label


class WorldMapSettlementMixin(GameMixinBase):

    def region_subtitle_text(self):
        label = self.region_display_label()
        if self.region_max_depth > 1:
            return f"{label}  Depth {self.region_depth}/{self.region_max_depth}"
        return label

    def choose_settlement_size(self, parent_biome, hostile=False):
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

    def town_palette_for_parent_biome(self, parent_biome, hostile=False):
        source = self.region_palette if parent_biome == self.region_type else self.world_palette_for_region(parent_biome)
        wall_scale = 0.78 if not hostile else 0.62
        floor_scale = 0.58 if not hostile else 0.46
        path_scale = 1.18 if not hostile else 0.88
        floor_target = (168, 130, 86) if not hostile else (120, 64, 72)
        floor_blend = 0.42 if not hostile else 0.34
        if parent_biome == "desert" and not hostile:
            wall_scale = 0.64
            floor_target = (186, 148, 98)
            floor_blend = 0.34
        return RegionPalette(
            self.scale_color(source.wall, wall_scale),
            self.blend_colors(source.floor, floor_target, floor_blend),
            self.scale_color(source.memory_wall, 0.96),
            self.scale_color(source.memory_floor, 0.92),
            self.scale_color(source.banner_fill, 0.92 if not hostile else 0.76),
            self.scale_color(source.banner_border, path_scale),
            self.scale_color(source.banner_text, 1.0),
        )

    def world_palette_for_region(self, region_type):
        return palette_for_region(region_type)

    def scale_color(self, color, factor):
        return (
            max(0, min(255, int(color[0] * factor))),
            max(0, min(255, int(color[1] * factor))),
            max(0, min(255, int(color[2] * factor))),
        )

    def blend_colors(self, left, right, ratio):
        return (
            max(0, min(255, int(left[0] * (1 - ratio) + right[0] * ratio))),
            max(0, min(255, int(left[1] * (1 - ratio) + right[1] * ratio))),
            max(0, min(255, int(left[2] * (1 - ratio) + right[2] * ratio))),
        )

    def settlement_metadata(self, state=None):
        dungeon = self.dungeon if state is None else state["dungeon"]
        return getattr(dungeon, "metadata", {})

    def settlement_parent_biome(self, state=None):
        return self.settlement_metadata(state).get("town_parent_biome")

    def settlement_label(self, state=None):
        metadata = self.settlement_metadata(state)
        size = metadata.get("settlement_size")
        label = metadata.get("settlement_label")
        return label or (settlement_size_label(size) if size else None)

    def settlement_size_rank(self, state=None):
        region_type = (state or {}).get("region_type", self.region_type)
        if region_type in ("hamlet", "waystation"):
            return 1
        size = self.settlement_metadata(state).get("settlement_size") or ""
        return {"hamlet": 1, "village": 2, "town": 3, "large_town": 4}.get(size, 0)

    def settlement_building_count(self, state=None):
        return len(self.settlement_metadata(state).get("town_buildings", []))

    def region_display_label(self, region_type=None, state=None):
        region_type = region_type or (state["region_type"] if state else self.region_type)
        if region_type == "monster_town":
            base = "Monster Town"
        else:
            base = region_type.replace("_", " ").title()
        if region_type in {"town", "monster_town"}:
            biome = self.settlement_parent_biome(state)
            label = self.settlement_label(state)
            parts = [part for part in (biome.title() if biome else None, label, base if region_type == "monster_town" else None) if part]
            if region_type == "town" and parts:
                return " ".join(parts[:2])
            if region_type == "monster_town" and parts:
                return " ".join(parts)
        return base
