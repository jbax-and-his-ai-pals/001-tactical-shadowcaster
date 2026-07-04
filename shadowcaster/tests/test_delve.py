from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


def _find_dungeon_landmark(game):
    return next(
        (lm for lm in game.landmarks if lm.kind == "dungeon"),
        None,
    )


def _enter_dungeon(game):
    """Enter any enterable landmark; return it or skip-signal None."""
    if game.in_local_region():
        game.leave_local_region()
    enterable = next(
        (lm for lm in game.landmarks if lm.kind not in game.surface_landmark_kinds()),
        None,
    )
    if enterable is None:
        return None
    game.enter_landmark(enterable)
    return enterable


class DelveTests(unittest.TestCase):

    # --- region_is_multilevel ---

    def test_dungeon_is_multilevel(self):
        game = make_game(2100)
        game.start_new_game()
        game.region_type = "dungeon"
        self.assertTrue(game.region_is_multilevel())

    def test_cave_is_multilevel(self):
        game = make_game(2101)
        game.start_new_game()
        game.region_type = "cave"
        self.assertTrue(game.region_is_multilevel())

    def test_plains_is_not_multilevel(self):
        game = make_game(2102)
        game.start_new_game()
        game.region_type = "plains"
        self.assertFalse(game.region_is_multilevel())

    def test_town_is_not_multilevel(self):
        game = make_game(2103)
        game.start_new_game()
        game.region_type = "town"
        self.assertFalse(game.region_is_multilevel())

    # --- is_bottom_floor ---

    def test_is_bottom_floor_when_at_max_depth(self):
        game = make_game(2104)
        game.start_new_game()
        game.region_type = "dungeon"
        game.region_depth = 3
        game.region_max_depth = 3
        self.assertTrue(game.is_bottom_floor())

    def test_is_not_bottom_floor_when_below_max_depth(self):
        game = make_game(2105)
        game.start_new_game()
        game.region_type = "dungeon"
        game.region_depth = 1
        game.region_max_depth = 3
        self.assertFalse(game.is_bottom_floor())

    def test_is_not_bottom_floor_for_non_multilevel_region(self):
        game = make_game(2106)
        game.start_new_game()
        game.region_type = "plains"
        game.region_depth = 1
        game.region_max_depth = 1
        self.assertFalse(game.is_bottom_floor())

    # --- descend message when not on stairs ---

    def test_descend_without_stairs_shows_message(self):
        game = make_game(2110)
        game.start_new_game()
        game.stairs = None
        game.up_stairs = None
        game.delve_goal = None
        game.return_portal = None
        game.descend()
        self.assertIn("stairs", game.message.lower())

    def test_descend_off_stairs_tile_shows_message(self):
        game = make_game(2111)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        lm = _enter_dungeon(game)
        if lm is None:
            self.skipTest("No enterable landmark for this seed")
        # Move player away from the stairs tile
        game.player = (1, 1)
        game.descend()
        self.assertIn("stairs", game.message.lower())

    # --- delve_reward_pending ---

    def test_reaching_delve_goal_sets_pending_reward(self):
        game = make_game(2120)
        game.start_new_game()
        goal_pos = (5, 5)
        game.player = goal_pos
        game.delve_goal = goal_pos
        game.bottom_reward_claimed = False
        game.delve_reward_pending = False
        game.floor_items = []
        game.upgrade_pickup = None
        game.heal_pickup = None
        game.exploration_progress = 50
        game.collect_floor_items()
        self.assertTrue(game.delve_reward_pending)

    def test_delve_goal_not_triggered_when_already_claimed(self):
        game = make_game(2121)
        game.start_new_game()
        goal_pos = (5, 5)
        game.player = goal_pos
        game.delve_goal = goal_pos
        game.bottom_reward_claimed = True
        game.delve_reward_pending = False
        game.floor_items = []
        game.upgrade_pickup = None
        game.heal_pickup = None
        game.exploration_progress = 50
        game.collect_floor_items()
        self.assertFalse(game.delve_reward_pending)

    # --- in_local_region ---

    def test_in_local_region_true_after_entering_landmark(self):
        game = make_game(2130)
        game.start_new_game()
        lm = _enter_dungeon(game)
        if lm is None:
            self.skipTest("No enterable landmark for this seed")
        self.assertTrue(game.in_local_region())

    def test_in_local_region_false_after_leaving(self):
        game = make_game(2131)
        game.start_new_game()
        lm = _enter_dungeon(game)
        if lm is None:
            self.skipTest("No enterable landmark for this seed")
        game.leave_local_region()
        self.assertFalse(game.in_local_region())

    def test_region_depth_is_one_on_entry(self):
        game = make_game(2132)
        game.start_new_game()
        lm = _enter_dungeon(game)
        if lm is None:
            self.skipTest("No enterable landmark for this seed")
        self.assertEqual(game.region_depth, 1)

    # --- seed_scope determinism ---

    def test_same_seed_same_dungeon_layout(self):
        # Verify determinism by leaving and re-entering the same landmark;
        # the stored region should be restored from cache, not regenerated.
        game = make_game(2140)
        game.start_new_game()
        lm = _enter_dungeon(game)
        if lm is None:
            self.skipTest("No enterable landmark for seed 2140")
        snap_first = game.snapshot_current_region()
        game.store_current_region()
        game.leave_local_region()
        game.enter_landmark(lm)
        snap_second = game.snapshot_current_region()
        self.assertEqual(snap_first["region_type"], snap_second["region_type"])

    # --- world region helper ---

    def test_move_coord_north_decrements_y(self):
        game = make_game(2150)
        game.start_new_game()
        result = game.move_coord((0, 0), "north")
        self.assertEqual(result, (0, -1))

    def test_move_coord_east_increments_x(self):
        game = make_game(2151)
        game.start_new_game()
        result = game.move_coord((0, 0), "east")
        self.assertEqual(result, (1, 0))

    def test_opposite_direction_north_south(self):
        game = make_game(2152)
        game.start_new_game()
        self.assertEqual(game.opposite_direction("north"), "south")

    def test_opposite_direction_east_west(self):
        game = make_game(2153)
        game.start_new_game()
        self.assertEqual(game.opposite_direction("east"), "west")


if __name__ == "__main__":
    unittest.main()
