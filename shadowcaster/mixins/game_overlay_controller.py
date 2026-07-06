from __future__ import annotations

from ..game_typing import GameMixinBase


class OverlayControllerMixin(GameMixinBase):

    def handle_controller_overlay_button(self, button):
        overlay = self.active_non_menu_overlay()
        if overlay == "locksmith":
            if button in (1, 7):
                self.close_locksmith()
            elif button == 0:
                self.locksmith_confirm_unlock()
            return True
        if overlay == "trade":
            if button in (1, 7):
                self.close_trade()
            elif button in (4, 5):
                self.trade_switch_panel()
            elif button == 0:
                if self.trade_panel == 0:
                    self.trade_buy()
                else:
                    self.trade_sell()
            return True
        if overlay == "choice":
            if button == 0:
                self.apply_current_choice()
            elif button in (4, 6):
                self.adjust_choice_index(-1)
            elif button in (5, 7):
                self.adjust_choice_index(1)
            elif button == 1 and self.town_choice_pending:
                self.town_choice_pending = None
                self.message = "You step away from the provisioner."
            return True
        if self.menu_mode:
            if button == 0:
                self.activate_menu_option()
            elif self.menu_mode == "controls" and button == 4:
                self.shift_controls_tab(-1)
            elif self.menu_mode == "controls" and button in (5, 7):
                self.shift_controls_tab(1)
            elif button == 1:
                if self.menu_mode == "pause":
                    self.close_menu()
                elif self.menu_mode in {"load", "controls"}:
                    self.return_to_parent_menu()
            return True
        if overlay == "tuner":
            if button in (1, 7):
                self.toggle_tuner()
            elif button == 4:
                self.shift_tuner_tab(-1)
            elif button == 5:
                self.shift_tuner_tab(1)
            elif button == 2:
                self.adjust_tuner_value(-1)
            elif button == 3:
                self.adjust_tuner_value(1)
            return True
        if overlay == "inventory":
            if button in (1, 7):
                self.toggle_inventory()
            elif button == 0:
                self.inventory_activate_selected()
            return True
        if overlay == "journal":
            if button in (1, 7):
                self.toggle_journal()
            elif button == 0:
                quest = self.selected_active_journal_quest()
                if quest is not None and self.can_show_map_for_selected_journal_quest():
                    self.open_world_map_for_quest(quest)
            elif button == 2:
                quest = self.selected_active_journal_quest()
                if quest is not None and self.can_abandon_selected_journal_quest():
                    self.abandon_quest(quest)
            elif button == 4:
                self.shift_journal_tab(-1)
            elif button == 5:
                self.shift_journal_tab(1)
            return True
        if overlay == "log":
            if button in (1, 7):
                self.toggle_log()
            return True
        if overlay == "notice_board":
            if button == 0:
                if self.notice_board_confirm_available():
                    self.accept_board_quest(self.notice_board_index)
            elif button in (1, 7):
                self.close_notice_board()
            return True
        if overlay == "world_map":
            if button in (1, 7):
                self.toggle_world_map()
            elif button in (4, 5):
                self.toggle_world_map_mode()
            elif button == 2:
                self.scroll_world_map_details(-72)
            elif button == 3:
                self.scroll_world_map_details(72)
            return True
        if overlay == "game_over":
            if button in (4, 6):
                self.shift_death_stats_tab(-1)
            elif button in (5, 7):
                self.shift_death_stats_tab(1)
            elif button in (0, 1, 9):
                self.open_pause_menu()
            return True
        if overlay == "levelup":
            choices = getattr(self, "levelup_ability_choices", [])
            if choices:
                if button == 14:  # dpad left
                    self.levelup_ability_index = (self.levelup_ability_index - 1) % len(choices)
                elif button == 15:  # dpad right
                    self.levelup_ability_index = (self.levelup_ability_index + 1) % len(choices)
                elif button in (0, 1, 7):
                    self.confirm_ability_choice(self.levelup_ability_index)
            else:
                if button in (0, 1, 7, 9):
                    self.dismiss_levelup()
            return True
        return False
