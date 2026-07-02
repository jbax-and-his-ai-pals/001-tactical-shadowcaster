from __future__ import annotations

import random
from typing import cast

from ..constants import FLOOR_BASE_HEIGHT, FLOOR_BASE_WIDTH
from ..game_typing import GameMixinBase, RegionMapLike
from ..regions import generate_region
from ..systems import flood_reachable_tiles, heuristic


class FloorGenerationMixin(GameMixinBase):

    def region_rules(self):
        rules = {
            "ranged_bonus": 0,
            "player_on_enter_heal": 0,
            "enemy_on_hit_effect": None,
            "enemy_health_bonus": 0,
            "enemy_damage_bonus": 0,
        }
        if self.region_type == "desert":
            rules["ranged_bonus"] = 1
        elif self.region_type == "badlands":
            rules["ranged_bonus"] = 1
        elif self.region_type == "swamp":
            rules["enemy_on_hit_effect"] = "poison"
        elif self.region_type == "mountain":
            rules["enemy_health_bonus"] = 1
        elif self.region_type == "tundra":
            rules["enemy_health_bonus"] = 1
        elif self.region_type == "castle":
            rules["enemy_health_bonus"] = 1
            rules["enemy_damage_bonus"] = 1
        elif self.region_type == "volcanic":
            rules["enemy_on_hit_effect"] = "burn"
            rules["enemy_damage_bonus"] = 1
        elif self.region_type == "town":
            rules["player_on_enter_heal"] = 2
        elif self.region_type == "monster_town":
            rules["enemy_on_hit_effect"] = "burn"
        pressure = max(0, self.danger_value() - 3)
        if pressure >= 2:
            rules["enemy_health_bonus"] += pressure // 2
        if pressure >= 4:
            rules["enemy_damage_bonus"] += 1 + (pressure - 4) // 4
        return rules

    def build_floor(
        self,
        first_floor=False,
        chosen_region=None,
        delve_depth=None,
        delve_max_depth=None,
        world_coord=None,
        parent_danger_tier=None,
        fixed_danger_tier=None,
    ):
        floor_width = FLOOR_BASE_WIDTH + ((self.floor - 1) // 2) * 6
        floor_height = FLOOR_BASE_HEIGHT + ((self.floor - 1) // 2) * 4
        region = generate_region(
            self.floor,
            floor_width,
            floor_height,
            region_type=chosen_region.region_type if chosen_region else None,
            name=chosen_region.name if chosen_region else None,
            context=chosen_region.context if chosen_region else None,
        )
        self.dungeon = cast(RegionMapLike, region.map_data)
        self.region_type = region.region_type
        self.region_name = region.name
        self.region_palette = region.palette
        if self.region_type in {"town", "monster_town"}:
            parent_biome = getattr(self.dungeon, "metadata", {}).get("town_parent_biome")
            if parent_biome:
                self.region_palette = self.town_palette_for_parent_biome(parent_biome, hostile=self.region_type == "monster_town")
        self.service_type = self.region_type if self.region_type in {"inn", "clinic", "supply", "shrine", "smith", "cartographer"} else None
        self.service_claimed = False
        self.interaction_claims = set()
        if self.region_is_multilevel(region.region_type):
            self.region_depth = delve_depth if delve_depth is not None else 1
            self.region_max_depth = delve_max_depth if delve_max_depth is not None else self.choose_delve_depth(region.region_type)
        else:
            self.region_depth = 1
            self.region_max_depth = 1
        if fixed_danger_tier is not None:
            self.danger_tier = max(1, fixed_danger_tier)
            self.danger_floor = max(self.floor, self.danger_tier)
        else:
            self.assign_region_danger(
                coord=world_coord if world_coord is not None else self.world_position,
                region_type=self.region_type,
                parent_tier=parent_danger_tier,
                depth=self.region_depth,
            )
        self.bottom_reward_claimed = False if self.region_depth < self.region_max_depth else self.bottom_reward_claimed
        self.rules = self.region_rules()
        self.travel_mode = False
        self.travel_choices = []
        self.exploration_milestones = [100] if self.exploration_rewards_enabled(region.region_type) else []
        self.claimed_exploration_rewards = set()
        self.exploration_progress = 0
        self.exploration_reward_pending = None
        self.delve_reward_pending = False
        self.completion_modal_until = 0
        self.completion_modal_started = 0
        self.completion_modal_text = ""
        self.enemies_defeated = 0
        self.enemies_spawned = 0
        self.entrance, stairs = self.choose_floor_endpoints()
        self.up_stairs = None
        self.delve_goal = stairs if self.is_bottom_floor() else None
        self.return_portal = self.delve_goal if self.is_bottom_floor() else None
        self.stairs = stairs if self.region_is_multilevel() and self.region_depth < self.region_max_depth else None
        self.player = self.entrance
        self.floor_explorable_tiles: set[tuple[int, int]] = flood_reachable_tiles(self.dungeon, self.player)
        self.facing = (1, 0)
        self.attack_flash = None
        self.shot_flash = []
        self.seen_tiles = set()
        self.edge_exits = self.generate_edge_exits()
        if self.region_is_multilevel() and self.region_depth > 1:
            self.up_stairs = self.initial_local_entry_tile()
        self.terrain_features = self.generate_terrain_features()
        self.sync_vision_transparency()
        interior_regions = {"inn", "clinic", "supply", "shrine", "smith", "cartographer"}
        pickups_enabled = self.region_type not in interior_regions
        self.upgrade_pickup = None
        if pickups_enabled and not self.is_bottom_floor():
            self.upgrade_pickup = self.create_upgrade_pickup(exclude={self.player, self.stairs, self.up_stairs, self.delve_goal})
        self.heal_pickup = None
        if not pickups_enabled or self.is_bottom_floor():
            self.heal_pickup = None
        elif self.floor % self.tuning["heal_pickup_floor_interval"] == 0 and (
            not self.tuning["heal_pickup_require_missing_hp"] or self.health < self.max_health
        ):
            self.heal_pickup = self.place_feature(exclude={self.player, self.stairs, self.up_stairs, self.upgrade_pickup.position if self.upgrade_pickup else None, self.delve_goal})
        self.landmarks = self.generate_landmarks()
        self.floor_items = self.generate_floor_items(pickups_enabled)
        self.auto_move_path = []
        self.residents = []
        self.spawn_enemies()
        self.spawn_residents()
        if self.rules["player_on_enter_heal"]:
            self.health = min(self.max_health, self.health + self.rules["player_on_enter_heal"])
        self.update_visibility()
        self.last_interest_tiles = self.visible_interest_tiles()
        self.update_camera()
        if not first_floor:
            if self.region_is_multilevel():
                self.message = f"You enter {self.region_name}, depth {self.region_depth}/{self.region_max_depth}."
            else:
                self.message = f"You enter {self.region_name}."

    def choose_floor_endpoints(self):
        room_centers = [room.center for room in self.dungeon.rooms if not self.dungeon.is_blocked(*room.center)]
        walkable_tiles = [(x, y) for x in range(self.dungeon.width) for y in range(self.dungeon.height) if self.dungeon.tiles[x][y] == 0]
        if not walkable_tiles:
            return (1, 1), (1, 1)
        connected = list(self.largest_walkable_component(walkable_tiles))
        candidate_tiles = [center for center in room_centers if center in connected] or connected
        if len(candidate_tiles) == 1:
            return candidate_tiles[0], candidate_tiles[0]
        best_pair = None
        best_distance = -1
        sample = candidate_tiles if len(candidate_tiles) <= 24 else random.sample(candidate_tiles, 24)
        target_distance = (self.dungeon.width + self.dungeon.height) // 3
        for start in sample:
            for end in sample:
                if start == end:
                    continue
                distance = heuristic(start, end)
                if distance > best_distance:
                    best_pair = (start, end)
                    best_distance = distance
                if distance >= target_distance:
                    return start, end
        return best_pair if best_pair else (candidate_tiles[0], candidate_tiles[-1])

    def largest_walkable_component(self, walkable_tiles=None):
        walkable_tiles = walkable_tiles or [
            (x, y)
            for x in range(self.dungeon.width)
            for y in range(self.dungeon.height)
            if self.dungeon.tiles[x][y] == 0
        ]
        remaining = set(walkable_tiles)
        largest = set()
        while remaining:
            seed = next(iter(remaining))
            component = flood_reachable_tiles(self.dungeon, seed)
            if len(component) > len(largest):
                largest = component
            remaining.difference_update(component)
        return largest

    def reserved_special_tiles(self, include_units=False):
        reserved = {self.player, self.entrance, self.up_stairs, self.stairs, self.delve_goal, self.return_portal}
        reserved.update(getattr(self, "edge_exits", {}).values())
        upgrade_pickup = getattr(self, "upgrade_pickup", None)
        if upgrade_pickup is not None:
            reserved.add(upgrade_pickup.position)
        if getattr(self, "heal_pickup", None):
            reserved.add(self.heal_pickup)
        reserved.update(ground_item.position for ground_item in getattr(self, "floor_items", []))
        reserved.update(getattr(self, "terrain_features", {}).keys())
        for tiles in self.feature_footprints().values():
            reserved.update(tiles)
        reserved.update(landmark.position for landmark in getattr(self, "landmarks", []))
        if include_units:
            reserved.update(enemy.position for enemy in getattr(self, "enemies", []))
            reserved.update(resident.position for resident in getattr(self, "residents", []))
        return {tile for tile in reserved if tile is not None}

    def place_feature(self, exclude=None, prefer_last=False):
        exclude = set(exclude or set()) | self.reserved_special_tiles(include_units=True)
        rooms = self.dungeon.rooms[::-1] if prefer_last else self.dungeon.rooms[1:] or self.dungeon.rooms
        for room in rooms:
            if room.center in self.floor_explorable_tiles and room.center not in exclude:
                return room.center
        for tile in self.floor_explorable_tiles:
            if tile not in exclude:
                return tile
        return self.player
