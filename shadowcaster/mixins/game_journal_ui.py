from __future__ import annotations

import pygame

from ..game_typing import GameMixinBase
from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_WIDTH


class JournalUIMixin(GameMixinBase):

    def quest_tabs(self):
        return ["Active", "Completed"]

    def current_journal_entries(self):
        completed = [quest for quest in self.active_quests if quest.status == "complete"]
        if self.journal_tab == 0:
            return [quest for quest in self.active_quests if quest.status == "active"]
        return list(reversed(completed))

    def quest_status_label(self, quest):
        if quest.status == "complete":
            return "Complete"
        if quest.kind == "delivery":
            return "Delivery"
        if quest.kind == "scout":
            return "Scouting"
        if quest.kind == "bounty":
            return "Bounty"
        return quest.kind.title()

    def quest_progress_text(self, quest):
        if quest.kind == "delivery":
            return f"Deliver to {quest.to_town_hint} for {quest.reward_gold}g."
        if quest.kind == "scout":
            return f"Reach {quest.to_town_hint} and return for {quest.reward_gold}g."
        if quest.kind == "bounty":
            kills = max(0, self.enemies_defeated - quest.progress_count)
            if quest.status == "complete":
                kills = quest.target_count
            return f"{min(kills, quest.target_count)}/{quest.target_count} foes defeated. Reward {quest.reward_gold}g."
        return f"Reward {quest.reward_gold}g."

    def journal_entry_lines(self, quest):
        lines = [quest.description, self.quest_progress_text(quest)]
        if quest.status == "complete":
            lines.append(f"Completed near ({quest.from_world_pos[0]}, {quest.from_world_pos[1]}).")
        else:
            lines.append(f"Posted from ({quest.from_world_pos[0]}, {quest.from_world_pos[1]}).")
        return lines

    def quest_summary_counts(self):
        active = len([quest for quest in self.active_quests if quest.status == "active"])
        completed = len([quest for quest in self.active_quests if quest.status == "complete"])
        return {"active": active, "completed": completed}

    def journal_button_rect(self):
        map_width = VIEW_WIDTH * TILE_SIZE
        panel_x = map_width + 14
        panel_width = SCREEN_WIDTH - panel_x - 14
        top = 498
        button_gap = 8
        button_width = (panel_width - button_gap) // 2
        return pygame.Rect(panel_x, top, button_width, 42)

    def log_button_rect(self):
        journal_rect = self.journal_button_rect()
        return pygame.Rect(journal_rect.right + 8, journal_rect.top, journal_rect.width, journal_rect.height)

    def journal_layout(self):
        panel_w, panel_h = 700, 500
        left = (SCREEN_WIDTH - panel_w) // 2
        top = (SCREEN_HEIGHT - panel_h) // 2
        return {
            "left": left,
            "top": top,
            "panel_w": panel_w,
            "panel_h": panel_h,
            "viewport": pygame.Rect(left + 20, top + 88, panel_w - 40, panel_h - 152),
            "close_rect": pygame.Rect(left + panel_w - 144, top + panel_h - 48, 120, 32),
        }

    def journal_close_rect(self):
        return self.journal_layout()["close_rect"]

    def log_layout(self):
        panel_w, panel_h = 700, 520
        left = (SCREEN_WIDTH - panel_w) // 2
        top = (SCREEN_HEIGHT - panel_h) // 2
        return {
            "left": left,
            "top": top,
            "panel_w": panel_w,
            "panel_h": panel_h,
            "viewport": pygame.Rect(left + 20, top + 76, panel_w - 40, panel_h - 136),
            "close_rect": pygame.Rect(left + panel_w - 144, top + panel_h - 48, 120, 32),
        }

    def log_close_rect(self):
        return self.log_layout()["close_rect"]

    def journal_tab_from_screen(self, screen_x, screen_y):
        layout = self.journal_layout()
        return self.tab_index_from_screen(screen_x, screen_y, self.quest_tabs(), layout["left"] + 22, layout["top"] + 18, layout["panel_w"] - 44)

    def set_journal_tab(self, index):
        tabs = self.quest_tabs()
        self.journal_tab = max(0, min(index, len(tabs) - 1))
        self.journal_scroll = 0
        self.message = f"Journal tab: {tabs[self.journal_tab]}."

    def shift_journal_tab(self, delta):
        tabs = self.quest_tabs()
        self.journal_tab = (self.journal_tab + delta) % len(tabs)
        self.journal_scroll = 0
        self.message = f"Journal tab: {tabs[self.journal_tab]}."

    def journal_content_height(self):
        entries = self.current_journal_entries()
        if not entries:
            return 40
        content_width = self.journal_layout()["viewport"].width - 28
        height = 0
        for quest in entries:
            wrapped = 0
            for line in self.journal_entry_lines(quest):
                wrapped += self.wrap_line_count(line, content_width - 18)
            height += 40 + wrapped * 18 + 16
        return height

    def journal_max_scroll(self):
        layout = self.journal_layout()
        return max(0, self.journal_content_height() - layout["viewport"].height)

    def scroll_journal(self, delta):
        self.journal_scroll = max(0, min(self.journal_max_scroll(), self.journal_scroll + delta))

    def log_content_height(self):
        if not self.message_log:
            return 44
        width = self.log_layout()["viewport"].width - 28
        height = 0
        for entry in reversed(self.message_log):
            line_count = self.wrap_line_count(entry, width)
            height += 20 + line_count * 18
        return height

    def log_max_scroll(self):
        layout = self.log_layout()
        return max(0, self.log_content_height() - layout["viewport"].height)

    def scroll_log(self, delta):
        self.log_scroll = max(0, min(self.log_max_scroll(), self.log_scroll + delta))
