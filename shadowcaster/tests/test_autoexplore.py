from __future__ import annotations

import unittest

from shadowcaster.constants import VIEW_WIDTH
from shadowcaster.models import Enemy
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(width: int, height: int) -> RegionMap:
    region = RegionMap(width, height, fill=1)
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            region.tiles[x][y] = 0
    return region


class AutoexploreTests(unittest.TestCase):
    def test_autoexplore_is_blocked_by_on_screen_hostile(self):
        game = make_game(801)
        game.start_new_game()
        game.dungeon = build_open_map(12, 8)
        game.player = (2, 3)
        game.camera_x = 0
        game.camera_y = 0
        game.floor_explorable_tiles = {
            (x, y) for x in range(1, game.dungeon.width - 1) for y in range(1, game.dungeon.height - 1)
        }
        game.seen_tiles = {(x, y) for x in range(1, 5) for y in range(1, game.dungeon.height - 1)}
        game.visible_tiles = set(game.seen_tiles)
        game.exploration_progress = 0
        game.edge_exits = {}
        game.landmarks = []
        game.residents = []
        game.stairs = None
        game.up_stairs = None
        game.delve_goal = None
        game.return_portal = None
        game.terrain_features = {}
        game.enemies = [Enemy(position=(3, 3), kind="stalker", color=(255, 0, 0))]

        game.start_autoexplore()

        self.assertFalse(game.autoexplore_active)
        self.assertEqual(game.auto_move_path, [])
        self.assertIn("disabled while a hostile is in view", game.message.lower())

    def test_autoexplore_ignores_off_screen_visible_hostile(self):
        game = make_game(802)
        game.start_new_game()
        game.dungeon = build_open_map(max(VIEW_WIDTH + 20, 50), 8)
        game.player = (2, 3)
        game.camera_x = 0
        game.camera_y = 0
        game.floor_explorable_tiles = {
            (x, y) for x in range(1, game.dungeon.width - 1) for y in range(1, game.dungeon.height - 1)
        }
        game.seen_tiles = {(x, y) for x in range(1, 5) for y in range(1, game.dungeon.height - 1)}
        offscreen_enemy_pos = (VIEW_WIDTH + 5, 3)
        game.visible_tiles = set(game.seen_tiles) | {offscreen_enemy_pos}
        game.exploration_progress = 0
        game.edge_exits = {}
        game.landmarks = []
        game.residents = []
        game.stairs = None
        game.up_stairs = None
        game.delve_goal = None
        game.return_portal = None
        game.terrain_features = {}
        game.enemies = [Enemy(position=offscreen_enemy_pos, kind="stalker", color=(255, 0, 0))]

        game.start_autoexplore()

        self.assertTrue(game.autoexplore_active)
        self.assertTrue(game.auto_move_path)
        self.assertIn("autoexplore heads toward tile", game.message.lower())


if __name__ == "__main__":
    unittest.main()
