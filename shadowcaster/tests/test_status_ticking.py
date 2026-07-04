from __future__ import annotations

import unittest

from shadowcaster.models import Enemy
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(w=9, h=9) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def _open_game(seed: int):
    game = make_game(seed)
    game.start_new_game()
    game.dungeon = build_open_map()
    game.player = (4, 4)
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
        (x, y) for x in range(1, 8) for y in range(1, 8)
    }
    game.seen_tiles = set(game.floor_explorable_tiles)
    game.visible_tiles = set(game.floor_explorable_tiles)
    return game


class StatusTickingTests(unittest.TestCase):

    # --- add_status behaviour ---

    def test_add_status_sets_duration(self):
        game = make_game(1400)
        game.start_new_game()
        game.add_status(game.player_statuses, "poison", 3)
        self.assertEqual(game.player_statuses["poison"], 3)

    def test_add_status_does_not_reduce_existing_duration(self):
        game = make_game(1401)
        game.start_new_game()
        game.add_status(game.player_statuses, "ward", 5)
        game.add_status(game.player_statuses, "ward", 2)
        self.assertEqual(game.player_statuses["ward"], 5)

    def test_add_status_can_extend_duration(self):
        game = make_game(1402)
        game.start_new_game()
        game.add_status(game.player_statuses, "ward", 2)
        game.add_status(game.player_statuses, "ward", 8)
        self.assertEqual(game.player_statuses["ward"], 8)

    def test_add_status_zero_duration_does_nothing(self):
        game = make_game(1403)
        game.start_new_game()
        game.player_statuses.pop("poison", None)
        game.add_status(game.player_statuses, "poison", 0)
        self.assertNotIn("poison", game.player_statuses)

    # --- tick_player_statuses ---

    def test_poison_tick_deals_one_damage(self):
        game = _open_game(1410)
        game.health = 10
        game.player_statuses["poison"] = 2
        game.tick_player_statuses()
        self.assertEqual(game.health, 9)

    def test_poison_tick_decrements_duration(self):
        game = _open_game(1411)
        game.player_statuses["poison"] = 3
        game.tick_player_statuses()
        self.assertEqual(game.player_statuses["poison"], 2)

    def test_poison_clears_when_duration_reaches_zero(self):
        game = _open_game(1412)
        game.health = 10
        game.player_statuses["poison"] = 1
        game.tick_player_statuses()
        self.assertNotIn("poison", game.player_statuses)

    def test_burn_tick_deals_one_damage(self):
        game = _open_game(1413)
        game.health = 10
        game.player_statuses["burn"] = 2
        game.tick_player_statuses()
        self.assertEqual(game.health, 9)

    def test_ward_tick_does_not_deal_damage(self):
        game = _open_game(1414)
        game.health = 10
        game.player_statuses["ward"] = 3
        game.tick_player_statuses()
        self.assertEqual(game.health, 10)

    def test_ward_decrements_each_tick(self):
        game = _open_game(1415)
        game.player_statuses["ward"] = 4
        game.tick_player_statuses()
        self.assertEqual(game.player_statuses["ward"], 3)

    def test_ward_expires_after_sufficient_ticks(self):
        game = _open_game(1416)
        game.health = 20
        game.player_statuses["ward"] = 2
        game.tick_player_statuses()
        game.tick_player_statuses()
        self.assertNotIn("ward", game.player_statuses)

    def test_poison_kills_player_at_zero_hp(self):
        game = _open_game(1417)
        game.health = 1
        game.max_health = 10
        game.player_statuses["poison"] = 3
        game.tick_player_statuses()
        self.assertTrue(game.game_over)

    # --- tick_enemy_statuses ---

    def test_enemy_poison_tick_deals_damage(self):
        game = _open_game(1420)
        enemy = Enemy(position=(5, 4), kind="stalker", color=(200, 0, 0), health=5, max_health=5)
        enemy.status_effects["poison"] = 2
        game.enemies = [enemy]
        game.tick_enemy_statuses()
        self.assertEqual(enemy.health, 4)

    def test_enemy_poison_removes_when_killed(self):
        game = _open_game(1421)
        enemy = Enemy(position=(5, 4), kind="stalker", color=(200, 0, 0), health=1, max_health=3)
        enemy.status_effects["poison"] = 3
        game.enemies = [enemy]
        game.tick_enemy_statuses()
        self.assertNotIn(enemy, game.enemies)

    def test_enemy_status_decrements_each_tick(self):
        game = _open_game(1422)
        enemy = Enemy(position=(5, 4), kind="stalker", color=(200, 0, 0), health=10, max_health=10)
        enemy.status_effects["burn"] = 3
        game.enemies = [enemy]
        game.tick_enemy_statuses()
        self.assertEqual(enemy.status_effects["burn"], 2)

    # --- after_player_turn integrates status ticks ---

    def test_after_player_turn_ticks_player_poison(self):
        game = _open_game(1430)
        game.health = 10
        game.player_statuses["poison"] = 2
        game.exploration_reward_pending = None
        game.delve_reward_pending = False
        # Pre-claim the 100% milestone so collect_floor_items doesn't reopen it
        game.exploration_progress = 100
        game.claimed_exploration_rewards.add(100)
        game.after_player_turn(player_acted=True)
        self.assertEqual(game.health, 9)


if __name__ == "__main__":
    unittest.main()
