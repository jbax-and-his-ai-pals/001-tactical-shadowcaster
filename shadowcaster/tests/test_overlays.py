from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


class OverlayTests(unittest.TestCase):
    def test_inventory_toggle_is_blocked_by_pending_choice(self):
        game = make_game(601)
        game.start_new_game()
        game.exploration_reward_pending = 100

        game.toggle_inventory()

        self.assertFalse(game.inventory_open)
        self.assertEqual(game.active_overlay(), "choice")

    def test_world_map_toggle_is_blocked_by_inventory_overlay(self):
        game = make_game(602)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.toggle_inventory()

        game.toggle_world_map()

        self.assertTrue(game.inventory_open)
        self.assertFalse(game.world_map_open)
        self.assertEqual(game.active_overlay(), "inventory")

    def test_open_main_menu_closes_world_map(self):
        game = make_game(603)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.toggle_world_map()
        self.assertTrue(game.world_map_open)

        game.open_main_menu()

        self.assertEqual(game.menu_mode, "main")
        self.assertFalse(game.world_map_open)
        self.assertEqual(game.active_overlay(), "menu")


if __name__ == "__main__":
    unittest.main()
