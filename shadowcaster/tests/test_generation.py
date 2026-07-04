from __future__ import annotations

import unittest

from shadowcaster.regions_generate_town import generate_town
from shadowcaster.regions_town import generate_monster_town
from shadowcaster.systems import compute_fov, flood_reachable_tiles
from shadowcaster.tests.support import make_game


class GenerationTests(unittest.TestCase):
    def test_edge_exits_are_reachable_across_seed_sweep(self):
        for seed in range(1, 9):
            with self.subTest(seed=seed):
                game = make_game(seed)
                game.start_new_game()
                self.assertTrue(game.edge_exits, "Connected regions should expose edge exits")
                for direction, tile in game.edge_exits.items():
                    self.assertIn(tile, game.floor_explorable_tiles, f"{direction} exit should be reachable")
                    self.assertFalse(game.dungeon.is_blocked(*tile), f"{direction} exit should be walkable")

    def test_town_doors_stay_reachable(self):
        contexts = [
            {"parent_biome": "plains", "settlement_size": "village"},
            {"parent_biome": "forest", "settlement_size": "town"},
        ]
        for context in contexts:
            with self.subTest(kind="town", context=context):
                region = generate_town(48, 32, context=context)
                plaza = region.rooms[0].center
                reachable = flood_reachable_tiles(region, plaza)
                doors = [building["door"] for building in region.metadata.get("town_buildings", [])]
                self.assertTrue(doors, "Town generation should create doors")
                for door in doors:
                    self.assertIn(door, reachable, "Every town door should connect back to the plaza")

            with self.subTest(kind="monster_town", context=context):
                region = generate_monster_town(48, 32, context=context)
                plaza = region.rooms[0].center
                reachable = flood_reachable_tiles(region, plaza)
                doors = [building["door"] for building in region.metadata.get("town_buildings", [])]
                self.assertTrue(doors, "Monster-town generation should keep service doors")
                for door in doors:
                    self.assertIn(door, reachable, "Every monster-town door should connect back to the plaza")

    def test_transparent_blockers_do_not_break_line_of_sight(self):
        game = make_game(99)
        game.start_new_game()
        game.dungeon.tiles = [[1 for _ in range(7)] for _ in range(7)]
        for x in range(1, 6):
            game.dungeon.tiles[x][3] = 0
        game.dungeon.tiles[4][3] = 1
        game.dungeon.transparent_tiles = {(4, 3)}
        visible = compute_fov(2, 3, 4, game.dungeon)
        self.assertIn((5, 3), visible, "Transparent blocking terrain should still allow sight beyond it")


if __name__ == "__main__":
    unittest.main()
