from __future__ import annotations

import pygame

from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT
from ..game_typing import GameMixinBase
from ..persistence import has_save, list_saves


class MenuUIMixin(GameMixinBase):

    def menu_options(self):
        if self.menu_mode == "main":
            return ["New Game", "Load Game", "Settings", "Exit"]
        if self.menu_mode == "controls":
            return ["Back"]
        if self.menu_mode == "load":
            return [entry["label"] for entry in self.save_entries] + ["Back"]
        if self.menu_mode == "settings":
            return self.settings_option_labels() + ["Back"]
        if self.menu_mode == "confirm_main_menu":
            return ["Yes — Save & Return", "No — Return Without Saving", "Cancel"]
        if self.menu_mode == "confirm_exit_game":
            return ["Yes — Save & Quit", "No — Quit Without Saving", "Cancel"]
        return ["Resume", "Save Game", "Load Game", "Settings", "Main Menu", "Exit Game"]

    def open_menu_mode(self, mode, *, return_mode=None, stop_auto=True, close_world_map=False, clear_inspect=True, reset_controls_tab=False):
        self.menu_mode = mode
        if return_mode is not None:
            self.menu_return_mode = return_mode
        self.menu_index = 0
        self.menu_scroll = 0
        self.menu_message = ""
        if reset_controls_tab:
            self.controls_tab = 0
        if stop_auto:
            self.stop_auto_movement()
        if close_world_map:
            self.world_map_open = False
        if clear_inspect:
            self.clear_inspect_focus()

    def open_main_menu(self):
        self.open_menu_mode("main", stop_auto=True, close_world_map=True)

    def open_pause_menu(self):
        self.open_menu_mode("pause", stop_auto=True, close_world_map=True)

    def open_load_menu(self, return_mode):
        self.save_entries = list_saves()
        self.open_menu_mode("load", return_mode=return_mode)

    def load_layout(self):
        box_width = 580
        box_height = 460
        left = (SCREEN_WIDTH - box_width) // 2
        top = 160
        footer_h = 40
        row_h = 52
        content_top = 14
        content_left = 14
        content_w = box_width - 28
        content_visible_h = box_height - content_top - footer_h - 10
        btn_h = 28
        btn_y = top + box_height - footer_h + (footer_h - btn_h) // 2
        back_width = 80
        back_left = left + box_width - back_width - 14
        load_btn_width = 130
        load_btn_left = back_left - load_btn_width - 10
        return {
            "box_width": box_width, "box_height": box_height,
            "left": left, "top": top, "footer_h": footer_h,
            "row_h": row_h, "content_top": content_top,
            "content_left": content_left, "content_w": content_w,
            "content_visible_h": content_visible_h,
            "back_width": back_width, "back_height": btn_h,
            "back_left": back_left, "back_top": btn_y,
            "load_btn_left": load_btn_left, "load_btn_width": load_btn_width,
            "load_btn_height": btn_h, "load_btn_top": btn_y,
            "max_visible": content_visible_h // row_h,
        }

    def load_scroll_clamp(self):
        layout = self.load_layout()
        max_scroll = max(0, len(self.save_entries) - layout["max_visible"])
        sel = self.menu_index if self.menu_index < len(self.save_entries) else len(self.save_entries) - 1
        if sel >= 0:
            if sel < self.menu_scroll:
                self.menu_scroll = sel
            elif sel >= self.menu_scroll + layout["max_visible"]:
                self.menu_scroll = sel - layout["max_visible"] + 1
        self.menu_scroll = max(0, min(max_scroll, self.menu_scroll))

    def open_controls_menu(self, return_mode):
        self.open_menu_mode("controls", return_mode=return_mode, reset_controls_tab=True)

    def open_settings_menu(self, return_mode):
        self._settings_parent = return_mode
        self.open_menu_mode("settings", return_mode=return_mode)

    def settings_option_labels(self):
        return ["Controls", f"Log Length: {self.max_message_log}"]

    def settings_adjust(self, delta):
        options = self.settings_option_labels()
        if not options or self.menu_index >= len(options):
            return
        label = options[self.menu_index]
        if label.startswith("Log Length"):
            choices = [50, 100, 200, 500]
            current = self.max_message_log
            idx = choices.index(current) if current in choices else 0
            self.max_message_log = choices[(idx + delta) % len(choices)]
            self.message_log = self.message_log[-self.max_message_log:]
            self.message = f"Log length set to {self.max_message_log}."

    def activate_menu_option(self):
        option = self.menu_options()[self.menu_index]
        if self.menu_mode == "load":
            if option == "Back":
                self.return_to_parent_menu()
            elif self.save_entries:
                self.load_run(self.save_entries[self.menu_index]["path"])
            return
        if self.menu_mode == "controls":
            if option == "Back":
                self.return_to_parent_menu()
            return
        if self.menu_mode == "confirm_main_menu":
            if option == "Yes — Save & Return":
                self.save_run()
                self.close_menu()
                self.open_main_menu()
            elif option == "No — Return Without Saving":
                self.close_menu()
                self.open_main_menu()
            else:
                self.return_to_parent_menu()
            return
        if self.menu_mode == "confirm_exit_game":
            if option == "Yes — Save & Quit":
                self.save_run()
                self.running = False
            elif option == "No — Quit Without Saving":
                self.running = False
            else:
                self.return_to_parent_menu()
            return
        if self.menu_mode == "settings":
            if option == "Back":
                self.return_to_parent_menu()
            elif option == "Controls":
                self.open_controls_menu("settings")
            else:
                self.settings_adjust(1)
            return
        if option == "New Game":
            self.start_new_game()
        elif option == "Load Game":
            if self.menu_mode == "main" and not has_save():
                self.menu_message = "No saves found."
            else:
                self.open_load_menu(self.menu_mode)
        elif option == "Controls":
            self.open_controls_menu(self.menu_mode)
        elif option == "Settings":
            self.open_settings_menu(self.menu_mode)
        elif option == "Tuner":
            self.toggle_tuner()
        elif option == "Save Game":
            self.save_run()
        elif option == "Resume":
            self.close_menu()
        elif option == "Main Menu":
            self.open_menu_mode("confirm_main_menu", return_mode="pause", stop_auto=False, clear_inspect=False)
        elif option == "Exit":
            self.running = False
        elif option == "Exit Game":
            self.open_menu_mode("confirm_exit_game", return_mode="pause", stop_auto=False, clear_inspect=False)

    def inventory_action_button_rects(self):
        panel_width = 720
        panel_height = 500
        left = (SCREEN_WIDTH - panel_width) // 2
        top = 136
        btn_y = top + panel_height - 100
        btn_h = 36
        use_rect = pygame.Rect(left + 20, btn_y, 150, btn_h)
        equip_rect = pygame.Rect(left + 20 + 150 + 12, btn_y, 190, btn_h)
        return {"use": use_rect, "equip": equip_rect}

    def visible_menu_options(self):
        options = self.menu_options()
        max_visible = 7 if self.menu_mode == "main" else 8
        if len(options) <= max_visible:
            self.menu_scroll = 0
            return options, 0
        if self.menu_index < self.menu_scroll:
            self.menu_scroll = self.menu_index
        if self.menu_index >= self.menu_scroll + max_visible:
            self.menu_scroll = self.menu_index - max_visible + 1
        return options[self.menu_scroll : self.menu_scroll + max_visible], self.menu_scroll

    def menu_layout(self):
        visible_options, scroll = self.visible_menu_options()
        box_width = 340 if self.menu_mode == "main" else 400 if self.menu_mode in {"settings", "confirm_main_menu", "confirm_exit_game"} else 360 if self.menu_mode == "pause" else 320
        box_height = 56 if self.menu_mode in {"main", "pause", "settings"} else 48
        gap = 14 if self.menu_mode in {"main", "pause", "settings"} else 10
        total_height = len(visible_options) * box_height + max(0, len(visible_options) - 1) * gap
        if self.menu_mode == "pause":
            top_limit = 72
            bottom_limit = SCREEN_HEIGHT - 72
        else:
            top_limit = 208
            bottom_limit = SCREEN_HEIGHT - 88
        available = max(total_height, bottom_limit - top_limit)
        start_y = top_limit + max(0, (available - total_height) // 2)
        left = (SCREEN_WIDTH - box_width) // 2
        return {
            "box_width": box_width,
            "box_height": box_height,
            "gap": gap,
            "left": left,
            "start_y": start_y,
            "visible_options": visible_options,
            "scroll": scroll,
        }

    def tuner_entries(self):
        entries = []
        for entry in self.tuner_schema():
            value = self.tuning[entry["key"]]
            display = "Yes" if entry["key"] == "heal_pickup_require_missing_hp" and value else "No" if entry["key"] == "heal_pickup_require_missing_hp" else str(value)
            entries.append({**entry, "value": value, "display": display})
        return entries

    def tuner_tabs(self):
        return ["Recovery", "Rewards", "Upgrades"]

    def grouped_tuner_entries(self):
        groups = {
            "Recovery": {"heal_pickup_floor_interval", "heal_pickup_restore", "heal_pickup_require_missing_hp", "medkit_heal"},
            "Rewards": {
                "full_explore_vitality_bonus",
                "full_explore_power_bonus",
                "full_explore_recovery_medkits",
                "full_explore_recovery_tonics",
                "bottom_reward_ammo",
                "bottom_reward_medkits",
            },
            "Upgrades": {"vitality_upgrade_amount", "power_upgrade_amount", "light_upgrade_amount"},
        }
        group_name = self.tuner_tabs()[self.tuner_tab]
        allowed = groups[group_name]
        return [entry for entry in self.tuner_entries() if entry["key"] in allowed]

    def toggle_tuner(self):
        active_overlay = self.active_overlay()
        if active_overlay not in {None, "tuner"}:
            return
        self.tuner_open = not self.tuner_open
        if self.tuner_open:
            self.tuner_return_mode = self.menu_mode
            self.tuner_tab = 0
            self.tuner_index = 0
        self.prepare_overlay_toggle(opening=self.tuner_open, clear_manual=True, close_menu_on_open=True)
        if self.tuner_open:
            self.message = "Balance tuner open."
        else:
            self.reopen_menu_if_needed(self.tuner_return_mode)
            self.tuner_return_mode = None
            self.message = f"You return to {self.region_name}."

    def adjust_tuner_value(self, delta):
        entries = self.grouped_tuner_entries()
        if not entries:
            return
        entry = entries[self.tuner_index]
        current = self.tuning[entry["key"]]
        new_value = max(entry["min"], min(entry["max"], current + entry["step"] * delta))
        if new_value == current:
            return
        self.tuning[entry["key"]] = new_value
        new_display = "Yes" if entry["key"] == "heal_pickup_require_missing_hp" and new_value else "No" if entry["key"] == "heal_pickup_require_missing_hp" else str(new_value)
        self.message = f"{entry['label']}: {new_display}"

    def toggle_inventory(self):
        active_overlay = self.active_overlay()
        if active_overlay not in {None, "inventory"}:
            return
        self.inventory_open = not self.inventory_open
        self.prepare_overlay_toggle(opening=self.inventory_open, clear_manual=True)
        if self.inventory_open:
            self.inventory_index = 0
            self.message = "Inventory open."
        else:
            self.message = f"You return to {self.region_name}."

    def toggle_journal(self):
        active_overlay = self.active_overlay()
        if active_overlay not in {None, "journal"}:
            return
        self.journal_open = not self.journal_open
        self.prepare_overlay_toggle(opening=self.journal_open, clear_manual=True)
        if self.journal_open:
            self.journal_tab = 0
            self.journal_scroll = 0
            self.journal_index = -1
            self.message = "Journal open."
        else:
            self.message = f"You return to {self.region_name}."

    def toggle_log(self):
        active_overlay = self.active_overlay()
        if active_overlay not in {None, "log"}:
            return
        self.log_open = not self.log_open
        self.prepare_overlay_toggle(opening=self.log_open, clear_manual=True)
        if self.log_open:
            self.log_scroll = 0
            self.message = "Recent log open."
        else:
            self.message = f"You return to {self.region_name}."

    def inventory_rows(self):
        rows = []
        for item in self.inventory:
            if item.category == "consumable":
                if item.quantity <= 0:
                    continue
                rarity = getattr(item, "rarity", "common")
                rarity_tag = f"[{rarity}] " if rarity != "common" else ""
                rows.append({"key": item.key, "label": f"{item.name} ×{item.quantity}", "detail": f"{rarity_tag}{item.description or 'Use this item'}", "action": "use", "color": item.color})
            elif item.category == "weapon":
                status = "Equipped" if item.equipped else "Owned"
                stat = f"+{item.melee_bonus} melee" if item.melee_bonus else f"+{item.ranged_bonus} ranged"
                rows.append({"key": item.key, "label": f"{item.name} ({status})", "detail": stat, "action": "equip", "color": item.color})
            elif item.category == "armor":
                status = "Equipped" if item.equipped else "Owned"
                rows.append({"key": item.key, "label": f"{item.name} ({status})", "detail": f"+{item.defense_bonus} defense", "action": "equip", "color": item.color})
            elif item.category == "trinket":
                status = "Equipped" if item.equipped else "Owned"
                rarity = getattr(item, "rarity", "uncommon")
                rarity_tag = f"[{rarity}] " if rarity != "uncommon" else ""
                rows.append({"key": item.key, "label": f"{item.name} ({status})", "detail": f"{rarity_tag}{item.description}", "action": "equip", "color": item.color, "locked": False})
            elif item.category == "quest":
                rows.append({"key": item.key, "label": item.name, "detail": "Quest item — cannot drop", "action": None, "color": item.color})
        has_trinket = any(item.category == "trinket" for item in self.inventory)
        if not has_trinket and getattr(self, "player_level", 1) < 2:
            rows.append({"key": "__trinket_locked__", "label": "Trinket Slot (Locked)", "detail": "Unlocks at Level 2 — Seasoned", "action": None, "color": (100, 90, 70), "locked": True})
        return rows

    def inventory_activate_selected(self):
        rows = self.inventory_rows()
        if not rows or self.inventory_index >= len(rows):
            return
        row = rows[self.inventory_index]
        if row["action"] is None:
            self.message = f"{row['label']}: {row['detail']}"
        elif row["action"] == "use":
            self.use_item(row["key"])
        else:
            self.equip_item(row["key"])
        self.inventory_index = min(self.inventory_index, max(0, len(self.inventory_rows()) - 1))

    def inventory_choice_from_screen(self, screen_x, screen_y):
        rows = self.inventory_rows()
        panel_width = 720
        left = (SCREEN_WIDTH - panel_width) // 2
        top = 136
        y = 20
        for index in range(len(rows)):
            row_rect = pygame.Rect(left + 12, top + y - 4, panel_width - 24, 30)
            if row_rect.collidepoint(screen_x, screen_y):
                return index
            y += 34
        return None

    def shift_tuner_tab(self, delta):
        tabs = self.tuner_tabs()
        self.tuner_tab = (self.tuner_tab + delta) % len(tabs)
        self.tuner_index = 0
        self.message = f"Tuner tab: {tabs[self.tuner_tab]}."

    def menu_choice_from_screen(self, screen_x, screen_y):
        if self.menu_mode == "controls":
            layout = self.controls_layout()
            if pygame.Rect(layout["back_left"], layout["back_top"], layout["back_width"], layout["back_height"]).collidepoint(screen_x, screen_y):
                return 0
            return None
        if self.menu_mode == "load":
            layout = self.load_layout()
            if pygame.Rect(layout["back_left"], layout["back_top"], layout["back_width"], layout["back_height"]).collidepoint(screen_x, screen_y):
                return len(self.save_entries)  # "Back" index in menu_options
            content_top_abs = layout["top"] + layout["content_top"]
            if content_top_abs <= screen_y < content_top_abs + layout["content_visible_h"]:
                row_i = (screen_y - content_top_abs) // layout["row_h"]
                save_idx = self.menu_scroll + row_i
                if 0 <= save_idx < len(self.save_entries):
                    return save_idx
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
