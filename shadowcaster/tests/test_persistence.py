from __future__ import annotations

import unittest
from pathlib import Path

from shadowcaster.constants import COLOR_ACCENT
from shadowcaster.models import Landmark
from shadowcaster.persistence import load_game, save_game
from shadowcaster.tests.support import make_game


class PersistenceTests(unittest.TestCase):
    def test_save_load_preserves_current_local_region_context(self):
        game = make_game(554)
        game.start_new_game()
        if not game.in_local_region():
            landmark = next((lm for lm in game.landmarks if lm.kind not in game.surface_landmark_kinds()), None)
            self.assertIsNotNone(landmark)
            game.enter_landmark(landmark)
        self.assertTrue(game.in_local_region())
        original_local_key = game.current_local_region
        original_region_type = game.region_type
        original_region_name = game.region_name
        save_path = Path("tmp_test_local_region_save.json")
        save_game(game, save_path)
        data = load_game(save_path)

        loaded_game = make_game()
        loaded_game.apply_loaded_state(data)

        self.assertEqual(loaded_game.current_local_region, original_local_key)
        self.assertEqual(loaded_game.region_type, original_region_type)
        self.assertEqual(loaded_game.region_name, original_region_name)
        self.assertTrue(loaded_game.in_local_region())

    def test_save_load_round_trips_surface_landmark_claims(self):
        game = make_game(555)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        landmark = Landmark(
            key="test_waystone",
            position=game.player,
            kind="waystone",
            name="Test Waystone",
            color=COLOR_ACCENT,
            marker="waystone",
        )
        game.apply_surface_landmark(landmark)
        game.store_current_region()
        save_path = Path("tmp_test_save_roundtrip.json")
        save_game(game, save_path)
        data = load_game(save_path)

        loaded_game = make_game()
        loaded_game.apply_loaded_state(data)

        self.assertEqual(loaded_game.world_seed, game.world_seed)
        self.assertIn("test_waystone", loaded_game.claimed_surface_landmark_keys)
        region_key = loaded_game.region_key(loaded_game.world_position)
        self.assertIn(
            "test_waystone",
            loaded_game.world_regions[region_key]["claimed_surface_landmark_keys"],
        )


if __name__ == "__main__":
    unittest.main()
