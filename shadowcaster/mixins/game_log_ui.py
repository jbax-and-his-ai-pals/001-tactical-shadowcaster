from __future__ import annotations

import pygame

from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH
from ..game_typing import GameMixinBase


class LogUIMixin(GameMixinBase):
    def log_button_rect(self):
        panel_x, top, btn_w, btn_h, gap = self._side_panel_button_row()
        return pygame.Rect(panel_x + 2 * (btn_w + gap), top, btn_w, btn_h)

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

    def log_content_height(self):
        if not self.message_log:
            return 44
        width = self.log_layout()["viewport"].width - 28
        height = 12
        entries = list(reversed(self.message_log))
        for index, entry in enumerate(entries):
            line_count = self.wrap_line_count(entry, width)
            height += 16 + line_count * 18 + 10
            if index < len(entries) - 1:
                height += 8
        return height + 12

    def log_max_scroll(self):
        layout = self.log_layout()
        return max(0, self.log_content_height() - layout["viewport"].height)

    def scroll_log(self, delta):
        self.log_scroll = max(0, min(self.log_max_scroll(), self.log_scroll + delta))
