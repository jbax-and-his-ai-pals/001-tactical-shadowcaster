from __future__ import annotations

import unittest

from shadowcaster.models import Enemy
from shadowcaster.tests.support import make_game


class CombatTests(unittest.TestCase):

    # --- take_damage / effective_defense ---

    def test_take_damage_reduces_health(self):
        game = make_game(100)
        game.start_new_game()
        before = game.health
        game.take_damage(3)
        self.assertEqual(game.health, before - 3)
        self.assertFalse(game.game_over)

    def test_effective_defense_reduces_incoming_damage(self):
        game = make_game(101)
        game.start_new_game()
        game.add_item("chain_mail", "Chain Mail", "armor", (200, 200, 200), "armor",
                      defense_bonus=2)
        game.equip_item("chain_mail")
        self.assertEqual(game.effective_defense, 2)
        before = game.health
        game.take_damage(5)
        self.assertEqual(game.health, before - 3)

    def test_take_damage_floors_at_one_not_zero_due_to_defense(self):
        game = make_game(102)
        game.start_new_game()
        game.add_item("plate_coat", "Plate Coat", "armor", (200, 200, 200), "armor",
                      defense_bonus=10)
        game.equip_item("plate_coat")
        before = game.health
        game.take_damage(2)
        self.assertEqual(game.health, before - 1)

    def test_take_damage_triggers_game_over(self):
        game = make_game(103)
        game.start_new_game()
        game.health = 1
        game.take_damage(10)
        self.assertTrue(game.game_over)
        self.assertEqual(game.health, 0)

    # --- damage_enemy / remove_enemy ---

    def test_damage_enemy_reduces_health(self):
        game = make_game(110)
        game.start_new_game()
        enemy = Enemy(position=game.player, kind="stalker", color=(255, 0, 0))
        enemy.health = 5
        enemy.max_health = 5
        game.enemies = [enemy]
        game.damage_enemy(enemy, 2)
        self.assertEqual(enemy.health, 3)
        self.assertIn(enemy, game.enemies)

    def test_damage_enemy_removes_enemy_at_zero_hp(self):
        game = make_game(111)
        game.start_new_game()
        enemy = Enemy(position=game.player, kind="stalker", color=(255, 0, 0))
        enemy.health = 3
        enemy.max_health = 3
        game.enemies = [enemy]
        game.damage_enemy(enemy, 3)
        self.assertNotIn(enemy, game.enemies)

    def test_damage_enemy_increments_defeated_counter(self):
        game = make_game(112)
        game.start_new_game()
        enemy = Enemy(position=game.player, kind="stalker", color=(255, 0, 0))
        enemy.health = 1
        enemy.max_health = 1
        game.enemies = [enemy]
        before = game.enemies_defeated
        game.damage_enemy(enemy, 99)
        self.assertEqual(game.enemies_defeated, before + 1)
        self.assertEqual(game.total_monsters_killed, before + 1)

    # --- status ticks ---

    def test_poison_tick_deals_damage(self):
        game = make_game(120)
        game.start_new_game()
        game.player_statuses["poison"] = 3
        before = game.health
        game.tick_player_statuses()
        self.assertEqual(game.health, before - 1)

    def test_burn_tick_deals_damage(self):
        game = make_game(121)
        game.start_new_game()
        game.player_statuses["burn"] = 2
        before = game.health
        game.tick_player_statuses()
        self.assertEqual(game.health, before - 1)

    def test_status_duration_decrements_each_tick(self):
        game = make_game(122)
        game.start_new_game()
        game.player_statuses["poison"] = 3
        game.tick_player_statuses()
        self.assertEqual(game.player_statuses.get("poison"), 2)

    def test_status_removed_when_expired(self):
        game = make_game(123)
        game.start_new_game()
        game.player_statuses["poison"] = 1
        game.tick_player_statuses()
        self.assertNotIn("poison", game.player_statuses)

    def test_enemy_poison_tick_deals_damage(self):
        game = make_game(124)
        game.start_new_game()
        enemy = Enemy(position=game.player, kind="stalker", color=(255, 0, 0))
        enemy.health = 5
        enemy.max_health = 5
        enemy.status_effects = {"poison": 2}
        game.enemies = [enemy]
        game.tick_enemy_statuses()
        self.assertEqual(enemy.health, 4)

    def test_enemy_removed_by_status_tick(self):
        game = make_game(125)
        game.start_new_game()
        enemy = Enemy(position=game.player, kind="stalker", color=(255, 0, 0))
        enemy.health = 1
        enemy.max_health = 1
        enemy.status_effects = {"poison": 1}
        game.enemies = [enemy]
        game.tick_enemy_statuses()
        self.assertNotIn(enemy, game.enemies)

    # --- ward ---

    def test_ward_is_consumed_blocking_hit_effect(self):
        game = make_game(130)
        game.start_new_game()
        game.player_statuses["ward"] = 3
        enemy = Enemy(position=game.player, kind="shaman", color=(255, 0, 0))
        enemy.on_hit_effect = "poison"
        enemy.on_hit_duration = 3
        enemy.damage = 2
        enemy_messages = []
        game.apply_enemy_hit_effect(enemy, enemy_messages)
        self.assertNotIn("poison", game.player_statuses)
        self.assertEqual(game.player_statuses.get("ward"), 2)

    # --- effective stats ---

    def test_effective_melee_adds_weapon_bonus(self):
        game = make_game(140)
        game.start_new_game()
        base = game.effective_melee_damage
        game.add_item("dagger", "Dagger", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=1, ranged_bonus=0)
        game.equip_item("dagger")
        self.assertEqual(game.effective_melee_damage, base + 1)

    def test_effective_ranged_adds_weapon_bonus(self):
        game = make_game(141)
        game.start_new_game()
        base = game.effective_ranged_damage
        game.add_item("longbow", "Longbow", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=0, ranged_bonus=2)
        game.equip_item("longbow")
        self.assertEqual(game.effective_ranged_damage, base + 2)

    def test_unequipped_weapon_does_not_add_bonus(self):
        game = make_game(142)
        game.start_new_game()
        base = game.effective_melee_damage
        game.add_item("dagger", "Dagger", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=1, ranged_bonus=0)
        self.assertEqual(game.effective_melee_damage, base)


if __name__ == "__main__":
    unittest.main()
