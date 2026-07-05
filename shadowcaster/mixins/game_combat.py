from __future__ import annotations
import math
import random
import pygame
from ..constants import (
    AUTO_MOVE_INTERVAL_MS, COLOR_ACCENT, COLOR_ENEMY, COLOR_ENEMY_BRUTE,
    COLOR_FRIEND, COLOR_FRIEND_ANIMAL, COLOR_HEAL, COLOR_HOSTILE_BEAST,
    COLOR_HOSTILE_SETTLER, COLOR_ITEM_ARMOR, COLOR_ITEM_CONSUMABLE,
    COLOR_ITEM_WEAPON, COLOR_MEMORY_HEAL, COLOR_STAIRS, COLOR_TEXT,
    FOV_RADIUS, MOVE_REPEAT_DELAY_MS, MOVE_REPEAT_INTERVAL_MS,
    SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT, VIEW_WIDTH,
)
from ..models import Enemy, GroundItem, Item, Resident, UpgradePickup
from ..regions import RegionChoice
from ..systems import can_step, direction_toward, find_path, flood_reachable_tiles
from ..systems import heuristic
from ..game_typing import GameMixinBase


class CombatMixin(GameMixinBase):
    def _armor_damage_reduction(self):
        armor = self.equipped_armor
        if not armor:
            return 0
        if armor.key == "war_plate":
            return 2
        if armor.key == "leather_armor":
            return 1
        return 0

    def take_damage(self, amount, cause=None):
        if amount > 0:
            amount = max(1, amount - self.effective_defense - self._armor_damage_reduction())
            if hasattr(self, "ability_on_hit_received"):
                amount = self.ability_on_hit_received(amount)
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.trigger_death(cause or "Unknown")
            return
        self.update_visibility()

    def add_status(self, statuses, effect, duration):
        if not effect or duration <= 0:
            return False
        # Armor passives only modify statuses applied to the player
        if statuses is self.player_statuses and effect in ("poison", "burn"):
            armor = self.equipped_armor
            if armor:
                if armor.key == "war_plate":
                    return False  # immune to burn/poison
                if armor.key == "plate_coat" and random.random() < 0.25:
                    return False  # 25% chance to block
                if armor.key == "chain_mail":
                    duration = max(1, duration - 1)
            # Resistance halves duration
            resist_key = "resist_poison" if effect == "poison" else ("resist_fire" if effect == "burn" else None)
            if resist_key and resist_key in statuses:
                duration = max(1, duration // 2)
                del statuses[resist_key]
        current = statuses.get(effect, 0)
        statuses[effect] = max(current, duration)
        return statuses[effect] != current

    def status_summary(self):
        if not self.player_statuses:
            return "clear"
        labels = {
            "poison": "Poison", "burn": "Burn", "ward": "Ward",
            "regen": "Regen", "resist_poison": "ResPoison", "resist_fire": "ResFire",
            "fortify_attack": "AtkUp", "fortify_defense": "DefUp",
            "fortify_speed": "SwiftUp", "fortify_light": "SightUp",
        }
        return ", ".join(f"{labels.get(name, name.title())} {turns}t" for name, turns in sorted(self.player_statuses.items()))

    def tick_player_statuses(self):
        messages = []
        for effect in list(self.player_statuses):
            if effect == "poison":
                source = self.player_status_sources.get("poison")
                cause = f"poison from {source}" if source else "poison"
                self.take_damage(1, cause)
                messages.append("Poison drains 1 HP from you.")
            elif effect == "burn":
                source = self.player_status_sources.get("burn")
                cause = f"burn from {source}" if source else "burn"
                self.take_damage(1, cause)
                messages.append("Flames scorch you for 1 HP.")
            elif effect == "regen":
                if self.health < self.max_health:
                    self.health = min(self.max_health, self.health + 1)
                    messages.append("You regenerate 1 HP.")
            # fortify/resist statuses just tick down silently
            self.player_statuses[effect] -= 1
            if self.player_statuses[effect] <= 0:
                self.clear_player_status(effect)
                if effect not in ("poison", "burn"):
                    messages.append(f"The {effect.replace('_', ' ')} fades.")
                else:
                    messages.append(f"You shake off {effect}.")
            if self.game_over:
                break
        return messages

    def tick_enemy_statuses(self):
        messages = []
        for enemy in self.enemies[:]:
            for effect in list(enemy.status_effects):
                if effect == "poison":
                    enemy.health -= 1
                    messages.append(f"The {enemy.kind} suffers poison.")
                elif effect == "burn":
                    enemy.health -= 1
                    messages.append(f"The {enemy.kind} burns.")
                elif effect == "stun":
                    pass  # stun dealt with in enemy turn loop
                enemy.status_effects[effect] -= 1
                if enemy.status_effects[effect] <= 0:
                    del enemy.status_effects[effect]
                if enemy.health <= 0:
                    messages.append(f"The {enemy.kind} falls.")
                    self.remove_enemy(enemy)
                    break
        return messages

    def _weapon_passive_on_kill(self, kind):
        weapon = self.equipped_weapon
        if not weapon:
            return None
        if weapon.key == "dagger":
            gained = min(1, self.max_health - self.health)
            if gained > 0:
                self.health += gained
                return f"The kill restores {gained} HP."
        if weapon.key == "halberd":
            self.add_status(self.player_statuses, "ward", 1)
            return "The decisive blow grants ward."
        return None

    def damage_enemy(self, enemy, amount, effect=None, duration=0):
        enemy.health -= amount
        effect_applied = self.add_status(enemy.status_effects, effect, duration)
        if enemy.health <= 0:
            passive_msg = self._weapon_passive_on_kill(enemy.kind)
            self.remove_enemy(enemy)
            kill_msg = f"You bring down the {enemy.kind}."
            return f"{kill_msg} {passive_msg}" if passive_msg else kill_msg
        detail = f"The {enemy.kind} has {enemy.health}/{enemy.max_health} HP left."
        if effect_applied and effect:
            detail += f" {effect.title()} takes hold."
        return detail

    def choose_adjacent_enemy(self):
        current = self.player
        for _ in range(self.melee_range):
            current = (current[0] + self.facing[0], current[1] + self.facing[1])
            if self.dungeon.is_blocked(*current):
                break
            enemy = self.get_enemy_at(current)
            if enemy:
                return enemy
        adjacent = [enemy for enemy in self.enemies if max(abs(enemy.position[0] - self.player[0]), abs(enemy.position[1] - self.player[1])) == 1]
        if not adjacent:
            return None
        adjacent.sort(key=lambda enemy: (0 if enemy.position in self.visible_tiles else 1, 0 if enemy.position[0] == self.player[0] or enemy.position[1] == self.player[1] else 1, heuristic(self.player, enemy.position)))
        return adjacent[0]

    def line_to_target(self, target):
        direction = direction_toward(self.player, target)
        if direction == (0, 0):
            return []
        line = []
        current = (self.player[0] + direction[0], self.player[1] + direction[1])
        while 0 <= current[0] < self.dungeon.width and 0 <= current[1] < self.dungeon.height:
            line.append(current)
            if current == target:
                return line
            if self.dungeon.is_blocked(*current):
                return []
            current = (current[0] + direction[0], current[1] + direction[1])
        return []

    def choose_ranged_target(self):
        shot_line = []
        current = (self.player[0] + self.facing[0], self.player[1] + self.facing[1])
        while 0 <= current[0] < self.dungeon.width and 0 <= current[1] < self.dungeon.height:
            shot_line.append(current)
            if self.dungeon.is_blocked(*current):
                return None, shot_line
            enemy = self.get_enemy_at(current)
            if enemy:
                return enemy, shot_line
            current = (current[0] + self.facing[0], current[1] + self.facing[1])
        candidates = []
        for enemy in self.enemies:
            dx = enemy.position[0] - self.player[0]
            dy = enemy.position[1] - self.player[1]
            aligned = dx == 0 or dy == 0 or abs(dx) == abs(dy)
            if aligned and enemy.position in self.visible_tiles:
                line = self.line_to_target(enemy.position)
                if line:
                    candidates.append((heuristic(self.player, enemy.position), enemy, line))
        if not candidates:
            return None, shot_line
        _, enemy, line = sorted(candidates, key=lambda item: item[0])[0]
        return enemy, line

    def attack(self):
        if self.run_has_ended():
            return
        enemy = self.choose_adjacent_enemy()
        if enemy:
            self.attack_flash = enemy.position
            self.facing = direction_toward(self.player, enemy.position)
            message = self.damage_enemy(enemy, self.effective_melee_damage)
            weapon = self.equipped_weapon
            stun_msg = ""
            if weapon and weapon.key == "warhammer" and enemy in self.enemies and random.random() < 0.25:
                self.add_status(enemy.status_effects, "stun", 1)
                stun_msg = " The blow staggers it."
            self.after_player_turn(player_acted=False, base_message=f"You strike the {enemy.kind}. {message}{stun_msg}")
            return
        resident = self.choose_adjacent_resident()
        if resident is not None:
            self.talk_to_resident(resident)
            return
        target = (self.player[0] + self.facing[0], self.player[1] + self.facing[1])
        self.attack_flash = target
        if self.dungeon.is_blocked(*target):
            self.after_player_turn(player_acted=False, base_message="Your weapon sparks against the wall.")
            return
        self.after_player_turn(player_acted=False, base_message="Your swing cuts only empty air.")

    def fire_ranged(self):
        if self.run_has_ended():
            return
        if self.ammo <= 0:
            self.message = "Your ranged weapon clicks empty."
            return
        weapon = self.equipped_weapon
        if weapon and weapon.key == "shortbow":
            self._shortbow_shot_count = getattr(self, "_shortbow_shot_count", 0) + 1
            if self._shortbow_shot_count % 3 == 0:
                pass  # free shot — don't consume ammo
            else:
                self.ammo -= 1
        else:
            self._shortbow_shot_count = 0
            self.ammo -= 1
        enemy, shot_line = self.choose_ranged_target()
        self.shot_flash = shot_line
        if enemy:
            self.facing = direction_toward(self.player, enemy.position)
            damage = self.effective_ranged_damage + self.rules["ranged_bonus"]
            effect = "burn" if self.region_type == "desert" else None
            message = self.damage_enemy(enemy, damage, effect=effect, duration=2 if effect else 0)
            self.after_player_turn(player_acted=False, base_message=f"Your shot hits the {enemy.kind}. {message}")
            return
        if shot_line and self.dungeon.is_blocked(*shot_line[-1]):
            self.after_player_turn(player_acted=False, base_message="Your shot splashes against stone.")
            return
        self.after_player_turn(player_acted=False, base_message="Your shot vanishes into the dark.")

    def apply_enemy_hit_effect(self, enemy, enemy_messages):
        effect_applied = False
        if enemy.on_hit_effect and "ward" not in self.player_statuses:
            effect_applied = self.add_status(self.player_statuses, enemy.on_hit_effect, self.enemy_status_duration(enemy))
            if effect_applied:
                self.set_player_status_source(enemy.on_hit_effect, f"the {enemy.kind}")
        elif "ward" in self.player_statuses:
            self.player_statuses["ward"] -= 1
            if self.player_statuses["ward"] <= 0:
                del self.player_statuses["ward"]
            enemy_messages.append(f"Your ward blunts the {enemy.kind}'s curse.")
        return effect_applied

    def after_player_turn(self, player_acted=True, base_message=None):
        if self.run_has_ended():
            return
        self.turn_newly_discovered_tiles = set()
        self.update_visibility()
        item_message = self.collect_floor_items()
        if self.delve_reward_pending:
            self.message = item_message or "The delve terminus stirs. Choose your reward."
            return
        if self.exploration_reward_pending is not None:
            self.message = item_message or "Floor fully explored: choose a boon."
            return
        status_messages = self.tick_enemy_statuses()
        player_status_messages = self.tick_player_statuses()
        if self.run_has_ended():
            return
        pending_message = item_message or base_message or (f"You move through {self.region_name}." if player_acted else None)
        visible_enemies = [enemy for enemy in self.enemies if enemy.position in self.visible_tiles]
        occupied_positions = {enemy.position for enemy in self.enemies}
        enemy_messages = []
        for enemy in visible_enemies:
            if enemy.status_effects.get("stun", 0) > 0:
                enemy_messages.append(f"The {enemy.kind} is staggered.")
                continue
            # Trait: regen — heal 1 HP per turn if damaged
            if "regen" in enemy.traits and enemy.health < enemy.max_health:
                enemy.health = min(enemy.max_health, enemy.health + 1)
            # Trait: berserks — double damage at half HP
            effective_damage = enemy.damage
            if "berserks" in enemy.traits and enemy.health <= enemy.max_health // 2:
                effective_damage = enemy.damage * 2
            # Trait: pack_bonus — +1 damage if another friendly adjacent
            if "pack_bonus" in enemy.traits:
                allies_near = sum(
                    1 for other in self.enemies
                    if other is not enemy and heuristic(other.position, enemy.position) <= 2
                )
                if allies_near >= 1:
                    effective_damage += 1
            self._run_enemy_ai(enemy, effective_damage, occupied_positions, enemy_messages)
            if self.run_has_ended():
                return
            # Trait: calls_reinforcements — rare chance to spawn a low-tier ally nearby
            if "calls_reinforcements" in enemy.traits and not self.run_has_ended():
                if random.random() < 0.08:
                    self._try_call_reinforcement(enemy, occupied_positions, enemy_messages)
        self.move_residents()
        self.update_visibility()
        parts = [pending_message]
        if enemy_messages:
            parts.append(" ".join(enemy_messages[:2]))
        if status_messages:
            parts.append(" ".join(status_messages[:2]))
        if player_status_messages:
            parts.append(" ".join(player_status_messages[:2]))
        self.last_interest_tiles = self.visible_interest_tiles()
        self.message = " ".join(part for part in parts if part) or "The dungeon stays silent beyond your torchlight."
