from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


def _game_with_service(seed: int, service_type: str):
    game = make_game(seed)
    game.start_new_game()
    game.region_type = service_type
    game.service_claimed = False
    return game


class TownServiceTests(unittest.TestCase):

    # --- inn ---

    def test_inn_heals_player(self):
        game = _game_with_service(1300, "inn")
        game.health = 1
        game.apply_town_service()
        self.assertGreater(game.health, 1)

    def test_inn_does_not_exceed_max_health(self):
        game = _game_with_service(1301, "inn")
        game.health = game.max_health
        game.apply_town_service()
        self.assertEqual(game.health, game.max_health)

    def test_inn_marks_service_claimed(self):
        game = _game_with_service(1302, "inn")
        game.apply_town_service()
        self.assertTrue(game.service_claimed)

    def test_inn_opens_service_modal(self):
        game = _game_with_service(1303, "inn")
        game.apply_town_service()
        self.assertTrue(game.service_modal_open)
        self.assertTrue(game.service_modal_lines)

    # --- clinic ---

    def test_clinic_cleanses_poison(self):
        game = _game_with_service(1310, "clinic")
        game.player_statuses["poison"] = 3
        game.apply_town_service()
        self.assertNotIn("poison", game.player_statuses)

    def test_clinic_heals_partial_damage(self):
        game = _game_with_service(1311, "clinic")
        game.health = 1
        game.apply_town_service()
        self.assertGreater(game.health, 1)

    # --- supply ---

    def test_supply_grants_ammo(self):
        game = _game_with_service(1320, "supply")
        before = game.ammo
        game.apply_town_service()
        self.assertGreater(game.ammo, before)

    def test_supply_grants_medkit(self):
        game = _game_with_service(1321, "supply")
        before = game.inventory_quantity("medkit")
        game.apply_town_service()
        self.assertGreater(game.inventory_quantity("medkit"), before)

    # --- shrine ---

    def test_shrine_fully_heals_player(self):
        game = _game_with_service(1330, "shrine")
        game.health = 1
        game.apply_town_service()
        self.assertEqual(game.health, game.max_health)

    def test_shrine_cleanses_burn(self):
        game = _game_with_service(1331, "shrine")
        game.player_statuses["burn"] = 2
        game.apply_town_service()
        self.assertNotIn("burn", game.player_statuses)

    # --- smith ---

    def test_smith_grants_ammo(self):
        game = _game_with_service(1340, "smith")
        before = game.ammo
        game.apply_town_service()
        self.assertGreater(game.ammo, before)

    def test_smith_grants_tonic(self):
        game = _game_with_service(1341, "smith")
        before = game.inventory_quantity("tonic")
        game.apply_town_service()
        self.assertGreater(game.inventory_quantity("tonic"), before)

    # --- chapel ---

    def test_chapel_grants_ward(self):
        game = _game_with_service(1350, "chapel")
        game.player_statuses.pop("ward", None)
        game.apply_town_service()
        self.assertIn("ward", game.player_statuses)
        self.assertGreater(game.player_statuses["ward"], 0)

    def test_chapel_cleanses_and_gives_stronger_ward(self):
        game = _game_with_service(1351, "chapel")
        game.player_statuses["poison"] = 2
        game.player_statuses.pop("ward", None)
        game.apply_town_service()
        self.assertNotIn("poison", game.player_statuses)
        self.assertGreaterEqual(game.player_statuses.get("ward", 0), 6)

    # --- cache ---

    def test_cache_grants_ammo_and_supplies(self):
        game = _game_with_service(1360, "cache")
        ammo_before = game.ammo
        kits_before = game.inventory_quantity("medkit")
        tonics_before = game.inventory_quantity("tonic")
        game.apply_town_service()
        self.assertEqual(game.ammo, ammo_before + 3)
        self.assertEqual(game.inventory_quantity("medkit"), kits_before + 2)
        self.assertEqual(game.inventory_quantity("tonic"), tonics_before + 1)

    # --- idempotency ---

    def test_service_does_nothing_when_already_claimed(self):
        game = _game_with_service(1370, "supply")
        game.apply_town_service()
        ammo_after_first = game.ammo
        game.service_modal_open = False
        game.apply_town_service()
        self.assertEqual(game.ammo, ammo_after_first)
        self.assertFalse(game.service_modal_open)

    # --- ruins / dungeon / castle ---

    def test_ruins_grants_medkit(self):
        game = _game_with_service(1380, "ruins")
        before = game.inventory_quantity("medkit")
        game.apply_town_service()
        self.assertEqual(game.inventory_quantity("medkit"), before + 1)

    def test_cave_grants_ammo(self):
        game = _game_with_service(1381, "cave")
        before = game.ammo
        game.apply_town_service()
        self.assertEqual(game.ammo, before + 2)

    def test_dungeon_grants_tonic(self):
        game = _game_with_service(1382, "dungeon")
        before = game.inventory_quantity("tonic")
        game.apply_town_service()
        self.assertEqual(game.inventory_quantity("tonic"), before + 1)


if __name__ == "__main__":
    unittest.main()
