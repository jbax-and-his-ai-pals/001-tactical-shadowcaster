from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..systems import heuristic


class TownsRevealMixin(GameMixinBase):

    def reveal_one_adjacent_world_region(self):
        candidates = []
        for direction in ("north", "south", "west", "east"):
            coord = self.move_coord(self.world_position, direction)
            key = self.region_key(coord)
            if key in self.world_regions:
                continue
            candidates.append(coord)
        if not candidates:
            return None
        with self.seed_scope("scout_reveal", self.world_position, tuple(sorted(candidates))):
            coord = random.choice(candidates)
        state = self.create_world_region_state(coord)
        self.world_regions[self.region_key(coord)] = state
        return coord, state["region_name"]

    def _reveal_distant_world_region(self):
        candidates = []
        for direction in ("north", "south", "west", "east"):
            step1 = self.move_coord(self.world_position, direction)
            step2 = self.move_coord(step1, direction)
            key = self.region_key(step2)
            if key not in self.world_regions:
                candidates.append(step2)
        if not candidates:
            for direction in ("north", "south", "west", "east"):
                coord = self.move_coord(self.world_position, direction)
                key = self.region_key(coord)
                if key not in self.world_regions:
                    candidates.append(coord)
        if not candidates:
            return None
        with self.seed_scope("wanderer_reveal", self.world_position, tuple(sorted(candidates))):
            coord = random.choice(candidates)
        state = self.create_world_region_state(coord)
        self.world_regions[self.region_key(coord)] = state
        return coord, state["region_name"]

    def reveal_one_hidden_town_building(self):
        hidden_buildings = [
            building
            for building in self.town_building_data()
            if building.get("door") not in self.seen_tiles
        ]
        if not hidden_buildings:
            return None
        building = min(
            hidden_buildings,
            key=lambda entry: heuristic(self.player, entry.get("door") or entry.get("center") or self.player),
        )
        door = building.get("door")
        center = building.get("center")
        if door is not None:
            self.seen_tiles.add(door)
        if center is not None:
            self.seen_tiles.add(center)
        return building

    def reveal_one_town_exit(self):
        hidden_exits = [tile for tile in self.edge_exits.values() if tile is not None and tile not in self.seen_tiles]
        if not hidden_exits:
            return None
        exit_tile = min(hidden_exits, key=lambda tile: heuristic(self.player, tile))
        self.seen_tiles.add(exit_tile)
        return exit_tile
