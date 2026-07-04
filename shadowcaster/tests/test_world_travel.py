from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


OVERWORLD_BIOMES = [
    "plains", "forest", "farmland", "desert", "swamp",
    "mountain", "badlands", "tundra", "volcanic",
]


class WorldTravelTests(unittest.TestCase):

    # --- seed determinism ---

    def test_same_seed_produces_same_region_type(self):
        game_a = make_game(400)
        game_a.start_new_game()
        game_b = make_game(400)
        game_b.start_new_game()
        self.assertEqual(game_a.region_type, game_b.region_type)

    def test_same_seed_produces_same_edge_exit_directions(self):
        game_a = make_game(401)
        game_a.start_new_game()
        game_b = make_game(401)
        game_b.start_new_game()
        self.assertEqual(set(game_a.edge_exits.keys()), set(game_b.edge_exits.keys()))

    def test_different_seeds_produce_different_layouts(self):
        # The starting overworld at (0,0) is always "plains" by design (safe start).
        # Use landmark positions as a proxy — they are seeded per world seed and should vary.
        layouts = set()
        for seed in range(1, 20):
            g = make_game(seed)
            g.start_new_game()
            if g.in_local_region():
                g.leave_local_region()
            layouts.add(tuple(sorted(lm.position for lm in g.landmarks)))
        self.assertGreater(len(layouts), 1, "Different seeds should produce different landmark layouts")

    # --- world region transition ---

    def test_transition_changes_world_position(self):
        game = make_game(410)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        start = game.world_position
        direction = next(iter(game.edge_exits))
        game.transition_to_world_region(direction)
        self.assertNotEqual(game.world_position, start)

    def test_transition_loads_connected_region(self):
        game = make_game(411)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        direction = next(iter(game.edge_exits))
        game.transition_to_world_region(direction)
        self.assertIsNotNone(game.dungeon)
        self.assertTrue(game.region_name)
        self.assertIn(game.player, game.floor_explorable_tiles)

    def test_transition_stores_previous_region(self):
        game = make_game(412)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        original_key = game.region_key(game.world_position)
        direction = next(iter(game.edge_exits))
        game.transition_to_world_region(direction)
        self.assertIn(original_key, game.world_regions)

    def test_return_transition_restores_previous_region_state(self):
        game = make_game(413)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        original_name = game.region_name
        direction = next(iter(game.edge_exits))
        opposite = game.opposite_direction(direction)
        game.transition_to_world_region(direction)
        game.transition_to_world_region(opposite)
        self.assertEqual(game.region_name, original_name)

    # --- biome generation sweep ---

    def test_all_overworld_biomes_generate_without_crash(self):
        for biome in OVERWORLD_BIOMES:
            with self.subTest(biome=biome):
                game = make_game(500)
                game.start_new_game()
                if game.in_local_region():
                    game.leave_local_region()
                game.debug_jump_to_biome(biome)
                self.assertEqual(game.region_type, biome)
                self.assertIsNotNone(game.dungeon)
                self.assertIn(game.player, game.floor_explorable_tiles)

    def test_all_biomes_have_reachable_edge_exits(self):
        for biome in OVERWORLD_BIOMES:
            with self.subTest(biome=biome):
                game = make_game(501)
                game.start_new_game()
                if game.in_local_region():
                    game.leave_local_region()
                game.debug_jump_to_biome(biome)
                for direction, tile in game.edge_exits.items():
                    self.assertIn(
                        tile, game.floor_explorable_tiles,
                        f"{biome} {direction} exit not reachable",
                    )

    # --- landmark tile validity ---

    def test_landmark_positions_are_walkable_across_seeds(self):
        for seed in range(1, 8):
            with self.subTest(seed=seed):
                game = make_game(seed)
                game.start_new_game()
                if game.in_local_region():
                    game.leave_local_region()
                for lm in game.landmarks:
                    self.assertFalse(
                        game.dungeon.is_blocked(*lm.position),
                        f"Seed {seed}: landmark '{lm.kind}' at {lm.position} is on a wall",
                    )

    def test_landmark_positions_are_in_explorable_tiles(self):
        for seed in range(1, 8):
            with self.subTest(seed=seed):
                game = make_game(seed)
                game.start_new_game()
                if game.in_local_region():
                    game.leave_local_region()
                for lm in game.landmarks:
                    self.assertIn(
                        lm.position, game.floor_explorable_tiles,
                        f"Seed {seed}: landmark '{lm.kind}' at {lm.position} not reachable from start",
                    )


if __name__ == "__main__":
    unittest.main()
