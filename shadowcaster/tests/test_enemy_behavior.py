from __future__ import annotations

import unittest

from shadowcaster.models import Enemy
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def _open_map(w: int = 12, h: int = 10) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def _make_enemy(pos, kind="stalker", damage=1, health=5, attack_range=1, on_hit_effect=None):
    return Enemy(
        position=pos,
        kind=kind,
        color=(200, 0, 0),
        health=health,
        max_health=health,
        damage=damage,
        attack_range=attack_range,
        on_hit_effect=on_hit_effect,
    )


def _combat_game(seed: int):
    """Game with open map and pre-claimed exploration milestone."""
    game = make_game(seed)
    game.start_new_game()
    game.dungeon = _open_map()
    game.player = (5, 5)
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
        (x, y) for x in range(1, 11) for y in range(1, 9)
    }
    game.seen_tiles = set(game.floor_explorable_tiles)
    game.visible_tiles = set(game.floor_explorable_tiles)
    game.exploration_progress = 100
    game.claimed_exploration_rewards.add(100)
    game.upgrade_pickup = None
    game.heal_pickup = None
    game.floor_items = []
    return game


class EnemyBehaviorTests(unittest.TestCase):

    # --- enemy moves toward player ---

    def test_enemy_moves_toward_player(self):
        game = _combat_game(3000)
        # Enemy 3 tiles away — should step at least 1 tile (Chebyshev distance decreases)
        enemy = _make_enemy((5, 2))
        game.enemies = [enemy]
        pos_before = enemy.position
        game.after_player_turn(player_acted=False)
        self.assertNotEqual(enemy.position, pos_before)

    def test_enemy_message_includes_kind_when_moving(self):
        game = _combat_game(3001)
        enemy = _make_enemy((5, 2))
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertIn("stalker", game.message.lower())

    # --- enemy attacks when adjacent ---

    def test_adjacent_enemy_attacks_player(self):
        game = _combat_game(3010)
        game.health = game.max_health
        enemy = _make_enemy((5, 4), damage=2)
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertLess(game.health, game.max_health)

    def test_adjacent_enemy_damage_matches_enemy_damage_stat(self):
        game = _combat_game(3011)
        game.health = game.max_health
        expected_damage = 3
        enemy = _make_enemy((5, 4), damage=expected_damage)
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertEqual(game.health, game.max_health - expected_damage)

    def test_enemy_attack_message_includes_damage(self):
        game = _combat_game(3012)
        enemy = _make_enemy((5, 4), damage=1)
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertRegex(game.message, r'\d')

    # --- ranged enemy ---

    def test_ranged_enemy_attacks_from_range(self):
        game = _combat_game(3020)
        game.health = game.max_health
        # Enemy 4 tiles away with attack_range=5
        enemy = _make_enemy((5, 1), damage=2, attack_range=5)
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertLess(game.health, game.max_health)

    def test_ranged_enemy_does_not_move_when_in_range(self):
        game = _combat_game(3021)
        enemy = _make_enemy((5, 2), damage=1, attack_range=5)
        game.enemies = [enemy]
        pos_before = enemy.position
        game.after_player_turn(player_acted=False)
        # Ranged enemy fired, so it didn't walk — position unchanged
        self.assertEqual(enemy.position, pos_before)

    def test_ranged_enemy_message_says_strikes_from_range(self):
        game = _combat_game(3022)
        enemy = _make_enemy((5, 2), damage=1, attack_range=5)
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertIn("range", game.message.lower())

    # --- enemy out of visible tiles doesn't act ---

    def test_enemy_behind_wall_does_not_attack(self):
        game = _combat_game(3030)
        game.health = game.max_health
        # Build a wall between player (5,5) and enemy (5,3)
        game.dungeon.tiles[5][4] = 1  # wall at (5,4) blocks LoS
        enemy = _make_enemy((5, 3), damage=5, attack_range=5)
        game.enemies = [enemy]
        # Reset seen/visible so update_visibility recomputes fresh
        game.seen_tiles = set()
        game.floor_explorable_tiles = {(x, y) for x in range(1, 11) for y in range(1, 9)
                                        if not (x == 5 and y == 4)}
        game.after_player_turn(player_acted=False)
        # Enemy behind wall should not be visible → should not attack
        self.assertEqual(game.health, game.max_health)

    # --- on_hit_effect applied ---

    def test_enemy_hit_applies_poison_status(self):
        game = _combat_game(3040)
        game.player_statuses = {}
        enemy = _make_enemy((5, 4), damage=1, on_hit_effect="poison")
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertIn("poison", game.player_statuses)

    def test_enemy_hit_effect_blocked_by_ward(self):
        game = _combat_game(3041)
        game.player_statuses = {"ward": 3}
        enemy = _make_enemy((5, 4), damage=1, on_hit_effect="poison")
        game.enemies = [enemy]
        game.after_player_turn(player_acted=False)
        self.assertNotIn("poison", game.player_statuses)

    # --- enemy killed by player; then no attack ---

    def test_dead_enemy_removed_from_enemies_list(self):
        game = _combat_game(3050)
        enemy = _make_enemy((5, 4), health=1)
        game.enemies = [enemy]
        game.direction = "north"  # player faces north toward (5,4)
        game.attack()
        self.assertEqual(len(game.enemies), 0)

    def test_dead_enemy_does_not_attack_after_removal(self):
        game = _combat_game(3051)
        game.health = game.max_health
        enemy = _make_enemy((5, 4), health=1, damage=99)
        game.enemies = [enemy]
        game.direction = "north"
        game.attack()
        # Enemy is dead; now run after_player_turn
        game.after_player_turn(player_acted=True)
        self.assertEqual(game.health, game.max_health)

    # --- multiple enemies ---

    def test_two_adjacent_enemies_both_attack(self):
        game = _combat_game(3060)
        game.health = game.max_health
        e1 = _make_enemy((5, 4), damage=1)
        e2 = _make_enemy((4, 5), damage=1)
        game.enemies = [e1, e2]
        game.after_player_turn(player_acted=False)
        self.assertLessEqual(game.health, game.max_health - 2)

    def test_enemy_cannot_walk_into_occupied_tile(self):
        game = _combat_game(3061)
        e1 = _make_enemy((5, 3), damage=1)
        e2 = _make_enemy((5, 2), damage=1)  # blocked by e1
        game.enemies = [e1, e2]
        game.after_player_turn(player_acted=False)
        # They can't both be at (5,3) after the turn
        self.assertNotEqual(e1.position, e2.position)


if __name__ == "__main__":
    unittest.main()
