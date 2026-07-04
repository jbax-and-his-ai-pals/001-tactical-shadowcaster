from __future__ import annotations

import unittest

from shadowcaster.models import Enemy, GroundItem, Item, Landmark, Resident, UpgradePickup
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(w: int = 10, h: int = 8) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def _inspect_game(seed: int):
    game = make_game(seed)
    game.start_new_game()
    game.dungeon = build_open_map()
    game.player = (3, 3)
    game.camera_x = 0
    game.camera_y = 0
    game.enemies = []
    game.residents = []
    game.landmarks = []
    game.edge_exits = {}
    game.stairs = None
    game.up_stairs = None
    game.delve_goal = None
    game.return_portal = None
    game.terrain_features = {}
    game.floor_explorable_tiles = {
        (x, y) for x in range(1, 9) for y in range(1, 7)
    }
    game.seen_tiles = set(game.floor_explorable_tiles)
    game.visible_tiles = set(game.floor_explorable_tiles)
    return game


class InspectTests(unittest.TestCase):

    # --- player tile ---

    def test_inspect_player_tile_returns_hp_info(self):
        game = _inspect_game(1700)
        info = game.inspect_tile_info(game.player)
        self.assertIsNotNone(info)
        joined = " ".join(info["lines"])
        self.assertIn("HP", joined)

    def test_inspect_player_tile_title_contains_you(self):
        game = _inspect_game(1701)
        info = game.inspect_tile_info(game.player)
        self.assertIn("You", info["title"])

    # --- enemy tile ---

    def test_inspect_visible_enemy_returns_stats(self):
        game = _inspect_game(1710)
        enemy = Enemy(position=(5, 3), kind="stalker", color=(200, 0, 0),
                      health=3, max_health=5, damage=2, attack_range=1)
        game.enemies = [enemy]
        info = game.inspect_tile_info((5, 3))
        self.assertIsNotNone(info)
        joined = " ".join(info["lines"])
        self.assertIn("HP", joined)
        self.assertIn("Damage", joined)

    def test_inspect_enemy_title_contains_kind(self):
        game = _inspect_game(1711)
        enemy = Enemy(position=(5, 3), kind="brute", color=(200, 0, 0), health=5, max_health=5, damage=2)
        game.enemies = [enemy]
        info = game.inspect_tile_info((5, 3))
        self.assertIn("Brute", info["title"])

    def test_inspect_enemy_not_visible_returns_none_for_enemy(self):
        game = _inspect_game(1712)
        enemy = Enemy(position=(5, 3), kind="stalker", color=(200, 0, 0), health=3, max_health=3, damage=1)
        game.enemies = [enemy]
        game.visible_tiles = set()
        info = game.inspect_tile_info((5, 3))
        # When enemy not visible the enemy branch is skipped; may return None or non-enemy info
        if info is not None:
            self.assertNotIn("Damage", " ".join(info["lines"]))

    # --- resident tile ---

    def test_inspect_visible_resident_returns_role_info(self):
        game = _inspect_game(1720)
        game.region_type = "town"
        resident = Resident(position=(5, 3), kind="farmer", color=(200, 200, 100),
                            title="Farmer", name="Old Tom")
        game.residents = [resident]
        info = game.inspect_tile_info((5, 3))
        self.assertIsNotNone(info)
        self.assertIn("Interact", " ".join(info["lines"]))

    # --- landmark tile ---

    def test_inspect_landmark_returns_landmark_info(self):
        game = _inspect_game(1730)
        if game.in_local_region():
            game.leave_local_region()
        lm = Landmark(key="lm_inn", position=(5, 3), kind="inn", name="Lakeside Inn",
                      color=(200, 200, 200), marker="inn")
        game.landmarks = [lm]
        game.seen_tiles.add((5, 3))
        game.visible_tiles.add((5, 3))
        info = game.inspect_tile_info((5, 3))
        self.assertIsNotNone(info)
        self.assertIn("Lakeside Inn", info["title"])

    # --- stairs ---

    def test_inspect_stairs_tile_returns_down_stairs_info(self):
        game = _inspect_game(1740)
        game.stairs = (6, 3)
        info = game.inspect_tile_info((6, 3))
        self.assertIsNotNone(info)
        self.assertIn("Down", info["title"])

    def test_inspect_up_stairs_tile_returns_up_stairs_info(self):
        game = _inspect_game(1741)
        game.up_stairs = (6, 4)
        info = game.inspect_tile_info((6, 4))
        self.assertIsNotNone(info)
        self.assertIn("Up", info["title"])

    # --- edge exit ---

    def test_inspect_edge_exit_returns_direction_info(self):
        game = _inspect_game(1750)
        game.edge_exits = {"north": (3, 1)}
        game.seen_tiles.add((3, 1))
        game.visible_tiles.add((3, 1))
        info = game.inspect_tile_info((3, 1))
        self.assertIsNotNone(info)
        joined = info["title"] + " ".join(info["lines"])
        self.assertTrue(
            "north" in joined.lower() or "exit" in joined.lower() or "route" in joined.lower()
        )

    # --- floor item ---

    def test_inspect_floor_weapon_shows_stat_bonus(self):
        game = _inspect_game(1760)
        item = Item(key="spear", name="Spear", category="weapon", color=(200, 200, 200),
                    marker="weapon", melee_bonus=2, ranged_bonus=1)
        game.floor_items = [GroundItem(position=(5, 3), item=item)]
        info = game.inspect_tile_info((5, 3))
        self.assertIsNotNone(info)
        self.assertIn("Spear", info["title"])
        joined = " ".join(info["lines"])
        self.assertIn("melee", joined.lower())

    def test_inspect_floor_armor_shows_defense_bonus(self):
        game = _inspect_game(1761)
        item = Item(key="leather_armor", name="Leather Armor", category="armor",
                    color=(200, 200, 200), marker="armor", defense_bonus=2)
        game.floor_items = [GroundItem(position=(5, 3), item=item)]
        info = game.inspect_tile_info((5, 3))
        self.assertIsNotNone(info)
        joined = " ".join(info["lines"])
        self.assertIn("defense", joined.lower())

    # --- upgrade cache ---

    def test_inspect_upgrade_cache_returns_upgrade_info(self):
        game = _inspect_game(1770)
        game.upgrade_pickup = UpgradePickup(position=(6, 3), kind="vitality",
                                            color=(100, 200, 100), memory_color=(50, 100, 50))
        info = game.inspect_tile_info((6, 3))
        self.assertIsNotNone(info)
        self.assertIn("Vitality", " ".join(info["lines"]))

    # --- unseen / empty tile ---

    def test_inspect_unseen_tile_returns_none(self):
        game = _inspect_game(1780)
        # Remove a tile from seen_tiles so inspect has nothing to report
        tile = (8, 6)
        game.seen_tiles.discard(tile)
        game.visible_tiles.discard(tile)
        info = game.inspect_tile_info(tile)
        self.assertIsNone(info)

    def test_inspect_none_position_returns_none(self):
        game = _inspect_game(1781)
        self.assertIsNone(game.inspect_tile_info(None))


if __name__ == "__main__":
    unittest.main()
