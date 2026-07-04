from __future__ import annotations

import unittest

from shadowcaster.models import GroundItem, Item, UpgradePickup
from shadowcaster.regions import RegionMap
from shadowcaster.tests.support import make_game


def build_open_map(w: int = 10, h: int = 8) -> RegionMap:
    region = RegionMap(w, h, fill=1)
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            region.tiles[x][y] = 0
    return region


def _upgrade_game(seed: int):
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
    game.upgrade_pickup = None
    game.heal_pickup = None
    game.floor_items = []
    game.exploration_progress = 100
    game.claimed_exploration_rewards.add(100)
    return game


def _place_upgrade(game, kind: str):
    colors = {
        "vitality": ((255, 90, 170), (100, 38, 70)),
        "power":    ((255, 180, 0),  (100, 70, 0)),
        "haste":    ((110, 224, 255), (38, 84, 96)),
        "reach":    ((240, 150, 230), (94, 50, 90)),
        "light":    ((255, 255, 180), (100, 100, 60)),
    }
    color, mem_color = colors.get(kind, ((200, 200, 200), (100, 100, 100)))
    game.upgrade_pickup = UpgradePickup(
        position=game.player, kind=kind, color=color, memory_color=mem_color
    )


class UpgradePickupTests(unittest.TestCase):

    # --- vitality ---

    def test_vitality_upgrade_increases_max_health(self):
        game = _upgrade_game(1900)
        before = game.max_health
        _place_upgrade(game, "vitality")
        game.collect_floor_items()
        amount = game.tuning["vitality_upgrade_amount"]
        self.assertEqual(game.max_health, before + amount)

    def test_vitality_upgrade_also_heals_player(self):
        game = _upgrade_game(1901)
        game.health = 1
        _place_upgrade(game, "vitality")
        game.collect_floor_items()
        self.assertGreater(game.health, 1)

    def test_vitality_upgrade_removes_pickup(self):
        game = _upgrade_game(1902)
        _place_upgrade(game, "vitality")
        game.collect_floor_items()
        self.assertIsNone(game.upgrade_pickup)

    def test_vitality_upgrade_increments_powerups_collected(self):
        game = _upgrade_game(1903)
        _place_upgrade(game, "vitality")
        game.collect_floor_items()
        self.assertEqual(game.powerups_collected["vitality"], 1)

    # --- power ---

    def test_power_upgrade_increases_melee_and_ranged(self):
        game = _upgrade_game(1910)
        before_m = game.melee_damage
        before_r = game.ranged_damage
        _place_upgrade(game, "power")
        game.collect_floor_items()
        amount = game.tuning["power_upgrade_amount"]
        self.assertEqual(game.melee_damage, before_m + amount)
        self.assertEqual(game.ranged_damage, before_r + amount)

    def test_power_upgrade_grants_one_ammo(self):
        game = _upgrade_game(1911)
        before = game.ammo
        _place_upgrade(game, "power")
        game.collect_floor_items()
        self.assertEqual(game.ammo, before + 1)

    # --- light ---

    def test_light_upgrade_increases_light_bonus(self):
        game = _upgrade_game(1920)
        before = game.light_bonus
        _place_upgrade(game, "light")
        game.collect_floor_items()
        amount = game.tuning["light_upgrade_amount"]
        self.assertEqual(game.light_bonus, before + amount)

    def test_light_upgrade_increases_effective_light_radius(self):
        game = _upgrade_game(1921)
        before = game.light_radius
        _place_upgrade(game, "light")
        game.collect_floor_items()
        self.assertGreater(game.light_radius, before)

    # --- haste ---

    def test_haste_upgrade_increases_haste_bonus(self):
        game = _upgrade_game(1930)
        before = game.haste_bonus
        _place_upgrade(game, "haste")
        game.collect_floor_items()
        amount = game.tuning["haste_upgrade_amount"]
        self.assertEqual(game.haste_bonus, before + amount)

    # --- reach ---

    def test_reach_upgrade_increases_reach_bonus(self):
        game = _upgrade_game(1940)
        before = game.reach_bonus
        _place_upgrade(game, "reach")
        game.collect_floor_items()
        amount = game.tuning["reach_upgrade_amount"]
        self.assertEqual(game.reach_bonus, before + amount)

    # --- heal pickup ---

    def test_heal_pickup_restores_health(self):
        game = _upgrade_game(1950)
        game.health = 1
        game.heal_pickup = game.player
        game.collect_floor_items()
        self.assertGreater(game.health, 1)

    def test_heal_pickup_removes_after_collection(self):
        game = _upgrade_game(1951)
        game.health = 1
        game.heal_pickup = game.player
        game.collect_floor_items()
        self.assertIsNone(game.heal_pickup)

    def test_heal_pickup_does_nothing_at_full_health(self):
        game = _upgrade_game(1952)
        game.health = game.max_health
        game.heal_pickup = game.player
        game.collect_floor_items()
        self.assertEqual(game.health, game.max_health)

    def test_heal_pickup_increments_powerups_collected(self):
        game = _upgrade_game(1953)
        game.health = 1
        game.heal_pickup = game.player
        game.collect_floor_items()
        self.assertEqual(game.powerups_collected["heal"], 1)

    # --- pickup not triggered when not on tile ---

    def test_upgrade_not_collected_when_player_elsewhere(self):
        game = _upgrade_game(1960)
        before_m = game.melee_damage
        game.upgrade_pickup = UpgradePickup(
            position=(7, 5), kind="power",
            color=(255, 180, 0), memory_color=(100, 70, 0),
        )
        game.collect_floor_items()
        self.assertEqual(game.melee_damage, before_m)
        self.assertIsNotNone(game.upgrade_pickup)


if __name__ == "__main__":
    unittest.main()
