from __future__ import annotations

from typing import cast

import pygame

from ..config import DEFAULT_WORLD_SEED
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
    AUTO_MOVE_INTERVAL_MS,
    COLOR_ACCENT,
    COLOR_HEAL,
    COLOR_MEMORY_HEAL,
    FOV_RADIUS,
    FPS,
    INPUT_BINDINGS,
    MOVE_REPEAT_DELAY_MS,
    MOVE_REPEAT_INTERVAL_MS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    VIEW_HEIGHT,
    VIEW_WIDTH,
)
from ..game_typing import GameMixinBase, RegionMapLike
from ..persistence import has_save, list_saves, load_game, save_game
from ..rendering import render_game
from ..systems import direction_toward


class GameCoreMixin(GameMixinBase):
    @staticmethod
    def default_tuning():
        return {
            "heal_pickup_floor_interval": 3,
            "heal_pickup_restore": 1,
            "heal_pickup_require_missing_hp": 1,
            "full_explore_vitality_bonus": 1,
            "full_explore_power_bonus": 1,
            "full_explore_recovery_medkits": 1,
            "full_explore_recovery_tonics": 1,
            "medkit_heal": 4,
            "bottom_reward_ammo": 2,
            "bottom_reward_medkits": 2,
            "delve_reward_vitality_bonus": 3,
            "delve_reward_power_bonus": 1,
            "delve_reward_recovery_tonics": 1,
            "vitality_upgrade_amount": 2,
            "power_upgrade_amount": 1,
            "light_upgrade_amount": 1,
            "haste_upgrade_amount": 8,
            "reach_upgrade_amount": 1,
            "completion_modal_duration_ms": 1500,
            "enemy_status_duration": 3,
            "shaman_poison_duration": 1,
        }

    @staticmethod
    def tuner_schema():
        return [
            {"key": "heal_pickup_floor_interval", "label": "Heal pickup every N floors", "min": 1, "max": 6, "step": 1},
            {"key": "heal_pickup_restore", "label": "Heal pickup restore", "min": 1, "max": 6, "step": 1},
            {"key": "heal_pickup_require_missing_hp", "label": "Require missing HP for spawn", "min": 0, "max": 1, "step": 1},
            {"key": "full_explore_vitality_bonus", "label": "100% vitality bonus", "min": 1, "max": 4, "step": 1},
            {"key": "full_explore_power_bonus", "label": "100% power bonus", "min": 1, "max": 3, "step": 1},
            {"key": "full_explore_recovery_medkits", "label": "100% reward medkits", "min": 0, "max": 3, "step": 1},
            {"key": "full_explore_recovery_tonics", "label": "100% reward tonics", "min": 0, "max": 3, "step": 1},
            {"key": "medkit_heal", "label": "Medkit healing", "min": 1, "max": 10, "step": 1},
            {"key": "enemy_status_duration", "label": "Enemy status duration", "min": 1, "max": 5, "step": 1},
            {"key": "shaman_poison_duration", "label": "Shaman poison duration", "min": 1, "max": 4, "step": 1},
            {"key": "bottom_reward_ammo", "label": "Delve reward: recovery ammo", "min": 0, "max": 5, "step": 1},
            {"key": "bottom_reward_medkits", "label": "Delve reward: recovery medkits", "min": 0, "max": 4, "step": 1},
            {"key": "delve_reward_vitality_bonus", "label": "Delve reward: vitality bonus", "min": 1, "max": 6, "step": 1},
            {"key": "delve_reward_power_bonus", "label": "Delve reward: power bonus", "min": 1, "max": 3, "step": 1},
            {"key": "delve_reward_recovery_tonics", "label": "Delve reward: recovery tonics", "min": 0, "max": 3, "step": 1},
            {"key": "vitality_upgrade_amount", "label": "Vitality upgrade HP", "min": 1, "max": 6, "step": 1},
            {"key": "power_upgrade_amount", "label": "Power upgrade damage", "min": 1, "max": 4, "step": 1},
            {"key": "light_upgrade_amount", "label": "Light upgrade radius", "min": 1, "max": 4, "step": 1},
            {"key": "haste_upgrade_amount", "label": "Haste upgrade (ms per pickup)", "min": 2, "max": 15, "step": 1},
            {"key": "reach_upgrade_amount", "label": "Reach upgrade (tiles per pickup)", "min": 1, "max": 2, "step": 1},
            {"key": "completion_modal_duration_ms", "label": "Popup duration (ms)", "min": 900, "max": 3000, "step": 100},
        ]

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tactical Shadowcaster")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self._message = ""
        self.message_log = []
        self.max_message_log = 50
        self.message_log_scroll = 0
        self.mouse_screen_pos = (0, 0)
        self.hovered_world_tile = None
        self.hovered_world_region = None
        self.selected_inspect_tile = None
        self.options = {"large_text": False, "reduced_flash": False, "persistent_memory": True}
        self.held_move: tuple[int, int] | None = None
        self.next_repeat_ms = 0
        self.controller_held_move: tuple[int, int] | None = None
        self.controller_move_source: str | None = None
        self.next_controller_repeat_ms = 0
        self.auto_move_path: list[tuple[int, int]] = []
        self.autoexplore_active = False
        self.next_auto_move_ms = 0
        self.dungeon = cast(RegionMapLike, None)
        self.last_interest_tiles = set()
        self.camera_x = 0
        self.camera_y = 0
        self.heal_color = COLOR_HEAL
        self.heal_memory_color = COLOR_MEMORY_HEAL
        self.travel_mode = False
        self.travel_choices = []
        self.world_map_open = False
        self.world_map_mode = "discovered"
        self.selected_world_region = None
        self.world_map_view_center = None
        self.world_map_detail_scroll = 0
        self.world_map_dragging = False
        self.world_map_drag_moved = False
        self.world_map_drag_anchor_screen = None
        self.world_map_drag_anchor_center = None
        self.world_map_center_animation = None
        self.preview_world_regions = {}
        self.preview_generation_queue = []
        self.preview_generation_keys = set()
        self.local_debug_target_coords = set()
        self.menu_mode = None
        self.menu_index = 0
        self.menu_scroll = 0
        self.menu_return_mode = "pause"
        self.controller_menu_move = None
        self.next_menu_repeat_ms = 0
        self.controls_tab = 0
        self.controls_scroll = [0, 0]
        self.tuner_open = False
        self.tuner_index = 0
        self.tuner_return_mode = None
        self.tuner_tab = 0
        self.inventory_open = False
        self.inventory_index = 0
        self.journal_open = False
        self.journal_tab = 0
        self.journal_scroll = 0
        self.log_open = False
        self.log_scroll = 0
        self.inventory = []
        self.gold = 0
        self.active_quests = []
        self.notice_board_open = False
        self.notice_board_quests = []
        self.notice_board_index = 0
        self.tuning = self.default_tuning()
        self.exploration_reward_pending = None
        self.town_choice_pending = None
        self.exploration_choice_index = 0
        self.completion_modal_text = ""
        self.death_stats_tab = 0
        self.death_cause = ""
        self.newly_discovered_tiles = set()
        self.turn_newly_discovered_tiles = set()
        self.save_entries = []
        self.menu_message = ""
        self.touch_ui_active = False
        self.controllers = {}
        self.active_controller_id = None
        self.running = True
        self.config_world_seed = DEFAULT_WORLD_SEED
        self.world_seed = None
        self.refresh_controllers()
        self.reset()
        self.open_main_menu()

    @property
    def light_radius(self):
        return self.base_light_radius + self.light_bonus

    @property
    def autoexplore_interval(self):
        return max(25, AUTO_MOVE_INTERVAL_MS - self.haste_bonus)

    @property
    def melee_range(self):
        return 1 + self.reach_bonus

    @property
    def equipped_weapon(self):
        return next((item for item in self.inventory if item.category == "weapon" and item.equipped), None)

    @property
    def equipped_armor(self):
        return next((item for item in self.inventory if item.category == "armor" and item.equipped), None)

    @property
    def effective_melee_damage(self):
        weapon = self.equipped_weapon
        return self.melee_damage + (weapon.melee_bonus if weapon else 0)

    @property
    def effective_ranged_damage(self):
        weapon = self.equipped_weapon
        return self.ranged_damage + (weapon.ranged_bonus if weapon else 0)

    @property
    def effective_defense(self):
        armor = self.equipped_armor
        return armor.defense_bonus if armor else 0

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        value = value or ""
        self._message = value
        if not value:
            return
        if not self.message_log or self.message_log[-1] != value:
            self.message_log.append(value)
            self.message_log_scroll = 0
            self.log_scroll = 0
            if len(self.message_log) > self.max_message_log:
                self.message_log = self.message_log[-self.max_message_log :]

    def reset(self):
        if self.world_seed is None:
            self.world_seed = self.new_run_seed()
        self.message_log = []
        self.message_log_scroll = 0
        self._message = ""
        self.floor = 1
        self.max_health = 12
        self.health = self.max_health
        self.weapon_name = "Blade"
        self.ammo = 3
        self.base_light_radius = FOV_RADIUS
        self.light_bonus = 0
        self.haste_bonus = 0
        self.reach_bonus = 0
        self.melee_damage = 2
        self.ranged_damage = 2
        self.inventory = []
        self.inventory_open = False
        self.inventory_index = 0
        self.journal_open = False
        self.journal_tab = 0
        self.journal_scroll = 0
        self.log_open = False
        self.log_scroll = 0
        self.floor_items = []
        self.add_starting_items()
        self.player_statuses = {}
        self.player_status_sources = {}
        self.facing = (1, 0)
        self.attack_flash = None
        self.shot_flash = []
        self.game_over = False
        self.death_cause = ""
        self.held_move = None
        self.auto_move_path = []
        self.autoexplore_active = False
        self.next_repeat_ms = 0
        self.controller_held_move = None
        self.controller_move_source = None
        self.next_controller_repeat_ms = 0
        self.next_auto_move_ms = 0
        self.travel_mode = False
        self.travel_choices = []
        self.world_map_open = False
        self.world_map_mode = "discovered"
        self.selected_world_region = None
        self.world_map_view_center = None
        self.world_map_detail_scroll = 0
        self.world_map_dragging = False
        self.world_map_drag_moved = False
        self.world_map_drag_anchor_screen = None
        self.world_map_drag_anchor_center = None
        self.world_map_center_animation = None
        self.preview_generation_queue = []
        self.preview_generation_keys = set()
        self.local_debug_target_coords = set()
        self.hovered_world_region = None
        self.hovered_world_tile = None
        self.selected_inspect_tile = None
        self.controller_menu_move = None
        self.next_menu_repeat_ms = 0
        self.controls_tab = 0
        self.controls_scroll = [0, 0]
        self.tuner_open = False
        self.tuner_index = 0
        self.tuner_return_mode = None
        self.tuner_tab = 0
        self.exploration_reward_pending = None
        self.delve_reward_pending = False
        self.town_choice_pending = None
        self.exploration_choice_index = 0
        self.notice_board_open = False
        self.notice_board_quests = []
        self.notice_board_index = 0
        self.completion_modal_text = ""
        self.death_stats_tab = 0
        self.newly_discovered_tiles = set()
        self.turn_newly_discovered_tiles = set()
        self.touch_ui_active = False
        self.world_position = (0, 0)
        self.world_regions = {}
        self.preview_world_regions = {}
        self.local_regions = {}
        self.current_local_region = None
        self.service_type = None
        self.service_claimed = False
        self.interaction_claims = set()
        self.region_depth = 1
        self.region_max_depth = 1
        self.danger_tier = 1
        self.danger_floor = 1
        self.bottom_reward_claimed = False
        self.delve_goal = None
        self.return_portal = None
        self.enemies_defeated = 0
        self.enemies_spawned = 0
        self.total_steps = 0
        self.total_monsters_killed = 0
        self.powerups_collected = {"light": 0, "vitality": 0, "power": 0, "haste": 0, "reach": 0, "heal": 0}
        self.medkits_used = 0
        self.tonics_used = 0
        self.best_exploration_percent = 0
        self.full_clears = 0
        with self.seed_scope("build_floor", ("world", (0, 0)), self.floor):
            self.build_floor(first_floor=True, chosen_region=self.choose_start_region())
        self.store_current_region()
        self.message = f"Move with WASD or arrows. Q/E/Z/C move diagonally. Space attacks, F fires. Seed {self.world_seed_label()}."

    def clear_inspect_focus(self):
        self.hovered_world_tile = None
        self.selected_inspect_tile = None

    def active_non_menu_overlay(self):
        if self.game_over:
            return "game_over"
        if self.has_pending_choice():
            return "choice"
        if self.notice_board_open:
            return "notice_board"
        if self.inventory_open:
            return "inventory"
        if self.journal_open:
            return "journal"
        if self.log_open:
            return "log"
        if self.tuner_open:
            return "tuner"
        if self.world_map_open:
            return "world_map"
        if self.travel_mode:
            return "travel"
        return None

    def active_overlay(self):
        if self.menu_mode:
            return "menu"
        return self.active_non_menu_overlay()

    def run_has_ended(self):
        return self.game_over

    def halt_auto_movement(self, message=None):
        self.stop_auto_movement()
        if message is not None:
            self.message = message

    def render(self):
        render_game(self)

    def run(self):
        self.running = True
        while self.running:
            keep_running = self.handle_input()
            if not self.running or not keep_running:
                break
            self.update_continuous_movement()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
