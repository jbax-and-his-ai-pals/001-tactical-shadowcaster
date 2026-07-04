from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


class WorldStateTests(unittest.TestCase):

    # --- snapshot_current_region roundtrip ---

    def test_snapshot_preserves_region_type(self):
        game = make_game(2000)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        snap = game.snapshot_current_region()
        self.assertEqual(snap["region_type"], game.region_type)

    def test_snapshot_preserves_region_name(self):
        game = make_game(2001)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        snap = game.snapshot_current_region()
        self.assertEqual(snap["region_name"], game.region_name)

    def test_snapshot_preserves_seen_tiles(self):
        game = make_game(2002)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.seen_tiles.add((5, 5))
        snap = game.snapshot_current_region()
        self.assertIn((5, 5), snap["seen_tiles"])

    def test_snapshot_preserves_enemies(self):
        from shadowcaster.models import Enemy
        game = make_game(2003)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        enemy = Enemy(position=(4, 4), kind="stalker", color=(200, 0, 0), health=3, max_health=3, damage=1)
        game.enemies = [enemy]
        snap = game.snapshot_current_region()
        self.assertIn(enemy, snap["enemies"])

    def test_snapshot_preserves_landmarks(self):
        from shadowcaster.models import Landmark
        game = make_game(2004)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        lm = Landmark(key="test_lm", position=(6, 6), kind="shrine", name="Shrine",
                      color=(200, 200, 200), marker="shrine")
        game.landmarks = [lm]
        snap = game.snapshot_current_region()
        self.assertIn(lm, snap["landmarks"])

    def test_snapshot_preserves_service_claimed(self):
        game = make_game(2005)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.service_claimed = True
        snap = game.snapshot_current_region()
        self.assertTrue(snap["service_claimed"])

    # --- store and reload cycle ---

    def test_store_then_leave_and_reenter_restores_enemies(self):
        from shadowcaster.models import Enemy, Landmark
        game = make_game(2010)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        enterable = next(
            (lm for lm in game.landmarks if lm.kind not in game.surface_landmark_kinds()),
            None,
        )
        if enterable is None:
            self.skipTest("No enterable landmark for this seed")
        game.enter_landmark(enterable)
        enemy = Enemy(position=(4, 4), kind="stalker", color=(200, 0, 0), health=5, max_health=5, damage=1)
        game.enemies = [enemy]
        game.store_current_region()
        game.leave_local_region()
        game.enter_landmark(enterable)
        self.assertTrue(any(e.kind == "stalker" for e in game.enemies))

    # --- world region creation ---

    def test_create_world_region_state_returns_a_valid_region(self):
        game = make_game(2020)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        state = game.create_world_region_state((1, 0))
        self.assertIn("region_type", state)
        self.assertIn("region_name", state)
        self.assertIsNotNone(state["dungeon"])

    def test_create_world_region_state_has_empty_seen_tiles(self):
        game = make_game(2021)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        state = game.create_world_region_state((2, 1))
        self.assertEqual(len(state["seen_tiles"]), 0)

    def test_create_world_region_state_does_not_change_current_position(self):
        game = make_game(2022)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        pos_before = game.world_position
        game.create_world_region_state((3, 2))
        self.assertEqual(game.world_position, pos_before)

    def test_create_world_region_state_does_not_clobber_current_dungeon(self):
        game = make_game(2023)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        dungeon_before = game.dungeon
        game.create_world_region_state((3, 3))
        self.assertIs(game.dungeon, dungeon_before)

    # --- reveal_adjacent_world_regions ---

    def test_reveal_adjacent_adds_neighbors_to_world_regions(self):
        game = make_game(2030)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        known_before = set(game.world_regions)
        game.reveal_adjacent_world_regions()
        self.assertGreater(len(game.world_regions), len(known_before))

    def test_reveal_adjacent_returns_list_of_revealed_coords_and_names(self):
        game = make_game(2031)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        # Clear all neighbors first to guarantee reveals
        for direction in ("north", "south", "east", "west"):
            coord = game.move_coord(game.world_position, direction)
            game.world_regions.pop(game.region_key(coord), None)
        revealed = game.reveal_adjacent_world_regions()
        self.assertTrue(revealed)
        for coord, name in revealed:
            self.assertIsInstance(name, str)
            self.assertTrue(name)

    def test_reveal_adjacent_skips_already_known_regions(self):
        game = make_game(2032)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        # Reveal once so all neighbors are known
        game.reveal_adjacent_world_regions()
        revealed_second = game.reveal_adjacent_world_regions()
        self.assertEqual(revealed_second, [])

    # --- local_region_depth_key ---

    def test_local_region_depth_key_format(self):
        game = make_game(2040)
        game.start_new_game()
        key = game.local_region_depth_key("base_landmark_key", 3)
        self.assertEqual(key, "base_landmark_key::depth:3")

    def test_local_region_base_key_strips_depth_suffix(self):
        game = make_game(2041)
        game.start_new_game()
        game.current_local_region = "some_landmark::depth:2"
        base = game.local_region_base_key()
        self.assertEqual(base, "some_landmark")


if __name__ == "__main__":
    unittest.main()
