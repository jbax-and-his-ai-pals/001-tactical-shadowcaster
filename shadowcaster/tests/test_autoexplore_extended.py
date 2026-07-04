from __future__ import annotations

import unittest

from shadowcaster.models import Enemy
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(w: int = 14, h: int = 8) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def _setup(game, seen_fraction=0.5):
    game.dungeon = build_open_map()
    game.player = (2, 3)
    game.camera_x = 0
    game.camera_y = 0
    explorable = {
        (x, y) for x in range(1, game.dungeon.width - 1) for y in range(1, game.dungeon.height - 1)
    }
    game.floor_explorable_tiles = explorable
    seen_count = int(len(explorable) * seen_fraction)
    game.seen_tiles = set(list(sorted(explorable))[:seen_count])
    game.visible_tiles = set(game.seen_tiles)
    game.exploration_progress = int(seen_fraction * 100)
    game.enemies = []
    game.residents = []
    game.landmarks = []
    game.edge_exits = {}
    game.stairs = None
    game.up_stairs = None
    game.delve_goal = None
    game.return_portal = None
    game.terrain_features = {}


class AutoexploreExtendedTests(unittest.TestCase):

    def test_start_autoexplore_sets_path_when_unexplored_tiles_exist(self):
        game = make_game(1500)
        game.start_new_game()
        _setup(game, seen_fraction=0.3)
        game.start_autoexplore()
        self.assertTrue(game.autoexplore_active)
        self.assertTrue(game.auto_move_path)

    def test_start_autoexplore_refuses_when_fully_explored(self):
        game = make_game(1501)
        game.start_new_game()
        _setup(game, seen_fraction=1.0)
        game.exploration_progress = 100
        game.start_autoexplore()
        self.assertFalse(game.autoexplore_active)
        self.assertIn("fully explored", game.message.lower())

    def test_autoexplore_blocked_tiles_includes_edge_exits(self):
        game = make_game(1502)
        game.start_new_game()
        _setup(game)
        game.edge_exits = {"north": (5, 1)}
        blocked = game.autoexplore_blocked_tiles()
        self.assertIn((5, 1), blocked)

    def test_autoexplore_blocked_tiles_includes_landmark_positions(self):
        from shadowcaster.models import Landmark
        game = make_game(1503)
        game.start_new_game()
        _setup(game)
        lm = Landmark(key="t", position=(7, 3), kind="shrine", name="Shrine",
                      color=(200, 200, 200), marker="shrine")
        game.landmarks = [lm]
        blocked = game.autoexplore_blocked_tiles()
        self.assertIn((7, 3), blocked)

    def test_autoexplore_path_avoids_blocked_tiles(self):
        game = make_game(1504)
        game.start_new_game()
        _setup(game, seen_fraction=0.3)
        # Put an edge exit in the middle of the room so the path must route around it
        game.edge_exits = {"east": (7, 3)}
        game.start_autoexplore()
        if game.auto_move_path:
            self.assertNotIn((7, 3), game.auto_move_path)

    def test_exploration_effectively_complete_when_all_seen(self):
        game = make_game(1505)
        game.start_new_game()
        _setup(game, seen_fraction=1.0)
        self.assertTrue(game.exploration_effectively_complete())

    def test_exploration_not_complete_when_tiles_remain(self):
        game = make_game(1506)
        game.start_new_game()
        _setup(game, seen_fraction=0.3)
        self.assertFalse(game.exploration_effectively_complete())

    def test_hazardous_tile_costs_returns_muck_and_embers(self):
        game = make_game(1507)
        game.start_new_game()
        _setup(game)
        game.terrain_features = {(3, 3): "muck", (4, 3): "embers", (5, 3): "high_ground"}
        costs = game.hazardous_tile_costs()
        self.assertIn((3, 3), costs)
        self.assertIn((4, 3), costs)
        self.assertNotIn((5, 3), costs)

    def test_frontier_tiles_returns_tiles_adjacent_to_unseen(self):
        game = make_game(1508)
        game.start_new_game()
        game.dungeon = build_open_map(7, 7)
        game.player = (1, 1)
        explorable = {(x, y) for x in range(1, 6) for y in range(1, 6)}
        game.floor_explorable_tiles = explorable
        game.seen_tiles = {(x, y) for x in range(1, 4) for y in range(1, 4)}
        frontier = game.frontier_tiles()
        self.assertTrue(frontier)
        for tile in frontier:
            self.assertIn(tile, game.seen_tiles)


if __name__ == "__main__":
    unittest.main()
