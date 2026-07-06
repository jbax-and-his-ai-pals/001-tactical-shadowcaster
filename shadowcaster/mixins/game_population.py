from __future__ import annotations

import random

from ..constants import (
    COLOR_HOSTILE_BEAST,
    COLOR_HOSTILE_SETTLER,
    INTERIOR_REGION_TYPES,
)
from ..enemy_catalog import ENEMY_CATALOG, biome_pool, weighted_choice
from ..game_typing import GameMixinBase
from ..models import Enemy
from ..systems import heuristic


def _build_enemy(position, key, rules) -> Enemy:
    spec = ENEMY_CATALOG[key]
    return Enemy(
        position=position,
        kind=spec["name"],
        color=spec["color"],
        damage=spec["damage"] + rules["enemy_damage_bonus"],
        marker=spec["marker"],
        max_health=spec["health"] + rules["enemy_health_bonus"],
        health=spec["health"] + rules["enemy_health_bonus"],
        on_hit_effect=spec.get("on_hit_effect") or rules["enemy_on_hit_effect"],
        attack_range=spec.get("attack_range", 1),
        preferred_range=spec.get("preferred_range", 1),
        moves_per_turn=spec.get("moves_per_turn", 1),
        behavior=spec.get("behavior", "pursuer"),
        traits=list(spec.get("traits", [])),
        catalog_key=key,
    )


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

    def _spawn_pool_for_region(self, threat: int) -> list[str]:
        """Build a weighted spawn pool for the current biome and danger tier."""
        rt = self.region_type
        level = getattr(self, "player_level", 1)
        pool = biome_pool(rt, threat, level)
        if not pool:
            pool = biome_pool("", threat, level)  # universal fillers
        if not pool:
            pool = ["stalker"]
        return pool

    def _pick_bookend(self, threat: int, index: int, enemy_count: int) -> str | None:
        """Return a bookend key for last-slot special enemies, or None."""
        rt = self.region_type
        if index != enemy_count - 1 or enemy_count <= 1:
            return None
        if rt in ("castle", "dungeon") and threat >= 4:
            return "dungeon_warden" if rt == "dungeon" else "castle_warden"
        if threat >= 5:
            return "warden"
        if threat >= 3:
            return "brute"
        return None

    def _pick_signature(self, threat: int) -> str | None:
        """Return a high-identity index-0 key for the current biome, or None."""
        rt = self.region_type
        # Explicit signatures that feel strongly biome-tied at first glance
        _sigs = {
            "forest":   {1: "pouncer",    3: "pack_hunter",  5: "shadow_stalker"},
            "swamp":    {1: "bogling",    3: "bog_shaman",   5: "plague_caller"},
            "plains":   {1: "raider",     3: "pack_raider",  5: "warlord"},
            "farmland": {1: "raider",     3: "siege_archer", 5: "warlord"},
            "desert":   {1: "dust_crawler",3:"hexer",        5: "sand_titan"},
            "mountain": {1: "sentinel",   3: "stone_golem",  5: "mountain_warden"},
            "tundra":   {1: "sentinel",   3: "frost_shaman", 5: "glacier_brute"},
            "cave":     {1: "bogling",    3: "lurker",       5: "lair_sentinel"},
            "dungeon":  {1: "trap_springer",3: "cave_brute",   5: "dungeon_warden"},
            "maze":     {1: "bogling",    3: "maze_specter", 5: "dungeon_warden"},
            "volcanic": {1: "ember_sprite",3:"cinder_hound", 5: "magma_titan"},
            "badlands": {1: "scorched_raider",3:"dust_wraith",5:"ash_warden"},
            "ruins":    {1: "grave_crawler",3:"armored_lurker",5:"lich"},
            "castle":   {1: "herald",     3: "knight",       5: "castle_warden"},
            "monster_town":{1:"goblin",   3:"orc_shaman",    5:"war_chief"},
            "stronghold":  {3:"knight",   4:"castle_warden", 5:"castle_warden"},
        }
        tiers = _sigs.get(rt, {})
        if not tiers:
            return None
        # Pick the highest threshold that does not exceed current threat
        best = None
        for threshold in sorted(tiers):
            if threat >= threshold:
                best = tiers[threshold]
        return best

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

        pool = self._spawn_pool_for_region(threat)
        with self.seed_scope("enemy_spawn", self.world_position, self.floor):
            rng = random.Random()

        for index in range(min(enemy_count, len(positions))):
            pos = positions[index]
            # Bookend slot
            bookend = self._pick_bookend(threat, index, enemy_count)
            if bookend and bookend in ENEMY_CATALOG:
                self.enemies.append(_build_enemy(pos, bookend, self.rules))
                continue
            # Signature slot (index 0)
            if index == 0:
                sig = self._pick_signature(threat)
                if sig and sig in ENEMY_CATALOG:
                    spec = ENEMY_CATALOG[sig]
                    if spec["tier_min"] <= threat and (spec["tier_max"] is None or spec["tier_max"] >= threat):
                        self.enemies.append(_build_enemy(pos, sig, self.rules))
                        continue
            # Generic weighted pick from biome pool
            key = weighted_choice(rng, pool)
            self.enemies.append(_build_enemy(pos, key, self.rules))

        self.enemies_spawned = len(self.enemies)

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
            spec = ENEMY_CATALOG.get(getattr(enemy, "catalog_key", ""), {})
            if spec.get("rarity") == "elite" and hasattr(self, "award_xp"):
                self.award_xp("found_named_elite")
            if hasattr(self, "ability_on_kill"):
                self.ability_on_kill()
            scavenge_gold = self.skill_scavenge_gold() if hasattr(self, "skill_scavenge_gold") else 0
            if scavenge_gold > 0:
                self.gold += scavenge_gold
            if hasattr(self, "_maybe_drop_locked_container"):
                self._maybe_drop_locked_container(enemy)
            if hasattr(self, "_maybe_drop_gem"):
                self._maybe_drop_gem(enemy)
            if hasattr(self, "_maybe_drop_curio"):
                self._maybe_drop_curio(enemy)
