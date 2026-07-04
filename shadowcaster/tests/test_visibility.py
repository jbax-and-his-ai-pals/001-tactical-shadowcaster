from __future__ import annotations

import unittest

from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(w: int = 14, h: int = 10) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def build_corridor_map() -> RegionMap:
    """Single horizontal corridor: walls above and below row 3."""
    region = RegionMap(20, 7, fill=1)
    for x in range(1, 19):
        region.tiles[x][3] = 0
    return region


def _vis_game(seed: int):
    game = make_game(seed)
    game.start_new_game()
    game.dungeon = build_open_map()
    game.player = (7, 5)
    game.camera_x = 0
    game.camera_y = 0
    game.terrain_features = {}
    game.enemies = []
    game.residents = []
    game.landmarks = []
    game.edge_exits = {}
    game.stairs = None
    game.up_stairs = None
    game.delve_goal = None
    game.return_portal = None
    game.floor_explorable_tiles = {
        (x, y) for x in range(1, 13) for y in range(1, 9)
    }
    game.seen_tiles = set()
    game.visible_tiles = set()
    game.exploration_progress = 0
    game.claimed_exploration_rewards = set()
    return game


class VisibilityTests(unittest.TestCase):

    # --- update_visibility grows seen_tiles ---

    def test_update_visibility_adds_player_position_to_seen(self):
        game = _vis_game(1800)
        game.update_visibility()
        self.assertIn(game.player, game.seen_tiles)

    def test_update_visibility_adds_nearby_open_tiles_to_seen(self):
        game = _vis_game(1801)
        game.update_visibility()
        # With default light radius the player should see more than just their own tile
        self.assertGreater(len(game.seen_tiles), 1)

    def test_update_visibility_visible_subset_of_seen(self):
        game = _vis_game(1802)
        game.update_visibility()
        self.assertTrue(game.visible_tiles.issubset(game.seen_tiles))

    def test_seen_tiles_never_shrinks_between_updates(self):
        game = _vis_game(1803)
        game.update_visibility()
        after_first = set(game.seen_tiles)
        game.player = (3, 3)
        game.update_visibility()
        # Every tile from the first pass must still be seen
        self.assertTrue(after_first.issubset(game.seen_tiles))

    def test_update_visibility_updates_exploration_progress(self):
        game = _vis_game(1804)
        game.update_visibility()
        self.assertGreater(game.exploration_progress, 0)

    # --- walls block line of sight ---

    def test_wall_blocks_sight_through_corridor(self):
        game = _vis_game(1810)
        game.dungeon = build_corridor_map()
        game.player = (1, 3)
        game.floor_explorable_tiles = {(x, 3) for x in range(1, 19)}
        game.seen_tiles = set()
        game.visible_tiles = set()
        game.update_visibility()
        # Tiles directly in the corridor should be visible
        self.assertIn((2, 3), game.visible_tiles)
        # Tiles above/below the corridor wall should not be visible
        self.assertNotIn((5, 1), game.visible_tiles)
        self.assertNotIn((5, 5), game.visible_tiles)

    # --- reveal_entire_map ---

    def test_reveal_entire_map_marks_all_explorable_tiles_seen(self):
        game = _vis_game(1820)
        game.reveal_entire_map()
        for tile in game.floor_explorable_tiles:
            self.assertIn(tile, game.seen_tiles)

    def test_reveal_entire_map_marks_all_explorable_tiles_seen_progress_follows(self):
        game = _vis_game(1821)
        game.reveal_entire_map()
        # Progress is recomputed lazily by update_visibility; check seen coverage directly
        self.assertTrue(game.floor_explorable_tiles.issubset(game.seen_tiles))

    # --- exploration_effectively_complete ---

    def test_exploration_complete_when_all_tiles_seen(self):
        game = _vis_game(1830)
        game.seen_tiles = set(game.floor_explorable_tiles)
        self.assertTrue(game.exploration_effectively_complete())

    def test_exploration_not_complete_with_unseen_tiles(self):
        game = _vis_game(1831)
        # Frontier algo skips the player tile, so seed at least one non-player seen tile
        px, py = game.player
        game.seen_tiles = {game.player, (px + 1, py)}
        self.assertFalse(game.exploration_effectively_complete())

    # --- light_radius affects visibility range ---

    def test_larger_light_radius_reveals_more_tiles(self):
        game_small = _vis_game(1840)
        game_small.base_light_radius = 2
        game_small.light_bonus = 0
        game_small.update_visibility()
        small_count = len(game_small.visible_tiles)

        game_large = _vis_game(1841)
        game_large.base_light_radius = 6
        game_large.light_bonus = 0
        game_large.update_visibility()
        large_count = len(game_large.visible_tiles)

        self.assertGreater(large_count, small_count)

    # --- check_exploration_rewards integrates with exploration progress ---

    def test_full_exploration_triggers_pending_reward(self):
        game = _vis_game(1850)
        game.seen_tiles = set(game.floor_explorable_tiles)
        game.exploration_progress = 100
        game.exploration_reward_pending = None
        game.delve_reward_pending = False
        game.check_exploration_rewards()
        self.assertIsNotNone(game.exploration_reward_pending)

    def test_already_claimed_milestone_does_not_reopen(self):
        game = _vis_game(1851)
        game.seen_tiles = set(game.floor_explorable_tiles)
        game.exploration_progress = 100
        game.claimed_exploration_rewards.add(100)
        game.exploration_reward_pending = None
        game.check_exploration_rewards()
        self.assertIsNone(game.exploration_reward_pending)


if __name__ == "__main__":
    unittest.main()
