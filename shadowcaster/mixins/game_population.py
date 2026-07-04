from __future__ import annotations

import random

from ..constants import (
    COLOR_ENEMY,
    COLOR_ENEMY_BRUTE,
    COLOR_HOSTILE_BEAST,
    COLOR_HOSTILE_SETTLER,
    INTERIOR_REGION_TYPES,
)
from ..game_typing import GameMixinBase
from ..models import Enemy
from ..systems import heuristic


class PopulationMixin(GameMixinBase):

    def protected_arrival_tiles(self):
        tiles = {self.player, self.entrance, self.up_stairs, self.stairs, self.delve_goal}
        tiles.update(self.edge_exits.values())
        return {tile for tile in tiles if tile is not None}

    def enemy_spawn_positions(self, extra_exclude=None):
        used = self.reserved_special_tiles(include_units=True)
        if extra_exclude:
            used.update(tile for tile in extra_exclude if tile is not None)
        protected_tiles = self.protected_arrival_tiles()
        minimum_spacing = 4
        if self.region_type in ("town", "monster_town"):
            candidates = [
                (x, y)
                for x in range(1, self.dungeon.width - 1)
                for y in range(1, self.dungeon.height - 1)
                if self.dungeon.tiles[x][y] == 0
                and (x, y) in self.floor_explorable_tiles
                and (x, y) not in used
                and all(heuristic((x, y), protected) >= minimum_spacing for protected in protected_tiles)
            ]
            random.shuffle(candidates)
            candidates.sort(key=lambda position: heuristic(position, self.player), reverse=True)
            positions = []
            for position in candidates:
                if any(heuristic(position, existing) < 4 for existing in positions):
                    continue
                positions.append(position)
                used.add(position)
                if len(positions) >= 12:
                    break
            return positions
        spawn_rooms = self.dungeon.rooms[1:] or self.dungeon.rooms
        rooms_by_distance = sorted(spawn_rooms, key=lambda room: heuristic(room.center, self.player), reverse=True)
        positions = []
        for room in rooms_by_distance:
            if (
                room.center in self.floor_explorable_tiles
                and room.center not in used
                and all(heuristic(room.center, protected) >= minimum_spacing for protected in protected_tiles)
            ):
                positions.append(room.center)
                used.add(room.center)
        if positions:
            return positions
        for tile in sorted(self.floor_explorable_tiles, key=lambda position: heuristic(position, self.player), reverse=True):
            if tile in used:
                continue
            if any(heuristic(tile, protected) < max(2, minimum_spacing - 1) for protected in protected_tiles):
                continue
            positions.append(tile)
            used.add(tile)
        return positions

    def spawn_enemies(self):
        self.enemies = []
        if self.region_type in {"town"} | INTERIOR_REGION_TYPES:
            self.enemies_spawned = 0
            return
        positions = self.enemy_spawn_positions()
        threat = self.danger_value()
        enemy_count = min(1 + threat // 2, max(2, len(positions)))
        if threat <= 1 and self.is_overworld_region():
            enemy_count = min(1, len(positions))
        elif threat <= 2 and self.is_overworld_region():
            enemy_count = min(enemy_count, max(1, len(positions)))
        if self.region_type == "monster_town":
            enemy_count = min(enemy_count + 2, len(positions))
        for index in range(min(enemy_count, len(positions))):
            if self.region_type == "monster_town":
                if index % 2 == 0:
                    self.enemies.append(Enemy(positions[index], "mad settler", COLOR_HOSTILE_SETTLER, 1 + self.rules["enemy_damage_bonus"], "settler", 4 + self.rules["enemy_health_bonus"], 4 + self.rules["enemy_health_bonus"], self.rules["enemy_on_hit_effect"], 1, 1))
                else:
                    beast_damage = (1 if self.floor < 7 else 2) + self.rules["enemy_damage_bonus"]
                    self.enemies.append(Enemy(positions[index], "feral beast", COLOR_HOSTILE_BEAST, beast_damage, "beast", 5 + self.rules["enemy_health_bonus"], 5 + self.rules["enemy_health_bonus"], self.rules["enemy_on_hit_effect"], 1, 1))
                continue
            profile = self.enemy_profile_for_spawn(index, enemy_count)
            self.enemies.append(
                Enemy(
                    positions[index],
                    profile["kind"],
                    profile["color"],
                    profile["damage"] + self.rules["enemy_damage_bonus"],
                    profile["marker"],
                    profile["health"] + self.rules["enemy_health_bonus"],
                    profile["health"] + self.rules["enemy_health_bonus"],
                    profile.get("effect") or self.rules["enemy_on_hit_effect"],
                    profile.get("attack_range", 1),
                    profile.get("preferred_range", 1),
                    profile.get("moves_per_turn", 1),
                )
            )
        self.enemies_spawned = len(self.enemies)

    def _signature_enemy(self, threat):
        """Index-0 biome signature enemy, or None to use filler."""
        rt = self.region_type
        if threat <= 1 and self.is_overworld_region():
            if rt == "forest":
                return {"kind": "pouncer", "color": (255, 156, 96), "damage": 1, "marker": "beast", "health": 2}
            if rt == "swamp":
                return {"kind": "bogling", "color": (138, 188, 112), "damage": 1, "marker": "beast", "health": 2}
            if rt in {"mountain", "tundra"}:
                return {"kind": "sentinel", "color": (188, 196, 210), "damage": 1, "marker": "settler", "health": 4}
            return None
        if rt == "forest" and threat >= 2:
            return {"kind": "pouncer", "color": (255, 156, 96), "damage": 1, "marker": "beast", "health": 2}
        if rt in ("mountain", "tundra", "ruins", "castle") and threat >= 2:
            return {"kind": "sentinel", "color": (188, 196, 210), "damage": 1, "marker": "settler", "health": 4}
        if rt in ("plains", "desert", "farmland", "badlands") and threat >= 2:
            return {"kind": "archer", "color": (255, 210, 110), "damage": 1, "marker": "archer", "health": 3, "attack_range": 6, "preferred_range": 3}
        if rt == "swamp":
            if threat >= 4:
                return {"kind": "shaman", "color": (180, 110, 255), "damage": 1, "marker": "shaman", "health": 2, "effect": "poison", "attack_range": 4, "preferred_range": 2}
            return {"kind": "bogling", "color": (138, 188, 112), "damage": 1, "marker": "beast", "health": 2}
        if rt in ("cave", "maze", "volcanic"):
            if threat >= 3:
                effect = "burn" if rt == "volcanic" else "poison"
                return {"kind": "shaman", "color": (180, 110, 255), "damage": 1, "marker": "shaman", "health": 2, "effect": effect, "attack_range": 4, "preferred_range": 2}
            return {"kind": "bogling", "color": (138, 188, 112), "damage": 1, "marker": "beast", "health": 2}
        if rt in ("dungeon", "cave", "ruins") and threat >= 3:
            return {"kind": "lurker", "color": (160, 100, 220), "damage": 2, "marker": "enemy", "health": 2, "moves_per_turn": 2}
        if rt in ("desert", "volcanic", "badlands") and threat >= 3:
            effect = "burn" if rt == "volcanic" else "poison"
            return {"kind": "hexer", "color": (220, 160, 80), "damage": 1, "marker": "shaman", "health": 2,
                    "effect": effect, "attack_range": 5, "preferred_range": 4}
        return None

    def _biome_filler_pool(self, threat):
        """Candidate profiles for non-signature filler slots, weighted by biome."""
        rt = self.region_type
        stalker = {"kind": "stalker", "color": COLOR_ENEMY, "damage": 1, "marker": "enemy", "health": 3}
        pouncer = {"kind": "pouncer", "color": (255, 156, 96), "damage": 1, "marker": "beast", "health": 2}
        bogling = {"kind": "bogling", "color": (138, 188, 112), "damage": 1, "marker": "beast", "health": 2}
        sentinel = {"kind": "sentinel", "color": (188, 196, 210), "damage": 1, "marker": "settler", "health": 4}
        archer = {"kind": "archer", "color": (255, 210, 110), "damage": 1, "marker": "archer", "health": 3, "attack_range": 6, "preferred_range": 3}
        lurker = {"kind": "lurker", "color": (160, 100, 220), "damage": 2, "marker": "enemy", "health": 2, "moves_per_turn": 2}
        effect_sw = "poison"
        shaman_sw = {"kind": "shaman", "color": (180, 110, 255), "damage": 1, "marker": "shaman", "health": 2, "effect": effect_sw, "attack_range": 4, "preferred_range": 2}
        if rt == "forest":
            return [pouncer, pouncer, stalker] if threat <= 2 else [pouncer, stalker]
        if rt == "swamp":
            return [bogling, bogling, stalker] if threat < 4 else [bogling, shaman_sw, stalker]
        if rt in ("cave", "maze"):
            return [bogling, stalker] if threat < 3 else [bogling, lurker, stalker]
        if rt == "volcanic":
            effect_v = "burn"
            shaman_v = {**shaman_sw, "effect": effect_v}
            return [bogling, stalker] if threat < 3 else [shaman_v, bogling, stalker]
        if rt in ("plains", "farmland"):
            return [archer, stalker] if threat >= 2 else [stalker]
        if rt in ("desert", "badlands"):
            return [archer, stalker] if threat < 3 else [archer, stalker]
        if rt in ("mountain", "tundra"):
            return [sentinel, stalker] if threat >= 2 else [stalker]
        if rt in ("ruins", "castle"):
            return [sentinel, lurker, stalker] if threat >= 3 else [sentinel, stalker]
        if rt == "dungeon":
            return [lurker, stalker] if threat >= 3 else [stalker]
        return [stalker]

    def enemy_profile_for_spawn(self, index, enemy_count):
        threat = self.danger_value()
        rt = self.region_type
        # Warden bookend: last slot in castle/dungeon at high threat
        if rt in ("castle", "dungeon") and threat >= 4 and index == enemy_count - 1 and enemy_count > 1:
            return {"kind": "warden", "color": (140, 150, 160), "damage": 1, "marker": "enemy", "health": 7}
        # Brute bookend: last slot when threat is high enough and no warden
        if threat >= 3 and index == enemy_count - 1 and enemy_count > 1:
            return {"kind": "brute", "color": COLOR_ENEMY_BRUTE, "damage": 2, "marker": "enemy", "health": 5}
        # Signature enemy claims index 0
        if index == 0:
            sig = self._signature_enemy(threat)
            if sig:
                return sig
        # Biome-specific filler for remaining slots
        pool = self._biome_filler_pool(threat)
        return pool[index % len(pool)]

    def scatter_enemies(self):
        for enemy, position in zip(self.enemies, self.enemy_spawn_positions()):
            enemy.position = position

    def get_enemy_at(self, position):
        return next((enemy for enemy in self.enemies if enemy.position == position), None)

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            self.enemies_defeated += 1
            self.total_monsters_killed += 1
