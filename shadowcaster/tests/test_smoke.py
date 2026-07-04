from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


class SmokeTests(unittest.TestCase):
    def test_start_new_game_builds_a_playable_region(self):
        game = make_game(12345)
        game.start_new_game()
        self.assertTrue(game.region_name)
        self.assertTrue(game.region_type)
        self.assertIsNotNone(game.dungeon)
        self.assertIn(game.player, game.floor_explorable_tiles)
        self.assertFalse(game.dungeon.is_blocked(*game.player))
        self.assertGreater(game.dungeon.width, 0)
        self.assertGreater(game.dungeon.height, 0)


if __name__ == "__main__":
    unittest.main()
