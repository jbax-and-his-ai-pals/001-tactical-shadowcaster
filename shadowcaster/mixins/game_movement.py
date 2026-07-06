from __future__ import annotations

import random
import pygame

from ..constants import MOVE_REPEAT_INTERVAL_MS
from ..game_typing import GameMixinBase
from ..regions import RegionChoice
from ..systems import can_step, find_path

_SIGN_QUIPS = {
    "tavern": [
        "Ale cures most ills. The rest, we don't talk about.",
        "Trust the cook. Don't ask what's in the stew.",
        "No brawling. Unless it's Tuesday.",
        "Rooms rented by the night. Secrets kept for free.",
        "The house wine is worse than it sounds.",
        "Tab must be settled before departure. Or else.",
        "Mind your boots — the floor remembers everything.",
        "Travelers welcome. Trouble, less so.",
        "What happens in the common room stays in the common room.",
        "Finest spirits in the region. We've stopped comparing.",
    ],
    "hall": [
        "Speak plainly. Shout nothing.",
        "All grievances heard. All decisions final.",
        "Meeting days: whenever necessary.",
        "Civic duty is its own reward.",
    ],
    "supply": [
        "No credit extended. No exceptions.",
        "All sales final unless we made the error.",
        "Inspect before purchase.",
    ],
    "granary": [
        "Measure twice, pour once.",
        "All grain weighed at intake. All discrepancies noted.",
    ],
    "storehouse": [
        "Inventory is updated weekly. Mostly.",
        "Do not move items without a reason.",
    ],
}


