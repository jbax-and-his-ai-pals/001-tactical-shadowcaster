from __future__ import annotations

import random

from ..game_typing import GameMixinBase
from ..systems import find_path, heuristic


class CombatAIMixin(GameMixinBase):

    def _run_enemy_ai(self, enemy, effective_damage, occupied_positions, enemy_messages):
        """Run one enemy's AI turn, dispatching on behavior archetype."""
        behavior = getattr(enemy, "behavior", "pursuer")
        steps = max(1, enemy.moves_per_turn)

        for _step in range(steps):
            distance = heuristic(enemy.position, self.player)

            # Ranged attack — all behaviors attempt this first if in range
            if enemy.attack_range > 1 and distance <= enemy.attack_range and self.line_to_target(enemy.position):
                self.take_damage(effective_damage, f"the {enemy.kind}")
                effect_applied = self.apply_enemy_hit_effect(enemy, enemy_messages)
                if self.run_has_ended():
                    return
                effect_text = f" and inflicts {enemy.on_hit_effect}" if effect_applied else ""
                enemy_messages.append(f"The {enemy.kind} strikes from range for {effective_damage}{effect_text}.")
                return

            # Kiter: retreat when too close
            if (behavior == "kiter" or enemy.preferred_range > 1) and distance < enemy.preferred_range:
                dx = enemy.position[0] - self.player[0]
                dy = enemy.position[1] - self.player[1]
                retreat = (enemy.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0),
                           enemy.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0))
                if not self.dungeon.is_blocked(*retreat) and retreat not in occupied_positions:
                    occupied_positions.discard(enemy.position)
                    enemy.position = retreat
                    occupied_positions.add(enemy.position)
                return

            # Charger: straight-line dash at player
            if behavior == "charger":
                dx = self.player[0] - enemy.position[0]
                dy = self.player[1] - enemy.position[1]
                step = (
                    enemy.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0),
                    enemy.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0),
                )
                if step == self.player:
                    self.take_damage(effective_damage, f"the {enemy.kind}")
                    self.apply_enemy_hit_effect(enemy, enemy_messages)
                    if self.run_has_ended():
                        return
                    enemy_messages.append(f"The {enemy.kind} charges in for {effective_damage}!")
                    return
                if not self.dungeon.is_blocked(*step) and step not in occupied_positions:
                    occupied_positions.discard(enemy.position)
                    enemy.position = step
                    occupied_positions.add(enemy.position)
                    if _step == 0:
                        enemy_messages.append(f"The {enemy.kind} charges.")
                continue

            # Ambusher: waits at range, lunges when adjacent
            if behavior == "ambusher":
                if distance <= 2:
                    path = find_path(self.dungeon, enemy.position, self.player, occupied=occupied_positions - {enemy.position})
                    if path:
                        next_step = path[0]
                        if next_step == self.player:
                            self.take_damage(effective_damage, f"the {enemy.kind}")
                            self.apply_enemy_hit_effect(enemy, enemy_messages)
                            if self.run_has_ended():
                                return
                            enemy_messages.append(f"The {enemy.kind} lunges for {effective_damage}!")
                            return
                        occupied_positions.discard(enemy.position)
                        enemy.position = next_step
                        occupied_positions.add(enemy.position)
                return

            # Tank: advances slowly
            if behavior == "tank":
                if _step % 2 != 0:
                    continue
                path = find_path(self.dungeon, enemy.position, self.player, occupied=occupied_positions - {enemy.position})
                if path:
                    next_step = path[0]
                    if next_step == self.player:
                        self.take_damage(effective_damage, f"the {enemy.kind}")
                        self.apply_enemy_hit_effect(enemy, enemy_messages)
                        if self.run_has_ended():
                            return
                        enemy_messages.append(f"The {enemy.kind} slams you for {effective_damage}.")
                        return
                    occupied_positions.discard(enemy.position)
                    enemy.position = next_step
                    occupied_positions.add(enemy.position)
                    if _step == 0:
                        enemy_messages.append(f"The {enemy.kind} advances.")
                return

            # Swarmer: rushes in, relies on pack_bonus from allies
            if behavior == "swarmer":
                path = find_path(self.dungeon, enemy.position, self.player, occupied=occupied_positions - {enemy.position})
                if path:
                    next_step = path[0]
                    if next_step == self.player:
                        self.take_damage(effective_damage, f"the {enemy.kind}")
                        self.apply_enemy_hit_effect(enemy, enemy_messages)
                        if self.run_has_ended():
                            return
                        enemy_messages.append(f"The {enemy.kind} swarms you for {effective_damage}.")
                        return
                    occupied_positions.discard(enemy.position)
                    enemy.position = next_step
                    occupied_positions.add(enemy.position)
                continue

            # Flanker: tries to reach a side position relative to player
            if behavior == "flanker":
                px, py = self.player
                flank_targets = [
                    (px + fdx, py + fdy)
                    for fdx, fdy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if (px + fdx, py + fdy) not in occupied_positions
                    and not self.dungeon.is_blocked(px + fdx, py + fdy)
                ]
                target = min(flank_targets, key=lambda t: heuristic(t, enemy.position)) if flank_targets else self.player
                path = find_path(self.dungeon, enemy.position, target, occupied=occupied_positions - {enemy.position})
                if path:
                    next_step = path[0]
                    if next_step == self.player:
                        self.take_damage(effective_damage, f"the {enemy.kind}")
                        self.apply_enemy_hit_effect(enemy, enemy_messages)
                        if self.run_has_ended():
                            return
                        enemy_messages.append(f"The {enemy.kind} flanks you for {effective_damage}.")
                        return
                    occupied_positions.discard(enemy.position)
                    enemy.position = next_step
                    occupied_positions.add(enemy.position)
                    if _step == 0:
                        enemy_messages.append(f"The {enemy.kind} circles.")
                continue

            # Default: pursuer
            path = find_path(self.dungeon, enemy.position, self.player, occupied=occupied_positions - {enemy.position})
            if path:
                next_step = path[0]
                if next_step == self.player:
                    self.take_damage(effective_damage, f"the {enemy.kind}")
                    effect_applied = self.apply_enemy_hit_effect(enemy, enemy_messages)
                    if self.run_has_ended():
                        return
                    effect_text = f" and inflicts {enemy.on_hit_effect}" if effect_applied else ""
                    enemy_messages.append(f"The {enemy.kind} hits you for {effective_damage}{effect_text}.")
                    return
                occupied_positions.discard(enemy.position)
                enemy.position = next_step
                occupied_positions.add(enemy.position)
                if _step == 0:
                    label = "dashes" if enemy.moves_per_turn > 1 else "closes in"
                    enemy_messages.append(f"The {enemy.kind} {label}.")
            else:
                break

    def _try_call_reinforcement(self, enemy, occupied_positions, enemy_messages):
        """Spawn a low-tier ally adjacent to the caller (8% chance, caller decides)."""
        from ..enemy_catalog import biome_pool, ENEMY_CATALOG
        from ..models import Enemy
        pool = [k for k in biome_pool(self.region_type, 1) if k not in ("warden", "brute")]
        if not pool:
            return
        key = random.choice(pool)
        spec = ENEMY_CATALOG[key]
        ex, ey = enemy.position
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            pos = (ex + dx, ey + dy)
            if not self.dungeon.is_blocked(*pos) and pos not in occupied_positions and pos != self.player:
                new_enemy = Enemy(
                    position=pos,
                    kind=spec["name"],
                    color=spec["color"],
                    damage=spec["damage"] + self.rules["enemy_damage_bonus"],
                    marker=spec["marker"],
                    max_health=spec["health"] + self.rules["enemy_health_bonus"],
                    health=spec["health"] + self.rules["enemy_health_bonus"],
                    on_hit_effect=spec.get("on_hit_effect"),
                    attack_range=spec.get("attack_range", 1),
                    preferred_range=spec.get("preferred_range", 1),
                    moves_per_turn=spec.get("moves_per_turn", 1),
                    behavior=spec.get("behavior", "pursuer"),
                    traits=list(spec.get("traits", [])),
                )
                self.enemies.append(new_enemy)
                occupied_positions.add(pos)
                if pos in self.visible_tiles:
                    enemy_messages.append(f"The {enemy.kind} calls for aid!")
                return
