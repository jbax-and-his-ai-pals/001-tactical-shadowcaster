from __future__ import annotations

import unittest

from shadowcaster.models import Quest
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(width: int, height: int) -> RegionMap:
    region = RegionMap(width, height, fill=1)
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            region.tiles[x][y] = 0
    return region


class RoutingTests(unittest.TestCase):
    def test_click_pathing_avoids_exit_tiles_unless_explicitly_targeted(self):
        game = make_game(701)
        game.start_new_game()
        game.dungeon = build_open_map(7, 7)
        game.player = (1, 3)
        game.camera_x = 0
        game.camera_y = 0
        game.edge_exits = {"east": (3, 3)}
        game.landmarks = []
        game.enemies = []
        game.residents = []
        game.stairs = None
        game.up_stairs = None
        game.delve_goal = None
        game.return_portal = None
        game.terrain_features = {}
        game.seen_tiles = {
            (x, y)
            for x in range(1, game.dungeon.width - 1)
            for y in range(1, game.dungeon.height - 1)
        }

        game.set_click_destination((5, 3))

        self.assertTrue(game.auto_move_path)
        self.assertNotIn((3, 3), game.auto_move_path)

        game.set_click_destination((3, 3))
        self.assertEqual(game.auto_move_path[-1], (3, 3))

    def test_click_pathing_prefers_non_hazardous_route_when_available(self):
        game = make_game(702)
        game.start_new_game()
        game.dungeon = build_open_map(7, 7)
        game.player = (1, 3)
        game.camera_x = 0
        game.camera_y = 0
        game.edge_exits = {}
        game.landmarks = []
        game.enemies = []
        game.residents = []
        game.stairs = None
        game.up_stairs = None
        game.delve_goal = None
        game.return_portal = None
        game.seen_tiles = {
            (x, y)
            for x in range(1, game.dungeon.width - 1)
            for y in range(1, game.dungeon.height - 1)
        }
        game.terrain_features = {(2, 3): "muck", (3, 3): "muck"}

        game.set_click_destination((5, 3))

        self.assertTrue(game.auto_move_path)
        self.assertNotIn((2, 3), game.auto_move_path)
        self.assertNotIn((3, 3), game.auto_move_path)
        self.assertEqual(game.auto_move_path[-1], (5, 3))

    def test_journal_show_map_requires_selected_discovered_destination(self):
        game = make_game(703)
        game.start_new_game()
        quest = Quest(
            id="quest_test",
            kind="delivery",
            from_world_pos=(0, 0),
            to_world_pos=(3, 0),
            to_town_hint="East",
            item_key="parcel",
            item_name="Parcel",
            description="Deliver a parcel east.",
            reward_gold=3,
            status="active",
            target_region_name="Eastward",
            origin_town_name="Origin",
        )
        game.active_quests = [quest]
        game.journal_tab = 0
        game.journal_index = 0
        game.world_regions = {game.region_key(game.world_position): game.snapshot_current_region()}

        self.assertFalse(game.can_show_map_for_selected_journal_quest())

        game.world_regions[game.region_key((3, 0))] = {"region_name": "Eastward"}
        self.assertTrue(game.can_show_map_for_selected_journal_quest())

    def test_abandoning_selected_quest_clears_selection_when_last_entry_removed(self):
        game = make_game(704)
        game.start_new_game()
        quest = Quest(
            id="quest_only",
            kind="delivery",
            from_world_pos=(0, 0),
            to_world_pos=(1, 0),
            to_town_hint="East",
            item_key="parcel",
            item_name="Parcel",
            description="Deliver a parcel nearby.",
            reward_gold=2,
            status="active",
        )
        game.active_quests = [quest]
        game.journal_tab = 0
        game.journal_index = 0

        game.abandon_quest(quest)

        self.assertEqual(game.active_quests, [])
        self.assertEqual(game.journal_index, -1)


if __name__ == "__main__":
    unittest.main()