class MovementMixin(GameMixinBase):

    def apply_terrain_effect(self):
        feature = self.terrain_features.get(self.player)
        if feature == "muck":
            applied = self.add_status(self.player_statuses, "poison", 2)
            if applied:
                self.set_player_status_source("poison", "the muck")
            return "The muck seeps into your boots." if applied else None
        if feature == "embers":
            applied = self.add_status(self.player_statuses, "burn", 2)
            if applied:
                self.set_player_status_source("burn", "the embers")
            return "Hot embers lick at your feet." if applied else None
        if feature == "high_ground":
            return "You climb onto higher ground."
        if feature == "well":
            if self.health < self.max_health:
                self.health = min(self.max_health, self.health + 1)
                return f"The well refreshes you. HP {self.health}/{self.max_health}."
            if "poison" in self.player_statuses or "burn" in self.player_statuses:
                self.clear_player_status("poison")
                self.clear_player_status("burn")
                return "The cool water washes your afflictions away."
        if feature and feature.startswith("trap_"):
            return self._trigger_trap(feature)
        return None

    def _trigger_trap(self, trap_kind: str) -> str:
        # Fieldcraft rank 2+ detects traps before stepping — auto-dodge
        fieldcraft = self.get_skill_rank("fieldcraft") if hasattr(self, "get_skill_rank") else 0
        if fieldcraft >= 2:
            self.terrain_features.pop(self.player, None)
            return f"You spot and avoid a {trap_kind.replace('_', ' ')}."
        # Remove the trap (one-use)
        self.terrain_features.pop(self.player, None)
        if trap_kind == "trap_spike":
            dmg = 3
            self.take_damage(dmg, "a spike trap")
            return f"A spike trap springs! You take {dmg} damage."
        if trap_kind == "trap_poison":
            self.add_status(self.player_statuses, "poison", 4)
            self.set_player_status_source("poison", "a poison trap")
            return "A poison trap releases a cloud of toxin. You are poisoned."
        if trap_kind == "trap_alarm":
            # Wake the two nearest enemies
            enemies = sorted(
                getattr(self, "enemies", []),
                key=lambda e: abs(e.position[0] - self.player[0]) + abs(e.position[1] - self.player[1])
            )
            count = 0
            for enemy in enemies[:2]:
                if hasattr(enemy, "status_effects"):
                    enemy.status_effects.pop("stun", None)
                count += 1
            return f"An alarm trap blares! {count} nearby {'enemy rushes' if count == 1 else 'enemies rush'} toward you."
        return f"A trap activates."

    def try_move_player(self, dx, dy, automated=False):
        if self.run_has_ended():
            return False
        # Cripple: 50% chance the move step is wasted
        if "cripple" in getattr(self, "player_statuses", {}) and not automated:
            if random.random() < 0.5:
                self.after_player_turn(base_message="You stumble — the cripple slows you.")
                return True
        previous_adjacent_residents = {resident.position for resident in self.adjacent_residents()}
        nx, ny = self.player[0] + dx, self.player[1] + dy
        if not can_step(self.dungeon, self.player, (nx, ny)):
            self.message = "A wall blocks your path."
            if automated:
                self.auto_move_path = []
            return False
        if self.get_enemy_at((nx, ny)):
            self.message = "An enemy blocks that tile."
            if automated:
                self.auto_move_path = []
            return False
        if self.get_resident_at((nx, ny)):
            self.talk_to_resident(self.get_resident_at((nx, ny)))
            if automated:
                self.auto_move_path = []
            return False
        landmark = next((landmark for landmark in self.landmarks if landmark.position == (nx, ny)), None)
        if dx == 0 or dy == 0:
            self.facing = (dx, dy)
        self.selected_inspect_tile = None
        self.player = (nx, ny)
        self.total_steps += 1
        if landmark:
            self.enter_landmark(landmark)
            return True
        exit_direction = self.edge_direction_at(self.player)
        if exit_direction:
            if self.in_local_region():
                self.leave_local_region()
            else:
                self.transition_to_world_region(exit_direction)
            return True
        if self.player == self.stairs or (self.up_stairs and self.player == self.up_stairs) or (
            self.bottom_reward_claimed and self.return_portal and self.player == self.return_portal
        ):
            self.stop_auto_movement()
            self.descend()
            return True
        if self.terrain_kind_at(self.player) == "notice_board" and self.region_type == "town":
            anchor = self.feature_anchor_at(self.player) or self.player
            if anchor != self._notice_board_anchor:
                self._notice_board_anchor = anchor
                self.stop_auto_movement()
                self._notice_board_interact()
                return True
        else:
            self._notice_board_anchor = None
        if self.terrain_kind_at(self.player) == "sign":
            anchor = self.feature_anchor_at(self.player) or self.player
            if anchor != self._last_sign_anchor:
                self._last_sign_anchor = anchor
                quips = _SIGN_QUIPS.get(self.region_type)
                if quips:
                    self.message = f'The sign reads: "{random.choice(quips)}"'
        else:
            self._last_sign_anchor = None
        service_spot = getattr(self.dungeon, "metadata", {}).get("service_spot")
        if service_spot and self.player == service_spot and not self.service_claimed:
            self.stop_auto_movement()
            self.apply_town_service()
            return True
        terrain_message = self.apply_terrain_effect()
        self.after_player_turn(base_message=terrain_message)
        if automated and self.should_interrupt_auto_move():
            self.halt_auto_movement(self.first_sighting_message())
        elif not automated and not self.visible_hostiles():
            self.maybe_interact_with_adjacent_resident(previous_adjacent_residents)
        elif not automated:
            self.last_interest_tiles = self.visible_interest_tiles()
        # Haste: free bonus step (no extra enemy turn)
        if not automated and "haste" in getattr(self, "player_statuses", {}) and not self.run_has_ended():
            bnx, bny = self.player[0] + dx, self.player[1] + dy
            if can_step(self.dungeon, self.player, (bnx, bny)) and not self.get_enemy_at((bnx, bny)):
                self.player = (bnx, bny)
                self.total_steps += 1
                self.update_visibility()
                self.update_camera()
        return True

    def edge_direction_at(self, position):
        for direction, tile in self.edge_exits.items():
            if tile == position:
                return direction
        return None

    def descend(self):
        if self.run_has_ended():
            return
        if self.delve_goal and self.player == self.delve_goal and self.bottom_reward_claimed and self.in_local_region():
            self.leave_local_region()
            self.message = f"The return portal carries you back to {self.region_name}."
            return
        if self.up_stairs and self.player == self.up_stairs and self.region_depth > 1 and self.in_local_region():
            self.store_current_region()
            previous_depth = self.region_depth - 1
            self.current_local_region = self.local_region_depth_key(self.local_region_base_key(), previous_depth)
            self.load_region_state(self.local_regions[self.current_local_region])
            self.player = self.safe_arrival_tile(self.stairs or self.entrance)
            self.update_visibility()
            self.last_interest_tiles = self.visible_interest_tiles()
            self.update_camera()
            self.message = f"You climb back to depth {self.region_depth}/{self.region_max_depth} of {self.region_name}."
            return
        if self.stairs is None or self.player != self.stairs:
            self.message = "You need to stand on the stairs to travel between depths."
            return
        if self.region_is_multilevel() and self.region_depth < self.region_max_depth:
            self.store_current_region()
            next_depth = self.region_depth + 1
            chosen = RegionChoice(region_type=self.region_type, name=self.region_name, summary="")
            next_key = self.local_region_depth_key(self.local_region_base_key(), next_depth) if self.in_local_region() else None
            if next_key and next_key in self.local_regions:
                self.current_local_region = next_key
                self.load_region_state(self.local_regions[next_key])
                self.player = self.safe_arrival_tile(self.up_stairs or self.entrance)
                self.update_visibility()
                self.last_interest_tiles = self.visible_interest_tiles()
                self.update_camera()
            else:
                self.floor += 1
                with self.seed_scope("build_floor", ("local", next_key or self.local_region_depth_key(self.local_region_base_key(), next_depth)), self.floor):
                    self.build_floor(
                        chosen_region=chosen,
                        delve_depth=next_depth,
                        delve_max_depth=self.region_max_depth,
                        fixed_danger_tier=self.danger_tier + 1,
                    )
                self.player = self.safe_arrival_tile(self.up_stairs or self.entrance)
                self.update_visibility()
                self.last_interest_tiles = self.visible_interest_tiles()
                self.update_camera()
                if next_key:
                    self.current_local_region = next_key
                    self.store_current_region()
            if self.region_depth == self.region_max_depth:
                self.message = f"You reach the bottom of {self.region_name}. A reward cache awaits."
            else:
                self.message = f"You descend deeper into {self.region_name} ({self.region_depth}/{self.region_max_depth})."
            return
        self.message = "There are no deeper stairs here."

    def set_click_destination(self, destination):
        if self.run_has_ended() or destination is None:
            return
        if destination == self.player:
            self.stop_auto_movement()
            return
        if self.on_screen_hostiles():
            self.message = "Click-to-move is disabled while a hostile is in view."
            return
        if destination not in self.seen_tiles:
            self.message = "You can only path to tiles you have already seen."
            return
        if self.dungeon.is_blocked(*destination):
            self.message = "That destination is blocked."
            return
        occupied = {enemy.position for enemy in self.enemies if enemy.position in self.visible_tiles}
        occupied.update(resident.position for resident in self.residents if resident.position in self.visible_tiles)
        occupied.update(landmark.position for landmark in self.landmarks if landmark.position != destination)
        occupied.update(tile for tile in self.autoexplore_blocked_tiles() if tile != destination)
        path = find_path(
            self.dungeon,
            self.player,
            destination,
            occupied=occupied,
            allowed_tiles=self.seen_tiles,
            tile_costs=self.hazardous_tile_costs(),
        )
        if not path:
            self.message = "No safe route to that tile."
            return
        self.autoexplore_active = False
        self.auto_move_path = path
        self.clear_manual_movement()
        self.next_auto_move_ms = pygame.time.get_ticks()
        self.message = "You start moving toward your marked destination."

    def update_continuous_movement(self):
        if self.world_map_open:
            self.update_world_map_center_animation()
        if self.world_map_open and self.world_map_mode == "local_debug":
            self.process_preview_generation(budget=1)
        if self.active_overlay():
            self.update_controller_overlay_navigation()
            return
        if self.active_non_menu_overlay():
            return
        now = pygame.time.get_ticks()
        analog_move = self.controller_stick_move()
        if analog_move:
            if self.controller_move_source != "stick" or self.controller_held_move != analog_move:
                self.controller_press_move(analog_move, source="stick")
        else:
            self.controller_press_move(None, source="stick")
        if self.autoexplore_active and not self.auto_move_path:
            if self.on_screen_hostiles():
                self.halt_auto_movement("Autoexplore halts because a hostile is in view.")
                return
            if self.exploration_progress >= 100 or self.exploration_effectively_complete():
                self.exploration_progress = 100
                self.halt_auto_movement("Autoexplore finishes. This floor is fully explored.")
                return
            path, target = self.find_autoexplore_path()
            if not path:
                if self.exploration_effectively_complete():
                    self.exploration_progress = 100
                    self.halt_auto_movement("Autoexplore finishes. This floor is fully explored.")
                    return
                self.halt_auto_movement("Autoexplore cannot find any more safe unexplored tiles.")
                return
            self.auto_move_path = path
            self.next_auto_move_ms = now
        if self.auto_move_path and now >= self.next_auto_move_ms:
            next_tile = self.auto_move_path.pop(0)
            moved = self.try_move_player(next_tile[0] - self.player[0], next_tile[1] - self.player[1], automated=True)
            self.next_auto_move_ms = now + self.autoexplore_interval
            if not moved:
                self.auto_move_path = []
            return
        held_move = self.held_move
        if held_move is not None and now >= self.next_repeat_ms:
            moved = self.try_move_player(held_move[0], held_move[1], automated=True)
            self.next_repeat_ms = now + MOVE_REPEAT_INTERVAL_MS
            if not moved:
                self.held_move = None
        controller_held_move = self.controller_held_move
        if controller_held_move is not None and now >= self.next_controller_repeat_ms:
            moved = self.try_move_player(controller_held_move[0], controller_held_move[1], automated=True)
            self.next_controller_repeat_ms = now + MOVE_REPEAT_INTERVAL_MS
            if not moved:
                self.controller_held_move = None
                self.controller_move_source = None
