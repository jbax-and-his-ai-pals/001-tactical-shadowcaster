from __future__ import annotations
import hashlib
import math
import random
from contextlib import contextmanager
from typing import Any, cast
import pygame
from ..config import DEFAULT_WORLD_SEED
from ..constants import (
    COLOR_ACCENT, COLOR_ENEMY, COLOR_FRIEND, COLOR_HEAL, COLOR_ITEM_ARMOR,
    COLOR_ITEM_CONSUMABLE, COLOR_ITEM_WEAPON, COLOR_MEMORY_HEAL, COLOR_STAIRS,
    COLOR_TEXT, FLOOR_BASE_HEIGHT, FLOOR_BASE_WIDTH, FOV_RADIUS,
    SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT, VIEW_WIDTH,
)
from ..models import Enemy, GroundItem, Item, Landmark, RegionPalette, Resident, UpgradePickup
from ..persistence import has_save, list_saves, load_game, save_game
from ..regions import RegionChoice, carve_path, generate_region, palette_for_region, random_region_name, settlement_size_label
from ..systems import can_step, direction_toward, find_path, flood_reachable_tiles, heuristic
from ..game_typing import GameMixinBase, RegionMapLike


class WorldMixin(GameMixinBase):
    def region_key(self, coord):
        return f"{coord[0]},{coord[1]}"

    def overworld_region_types(self):
        return {"forest", "desert", "swamp", "plains", "mountain", "farmland", "badlands", "tundra", "volcanic"}

    def connected_region_types(self):
        return self.overworld_region_types()

    def multilevel_region_types(self):
        return {"dungeon", "cave", "monster_town", "ruins"}

    def landmark_region_types(self):
        return {"dungeon", "cave", "castle", "town", "ruins", "monster_town"}

    def exploration_rewards_enabled(self, region_type=None):
        return (region_type or self.region_type) not in {"inn", "clinic", "supply", "shrine", "smith", "cartographer", "tavern", "chapel", "stable"}

    def is_overworld_region(self, region_type=None):
        return (region_type or self.region_type) in self.overworld_region_types()

    def in_local_region(self):
        return self.current_local_region is not None

    def region_is_multilevel(self, region_type=None):
        return (region_type or self.region_type) in self.multilevel_region_types()

    def choose_start_region(self):
        with self.seed_scope("start_region"):
            region_type = "town"
            return RegionChoice(region_type=region_type, name=random_region_name(region_type), summary="")

    def new_run_seed(self):
        if self.config_world_seed is not None:
            return self.config_world_seed
        return random.SystemRandom().randrange(1, 2**63)

    def world_seed_label(self):
        return str(self.world_seed)

    def seed_value(self, *parts):
        payload = repr((self.world_seed, parts)).encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        return int.from_bytes(digest[:8], "big", signed=False)

    @contextmanager
    def seed_scope(self, *parts):
        state = random.getstate()
        random.seed(self.seed_value(*parts))
        try:
            yield
        finally:
            random.setstate(state)

    def overworld_region_weight(self, region_type, coord):
        distance = abs(coord[0]) + abs(coord[1])
        progress = min(1.0, distance / 10.0)
        near_far_weights = {
            "plains": (6.0, 2.0),
            "farmland": (5.0, 1.5),
            "forest": (4.5, 2.5),
            "desert": (2.0, 3.0),
            "swamp": (1.6, 3.2),
            "mountain": (1.2, 3.4),
            "tundra": (0.9, 3.3),
            "badlands": (0.45, 4.2),
            "volcanic": (0.15, 5.0),
        }
        near_weight, far_weight = near_far_weights.get(region_type, (1.0, 1.0))
        return near_weight + (far_weight - near_weight) * progress

    def debug_biome_hotkeys(self):
        return {
            pygame.K_F1: "swamp",
            pygame.K_F2: "forest",
            pygame.K_F3: "plains",
            pygame.K_F4: "farmland",
            pygame.K_F5: "desert",
            pygame.K_F6: "mountain",
            pygame.K_F7: "badlands",
            pygame.K_F8: "tundra",
            pygame.K_F9: "volcanic",
        }

    def debug_jump_to_biome(self, region_type):
        if self.active_overlay():
            return
        self.stop_auto_movement()
        if self.in_local_region():
            self.current_local_region = None
        with self.seed_scope("debug_jump", self.world_position, region_type):
            chosen = RegionChoice(region_type=region_type, name=random_region_name(region_type), summary="")
        with self.seed_scope("build_floor", ("world", self.world_position), self.floor):
            self.build_floor(chosen_region=chosen, world_coord=self.world_position)
        self.store_current_region()
        self.message = f"Debug jump: {self.region_name} [{region_type.title()}]."

    def choose_delve_depth(self, region_type):
        depth_ranges = {
            "dungeon": (2, 5),
            "cave": (2, 4),
            "monster_town": (2, 3),
            "ruins": (2, 4),
        }
        minimum, maximum = depth_ranges.get(region_type, (1, 1))
        return random.randint(minimum, maximum)

    def overworld_distance_tier(self, coord):
        return 1 + (abs(coord[0]) + abs(coord[1])) // 2

    def danger_offset_for_region(self, region_type):
        return {
            "forest": 0,
            "plains": 0,
            "farmland": 0,
            "desert": 1,
            "swamp": 1,
            "mountain": 1,
            "badlands": 1,
            "tundra": 1,
            "volcanic": 2,
            "town": 0,
            "inn": 0,
            "clinic": 0,
            "supply": 0,
            "shrine": 0,
            "smith": 0,
            "cartographer": 0,
            "cave": 1,
            "ruins": 1,
            "castle": 2,
            "dungeon": 2,
            "monster_town": 2,
            "maze": 2,
        }.get(region_type, 0)

    def assign_region_danger(self, coord=None, region_type=None, parent_tier=None, depth=1):
        region_type = region_type or self.region_type
        player_tier = self.player_strength_rating()
        if parent_tier is not None:
            tier = parent_tier + self.danger_offset_for_region(region_type) + max(0, depth - 1)
        else:
            baseline = self.overworld_distance_tier(coord or self.world_position)
            tier = baseline + max(0, player_tier - baseline) // 2 + self.danger_offset_for_region(region_type)
        self.danger_tier = max(1, tier)
        self.danger_floor = max(self.floor, self.danger_tier)

    def danger_value(self):
        return max(self.danger_floor, self.danger_tier + self.region_depth - 1)

    def region_is_connected(self, region_type=None):
        region_type = region_type or self.region_type
        if self.in_local_region():
            return self.region_depth == 1
        return region_type in self.connected_region_types()

    def opposite_direction(self, direction):
        return {"north": "south", "south": "north", "west": "east", "east": "west"}[direction]

    def move_coord(self, coord, direction):
        dx, dy = self.DIRECTION_VECTORS[direction]
        return (coord[0] + dx, coord[1] + dy)

    def display_region_coords(self):
        return (self.world_position[0], -self.world_position[1])

    def is_bottom_floor(self):
        return self.region_is_multilevel() and self.region_depth == self.region_max_depth

    def toggle_world_map(self):
        active_overlay = self.active_overlay()
        if active_overlay not in {None, "world_map"}:
            return
        self.world_map_open = not self.world_map_open
        self.prepare_overlay_toggle(opening=self.world_map_open, stop_auto=True, clear_manual=False)
        if self.world_map_open:
            self.world_map_mode = "discovered"
            self.selected_world_region = self.world_position
            self.world_map_detail_scroll = 0
            self.set_world_map_center(self.world_position)
            self.hovered_world_region = self.world_position
            self.update_world_map_hover(*self.mouse_screen_pos)
        else:
            self.hovered_world_region = None
            self.world_map_view_center = None
            self.world_map_dragging = False
            self.world_map_center_animation = None
            self.preview_generation_queue = []
            self.preview_generation_keys.clear()
            self.local_debug_target_coords = set()
        self.message = "World map open." if self.world_map_open else f"You return to {self.region_name}."

    def clear_player_status(self, effect):
        self.player_statuses.pop(effect, None)
        self.player_status_sources.pop(effect, None)

    def set_player_status_source(self, effect, source):
        if effect and source:
            self.player_status_sources[effect] = source

    def choose_connected_region(self, coord=None):
        coord = coord or self.world_position
        with self.seed_scope("world_choice", coord):
            region_types = sorted(self.overworld_region_types())
            weights = [self.overworld_region_weight(region_type, coord) for region_type in region_types]
            region_type = random.choices(region_types, weights=weights, k=1)[0]
            return RegionChoice(region_type=region_type, name=random_region_name(region_type), summary="")
