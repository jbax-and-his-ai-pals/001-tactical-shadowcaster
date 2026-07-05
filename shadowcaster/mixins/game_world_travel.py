from __future__ import annotations

import random

from ..constants import INTERIOR_REGION_TYPES
from ..game_typing import GameMixinBase
from ..regions import carve_path
from ..systems import flood_reachable_tiles, heuristic


class WorldTravelMixin(GameMixinBase):

    def arrival_position(self, exit_direction):
        if exit_direction not in self.edge_exits:
            return self.safe_arrival_tile(self.entrance)
        x, y = self.edge_exits[exit_direction]
        if 1 < x < self.dungeon.width - 2 and 1 < y < self.dungeon.height - 2:
            return self.safe_arrival_tile((x, y))
        inward = {
            "west": (x + 1, y),
            "east": (x - 1, y),
            "north": (x, y + 1),
            "south": (x, y - 1),
        }[exit_direction]
        if not self.dungeon.is_blocked(*inward):
            return self.safe_arrival_tile(inward)
        return self.safe_arrival_tile((x, y))

    def safe_arrival_tile(self, preferred):
        if preferred in self.floor_explorable_tiles and not self.dungeon.is_blocked(*preferred):
            return preferred
        if self.entrance in self.floor_explorable_tiles and not self.dungeon.is_blocked(*self.entrance):
            return self.entrance
        if self.floor_explorable_tiles:
            return min(self.floor_explorable_tiles, key=lambda tile: heuristic(tile, preferred))
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                if not self.dungeon.is_blocked(x, y):
                    return (x, y)
        return (1, 1)

    def region_uses_interior_world_exits(self, region_type=None):
        return (region_type or self.region_type) in {"dungeon", "cave", "monster_town", "ruins", "castle", "maze", "stronghold"}

    def reveal_adjacent_world_regions(self):
        return self.reveal_adjacent_world_regions_from(self.world_position)

    def reveal_adjacent_world_regions_from(self, from_coord):
        revealed = []
        for direction in ("north", "south", "west", "east"):
            coord = self.move_coord(from_coord, direction)
            key = self.region_key(coord)
            if key in self.world_regions:
                continue
            self.world_regions[key] = self.create_world_region_state(coord)
            revealed.append((coord, self.world_regions[key]["region_name"]))
        return revealed

    def create_world_region_state(self, coord):
        current_coord = self.world_position
        current_local = self.current_local_region
        current_state = self.snapshot_current_region()
        overlay_state = {
            "world_map_open": self.world_map_open,
            "world_map_mode": self.world_map_mode,
            "selected_world_region": self.selected_world_region,
            "hovered_world_region": self.hovered_world_region,
            "world_map_view_center": self.world_map_view_center,
            "world_map_detail_scroll": self.world_map_detail_scroll,
            "menu_mode": self.menu_mode,
        }
        chosen_region = self.choose_connected_region(coord)
        self.world_position = coord
        self.current_local_region = None
        with self.seed_scope("build_floor", ("world", coord), self.floor):
            self.build_floor(chosen_region=chosen_region, world_coord=coord)
        new_state = self.snapshot_current_region()
        # World-map previews should not reveal tiles before the player actually arrives.
        new_state["seen_tiles"] = set()
        new_state["preview_generated"] = True
        self.world_position = current_coord
        self.current_local_region = current_local
        self.load_region_state(current_state)
        self.world_map_open = overlay_state["world_map_open"]
        self.world_map_mode = overlay_state["world_map_mode"]
        self.selected_world_region = overlay_state["selected_world_region"]
        self.hovered_world_region = overlay_state["hovered_world_region"]
        self.world_map_view_center = overlay_state["world_map_view_center"]
        self.world_map_detail_scroll = overlay_state["world_map_detail_scroll"]
        self.menu_mode = overlay_state["menu_mode"]
        return new_state

    def leave_local_region(self):
        if not self.in_local_region():
            return
        self.store_current_region()
        parent_local_key = self.parent_local_region_key()
        if parent_local_key and parent_local_key in self.local_regions:
            self.current_local_region = parent_local_key
            self.load_region_state(self.local_regions[parent_local_key])
        else:
            self.current_local_region = None
            parent_key = self.region_key(self.world_position)
            self.load_region_state(self.world_regions[parent_key])
        self.message = f"You return to {self.region_name}."

    def initial_local_entry_tile(self):
        if not self.edge_exits:
            return self.entrance
        return min(self.edge_exits.values(), key=lambda tile: heuristic(tile, self.entrance))

    def normalize_edge_exits(self, exits):
        if not exits:
            return exits
        if self.in_local_region() and self.region_depth == 1:
            tile = min(exits.values(), key=lambda candidate: heuristic(candidate, self.entrance))
            return {"south": tile}
        return exits

    def edge_exit_candidates(self, direction):
        middle_y = self.dungeon.height // 2
        middle_x = self.dungeon.width // 2
        if direction in ("west", "east"):
            ys = sorted(range(2, self.dungeon.height - 2), key=lambda value: abs(value - middle_y))
            outer_x = 1 if direction == "west" else self.dungeon.width - 2
            inner_x = 2 if direction == "west" else self.dungeon.width - 3
            return [((outer_x, y), (inner_x, y)) for y in ys]
        xs = sorted(range(2, self.dungeon.width - 2), key=lambda value: abs(value - middle_x))
        outer_y = 1 if direction == "north" else self.dungeon.height - 2
        inner_y = 2 if direction == "north" else self.dungeon.height - 3
        return [((x, outer_y), (x, inner_y)) for x in xs]

    def carve_edge_exit(self, direction):
        outer_tile, inner_tile = self.edge_exit_candidates(direction)[0]
        self.dungeon.tiles[outer_tile[0]][outer_tile[1]] = 0
        self.dungeon.tiles[inner_tile[0]][inner_tile[1]] = 0
        if inner_tile not in self.floor_explorable_tiles:
            nearest = min(self.floor_explorable_tiles, key=lambda tile: heuristic(tile, inner_tile), default=self.player)
            carve_path(self.dungeon, inner_tile, nearest, width=1)
        self.floor_explorable_tiles |= flood_reachable_tiles(self.dungeon, self.player)
        return outer_tile

    def place_interior_world_exit(self, reserved_tiles):
        candidates = [tile for tile in self.floor_explorable_tiles if tile not in reserved_tiles]
        if not candidates:
            return self.entrance
        room_centers = [room.center for room in self.dungeon.rooms if room.center in self.floor_explorable_tiles and room.center not in reserved_tiles]
        origin = self.player
        reference = [self.stairs, *reserved_tiles]

        def score(tile):
            spacing = min((heuristic(tile, other) for other in reference if other is not None), default=0)
            distance_from_origin = heuristic(tile, origin)
            return (spacing, distance_from_origin, random.random())

        pool = room_centers or candidates
        return max(pool, key=score)

    def generate_edge_exits(self):
        if not self.region_is_connected():
            return {}
        if self.in_local_region() and self.region_depth == 1:
            if self.region_type == "town":
                return {"south": self.carve_edge_exit("south")}
            if self.region_type in INTERIOR_REGION_TYPES:
                exit_tile = getattr(self.dungeon, "metadata", {}).get("interior_exit")
                if exit_tile:
                    return {"south": exit_tile}
            return {"south": self.place_interior_world_exit({self.player, self.stairs, self.up_stairs})}
        exits = {}
        if self.region_uses_interior_world_exits():
            reserved = {self.player, self.stairs}
            for direction in ("north", "south", "west", "east"):
                exit_tile = self.place_interior_world_exit(reserved)
                exits[direction] = exit_tile
                reserved.add(exit_tile)
            return exits
        for direction in ("north", "south", "west", "east"):
            exits[direction] = self.carve_edge_exit(direction)
        return exits

    def generate_world_region(self, coord):
        self.world_position = coord
        self.current_local_region = None
        key = self.region_key(coord)
        if key in self.preview_world_regions:
            self.world_regions[key] = self.preview_world_regions.pop(key)
            return
        chosen_region = self.choose_connected_region(coord)
        with self.seed_scope("build_floor", ("world", coord), self.floor):
            self.build_floor(chosen_region=chosen_region, world_coord=coord)
        self.seen_tiles = set()
        self.store_current_region()

    def _level5_gate_message(self, target_coord) -> str | None:
        """Return a gate message if the player can't enter the target coord, or None if allowed."""
        level = getattr(self, "player_level", 1)
        if level >= 5:
            return None
        city = getattr(self, "world_city", {})
        district_type = city.get("districts", {}).get(target_coord)
        if district_type == "stronghold":
            return "The stronghold gates are sealed. Only a Master-rank traveler may enter."
        target_key = self.region_key(target_coord)
        known_type = (
            self.world_regions.get(target_key, {}).get("region_type")
            or self.preview_world_regions.get(target_key, {}).get("region_type")
        )
        if known_type in ("ossuary", "mirrorwood"):
            label = "Ossuary" if known_type == "ossuary" else "Mirrorwood"
            return f"The {label} resists your presence. Reach Master rank before you enter."
        return None

    def transition_to_world_region(self, direction):
        target_coord = self.move_coord(self.world_position, direction)
        if self.is_ocean_coord(target_coord):
            sea_name = self.world_coast.get("name", "the sea")
            self.message = f"{sea_name.capitalize()} lies beyond — the waters are impassable."
            return
        gate_msg = self._level5_gate_message(target_coord)
        if gate_msg:
            self.message = gate_msg
            return
        self.store_current_region()
        target_key = self.region_key(target_coord)
        if target_key not in self.world_regions:
            self.generate_world_region(target_coord)
        # Re-check after generation (region type now known)
        gate_msg = self._level5_gate_message(target_coord)
        if gate_msg:
            self.load_region_state(self.world_regions[self.region_key(self.world_position)])
            self.message = gate_msg
            return
        self.world_position = target_coord
        self.load_region_state(self.world_regions[target_key], arrival_direction=self.opposite_direction(direction))
        self.message = f"You cross into {self.region_name}."
