from __future__ import annotations
import math
import random
import pygame
from ..constants import (
    ACTION_AUTOEXPLORE,
    ACTION_CLEANSE,
    ACTION_DESCEND,
    ACTION_HEAL,
    ACTION_INVENTORY,
    ACTION_JOURNAL,
    ACTION_LOG,
    ACTION_MELEE,
    ACTION_RANGED,
    ACTION_WORLD_MAP,
    COLOR_ACCENT, COLOR_HEAL, COLOR_STAIRS, COLOR_TEXT,
    SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT, VIEW_WIDTH,
)
from ..models import RegionPalette
from ..persistence import has_save, list_saves
from ..regions import palette_for_region, settlement_size_label
from ..systems import heuristic
from ..game_typing import GameMixinBase


class UIMixin(GameMixinBase):

    def player_strength_rating(self):
        offense = int(getattr(self, "melee_damage", 0)) + int(getattr(self, "ranged_damage", 0))
        sustain = int(getattr(self, "max_health", 1)) // 2
        utility = int(getattr(self, "light_bonus", 0)) + int(getattr(self, "reach_bonus", 0)) + (int(getattr(self, "haste_bonus", 0)) // 12)
        resources = min(3, self.inventory_quantity("medkit") + self.inventory_quantity("tonic") + int(getattr(self, "ammo", 0)))
        momentum = int(getattr(self, "full_clears", 0))
        return max(1, (offense + sustain + utility + resources + momentum) // 6)

    def total_upgrade_count(self):
        return 1 if self.upgrade_pickup else 0

    def visible_hostiles(self):
        return [enemy for enemy in self.enemies if enemy.position in self.visible_tiles]

    def tile_in_viewport(self, position):
        if position is None:
            return False
        x, y = position
        return self.camera_x <= x < self.camera_x + VIEW_WIDTH and self.camera_y <= y < self.camera_y + VIEW_HEIGHT

    def on_screen_hostiles(self):
        return [enemy for enemy in self.visible_hostiles() if self.tile_in_viewport(enemy.position)]

    def touch_screen_pos(self, x_value, y_value):
        return (
            max(0, min(SCREEN_WIDTH - 1, int(x_value * SCREEN_WIDTH))),
            max(0, min(SCREEN_HEIGHT - 1, int(y_value * SCREEN_HEIGHT))),
        )

    def touch_action_buttons(self):
        map_width = VIEW_WIDTH * TILE_SIZE
        labels = [
            ("Atk", ACTION_MELEE),
            ("Shot", ACTION_RANGED),
            ("Auto", ACTION_AUTOEXPLORE),
            ("Use", ACTION_DESCEND),
            ("Kit", ACTION_HEAL),
            ("Tonic", ACTION_CLEANSE),
            ("Map", ACTION_WORLD_MAP),
            ("Inv", ACTION_INVENTORY),
            ("Log", ACTION_LOG),
            ("Msgs", ACTION_LOG),
            ("Menu", "menu"),
        ]
        columns = 4
        button_width = 104
        button_height = 40
        gap = 8
        rows = -(-len(labels) // columns)
        total_width = columns * button_width + (columns - 1) * gap
        total_height = rows * button_height + (rows - 1) * gap
        start_x = max(16, (map_width - total_width) // 2)
        start_y = VIEW_HEIGHT * TILE_SIZE - total_height - 14
        buttons = []
        for index, (label, action) in enumerate(labels):
            row = index // columns
            col = index % columns
            left = start_x + col * (button_width + gap)
            top = start_y + row * (button_height + gap)
            buttons.append({"label": label, "action": action, "rect": pygame.Rect(left, top, button_width, button_height)})
        return buttons

    def touch_action_at(self, screen_x, screen_y):
        if not self.touch_ui_active or self.active_overlay():
            return None
        for button in self.touch_action_buttons():
            if button["rect"].collidepoint(screen_x, screen_y):
                return button["action"]
        return None

    def first_sighting_message(self):
        visible_hostiles = [enemy for enemy in self.enemies if enemy.position in self.visible_tiles]
        if visible_hostiles:
            enemy = sorted(visible_hostiles, key=lambda foe: heuristic(self.player, foe.position))[0]
            article = "an" if enemy.kind[:1].lower() in "aeiou" else "a"
            return f"You see {article} {enemy.kind}."
        discovered = self.turn_newly_discovered_tiles & self.current_non_hostile_interest_tiles() & self.visible_tiles
        if not discovered:
            return "You see something important."
        position = sorted(discovered, key=lambda tile: heuristic(self.player, tile))[0]
        landmark = next((landmark for landmark in self.landmarks if landmark.position == position), None)
        if landmark:
            label = landmark.kind.replace("_", " ")
            article = "an" if label[:1].lower() in "aeiou" else "a"
            return f"You see {article} {label}."
        if self.up_stairs and position == self.up_stairs:
            return "You see stairs leading up."
        if self.stairs and position == self.stairs:
            return "You see stairs leading down."
        if self.delve_goal and position == self.delve_goal:
            return "You see the delve terminus."
        if self.bottom_reward_claimed and self.return_portal and position == self.return_portal:
            return "You see a return portal."
        if position in self.edge_exits.values():
            direction = next(direction for direction, tile in self.edge_exits.items() if tile == position)
            return f"You see an exit {direction}."
        if self.upgrade_pickup and position == self.upgrade_pickup.position:
            return "You see an upgrade cache."
        if self.heal_pickup and position == self.heal_pickup:
            return "You see a medical pickup."
        floor_item = self.floor_item_at(position)
        if floor_item:
            return f"You see {floor_item.item.name.lower()}."
        info = self.inspect_tile_info(position)
        if info:
            return f"You see {info['title'].lower()}."
        return "You see something important."

    def prepare_overlay_toggle(self, *, opening, stop_auto=False, clear_manual=True, clear_inspect_on_open=True, close_menu_on_open=False):
        if stop_auto:
            self.stop_auto_movement()
        if clear_manual:
            self.auto_move_path = []
            self.clear_manual_movement()
        if opening and close_menu_on_open:
            self.close_menu()
        if opening and clear_inspect_on_open:
            self.clear_inspect_focus()

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

    def scroll_message_log_by(self, delta):
        if not self.message_log:
            self.message_log_scroll = 0
            return
        max_scroll = max(0, len(self.message_log) - 1)
        self.message_log_scroll = max(0, min(max_scroll, self.message_log_scroll + delta))

    def move_inventory_selection(self, delta):
        rows = self.inventory_rows()
        if rows:
            self.inventory_index = (self.inventory_index + delta) % len(rows)

    def move_tuner_selection(self, delta):
        self.tuner_index = (self.tuner_index + delta) % len(self.grouped_tuner_entries())

    def travel_choice_from_screen(self, screen_x, screen_y):
        box_width = 280
        box_height = 86
        gap = 18
        total_width = box_width * len(self.travel_choices) + gap * max(0, len(self.travel_choices) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        top = (VIEW_HEIGHT * TILE_SIZE - box_height) // 2 + 36
        for index in range(len(self.travel_choices)):
            left = start_x + index * (box_width + gap)
            rect = pygame.Rect(left, top, box_width, gap)
            if rect.collidepoint(screen_x, screen_y):
                return index
        return -1

    def notice_board_layout(self):
        panel_w, panel_h = 660, 500
        left = (SCREEN_WIDTH - panel_w) // 2
        top = (SCREEN_HEIGHT - panel_h) // 2
        header_bottom = top + 86
        quest_area_top = top + 110
        row_h = 96
        row_rects = [
            pygame.Rect(left + 18, quest_area_top + i * row_h, panel_w - 36, row_h - 10)
            for i in range(len(self.notice_board_quests))
        ]
        hint_top = top + panel_h - 92
        button_top = top + panel_h - 52
        confirm_rect = pygame.Rect(left + 24, button_top, 188, 34)
        close_rect = pygame.Rect(left + panel_w - 148, button_top, 124, 34)
        return {
            "left": left,
            "top": top,
            "panel_w": panel_w,
            "panel_h": panel_h,
            "header_bottom": header_bottom,
            "row_rects": row_rects,
            "hint_top": hint_top,
            "confirm_rect": confirm_rect,
            "close_rect": close_rect,
        }

    def notice_board_choice_from_screen(self, screen_x, screen_y):
        layout = self.notice_board_layout()
        for index, rect in enumerate(layout["row_rects"]):
            if rect.collidepoint(screen_x, screen_y):
                return ("row", index)
        if layout["confirm_rect"].collidepoint(screen_x, screen_y):
            return ("confirm", None)
        if layout["close_rect"].collidepoint(screen_x, screen_y):
            return ("close", None)
        return (None, None)

    def notice_board_hovered_index(self):
        kind, index = self.notice_board_choice_from_screen(*self.mouse_screen_pos)
        return index if kind == "row" else None

    def notice_board_confirm_available(self):
        if not self.notice_board_quests:
            return False
        selected_state = self.notice_board_quest_state(self.notice_board_quests[self.notice_board_index])
        return selected_state == "available"

    def tab_index_from_screen(self, screen_x, screen_y, labels, left, top, width):
        gap = 10
        tab_width = max(110, (width - gap * max(0, len(labels) - 1)) // max(1, len(labels)))
        for index in range(len(labels)):
            tab_left = left + index * (tab_width + gap)
            if pygame.Rect(tab_left, top, tab_width, 34).collidepoint(screen_x, screen_y):
                return index
        return None

    def world_from_screen(self, screen_x, screen_y):
        if screen_x >= VIEW_WIDTH * TILE_SIZE or screen_y >= VIEW_HEIGHT * TILE_SIZE:
            return None
        tile_x = screen_x // TILE_SIZE + self.camera_x
        tile_y = screen_y // TILE_SIZE + self.camera_y
        return (tile_x, tile_y) if 0 <= tile_x < self.dungeon.width and 0 <= tile_y < self.dungeon.height else None

    def update_hovered_tile(self, screen_x, screen_y):
        self.mouse_screen_pos = (screen_x, screen_y)
        self.hovered_world_tile = self.world_from_screen(screen_x, screen_y)

    def open_travel_selection(self):
        self.travel_mode = False
        self.travel_choices = []
        self.auto_move_path = []
        self.clear_manual_movement()
        self.message = "Route selection is no longer used."

    def choose_travel_destination(self, index):
        self.message = "Route selection is no longer used."
