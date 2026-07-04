from __future__ import annotations

import unittest

from shadowcaster.models import Enemy
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(w: int = 12, h: int = 8) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def _combat_game(seed: int):
    game = make_game(seed)
    game.start_new_game()
    game.dungeon = build_open_map()
    game.player = (3, 3)
    game.facing = (1, 0)
    game.camera_x = 0
    game.camera_y = 0
    game.enemies = []
    game.residents = []
    game.landmarks = []
    game.edge_exits = {}
    game.stairs = None
    game.up_stairs = None
    game.delve_goal = None
    game.return_portal = None
    game.terrain_features = {}
    game.floor_explorable_tiles = {
        (x, y) for x in range(1, 11) for y in range(1, 7)
    }
    game.seen_tiles = set(game.floor_explorable_tiles)
    game.visible_tiles = set(game.floor_explorable_tiles)
    game.exploration_progress = 100
    game.claimed_exploration_rewards.add(100)
    return game


class CombatExtendedTests(unittest.TestCase):

    # --- attack() ---

    def test_attack_deals_damage_to_adjacent_enemy(self):
        game = _combat_game(1600)
        enemy = Enemy(position=(4, 3), kind="stalker", color=(200, 0, 0), health=5, max_health=5, damage=1)
        game.enemies = [enemy]
        before = enemy.health
        game.attack()
        self.assertLess(enemy.health, before)

    def test_attack_kills_enemy_at_zero_hp(self):
        game = _combat_game(1601)
        enemy = Enemy(position=(4, 3), kind="stalker", color=(200, 0, 0), health=1, max_health=1, damage=1)
        game.enemies = [enemy]
        game.attack()
        self.assertNotIn(enemy, game.enemies)

    def test_attack_increments_enemies_defeated(self):
        game = _combat_game(1602)
        enemy = Enemy(position=(4, 3), kind="stalker", color=(200, 0, 0), health=1, max_health=1, damage=1)
        game.enemies = [enemy]
        before = game.enemies_defeated
        game.attack()
        self.assertEqual(game.enemies_defeated, before + 1)

    def test_attack_with_no_enemy_reports_miss(self):
        game = _combat_game(1603)
        game.attack()
        self.assertIn("air", game.message.lower())

    def test_attack_facing_wall_reports_sparks(self):
        game = _combat_game(1604)
        game.player = (10, 3)
        game.facing = (1, 0)
        game.attack()
        self.assertIn("wall", game.message.lower())

    def test_attack_uses_effective_melee_damage(self):
        game = _combat_game(1605)
        game.add_item("warhammer", "Warhammer", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=3, ranged_bonus=0)
        game.equip_item("warhammer")
        enemy = Enemy(position=(4, 3), kind="stalker", color=(200, 0, 0), health=20, max_health=20, damage=1)
        game.enemies = [enemy]
        game.attack()
        expected_health = 20 - game.effective_melee_damage
        self.assertEqual(enemy.health, expected_health)

    # --- fire_ranged() ---

    def test_fire_ranged_with_no_ammo_prints_message(self):
        game = _combat_game(1610)
        game.ammo = 0
        game.fire_ranged()
        self.assertIn("empty", game.message.lower())

    def test_fire_ranged_consumes_one_ammo(self):
        game = _combat_game(1611)
        game.ammo = 5
        game.fire_ranged()
        self.assertEqual(game.ammo, 4)

    def test_fire_ranged_hits_enemy_in_line_of_sight(self):
        game = _combat_game(1612)
        game.ammo = 3
        enemy = Enemy(position=(7, 3), kind="stalker", color=(200, 0, 0), health=10, max_health=10, damage=1)
        game.enemies = [enemy]
        before = enemy.health
        game.fire_ranged()
        self.assertLess(enemy.health, before)

    def test_fire_ranged_in_desert_applies_burn(self):
        game = _combat_game(1613)
        game.ammo = 3
        game.region_type = "desert"
        game.rules = game.region_rules()
        enemy = Enemy(position=(7, 3), kind="stalker", color=(200, 0, 0), health=20, max_health=20, damage=1)
        game.enemies = [enemy]
        game.fire_ranged()
        self.assertIn("burn", enemy.status_effects)

    def test_fire_ranged_with_no_target_reports_shot(self):
        game = _combat_game(1614)
        game.ammo = 3
        game.fire_ranged()
        # Bounded map: shot either vanishes into the dark or splashes on stone — both are valid misses
        self.assertTrue(
            "dark" in game.message.lower() or "stone" in game.message.lower(),
            f"Unexpected miss message: {game.message}",
        )

    # --- apply_enemy_hit_effect ---

    def test_hit_effect_applies_status_without_ward(self):
        game = _combat_game(1620)
        enemy = Enemy(position=(4, 3), kind="shaman", color=(200, 0, 0), health=5, max_health=5,
                      damage=1, on_hit_effect="poison")
        game.player_statuses.pop("ward", None)
        game.apply_enemy_hit_effect(enemy, [])
        self.assertIn("poison", game.player_statuses)

    def test_hit_effect_is_blocked_by_ward(self):
        game = _combat_game(1621)
        enemy = Enemy(position=(4, 3), kind="shaman", color=(200, 0, 0), health=5, max_health=5,
                      damage=1, on_hit_effect="poison")
        game.player_statuses["ward"] = 3
        game.apply_enemy_hit_effect(enemy, [])
        self.assertNotIn("poison", game.player_statuses)

    def test_ward_decrements_when_blocking_hit_effect(self):
        game = _combat_game(1622)
        enemy = Enemy(position=(4, 3), kind="shaman", color=(200, 0, 0), health=5, max_health=5,
                      damage=1, on_hit_effect="poison")
        game.player_statuses["ward"] = 3
        game.apply_enemy_hit_effect(enemy, [])
        self.assertEqual(game.player_statuses["ward"], 2)

    def test_ward_expires_when_decremented_to_zero(self):
        game = _combat_game(1623)
        enemy = Enemy(position=(4, 3), kind="shaman", color=(200, 0, 0), health=5, max_health=5,
                      damage=1, on_hit_effect="poison")
        game.player_statuses["ward"] = 1
        game.apply_enemy_hit_effect(enemy, [])
        self.assertNotIn("ward", game.player_statuses)

    # --- choose_adjacent_enemy ---

    def test_choose_adjacent_enemy_returns_none_when_no_enemies(self):
        game = _combat_game(1630)
        self.assertIsNone(game.choose_adjacent_enemy())

    def test_choose_adjacent_enemy_returns_nearest_in_facing_direction(self):
        game = _combat_game(1631)
        close = Enemy(position=(4, 3), kind="stalker", color=(200, 0, 0), health=3, max_health=3, damage=1)
        far = Enemy(position=(6, 3), kind="stalker", color=(200, 0, 0), health=3, max_health=3, damage=1)
        game.enemies = [close, far]
        game.facing = (1, 0)
        result = game.choose_adjacent_enemy()
        self.assertEqual(result, close)

    # --- damage_enemy applies status ---

    def test_damage_enemy_applies_status_effect(self):
        game = _combat_game(1640)
        enemy = Enemy(position=(4, 3), kind="stalker", color=(200, 0, 0), health=10, max_health=10, damage=1)
        game.enemies = [enemy]
        game.damage_enemy(enemy, 1, effect="poison", duration=3)
        self.assertIn("poison", enemy.status_effects)
        self.assertEqual(enemy.status_effects["poison"], 3)


if __name__ == "__main__":
    unittest.main()
