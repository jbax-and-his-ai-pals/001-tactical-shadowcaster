from __future__ import annotations

from ..game_typing import GameMixinBase
from ..regions import palette_for_region
from ..systems import heuristic


class WorldMapPreviewMixin(GameMixinBase):

    def parse_region_key(self, region_key):
        x_text, y_text = region_key.split(",", 1)
        return (int(x_text), int(y_text))

    def discovered_world_regions(self):
        regions = dict(self.world_regions)
        current_key = self.region_key(self.world_position)
        if current_key not in regions:
            regions[current_key] = self.snapshot_current_region()
        return {self.parse_region_key(key): value for key, value in regions.items()}

    def world_map_regions(self):
        if self.world_map_mode == "local_debug":
            return self.local_debug_world_regions()
        return self.discovered_world_regions()

    def preview_placeholder_state(self, coord, expandable=False):
        return {
            "region_name": f"{'Expand survey' if expandable else 'Surveying'} {coord[0]}, {coord[1]}",
            "region_type": "plains",
            "region_palette": palette_for_region("plains"),
            "danger_tier": 1,
            "edge_exits": {},
            "landmarks": [],
            "enemies": [],
            "residents": [],
            "claimed_exploration_rewards": set(),
            "seen_tiles": set(),
            "region_depth": 1,
            "region_max_depth": 1,
            "loading_preview": not expandable,
            "expandable_preview": expandable,
        }

    def local_debug_core_coords(self, center=None):
        center = center or self.world_position
        return {(center[0] + dx, center[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3)}

    def seed_local_debug_targets(self, reset=False):
        if reset or not self.local_debug_target_coords:
            self.local_debug_target_coords = set(self.local_debug_core_coords())

    def local_debug_expandable_coords(self):
        frontier = set()
        for coord in self.local_debug_target_coords:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (coord[0] + dx, coord[1] + dy)
                    if neighbor in self.local_debug_target_coords:
                        continue
                    frontier.add(neighbor)
        return frontier

    def refresh_preview_generation_queue(self, desired_coords):
        center = self.hovered_world_region or self.selected_world_region or self.world_position
        desired_keys = []
        for coord in desired_coords:
            key = self.region_key(coord)
            if key in self.world_regions or key in self.preview_world_regions or key in self.preview_generation_keys:
                continue
            desired_keys.append((heuristic(coord, center), key, coord))
        desired_keys.sort(key=lambda item: (item[0], item[2][1], item[2][0]))
        for _, key, coord in desired_keys:
            self.preview_generation_queue.append(coord)
            self.preview_generation_keys.add(key)

    def process_preview_generation(self, budget=1):
        generated = 0
        while generated < budget and self.preview_generation_queue:
            coord = self.preview_generation_queue.pop(0)
            key = self.region_key(coord)
            self.preview_generation_keys.discard(key)
            if key in self.world_regions or key in self.preview_world_regions:
                continue
            self.preview_world_regions[key] = self.create_world_region_state(coord)
            generated += 1

    def local_debug_world_regions(self):
        regions = {}
        self.seed_local_debug_targets()
        desired_coords = sorted(self.local_debug_target_coords)
        frontier_coords = sorted(self.local_debug_expandable_coords())
        current_snapshot = self.snapshot_current_region() if self.in_local_region() else self.discovered_world_regions()[self.world_position]
        for coord in desired_coords:
            if coord == self.world_position:
                regions[coord] = current_snapshot
                continue
            key = self.region_key(coord)
            if key in self.world_regions:
                regions[coord] = self.world_regions[key]
            elif key in self.preview_world_regions:
                regions[coord] = self.preview_world_regions[key]
            else:
                regions[coord] = self.preview_placeholder_state(coord)
        for coord in frontier_coords:
            if coord in regions:
                continue
            key = self.region_key(coord)
            if key in self.world_regions:
                regions[coord] = self.world_regions[key]
            elif key in self.preview_world_regions:
                regions[coord] = self.preview_world_regions[key]
            else:
                regions[coord] = self.preview_placeholder_state(coord, expandable=True)
        self.refresh_preview_generation_queue(desired_coords)
        return regions

    def expand_local_debug_region(self, coord):
        if coord in self.local_debug_target_coords:
            return
        self.local_debug_target_coords.add(coord)
        self.hovered_world_region = coord
        self.selected_world_region = coord
        self.world_map_detail_scroll = 0
        self.refresh_preview_generation_queue([coord])
        self.process_preview_generation(budget=1)
        self.message = f"Survey expands toward {coord[0]}, {coord[1]}."

    def toggle_world_map_mode(self):
        if not self.world_map_open:
            return
        self.world_map_mode = "local_debug" if self.world_map_mode == "discovered" else "discovered"
        selectable = self.world_map_regions()
        if self.selected_world_region not in selectable:
            self.selected_world_region = self.world_position
        if self.hovered_world_region not in selectable:
            self.hovered_world_region = None
        self.world_map_detail_scroll = 0
        if self.world_map_view_center is None:
            self.set_world_map_center(self.selected_world_region or self.world_position)
        self.world_map_center_animation = None
        if self.world_map_mode == "local_debug":
            self.seed_local_debug_targets(reset=True)
            self.process_preview_generation(budget=1)
        label = "Local debug map" if self.world_map_mode == "local_debug" else "Discovered world map"
        self.message = f"{label} open."
