from __future__ import annotations

import pygame
from ..constants import VIEW_HEIGHT, VIEW_WIDTH
from ..systems import compute_fov
from ..game_typing import GameMixinBase


class VisibilityMixin(GameMixinBase):
    def trigger_completion_modal(self, text):
        self.completion_modal_text = text
        self.completion_modal_started = pygame.time.get_ticks()
        self.completion_modal_until = self.completion_modal_started + self.tuning["completion_modal_duration_ms"]

    def reveal_entire_map(self):
        reveal = set(self.floor_explorable_tiles)
        reveal.update(self.terrain_features.keys())
        reveal.update(self.current_interest_tiles())
        reveal.update(resident.position for resident in getattr(self, "residents", []))
        for x, y in list(self.floor_explorable_tiles):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neighbor = (x + dx, y + dy)
                    if not (0 <= neighbor[0] < self.dungeon.width and 0 <= neighbor[1] < self.dungeon.height):
                        continue
                    if self.dungeon.is_blocked(*neighbor):
                        reveal.add(neighbor)
        self.seen_tiles = reveal

    def update_visibility(self):
        previous_visible = getattr(self, "visible_tiles", set())
        previous_seen = set(getattr(self, "seen_tiles", set()))
        bonus = 5 if self.terrain_features.get(self.player) == "high_ground" else 0
        self.visible_tiles = compute_fov(self.player[0], self.player[1], self.light_radius + bonus, self.dungeon)
        self.newly_visible_tiles = self.visible_tiles - previous_visible
        self.newly_discovered_tiles = self.visible_tiles - previous_seen
        self.turn_newly_discovered_tiles.update(self.newly_discovered_tiles)
        self.seen_tiles.update(self.visible_tiles)
        explored_walkable = len(self.seen_tiles & self.floor_explorable_tiles)
        self.exploration_progress = int((explored_walkable / max(1, len(self.floor_explorable_tiles))) * 100)
        if self.exploration_effectively_complete():
            self.exploration_progress = 100
        self.best_exploration_percent = max(self.best_exploration_percent, self.exploration_progress)
        self.update_camera()

    def check_exploration_rewards(self):
        messages = []
        for milestone in self.exploration_milestones:
            if (
                self.exploration_progress < milestone
                or milestone in self.claimed_exploration_rewards
                or self.has_pending_choice()
            ):
                continue
            self.reveal_entire_map()
            self.exploration_reward_pending = milestone
            self.exploration_choice_index = 0
            self.stop_auto_movement()
            messages.append("Floor fully explored: choose a boon.")
        return " ".join(messages) if messages else None

    def update_camera(self):
        max_camera_x = max(0, self.dungeon.width - VIEW_WIDTH)
        max_camera_y = max(0, self.dungeon.height - VIEW_HEIGHT)
        self.camera_x = max(0, min(self.player[0] - VIEW_WIDTH // 2, max_camera_x))
        self.camera_y = max(0, min(self.player[1] - VIEW_HEIGHT // 2, max_camera_y))
        if self.game_over:
            self.hovered_world_tile = None
            self.selected_inspect_tile = None
        else:
            self.hovered_world_tile = self.world_from_screen(*self.mouse_screen_pos)

    def current_interest_tiles(self):
        interests = self.current_non_hostile_interest_tiles()
        interests.update(enemy.position for enemy in getattr(self, "enemies", []))
        return interests

    def current_non_hostile_interest_tiles(self):
        interests = set()
        if self.up_stairs:
            interests.add(self.up_stairs)
        if self.stairs:
            interests.add(self.stairs)
        if self.delve_goal:
            interests.add(self.delve_goal)
        interests.update(getattr(self, "edge_exits", {}).values())
        interests.update(landmark.position for landmark in getattr(self, "landmarks", []))
        if self.upgrade_pickup:
            interests.add(self.upgrade_pickup.position)
        if self.heal_pickup:
            interests.add(self.heal_pickup)
        interests.update(ground_item.position for ground_item in getattr(self, "floor_items", []))
        return interests

    def visible_interest_tiles(self):
        return self.current_interest_tiles() & self.visible_tiles

    def should_interrupt_auto_move(self):
        visible_hostiles = {enemy.position for enemy in self.on_screen_hostiles()}
        visible_non_hostile_interests = self.current_non_hostile_interest_tiles() & self.visible_tiles
        newly_discovered_interest = any(tile in self.turn_newly_discovered_tiles for tile in visible_non_hostile_interests)
        current_visible_interests = visible_hostiles | visible_non_hostile_interests
        self.last_interest_tiles = current_visible_interests
        return bool(visible_hostiles) or newly_discovered_interest

    def stop_auto_movement(self):
        self.auto_move_path = []
        self.autoexplore_active = False
        self.clear_manual_movement()
        self.next_auto_move_ms = 0

    def stop_pathing(self):
        self.auto_move_path = []
        self.autoexplore_active = False
