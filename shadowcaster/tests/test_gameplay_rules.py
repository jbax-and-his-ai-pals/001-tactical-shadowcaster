from __future__ import annotations

import unittest

from shadowcaster.constants import COLOR_ACCENT
from shadowcaster.models import Enemy, Landmark
from shadowcaster.tests.support import make_game


class GameplayRuleTests(unittest.TestCase):
    def test_surface_landmark_rewards_are_idempotent(self):
        game = make_game(222)
        game.start_new_game()
        landmark = Landmark(
            key="test_camp",
            position=game.player,
            kind="camp",
            name="Test Camp",
            color=COLOR_ACCENT,
            marker="camp",
        )
        ammo_before = game.ammo
        medkits_before = game.inventory_quantity("medkit")

        game.apply_surface_landmark(landmark)
        ammo_after_first = game.ammo
        medkits_after_first = game.inventory_quantity("medkit")

        game.service_modal_open = False
        game.apply_surface_landmark(landmark)

        self.assertEqual(ammo_after_first, ammo_before + 2)
        self.assertEqual(medkits_after_first, medkits_before + 1)
        self.assertEqual(game.ammo, ammo_after_first)
        self.assertEqual(game.inventory_quantity("medkit"), medkits_after_first)
        self.assertIn("already visited", game.message.lower())

    def test_auto_move_interrupts_for_visible_hostiles(self):
        game = make_game(333)
        game.start_new_game()
        enemy = Enemy(position=game.player, kind="stalker", color=(255, 0, 0))
        game.enemies = [enemy]
        game.visible_tiles = {game.player}
        game.turn_newly_discovered_tiles = set()

        self.assertTrue(game.should_interrupt_auto_move())

    def test_auto_move_only_interrupts_once_for_non_hostile_interest(self):
        game = make_game(444)
        game.start_new_game()
        interest_tile = next(iter(game.edge_exits.values()))
        game.visible_tiles = {game.player, interest_tile}
        game.turn_newly_discovered_tiles = {interest_tile}

        self.assertTrue(game.should_interrupt_auto_move())

        game.turn_newly_discovered_tiles = set()
        self.assertFalse(game.should_interrupt_auto_move())


if __name__ == "__main__":
    unittest.main()
