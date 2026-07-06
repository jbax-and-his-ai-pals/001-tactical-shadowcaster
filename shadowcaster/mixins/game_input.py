from __future__ import annotations

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
    ACTION_MOVE,
    ACTION_NEW_GAME,
    ACTION_RANGED,
    ACTION_TUNER,
    ACTION_WORLD_MAP,
    INPUT_BINDINGS,
    MOVE_REPEAT_DELAY_MS,
    MOVE_REPEAT_INTERVAL_MS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    VIEW_HEIGHT,
    VIEW_WIDTH,
)
from ..game_typing import GameMixinBase
from ..persistence import has_save
from ..systems import direction_toward


class InputMixin(GameMixinBase):

    def refresh_controllers(self):
        self.controllers = {}
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            joystick.init()
            self.controllers[joystick.get_instance_id()] = joystick
        self.active_controller_id = next(iter(self.controllers), None)

    def add_controller(self, device_index):
        joystick = pygame.joystick.Joystick(device_index)
        joystick.init()
        self.controllers[joystick.get_instance_id()] = joystick
        if self.active_controller_id is None:
            self.active_controller_id = joystick.get_instance_id()

    def remove_controller(self, instance_id):
        self.controllers.pop(instance_id, None)
        if self.active_controller_id == instance_id:
            self.active_controller_id = next(iter(self.controllers), None)

    def controller_present(self):
        return self.active_controller_id is not None

    def controller_move_vector(self, x_value, y_value):
        dx = 0 if x_value == 0 else (1 if x_value > 0 else -1)
        dy = 0 if y_value == 0 else (-1 if y_value > 0 else 1)
        return (dx, dy) if dx or dy else None

    def controller_press_move(self, move, source="hat"):
        if not move:
            if source == "stick":
                if self.controller_move_source == "stick":
                    self.controller_held_move = None
                    self.controller_move_source = None
            else:
                self.controller_held_move = None
                self.controller_move_source = None
            return
        self.controller_held_move = move
        self.controller_move_source = source
        self.next_controller_repeat_ms = pygame.time.get_ticks() + MOVE_REPEAT_DELAY_MS
        self.perform_action(ACTION_MOVE, move)

    def clear_manual_movement(self):
        self.held_move = None
        self.next_repeat_ms = 0
        self.controller_held_move = None
        self.controller_move_source = None
        self.next_controller_repeat_ms = 0

    def controller_stick_move(self):
        if not self.controller_present():
            return None
        controller = self.controllers.get(self.active_controller_id)
        if controller is None or controller.get_numaxes() < 2:
            return None
        deadzone = 0.35
        x_value = controller.get_axis(0)
        y_value = controller.get_axis(1)
        if abs(x_value) < deadzone:
            x_value = 0.0
        if abs(y_value) < deadzone:
            y_value = 0.0
        dy = 0 if y_value == 0 else (1 if y_value > 0 else -1)
        dx = 0 if x_value == 0 else (1 if x_value > 0 else -1)
        return (dx, dy) if dx or dy else None

    def adjacent_enemy_at(self, position):
        enemy = self.get_enemy_at(position)
        if enemy and max(abs(enemy.position[0] - self.player[0]), abs(enemy.position[1] - self.player[1])) <= self.melee_range:
            return enemy
        return None

    def handle_touch_map_tap(self, screen_x, screen_y):
        action = self.touch_action_at(screen_x, screen_y)
        if action:
            if action == "menu":
                self.open_pause_menu()
            else:
                self.perform_action(action)
            return
        if self.inventory_button_rect().collidepoint(screen_x, screen_y):
            self.toggle_inventory()
            return
        if self.journal_button_rect().collidepoint(screen_x, screen_y):
            self.toggle_journal()
            return
        if self.log_button_rect().collidepoint(screen_x, screen_y):
            self.toggle_log()
            return
        position = self.world_from_screen(screen_x, screen_y)
        if position is None:
            return
        self.hovered_world_tile = position
        self.selected_inspect_tile = position
        resident = self.get_resident_at(position)
        if resident and max(abs(resident.position[0] - self.player[0]), abs(resident.position[1] - self.player[1])) == 1:
            self.stop_auto_movement()
            self.talk_to_resident(resident)
            return
        enemy = self.adjacent_enemy_at(position)
        if enemy and position in self.visible_tiles:
            self.stop_auto_movement()
            self.facing = direction_toward(self.player, enemy.position)
            self.attack()
            return
        dungeon = self.dungeon
        if dungeon is None:
            return
        if self.get_enemy_at(position) or dungeon.is_blocked(*position):
            return
        self.set_click_destination(position)

    def handle_touch_tap(self, screen_x, screen_y):
        self.touch_ui_active = True
        self.mouse_screen_pos = (screen_x, screen_y)
        active_overlay = self.active_non_menu_overlay()
        if active_overlay == "service_modal":
            self.handle_service_modal_click(screen_x, screen_y)
            return
        if active_overlay == "choice":
            self.handle_choice_click(screen_x, screen_y)
            return
        if self.menu_mode:
            self.handle_menu_click(screen_x, screen_y)
            return
        if active_overlay == "tuner":
            self.toggle_tuner()
            return
        if active_overlay == "inventory":
            self.handle_inventory_click(screen_x, screen_y, dismiss_on_miss=True)
            return
        if active_overlay == "journal":
            self.handle_journal_click(screen_x, screen_y, dismiss_on_miss=True)
            return
        if active_overlay == "log":
            self.handle_log_click(screen_x, screen_y, dismiss_on_miss=True)
            return
        if active_overlay == "trade":
            self.handle_trade_click(screen_x, screen_y)
            return
        if active_overlay == "notice_board":
            self.handle_notice_board_click(screen_x, screen_y)
            return
        if active_overlay == "world_map":
            self.handle_world_map_click(screen_x, screen_y, dismiss_on_miss=True)
            return
        if active_overlay == "game_over":
            self.handle_game_over_click(screen_x, screen_y, dismiss_on_miss=True)
            return
        if active_overlay == "levelup":
            self.handle_levelup_click(screen_x, screen_y)
            return
        self.handle_touch_map_tap(screen_x, screen_y)

    def world_from_screen(self, screen_x, screen_y):
        if screen_x >= VIEW_WIDTH * TILE_SIZE or screen_y >= VIEW_HEIGHT * TILE_SIZE:
            return None
        dungeon = self.dungeon
        if dungeon is None:
            return None
        tile_x = screen_x // TILE_SIZE + self.camera_x
        tile_y = screen_y // TILE_SIZE + self.camera_y
        return (tile_x, tile_y) if 0 <= tile_x < dungeon.width and 0 <= tile_y < dungeon.height else None

    def update_hovered_tile(self, screen_x, screen_y):
        self.mouse_screen_pos = (screen_x, screen_y)
        self.hovered_world_tile = self.world_from_screen(screen_x, screen_y)

    def handle_map_click(self, screen_x, screen_y):
        if self.inventory_button_rect().collidepoint(screen_x, screen_y):
            self.toggle_inventory()
            return
        if self.journal_button_rect().collidepoint(screen_x, screen_y):
            self.toggle_journal()
            return
        if self.log_button_rect().collidepoint(screen_x, screen_y):
            self.toggle_log()
            return
        position = self.world_from_screen(screen_x, screen_y)
        if position is None:
            return
        self.hovered_world_tile = position
        resident = self.get_resident_at(position)
        if resident and max(abs(resident.position[0] - self.player[0]), abs(resident.position[1] - self.player[1])) == 1:
            self.selected_inspect_tile = position
            self.stop_auto_movement()
            self.talk_to_resident(resident)
            return
        if self.terrain_kind_at(position) == "notice_board" and max(abs(position[0] - self.player[0]), abs(position[1] - self.player[1])) == 1:
            self.selected_inspect_tile = position
            self.stop_auto_movement()
            self._notice_board_interact()
            return
        service_spot = getattr(self.dungeon, "metadata", {}).get("service_spot")
        if service_spot and position == service_spot and max(abs(position[0] - self.player[0]), abs(position[1] - self.player[1])) <= 1 and not self.service_claimed:
            self.selected_inspect_tile = position
            self.stop_auto_movement()
            self.apply_town_service()
            return
        info = self.inspect_tile_info(position)
        if info:
            self.selected_inspect_tile = position
        self.set_click_destination(position)

    def open_travel_selection(self):
        self.travel_mode = False
        self.travel_choices = []
        self.auto_move_path = []
        self.clear_manual_movement()
        self.message = "Route selection is no longer used."

    def choose_travel_destination(self, index):
        self.message = "Route selection is no longer used."

    def perform_action(self, action, payload=None):
        if action == ACTION_NEW_GAME:
            self.start_new_game()
        elif action == ACTION_WORLD_MAP:
            self.toggle_world_map()
        elif action == ACTION_AUTOEXPLORE:
            self.start_autoexplore()
        elif action == ACTION_HEAL:
            self.stop_auto_movement()
            self.consume_medkit()
        elif action == ACTION_CLEANSE:
            self.stop_auto_movement()
            self.consume_tonic()
        elif action == ACTION_MELEE:
            self.stop_auto_movement()
            self.attack()
        elif action == ACTION_RANGED:
            self.stop_auto_movement()
            self.fire_ranged()
        elif action == ACTION_DESCEND:
            self.stop_auto_movement()
            self.descend()
        elif action == ACTION_TUNER:
            self.toggle_tuner()
        elif action == ACTION_INVENTORY:
            self.toggle_inventory()
        elif action == ACTION_JOURNAL:
            self.toggle_journal()
        elif action == ACTION_LOG:
            self.toggle_log()
        elif action == "minimap":
            self.minimap_open = not getattr(self, "minimap_open", False)
        elif action == ACTION_MOVE and payload:
            self.stop_pathing()
            self.try_move_player(*payload)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.FINGERDOWN:
                screen_x, screen_y = self.touch_screen_pos(event.x, event.y)
                self.handle_touch_tap(screen_x, screen_y)
                continue
            if event.type == pygame.JOYDEVICEADDED:
                self.add_controller(event.device_index)
                continue
            if event.type == pygame.JOYDEVICEREMOVED:
                self.remove_controller(event.instance_id)
                continue
            if event.type == pygame.JOYBUTTONDOWN:
                if self.handle_controller_button(event.button):
                    continue
            if event.type == pygame.JOYHATMOTION:
                move = self.controller_move_vector(event.value[0], event.value[1])
                if self.handle_hat_overlay_move(move):
                    continue
                self.controller_press_move(move)
                continue
            if self.handle_overlay_event(event):
                continue
            if event.type == pygame.MOUSEWHEEL and not self.active_overlay():
                self.scroll_message_log_by(-event.y)
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.open_pause_menu()
                continue
            if event.type == pygame.MOUSEMOTION:
                self.update_hovered_tile(*event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_map_click(*event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    self.scroll_message_log_by(1)
                    continue
                if event.key == pygame.K_PAGEDOWN:
                    self.scroll_message_log_by(-1)
                    continue
                if event.key == pygame.K_F9:
                    self.perf_overlay = not self.perf_overlay
                    continue
                if event.key == pygame.K_F10:
                    self.toggle_debug_omniscience()
                    continue
                if event.key == pygame.K_h and self.region_type == "shrine" and not self.active_overlay():
                    self.set_homepoint()
                    continue
                biome_debug = self.debug_biome_hotkeys().get(event.key)
                if biome_debug:
                    self.debug_jump_to_biome(biome_debug)
                    continue
                binding = INPUT_BINDINGS.get(event.key)
                if binding:
                    if binding[0] == ACTION_MOVE:
                        self.held_move = binding[1]
                        self.next_repeat_ms = pygame.time.get_ticks() + MOVE_REPEAT_DELAY_MS
                    self.perform_action(*binding)
            if event.type == pygame.KEYUP:
                binding = INPUT_BINDINGS.get(event.key)
                if binding and binding[0] == ACTION_MOVE and self.held_move == binding[1]:
                    self.held_move = None
        return True

    def handle_controller_button(self, button):
        if self.handle_controller_overlay_button(button):
            return True
        if button == 7:
            self.open_pause_menu()
        elif button == 6:
            self.perform_action(ACTION_WORLD_MAP)
        elif button == 4:
            self.perform_action(ACTION_HEAL)
        elif button == 5:
            self.perform_action(ACTION_CLEANSE)
        elif button in (8, 9):
            self.perform_action(ACTION_TUNER)
        elif button == 0:
            self.perform_action(ACTION_MELEE)
        elif button == 2:
            self.perform_action(ACTION_RANGED)
        elif button == 3:
            self.perform_action(ACTION_AUTOEXPLORE)
        elif button == 1:
            self.open_pause_menu()
        else:
            return False
        return True
