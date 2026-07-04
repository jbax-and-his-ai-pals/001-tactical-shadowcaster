from __future__ import annotations

import unittest

from shadowcaster.models import Enemy
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(width: int = 9, height: int = 9) -> RegionMap:
    region = RegionMap(width, height, fill=1)
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            region.tiles[x][y] = 0
    return region


def _setup_open_room(game):
    game.dungeon = build_open_map()
    game.player = (2, 2)
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
        (x, y) for x in range(1, game.dungeon.width - 1)
        for y in range(1, game.dungeon.height - 1)
    }
    game.seen_tiles = set(game.floor_explorable_tiles)


class MovementTests(unittest.TestCase):

    # --- basic wall/floor rules ---

    def test_wall_blocks_movement(self):
        game = make_game(1001)
        game.start_new_game()
        _setup_open_room(game)
        game.player = (1, 1)
        result = game.try_move_player(-1, 0)
        self.assertFalse(result)
        self.assertEqual(game.player, (1, 1))
        self.assertIn("wall", game.message.lower())

    def test_open_tile_allows_movement(self):
        game = make_game(1002)
        game.start_new_game()
        _setup_open_room(game)
        result = game.try_move_player(1, 0)
        self.assertTrue(result)
        self.assertEqual(game.player, (3, 2))

    def test_diagonal_movement_updates_position(self):
        game = make_game(1003)
        game.start_new_game()
        _setup_open_room(game)
        result = game.try_move_player(1, 1)
        self.assertTrue(result)
        self.assertEqual(game.player, (3, 3))

    def test_enemy_tile_blocks_automated_movement(self):
        game = make_game(1004)
        game.start_new_game()
        _setup_open_room(game)
        enemy = Enemy(position=(3, 2), kind="stalker", color=(255, 0, 0))
        game.enemies = [enemy]
        game.auto_move_path = [(3, 2)]
        result = game.try_move_player(1, 0, automated=True)
        self.assertFalse(result)
        self.assertEqual(game.auto_move_path, [])

    def test_total_steps_increments_on_move(self):
        game = make_game(1005)
        game.start_new_game()
        _setup_open_room(game)
        before = game.total_steps
        game.try_move_player(1, 0)
        self.assertEqual(game.total_steps, before + 1)

    # --- terrain effects ---

    def test_muck_applies_poison_status(self):
        game = make_game(1010)
        game.start_new_game()
        _setup_open_room(game)
        game.terrain_features = {(3, 2): "muck"}
        game.player_statuses.pop("poison", None)
        game.try_move_player(1, 0)
        self.assertIn("poison", game.player_statuses)
        self.assertGreater(game.player_statuses["poison"], 0)

    def test_embers_applies_burn_status(self):
        game = make_game(1011)
        game.start_new_game()
        _setup_open_room(game)
        game.terrain_features = {(3, 2): "embers"}
        game.player_statuses.pop("burn", None)
        game.try_move_player(1, 0)
        self.assertIn("burn", game.player_statuses)

    def test_well_heals_one_hp_when_injured(self):
        game = make_game(1012)
        game.start_new_game()
        _setup_open_room(game)
        game.health = game.max_health - 3
        game.terrain_features = {(3, 2): "well"}
        game.try_move_player(1, 0)
        self.assertEqual(game.health, game.max_health - 2)

    def test_well_cleanses_at_full_health(self):
        game = make_game(1013)
        game.start_new_game()
        _setup_open_room(game)
        game.health = game.max_health
        game.player_statuses["poison"] = 3
        game.terrain_features = {(3, 2): "well"}
        game.try_move_player(1, 0)
        self.assertNotIn("poison", game.player_statuses)


if __name__ == "__main__":
    unittest.main()
