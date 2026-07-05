from __future__ import annotations

import pygame
from typing import Any

from ..game_typing import GameMixinBase
from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_WIDTH
from .game_journal_stats import JournalStatsMixin


class JournalUIMixin(JournalStatsMixin, GameMixinBase):
    def quest_focus_coord(self, quest):
        if quest.kind == "delivery":
            return quest.to_world_pos
        if quest.kind == "scout":
            return quest.from_world_pos if quest.stage >= 1 or quest.status == "complete" else quest.to_world_pos
        if quest.kind == "bounty":
            return quest.from_world_pos if quest.stage >= 1 or quest.status == "complete" else quest.to_world_pos
        if quest.kind == "chain":
            return quest.from_world_pos if quest.stage >= 2 or quest.status == "complete" else quest.to_world_pos
        return quest.from_world_pos

    def open_world_map_for_quest(self, quest):
        coord = self.quest_focus_coord(quest)
        self.journal_open = False
        self.world_map_open = True
        self.prepare_overlay_toggle(opening=True, stop_auto=True, clear_manual=False)
        self.world_map_mode = "discovered"
        self.selected_world_region = coord
        self.hovered_world_region = coord
        self.world_map_detail_scroll = 0
        self.center_world_map_on(coord, animated=True)
        label = getattr(quest, "target_region_name", "") or getattr(quest, "origin_town_name", "") or f"({coord[0]}, {coord[1]})"
        self.message = f"Focusing world map on {label}."

    def abandon_quest(self, quest):
        if quest.status != "active":
            return
        if quest.kind == "delivery":
            item = self.inventory_item(quest.item_key)
            if item is not None:
                self.inventory.remove(item)
        if quest in self.active_quests:
            self.active_quests.remove(quest)
        remaining = self.current_journal_entries()
        self.journal_index = min(self.journal_index, len(remaining) - 1) if remaining else -1
        self.ensure_journal_selection_visible()
        self.message = f"You abandon the {quest.kind} quest."

    def quest_tabs(self):
        return ["Active", "Completed", "Character"]

    def current_journal_entries(self):
        if self.journal_tab == 0:
            return [quest for quest in self.active_quests if quest.status == "active"]
        if self.journal_tab == 1:
            return list(reversed(self.completed_quests()))
        return []  # Character tab renders its own content

    def journal_button_rect(self):
        map_width = VIEW_WIDTH * TILE_SIZE
        panel_x = map_width + 14
        panel_width = SCREEN_WIDTH - panel_x - 14
        top = 498
        button_gap = 8
        button_width = (panel_width - button_gap) // 2
        return pygame.Rect(panel_x, top, button_width, 42)

    def journal_layout(self):
        panel_w, panel_h = 700, 540
        left = (SCREEN_WIDTH - panel_w) // 2
        top = (SCREEN_HEIGHT - panel_h) // 2
        tab_top = top + 92
        viewport_top = top + 138
        button_top = top + panel_h - 48
        return {
            "left": left,
            "top": top,
            "panel_w": panel_w,
            "panel_h": panel_h,
            "tab_top": tab_top,
            "viewport": pygame.Rect(left + 20, viewport_top, panel_w - 40, panel_h - 200),
            "show_map_rect": pygame.Rect(left + 24, button_top, 136, 32),
            "abandon_rect": pygame.Rect(left + 170, button_top, 136, 32),
            "close_rect": pygame.Rect(left + panel_w - 144, button_top, 120, 32),
        }

    def journal_close_rect(self):
        return self.journal_layout()["close_rect"]

    def journal_tab_from_screen(self, screen_x, screen_y):
        layout = self.journal_layout()
        return self.tab_index_from_screen(screen_x, screen_y, self.quest_tabs(), layout["left"] + 22, layout["tab_top"], layout["panel_w"] - 44)

    def set_journal_tab(self, index):
        tabs = self.quest_tabs()
        self.journal_tab = max(0, min(index, len(tabs) - 1))
        self.journal_scroll = 0
        self.journal_index = -1
        self.message = f"Journal tab: {tabs[self.journal_tab]}."

    def shift_journal_tab(self, delta):
        tabs = self.quest_tabs()
        self.journal_tab = (self.journal_tab + delta) % len(tabs)
        self.journal_scroll = 0
        self.journal_index = -1
        self.message = f"Journal tab: {tabs[self.journal_tab]}."

    def journal_content_height(self):
        entries = self.current_journal_entries()
        if not entries:
            return 40
        content_width = self.journal_layout()["viewport"].width - 28
        height = 12
        for index, quest in enumerate(entries):
            wrapped = 0
            for line in self.journal_entry_lines(quest):
                wrapped += self.wrap_line_count(line, content_width - 18)
            height += 40 + wrapped * 18 + 16
            if index < len(entries) - 1:
                height += 10
        return height + 12

    def journal_row_metrics(self, quest: Any, viewport_width: int):
        content_width = viewport_width - 28
        wrapped = 0
        for line in self.journal_entry_lines(quest):
            wrapped += self.wrap_line_count(line, content_width - 18)
        return 40 + wrapped * 18 + 16

    def journal_entry_index_at_screen(self, screen_x, screen_y):
        layout = self.journal_layout()
        viewport = layout["viewport"]
        if not viewport.collidepoint(screen_x, screen_y):
            return None
        entries = self.current_journal_entries()
        if not entries:
            return None
        local_y = screen_y - viewport.top + self.journal_scroll
        y = 12
        for index, quest in enumerate(entries):
            row_height = self.journal_row_metrics(quest, viewport.width)
            row_rect = pygame.Rect(8, y, viewport.width - 16, row_height)
            if row_rect.collidepoint(screen_x - viewport.left, local_y):
                return index
            y += row_height + 10
        return None

    def journal_entry_at_screen(self, screen_x, screen_y):
        index = self.journal_entry_index_at_screen(screen_x, screen_y)
        if index is None:
            return None
        entries = self.current_journal_entries()
        return entries[index] if 0 <= index < len(entries) else None

    def selected_journal_quest(self):
        entries = self.current_journal_entries()
        if not entries or self.journal_index < 0:
            return None
        self.journal_index = max(0, min(self.journal_index, len(entries) - 1))
        return entries[self.journal_index]

    def selected_active_journal_quest(self):
        quest = self.selected_journal_quest()
        if quest is None or quest.status != "active":
            return None
        return quest

    def journal_region_discovered(self, coord):
        return coord == self.world_position or self.region_key(coord) in self.world_regions

    def can_show_map_for_selected_journal_quest(self):
        quest = self.selected_active_journal_quest()
        if quest is None:
            return False
        return self.journal_region_discovered(self.quest_focus_coord(quest))

    def can_abandon_selected_journal_quest(self):
        return self.selected_active_journal_quest() is not None

    def move_journal_selection(self, delta):
        entries = self.current_journal_entries()
        if not entries:
            self.journal_index = -1
            return
        if self.journal_index < 0:
            self.journal_index = 0 if delta >= 0 else len(entries) - 1
        else:
            self.journal_index = (self.journal_index + delta) % len(entries)
        self.ensure_journal_selection_visible()

    def ensure_journal_selection_visible(self):
        layout = self.journal_layout()
        viewport = layout["viewport"]
        entries = self.current_journal_entries()
        if not entries:
            self.journal_scroll = 0
            self.journal_index = -1
            return
        if self.journal_index < 0:
            return
        self.journal_index = max(0, min(self.journal_index, len(entries) - 1))
        y = 12
        for index, quest in enumerate(entries):
            row_height = self.journal_row_metrics(quest, viewport.width)
            row_top = y
            row_bottom = y + row_height
            if index == self.journal_index:
                if row_top < self.journal_scroll:
                    self.journal_scroll = row_top
                elif row_bottom > self.journal_scroll + viewport.height:
                    self.journal_scroll = row_bottom - viewport.height
                break
            y += row_height + 10
        self.journal_scroll = max(0, min(self.journal_max_scroll(), self.journal_scroll))

    def journal_action_from_screen(self, screen_x, screen_y):
        layout = self.journal_layout()
        if layout["show_map_rect"].collidepoint(screen_x, screen_y):
            return "show_map"
        if self.journal_tab == 0 and layout["abandon_rect"].collidepoint(screen_x, screen_y):
            return "abandon"
        if layout["close_rect"].collidepoint(screen_x, screen_y):
            return "close"
        return None

    def journal_max_scroll(self):
        layout = self.journal_layout()
        return max(0, self.journal_content_height() - layout["viewport"].height)

    def scroll_journal(self, delta):
        self.journal_scroll = max(0, min(self.journal_max_scroll(), self.journal_scroll + delta))
