from __future__ import annotations

import pygame

from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH
from ..game_typing import GameMixinBase


class DeathUIMixin(GameMixinBase):

    def death_stats_tabs(self):
        return ["Run", "Exploration", "Items"]

    def death_cause_label(self):
        return self.death_cause or "Unknown"

    def enemy_status_duration(self, enemy):
        if enemy.on_hit_effect == "poison" and enemy.kind == "shaman":
            return self.tuning["shaman_poison_duration"]
        if enemy.on_hit_effect == "cripple":
            return 3
        return self.tuning["enemy_status_duration"]

    def death_overlay_rect(self):
        line_count = max(len(self.game_over_summary_lines(tab)) for tab in self.death_stats_tabs())
        panel_width = 620
        panel_height = max(500, 220 + line_count * 30)
        left = (SCREEN_WIDTH - panel_width) // 2
        top = (SCREEN_HEIGHT - panel_height) // 2
        return pygame.Rect(left, top, panel_width, panel_height)

    def death_tab_rects(self):
        rect = self.death_overlay_rect()
        labels = self.death_stats_tabs()
        gap = 10
        tab_height = 34
        width = rect.width - 48
        tab_width = (width - gap * (len(labels) - 1)) // len(labels)
        top = rect.top + 104
        left = rect.left + 24
        rects = []
        for index in range(len(labels)):
            tab_left = left + index * (tab_width + gap)
            rects.append(pygame.Rect(tab_left, top, tab_width, tab_height))
        return rects

    def death_respawn_rect(self):
        rect = self.death_overlay_rect()
        width = 220
        height = 50
        left = rect.left + 24
        top = rect.bottom - height - 24
        return pygame.Rect(left, top, width, height)

    def death_main_menu_rect(self):
        rect = self.death_overlay_rect()
        width = 220
        height = 50
        left = rect.right - width - 24
        top = rect.bottom - height - 24
        return pygame.Rect(left, top, width, height)

    def death_tab_from_screen(self, screen_x, screen_y):
        for index, rect in enumerate(self.death_tab_rects()):
            if rect.collidepoint(screen_x, screen_y):
                return index
        return None

    def game_over_summary_lines(self, tab=None):
        pickups = self.powerups_collected
        tab = tab or self.death_stats_tabs()[self.death_stats_tab]
        if tab == "Run":
            gold_lost = getattr(self, "death_gold_lost", 0)
            respawn = getattr(self, "death_respawn_label", "") or "starting town"
            lines = [
                f"Killed by: {self.death_cause_label()}",
                f"Gold lost: {gold_lost}g",
                f"Respawn: {respawn}",
                f"Steps taken: {self.total_steps}",
                f"Monsters killed: {self.total_monsters_killed}",
                f"Region: {self.region_name}",
            ]
            return lines
        if tab == "Exploration":
            return [
                f"Exploration this floor: {self.exploration_progress}%",
                f"Best exploration reached: {self.best_exploration_percent}%",
                f"Full clears: {self.full_clears}",
            ]
        return [
            f"Light caches: {pickups['light']}",
            f"Vitality caches: {pickups['vitality']}",
            f"Power caches: {pickups['power']}",
            f"Haste caches: {pickups['haste']}",
            f"Reach caches: {pickups['reach']}",
            f"Medical pickups: {pickups['heal']}",
            f"Medkits used: {self.medkits_used}",
            f"Tonics used: {self.tonics_used}",
        ]

    def shift_death_stats_tab(self, delta):
        tabs = self.death_stats_tabs()
        self.death_stats_tab = (self.death_stats_tab + delta) % len(tabs)
