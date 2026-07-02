from __future__ import annotations

import math

import pygame

from ..game_typing import GameMixinBase
from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH


class WorldMapUIMixin(GameMixinBase):

    def town_context_for_landmark(self, landmark):
        parent_biome = self.region_type if self.is_overworld_region() else self.settlement_parent_biome() or self.region_type
        context = {"parent_biome": parent_biome}
        if landmark.kind in {"town", "monster_town"}:
            context["settlement_size"] = self.choose_settlement_size(parent_biome, hostile=landmark.kind == "monster_town")
        return context

    def world_map_layout(self, regions=None):
        detail_width = 372
        gutter = 26
        map_left = 34
        map_top = 166
        map_area_width = SCREEN_WIDTH - map_left - detail_width - gutter - 34
        map_area_height = SCREEN_HEIGHT - map_top - 86
        map_content_left_pad = 18
        map_content_right_pad = 18
        map_content_top_pad = 52
        map_content_bottom_pad = 18
        map_content_width = map_area_width - map_content_left_pad - map_content_right_pad
        map_content_height = map_area_height - map_content_top_pad - map_content_bottom_pad
        cell_size = 54
        visible_cols = max(5, map_content_width // cell_size)
        visible_rows = max(4, map_content_height // cell_size)
        center_x, center_y = self.world_map_view_center or self.selected_world_region or self.world_position
        half_cols = visible_cols / 2.0
        half_rows = visible_rows / 2.0
        min_x = int(center_x - half_cols) - 1
        max_x = int(center_x + half_cols) + 1
        min_y = int(center_y - half_rows) - 1
        max_y = int(center_y + half_rows) + 1
        map_width = visible_cols * cell_size
        map_height = visible_rows * cell_size
        content_left = map_left + map_content_left_pad
        content_top = map_top + map_content_top_pad
        center_pixel_x = content_left + map_content_width / 2.0
        center_pixel_y = content_top + map_content_height / 2.0
        return {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "visible_cols": visible_cols,
            "visible_rows": visible_rows,
            "cell_size": cell_size,
            "map_width": map_width,
            "map_height": map_height,
            "origin_x": content_left + (map_content_width - map_width) // 2,
            "origin_y": content_top + (map_content_height - map_height) // 2,
            "center_x": center_x,
            "center_y": center_y,
            "center_pixel_x": center_pixel_x,
            "center_pixel_y": center_pixel_y,
            "map_left": map_left,
            "map_top": map_top,
            "map_area_width": map_area_width,
            "map_area_height": map_area_height,
            "map_content_left_pad": map_content_left_pad,
            "map_content_right_pad": map_content_right_pad,
            "map_content_top_pad": map_content_top_pad,
            "map_content_bottom_pad": map_content_bottom_pad,
            "detail_left": map_left + map_area_width + gutter,
            "detail_top": map_top,
            "detail_width": detail_width,
            "detail_height": map_area_height,
        }

    def select_world_region(self, coord):
        if coord in self.world_map_regions():
            self.selected_world_region = coord
            state = self.world_map_regions()[coord]
            mode_prefix = "Previewing" if self.world_map_mode == "local_debug" and coord != self.world_position and coord not in self.discovered_world_regions() else "Inspecting"
            self.message = f"{mode_prefix} {state['region_name']}."

    def update_world_map_hover(self, screen_x, screen_y):
        if not self.world_map_open:
            self.hovered_world_region = None
            return
        self.hovered_world_region = self.world_region_from_screen(screen_x, screen_y)

    def focused_world_region(self):
        return self.hovered_world_region or self.selected_world_region or self.world_position

    def set_world_map_center(self, coord):
        if coord is None:
            return
        self.world_map_view_center = (float(coord[0]), float(coord[1]))

    def center_world_map_on(self, coord, animated=False):
        if coord is None:
            return
        if animated:
            self.world_map_center_animation = (float(coord[0]), float(coord[1]))
        else:
            self.world_map_center_animation = None
            self.set_world_map_center(coord)

    def pan_world_map(self, dx, dy):
        center = self.world_map_view_center or (
            (float(self.selected_world_region[0]), float(self.selected_world_region[1]))
            if self.selected_world_region
            else (float(self.world_position[0]), float(self.world_position[1]))
        )
        self.world_map_center_animation = None
        self.world_map_view_center = (center[0] + dx, center[1] + dy)
        self.update_world_map_hover(*self.mouse_screen_pos)

    def update_world_map_center_animation(self):
        if self.world_map_center_animation is None:
            return
        current = self.world_map_view_center or (float(self.world_position[0]), float(self.world_position[1]))
        target = self.world_map_center_animation
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        if abs(dx) < 0.02 and abs(dy) < 0.02:
            self.world_map_view_center = target
            self.world_map_center_animation = None
            return
        self.world_map_view_center = (current[0] + dx * 0.32, current[1] + dy * 0.32)

    def scroll_world_map_details(self, delta, content_height=None):
        layout = self.world_map_layout()
        if not layout:
            return
        viewport_height = self.world_map_detail_viewport_rect().height
        max_scroll = max(0, (content_height or viewport_height) - viewport_height)
        self.world_map_detail_scroll = max(0, min(max_scroll, self.world_map_detail_scroll + delta))

    def world_map_detail_from_screen(self, screen_x, screen_y):
        return self.world_map_detail_viewport_rect().collidepoint(screen_x, screen_y)

    def world_map_detail_viewport_rect(self):
        layout = self.world_map_layout()
        detail_frame = pygame.Rect(layout["detail_left"], layout["detail_top"], layout["detail_width"], layout["detail_height"])
        inset = detail_frame.inflate(-24, -24)
        chip_y = detail_frame.y + 96
        detail_content_top = chip_y + 38
        viewport_height = detail_frame.height - (detail_content_top - detail_frame.y) - 16
        return pygame.Rect(inset.x, detail_content_top, inset.width, viewport_height)

    def handle_world_map_wheel(self, event):
        pointer = getattr(event, "pos", None) or pygame.mouse.get_pos()
        self.mouse_screen_pos = pointer
        if self.world_map_detail_from_screen(*pointer):
            self.scroll_world_map_details(-event.y * 40)
            return
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.pan_world_map(-event.y, 0)
        else:
            self.pan_world_map(0, -event.y)

    def world_region_from_screen(self, screen_x, screen_y):
        regions = self.world_map_regions()
        layout = self.world_map_layout(regions)
        if not layout:
            return None
        content_rect = pygame.Rect(
            layout["map_left"] + layout["map_content_left_pad"],
            layout["map_top"] + layout["map_content_top_pad"],
            layout["map_area_width"] - layout["map_content_left_pad"] - layout["map_content_right_pad"],
            layout["map_area_height"] - layout["map_content_top_pad"] - layout["map_content_bottom_pad"],
        )
        if not content_rect.collidepoint(screen_x, screen_y):
            return None
        rel_x = (screen_x - layout["center_pixel_x"]) / layout["cell_size"] + layout["center_x"]
        rel_y = (screen_y - layout["center_pixel_y"]) / layout["cell_size"] + layout["center_y"]
        coord = (math.floor(rel_x + 0.5), math.floor(rel_y + 0.5))
        return coord if coord in regions else None

    def world_map_content_rect(self):
        layout = self.world_map_layout()
        return pygame.Rect(
            layout["map_left"] + layout["map_content_left_pad"],
            layout["map_top"] + layout["map_content_top_pad"],
            layout["map_area_width"] - layout["map_content_left_pad"] - layout["map_content_right_pad"],
            layout["map_area_height"] - layout["map_content_top_pad"] - layout["map_content_bottom_pad"],
        )

    def world_map_recenter_rect(self):
        layout = self.world_map_layout()
        return pygame.Rect(layout["map_left"] + layout["map_area_width"] - 154, layout["map_top"] + 14, 136, 32)

    def reset_world_map_view(self):
        self.world_map_center_animation = None
        self.center_world_map_on(self.selected_world_region or self.world_position)
        self.message = "World map recentered."

    def step_world_map_selection(self, dx, dy):
        regions = self.world_map_regions()
        if not regions:
            return
        current = self.selected_world_region or self.world_position
        candidates = []
        for coord in regions:
            if coord == current:
                continue
            delta_x = coord[0] - current[0]
            delta_y = coord[1] - current[1]
            if dx and delta_x * dx <= 0:
                continue
            if dy and delta_y * dy <= 0:
                continue
            primary = abs(delta_x) if dx else abs(delta_y)
            secondary = abs(delta_y) if dx else abs(delta_x)
            candidates.append(((primary, secondary), coord))
        if not candidates:
            return
        _, coord = min(candidates, key=lambda item: item[0])
        self.hovered_world_region = coord
        self.select_world_region(coord)
        self.center_world_map_on(coord)
