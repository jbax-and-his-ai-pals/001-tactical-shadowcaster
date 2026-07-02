from __future__ import annotations

import pygame

from ..constants import (
    MOVE_REPEAT_DELAY_MS,
    MOVE_REPEAT_INTERVAL_MS,
)
from ..game_typing import GameMixinBase


class OverlayInputMixin(GameMixinBase):

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

    def update_controller_overlay_navigation(self):
        overlay = self.active_overlay()
        if not overlay:
            self.controller_menu_move = None
            self.next_menu_repeat_ms = 0
            return
        move = self.controller_stick_move()
        vertical = move[1] if move and move[1] else None
        horizontal = move[0] if move and move[0] else None
        now = pygame.time.get_ticks()
        if vertical is not None:
            direction = (0, vertical)
            changed = self.controller_menu_move != direction
            if changed or now >= self.next_menu_repeat_ms:
                if overlay == "menu" and self.menu_mode == "controls":
                    self.scroll_controls(36 if vertical > 0 else -36)
                elif overlay == "menu":
                    self.menu_index = (self.menu_index + 1) % len(self.menu_options()) if vertical > 0 else (self.menu_index - 1) % len(self.menu_options())
                elif overlay == "tuner":
                    self.move_tuner_selection(1 if vertical > 0 else -1)
                elif overlay == "inventory":
                    self.move_inventory_selection(1 if vertical > 0 else -1)
                elif overlay == "notice_board":
                    self.notice_board_index = (self.notice_board_index + (1 if vertical > 0 else -1)) % max(1, len(self.notice_board_quests))
                elif overlay == "choice":
                    self.adjust_choice_index(1 if vertical > 0 else -1)
                elif overlay == "world_map":
                    self.step_world_map_selection(0, vertical)
                elif overlay == "game_over":
                    self.shift_death_stats_tab(1 if vertical > 0 else -1)
                self.controller_menu_move = direction
                self.next_menu_repeat_ms = now + (MOVE_REPEAT_DELAY_MS if changed else MOVE_REPEAT_INTERVAL_MS)
            return
        if horizontal is not None:
            direction = (horizontal, 0)
            changed = self.controller_menu_move != direction
            if changed or now >= self.next_menu_repeat_ms:
                if overlay == "menu" and self.menu_mode == "controls":
                    self.shift_controls_tab(1 if horizontal > 0 else -1)
                else:
                    if overlay == "tuner":
                        self.adjust_tuner_value(1 if horizontal > 0 else -1)
                    elif overlay == "choice":
                        self.adjust_choice_index(1 if horizontal > 0 else -1)
                    elif overlay == "world_map":
                        self.step_world_map_selection(horizontal, 0)
                    elif overlay == "game_over":
                        self.shift_death_stats_tab(1 if horizontal > 0 else -1)
                self.controller_menu_move = direction
                self.next_menu_repeat_ms = now + (MOVE_REPEAT_DELAY_MS if changed else MOVE_REPEAT_INTERVAL_MS)
            return
        self.controller_menu_move = None
        self.next_menu_repeat_ms = 0

    def reset_menu_state(self, mode=None):
        self.menu_mode = mode
        self.menu_index = 0
        self.menu_scroll = 0
        self.menu_message = ""

    def close_menu(self):
        self.reset_menu_state()
        self.controller_menu_move = None
        self.next_menu_repeat_ms = 0
        self.selected_inspect_tile = None
        self.hovered_world_tile = self.world_from_screen(*self.mouse_screen_pos)

    def return_to_parent_menu(self):
        self.reset_menu_state(self.menu_return_mode)

    def reopen_menu_if_needed(self, mode):
        if mode == "main":
            self.open_main_menu()
        elif mode == "pause":
            self.open_pause_menu()

    def adjust_choice_index(self, delta):
        option_count = len(self.current_choice_options())
        self.exploration_choice_index = (self.exploration_choice_index + delta) % option_count

    def move_inventory_selection(self, delta):
        rows = self.inventory_rows()
        if rows:
            self.inventory_index = (self.inventory_index + delta) % len(rows)

    def move_tuner_selection(self, delta):
        self.tuner_index = (self.tuner_index + delta) % len(self.grouped_tuner_entries())

    def handle_hat_overlay_move(self, move):
        if self.menu_mode:
            if self.menu_mode == "controls" and move == (0, -1):
                self.scroll_controls(-36)
            elif self.menu_mode == "controls" and move == (0, 1):
                self.scroll_controls(36)
            elif move == (0, -1):
                self.menu_index = (self.menu_index - 1) % len(self.menu_options())
            elif move == (0, 1):
                self.menu_index = (self.menu_index + 1) % len(self.menu_options())
            elif self.menu_mode == "controls" and move == (-1, 0):
                self.shift_controls_tab(-1)
            elif self.menu_mode == "controls" and move == (1, 0):
                self.shift_controls_tab(1)
            return True
        overlay = self.active_non_menu_overlay()
        if overlay == "tuner":
            if move == (0, -1):
                self.move_tuner_selection(-1)
            elif move == (0, 1):
                self.move_tuner_selection(1)
            elif move == (-1, 0):
                self.adjust_tuner_value(-1)
            elif move == (1, 0):
                self.adjust_tuner_value(1)
            return True
        if overlay == "inventory":
            if move == (0, -1):
                self.move_inventory_selection(-1)
            elif move == (0, 1):
                self.move_inventory_selection(1)
            return True
        if overlay == "journal":
            if move == (0, -1):
                self.scroll_journal(-36)
            elif move == (0, 1):
                self.scroll_journal(36)
            elif move == (-1, 0):
                self.shift_journal_tab(-1)
            elif move == (1, 0):
                self.shift_journal_tab(1)
            return True
        if overlay == "log":
            if move == (0, -1):
                self.scroll_log(-36)
            elif move == (0, 1):
                self.scroll_log(36)
            return True
        if overlay == "notice_board":
            if move == (0, -1):
                self.notice_board_index = (self.notice_board_index - 1) % max(1, len(self.notice_board_quests))
            elif move == (0, 1):
                self.notice_board_index = (self.notice_board_index + 1) % max(1, len(self.notice_board_quests))
            return True
        if overlay == "choice":
            if move in {(-1, 0), (0, -1)}:
                self.adjust_choice_index(-1)
            elif move in {(1, 0), (0, 1)}:
                self.adjust_choice_index(1)
            return True
        if overlay == "game_over":
            if move == (-1, 0):
                self.shift_death_stats_tab(-1)
            elif move == (1, 0):
                self.shift_death_stats_tab(1)
            return True
        return False
