from __future__ import annotations

import pygame
from typing import Any

from ..game_typing import GameMixinBase
from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_WIDTH


class JournalUIMixin(GameMixinBase):
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

    def completed_quests(self):
        return [quest for quest in self.active_quests if quest.status == "complete"]

    def completed_quest_counts(self, coord=None):
        counts = {"delivery": 0, "scout": 0, "bounty": 0, "chain": 0}
        for quest in self.completed_quests():
            if coord is not None and quest.from_world_pos != coord:
                continue
            counts[quest.kind] = counts.get(quest.kind, 0) + 1
        return counts

    def town_prosperity_score(self, coord):
        counts = self.completed_quest_counts(coord)
        return counts.get("delivery", 0) + counts.get("scout", 0) + counts.get("chain", 0) * 2 + counts.get("bounty", 0) * 2

    def town_prosperity_label(self, coord):
        score = self.town_prosperity_score(coord)
        if score >= 10:
            return "Thriving"
        if score >= 6:
            return "Busy"
        if score >= 3:
            return "Steady"
        if score >= 1:
            return "Recovering"
        return "Quiet"

    def total_towns_helped(self):
        return len({quest.from_world_pos for quest in self.completed_quests()})

    def active_quests_for_region(self, coord):
        return [quest for quest in self.active_quests if quest.status == "active" and (quest.from_world_pos == coord or quest.to_world_pos == coord)]

    def active_quest_region_summary(self, coord):
        summary = {
            "posted_here": 0,
            "targets_here": 0,
            "report_here": 0,
            "kinds": set(),
            "lines": [],
        }
        for quest in self.active_quests:
            if quest.status != "active":
                continue
            touches_origin = quest.from_world_pos == coord
            touches_target = quest.to_world_pos == coord
            if not touches_origin and not touches_target:
                continue
            summary["kinds"].add(quest.kind)
            if touches_origin:
                summary["posted_here"] += 1
            if touches_target:
                summary["targets_here"] += 1
            if quest.kind == "scout" and quest.stage >= 1 and quest.from_world_pos == coord:
                summary["report_here"] += 1
            if quest.kind == "bounty" and quest.stage >= 1 and quest.from_world_pos == coord:
                summary["report_here"] += 1
            if quest.kind == "delivery":
                if touches_target:
                    summary["lines"].append(f"Delivery incoming from {quest.origin_town_name}.")
                elif touches_origin:
                    summary["lines"].append(f"Delivery posted for {quest.target_region_name}.")
            elif quest.kind == "scout":
                if touches_target and quest.stage == 0:
                    label = quest.target_landmark_name or quest.target_region_name
                    summary["lines"].append(f"Scout target: confirm {label}.")
                elif touches_origin and quest.stage >= 1:
                    summary["lines"].append("Scout report ready to turn in here.")
                elif touches_origin:
                    summary["lines"].append(f"Scout posted toward {quest.target_region_name}.")
            elif quest.kind == "bounty":
                if touches_target and quest.stage == 0:
                    summary["lines"].append(f"Bounty hunt active: {quest.target_count} foes.")
                elif touches_origin and quest.stage >= 1:
                    summary["lines"].append("Bounty turn-in ready here.")
                elif touches_origin:
                    summary["lines"].append(f"Bounty posted toward {quest.target_region_name}.")
            elif quest.kind == "chain":
                if touches_target and quest.stage <= 1:
                    if quest.objective_key == "hunt":
                        summary["lines"].append(f"Lead active: hunt {quest.target_count} foes.")
                    else:
                        summary["lines"].append(f"Lead active: recover {quest.item_name or 'proof'}.")
                elif touches_origin and quest.stage >= 2:
                    summary["lines"].append("Lead return ready here.")
                elif touches_origin:
                    summary["lines"].append(f"Lead posted toward {quest.target_region_name}.")
        deduped = []
        for line in summary["lines"]:
            if line not in deduped:
                deduped.append(line)
        summary["lines"] = deduped[:4]
        return summary

    def quest_tabs(self):
        return ["Active", "Completed"]

    def current_journal_entries(self):
        if self.journal_tab == 0:
            return [quest for quest in self.active_quests if quest.status == "active"]
        return list(reversed(self.completed_quests()))

    def quest_status_label(self, quest):
        if quest.status == "complete":
            return "Complete"
        if quest.kind == "delivery":
            return "Delivery"
        if quest.kind == "scout":
            return "Report Back" if quest.stage >= 1 else "Scouting"
        if quest.kind == "bounty":
            return "Turn In" if quest.stage >= 1 else "Bounty"
        if quest.kind == "chain":
            if quest.stage >= 2:
                return "Return Lead"
            if quest.objective_key == "hunt" and quest.stage == 1:
                return "Hunt Lead"
            if quest.objective_key == "survey" and quest.stage == 1:
                return "Survey Lead"
            if quest.stage == 1:
                return "Search Site"
            return "Follow Lead"
        return quest.kind.title()

    def quest_progress_text(self, quest):
        if quest.kind == "delivery":
            return f"Deliver to {self.quest_target_label(quest)} for {quest.reward_gold}g."
        if quest.kind == "scout":
            if quest.stage >= 1:
                home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
                return f"Lead confirmed. Return to {home_name} for {quest.reward_gold}g."
            if quest.target_landmark_name:
                target_label = f"{quest.target_landmark_name} in {self.quest_target_label(quest)}"
            else:
                target_label = self.quest_target_label(quest)
            home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
            return f"Confirm {target_label}, then return to {home_name} for {quest.reward_gold}g."
        if quest.kind == "bounty":
            if quest.stage == 0:
                return f"Reach {self.quest_target_label(quest)}, hunt {quest.target_count} foes, then return for {quest.reward_gold}g."
            kills = max(0, self.enemies_defeated - quest.progress_count)
            if quest.status == "complete":
                kills = quest.target_count
            home_name = quest.origin_town_name or f"({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
            return f"{min(kills, quest.target_count)}/{quest.target_count} foes defeated. Return to {home_name} for {quest.reward_gold}g."
        if quest.kind == "chain":
            return self.chain_stage_text(quest)
        return f"Reward {quest.reward_gold}g."

    def journal_entry_lines(self, quest):
        region_name = quest.origin_town_name or self.region_name
        origin_label = f"{region_name} - ({quest.from_world_pos[0]}, {quest.from_world_pos[1]})"
        status_line = f"Completed from {origin_label}." if quest.status == "complete" else f"Posted from {origin_label}."
        return [self.quest_progress_text(quest), status_line]

    def quest_summary_counts(self):
        active = len([quest for quest in self.active_quests if quest.status == "active"])
        completed = len(self.completed_quests())
        helped = self.total_towns_helped()
        counts = self.completed_quest_counts()
        return {
            "active": active,
            "completed": completed,
            "towns_helped": helped,
            "delivery": counts.get("delivery", 0),
            "scout": counts.get("scout", 0),
            "bounty": counts.get("bounty", 0),
            "chain": counts.get("chain", 0),
        }

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

    def current_journal_summary_lines(self):
        counts = self.quest_summary_counts()
        if self.journal_tab == 0:
            return [f"{counts['active']} active"]
        return [
            f"{counts['completed']} completed",
            f"Towns helped {counts['towns_helped']}  -  D {counts['delivery']} / S {counts['scout']} / B {counts['bounty']} / C {counts['chain']}",
        ]

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
