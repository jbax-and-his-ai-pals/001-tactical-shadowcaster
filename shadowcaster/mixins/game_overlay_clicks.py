from __future__ import annotations

import pygame

from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT
from ..game_typing import GameMixinBase
from ..persistence import has_save


class OverlayClickMixin(GameMixinBase):

    def handle_choice_click(self, screen_x, screen_y):
        choice = self.reward_choice_from_screen(screen_x, screen_y)
        if choice is None:
            return False
        self.exploration_choice_index = choice
        self.apply_current_choice()
        return True

    def handle_menu_click(self, screen_x, screen_y):
        if self.menu_mode == "controls":
            layout = self.controls_layout()
            tab_index = self.tab_index_from_screen(screen_x, screen_y, self.controls_tabs(), layout["left"] + 22, layout["top"] + 18, layout["box_width"] - 44)
            if tab_index is not None:
                self.set_controls_tab(tab_index)
                return True
        clicked = self.menu_choice_from_screen(screen_x, screen_y)
        if clicked is None:
            return False
        self.menu_index = clicked
        self.activate_menu_option()
        return True

    def handle_notice_board_click(self, screen_x, screen_y):
        choice_kind, index = self.notice_board_choice_from_screen(screen_x, screen_y)
        if choice_kind == "close":
            self.close_notice_board()
            return
        if choice_kind == "row" and index is not None:
            self.notice_board_index = index
            return
        if choice_kind == "confirm" and self.notice_board_confirm_available():
            self.accept_board_quest(self.notice_board_index)

    def handle_inventory_click(self, screen_x, screen_y, dismiss_on_miss=False):
        choice = self.inventory_choice_from_screen(screen_x, screen_y)
        if choice is None:
            if dismiss_on_miss:
                self.toggle_inventory()
                return True
            return False
        self.inventory_index = choice
        self.inventory_activate_selected()
        return True

    def handle_journal_click(self, screen_x, screen_y, dismiss_on_miss=False):
        tab_index = self.journal_tab_from_screen(screen_x, screen_y)
        if tab_index is not None:
            self.set_journal_tab(tab_index)
            return True
        action = self.journal_action_from_screen(screen_x, screen_y)
        if action == "close":
            self.toggle_journal()
            return True
        if action == "show_map":
            quest = self.selected_active_journal_quest()
            if quest is not None and self.can_show_map_for_selected_journal_quest():
                self.open_world_map_for_quest(quest)
            return True
        if action == "abandon":
            quest = self.selected_active_journal_quest()
            if quest is not None and self.can_abandon_selected_journal_quest():
                self.abandon_quest(quest)
            return True
        quest_index = self.journal_entry_index_at_screen(screen_x, screen_y)
        if quest_index is not None:
            self.journal_index = quest_index
            self.ensure_journal_selection_visible()
            return True
        if dismiss_on_miss:
            self.toggle_journal()
            return True
        return False

    def handle_log_click(self, screen_x, screen_y, dismiss_on_miss=False):
        if self.log_close_rect().collidepoint(screen_x, screen_y):
            self.toggle_log()
            return True
        if dismiss_on_miss:
            self.toggle_log()
            return True
        return False

    def handle_world_map_click(self, screen_x, screen_y, dismiss_on_miss=False):
        labels = ["Discovered", "Local Debug"]
        active_index = 0 if self.world_map_mode == "discovered" else 1
        tab_index = self.tab_index_from_screen(screen_x, screen_y, labels, SCREEN_WIDTH // 2 - 180, 118, 360)
        if tab_index is not None and tab_index != active_index:
            self.toggle_world_map_mode()
            return True
        if self.world_map_recenter_rect().collidepoint(screen_x, screen_y):
            self.reset_world_map_view()
            return True
        selected = self.world_region_from_screen(screen_x, screen_y)
        if selected is not None:
            if self.world_map_mode == "local_debug":
                state = self.world_map_regions().get(selected)
                if state and state.get("expandable_preview"):
                    self.expand_local_debug_region(selected)
                    return True
            self.hovered_world_region = selected
            self.select_world_region(selected)
            return True
        if dismiss_on_miss:
            self.toggle_world_map()
            return True
        return False

    def begin_world_map_drag(self, screen_x, screen_y):
        if not self.world_map_content_rect().collidepoint(screen_x, screen_y):
            return False
        current = self.world_map_view_center or (float(self.world_position[0]), float(self.world_position[1]))
        self.world_map_dragging = True
        self.world_map_drag_moved = False
        self.world_map_drag_anchor_screen = (screen_x, screen_y)
        self.world_map_drag_anchor_center = current
        self.world_map_center_animation = None
        return True

    def update_world_map_drag(self, screen_x, screen_y):
        if not self.world_map_dragging or not self.world_map_drag_anchor_screen or not self.world_map_drag_anchor_center:
            return
        layout = self.world_map_layout(self.world_map_regions())
        dx = screen_x - self.world_map_drag_anchor_screen[0]
        dy = screen_y - self.world_map_drag_anchor_screen[1]
        if abs(dx) >= 4 or abs(dy) >= 4:
            self.world_map_drag_moved = True
        self.world_map_view_center = (
            self.world_map_drag_anchor_center[0] - dx / layout["cell_size"],
            self.world_map_drag_anchor_center[1] - dy / layout["cell_size"],
        )
        self.update_world_map_hover(screen_x, screen_y)

    def end_world_map_drag(self, screen_x, screen_y, clicks=1):
        if not self.world_map_dragging:
            return False
        moved = self.world_map_drag_moved
        self.world_map_dragging = False
        self.world_map_drag_anchor_screen = None
        self.world_map_drag_anchor_center = None
        self.world_map_drag_moved = False
        if moved:
            return True
        selected = self.world_region_from_screen(screen_x, screen_y)
        if selected is None:
            return False
        if clicks >= 2 and not (self.world_map_mode == "local_debug" and self.world_map_regions().get(selected, {}).get("expandable_preview")):
            self.hovered_world_region = selected
            self.selected_world_region = selected
            self.center_world_map_on(selected, animated=True)
            self.message = f"Centering on {self.world_map_regions()[selected]['region_name']}."
            return True
        return self.handle_world_map_click(screen_x, screen_y)

    def handle_service_modal_click(self, screen_x, screen_y):
        ok_rect = self.service_modal_ok_rect()
        if ok_rect and ok_rect.collidepoint(screen_x, screen_y):
            self.close_service_modal()
            return True
        return False

    def service_modal_ok_rect(self):
        modal_width = 360
        modal_height = max(120, 80 + len(self.service_modal_lines) * 24)
        x = (SCREEN_WIDTH - modal_width) // 2
        y = (VIEW_HEIGHT * TILE_SIZE - modal_height) // 2
        btn_w, btn_h = 100, 32
        return pygame.Rect(x + (modal_width - btn_w) // 2, y + modal_height - btn_h - 14, btn_w, btn_h)

    def handle_game_over_click(self, screen_x, screen_y, dismiss_on_miss=False):
        tab_index = self.death_tab_from_screen(screen_x, screen_y)
        if tab_index is not None:
            self.death_stats_tab = tab_index
            return True
        if self.death_main_menu_rect().collidepoint(screen_x, screen_y):
            self.open_main_menu()
            return True
        if dismiss_on_miss:
            self.open_pause_menu()
            return True
        return False

    def reward_choice_from_screen(self, screen_x, screen_y):
        option_count = len(self.current_choice_options())
        box_width = 200
        box_height = 96
        gap = 20
        total_width = box_width * option_count + gap * max(0, option_count - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        top = (SCREEN_HEIGHT - box_height) // 2 + 30
        for index in range(option_count):
            left = start_x + index * (box_width + gap)
            if pygame.Rect(left, top, box_width, box_height).collidepoint(screen_x, screen_y):
                return index
        return None

    def menu_choice_from_screen(self, screen_x, screen_y):
        if self.menu_mode == "controls":
            layout = self.controls_layout()
            if pygame.Rect(layout["back_left"], layout["back_top"], layout["back_width"], layout["back_height"]).collidepoint(screen_x, screen_y):
                return 0
            return None
        layout = self.menu_layout()
        box_width = layout["box_width"]
        box_height = layout["box_height"]
        start_y = layout["start_y"]
        gap = layout["gap"]
        left = layout["left"]
        visible_options = layout["visible_options"]
        scroll = layout["scroll"]
        for visible_index in range(len(visible_options)):
            top = start_y + visible_index * (box_height + gap)
            option = visible_options[visible_index]
            if option == "Load Game" and self.menu_mode == "main" and not has_save():
                continue
            if pygame.Rect(left, top, box_width, box_height).collidepoint(screen_x, screen_y):
                return scroll + visible_index
        return None

    def travel_choice_from_screen(self, screen_x, screen_y):
        box_width = 280
        box_height = 86
        gap = 18
        total_width = box_width * len(self.travel_choices) + gap * max(0, len(self.travel_choices) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        top = (VIEW_HEIGHT * TILE_SIZE - box_height) // 2 + 36
        for index in range(len(self.travel_choices)):
            left = start_x + index * (box_width + gap)
            rect = pygame.Rect(left, top, box_width, box_height)
            if rect.collidepoint(screen_x, screen_y):
                return index
        return -1

    def tab_index_from_screen(self, screen_x, screen_y, labels, left, top, width):
        gap = 10
        tab_width = max(110, (width - gap * max(0, len(labels) - 1)) // max(1, len(labels)))
        for index in range(len(labels)):
            tab_left = left + index * (tab_width + gap)
            if pygame.Rect(tab_left, top, tab_width, 34).collidepoint(screen_x, screen_y):
                return index
        return None
