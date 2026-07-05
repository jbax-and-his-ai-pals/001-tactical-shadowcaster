from __future__ import annotations

import pygame

from ..constants import SCREEN_WIDTH
from ..game_typing import GameMixinBase


class OverlayEventMixin(GameMixinBase):

    def close_service_modal(self):
        self.service_modal_open = False
        self.service_modal_title = ""
        self.service_modal_lines = []

    def handle_overlay_event(self, event):
        overlay = self.active_overlay()
        if not overlay:
            return False
        if overlay == "service_modal":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE):
                self.close_service_modal()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_service_modal_click(*event.pos)
            return True
        if overlay == "choice":
            if event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_choice_click(*event.pos)
            return True
        if overlay == "menu":
            if event.type == pygame.MOUSEMOTION:
                self.mouse_screen_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_menu_click(*event.pos)
            elif self.menu_mode == "controls" and event.type == pygame.MOUSEWHEEL:
                self.scroll_controls(-event.y * 36)
            return True
        if overlay == "tuner":
            if event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            return True
        if overlay == "inventory":
            if event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_inventory_click(*event.pos)
            return True
        if overlay == "journal":
            if event.type == pygame.MOUSEMOTION:
                self.mouse_screen_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_journal_click(*event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_journal(-event.y * 36)
            return True
        if overlay == "log":
            if event.type == pygame.MOUSEMOTION:
                self.mouse_screen_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_log_click(*event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_log(-event.y * 36)
            return True
        if overlay == "notice_board":
            if event.type == pygame.MOUSEMOTION:
                self.mouse_screen_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_notice_board_click(*event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_notice_board(-event.y * 36)
            return True
        if overlay == "trade":
            if event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_trade_click(*event.pos)
            return True
        if overlay == "travel":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.choose_travel_destination(0)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.choose_travel_destination(1)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.choose_travel_destination(2)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.choose_travel_destination(self.travel_choice_from_screen(*event.pos))
            return True
        if overlay == "world_map":
            if event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_screen_pos = event.pos
                if self.world_map_dragging:
                    self.update_world_map_drag(*event.pos)
                else:
                    self.update_world_map_hover(*event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.handle_world_map_click(*event.pos):
                    self.begin_world_map_drag(*event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.end_world_map_drag(event.pos[0], event.pos[1], getattr(event, "clicks", 1))
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_world_map_wheel(event)
            return True
        if overlay == "game_over":
            if event.type == pygame.KEYDOWN:
                self.handle_overlay_keydown(event)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_screen_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_game_over_click(*event.pos)
            return True
        return False

    def handle_overlay_keydown(self, event):
        overlay = self.active_non_menu_overlay()
        if overlay == "trade":
            if event.key == pygame.K_ESCAPE:
                self.close_trade()
            elif event.key in (pygame.K_TAB, pygame.K_q, pygame.K_e):
                self.trade_switch_panel()
            elif event.key in (pygame.K_UP, pygame.K_w):
                if self.trade_panel == 0:
                    self.trade_move_stock(-1)
                else:
                    self.trade_move_pack(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.trade_panel == 0:
                    self.trade_move_stock(1)
                else:
                    self.trade_move_pack(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.trade_panel == 0:
                    self.trade_buy()
                else:
                    self.trade_sell()
            return True
        if overlay == "choice":
            if event.key == pygame.K_ESCAPE and self.town_choice_pending:
                self.town_choice_pending = None
                self.message = "You step away from the provisioner."
            elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                self.adjust_choice_index(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                self.adjust_choice_index(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.apply_current_choice()
            return True
        if self.menu_mode:
            if event.key == pygame.K_ESCAPE:
                if self.menu_mode == "pause":
                    self.close_menu()
                elif self.menu_mode in {"load", "controls"}:
                    self.return_to_parent_menu()
            elif self.menu_mode == "controls" and event.key in (pygame.K_UP, pygame.K_w):
                self.scroll_controls(-36)
            elif self.menu_mode == "controls" and event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll_controls(36)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(self.menu_options())
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(self.menu_options())
            elif self.menu_mode == "controls" and event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_q, pygame.K_TAB):
                self.shift_controls_tab(-1)
            elif self.menu_mode == "controls" and event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_e):
                self.shift_controls_tab(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.activate_menu_option()
            return True
        if overlay == "tuner":
            if event.key in (pygame.K_t, pygame.K_ESCAPE):
                self.toggle_tuner()
            elif event.key in (pygame.K_TAB, pygame.K_q):
                self.shift_tuner_tab(-1)
            elif event.key == pygame.K_e:
                self.shift_tuner_tab(1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_tuner_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_tuner_selection(1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.adjust_tuner_value(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.adjust_tuner_value(1)
            return True
        if overlay == "notice_board":
            if event.key == pygame.K_ESCAPE:
                self.close_notice_board()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.notice_board_index = (self.notice_board_index - 1) % max(1, len(self.notice_board_quests))
                self.ensure_notice_board_selection_visible()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.notice_board_index = (self.notice_board_index + 1) % max(1, len(self.notice_board_quests))
                self.ensure_notice_board_selection_visible()
            elif event.key == pygame.K_PAGEUP:
                self.scroll_notice_board(-144)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_notice_board(144)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.notice_board_confirm_available():
                    self.accept_board_quest(self.notice_board_index)
            return True
        if overlay == "inventory":
            if event.key in (pygame.K_i, pygame.K_ESCAPE):
                self.toggle_inventory()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_inventory_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_inventory_selection(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.inventory_activate_selected()
            return True
        if overlay == "journal":
            if event.key in (pygame.K_j, pygame.K_ESCAPE):
                self.toggle_journal()
            elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_q, pygame.K_TAB):
                self.shift_journal_tab(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_e):
                self.shift_journal_tab(1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_journal_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_journal_selection(1)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_journal(-144)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_journal(144)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_m):
                quest = self.selected_active_journal_quest()
                if quest is not None and self.can_show_map_for_selected_journal_quest():
                    self.open_world_map_for_quest(quest)
            elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                quest = self.selected_active_journal_quest()
                if quest is not None and self.can_abandon_selected_journal_quest():
                    self.abandon_quest(quest)
            return True
        if overlay == "log":
            if event.key in (pygame.K_l, pygame.K_ESCAPE):
                self.toggle_log()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll_log(-36)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll_log(36)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_log(-144)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_log(144)
            return True
        if overlay == "world_map":
            if event.key in (pygame.K_m, pygame.K_ESCAPE):
                self.toggle_world_map()
            elif event.key == pygame.K_TAB:
                self.toggle_world_map_mode()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.pan_world_map(0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.pan_world_map(0, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.pan_world_map(-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.pan_world_map(1, 0)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_world_map_details(-72)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_world_map_details(72)
            elif event.key in (pygame.K_HOME, pygame.K_r):
                self.reset_world_map_view()
            return True
        if overlay == "game_over":
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_q):
                self.shift_death_stats_tab(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_e, pygame.K_TAB):
                self.shift_death_stats_tab(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.respawn()
            elif event.key == pygame.K_ESCAPE:
                self.open_main_menu()
            return True
        if overlay == "levelup":
            choices = getattr(self, "levelup_ability_choices", [])
            if choices:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.levelup_ability_index = (self.levelup_ability_index - 1) % len(choices)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.levelup_ability_index = (self.levelup_ability_index + 1) % len(choices)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if hasattr(self, "confirm_ability_choice"):
                        self.confirm_ability_choice(self.levelup_ability_index)
            else:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.dismiss_levelup()
            return True
        return False
