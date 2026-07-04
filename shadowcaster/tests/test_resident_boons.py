from __future__ import annotations

import unittest

from shadowcaster.models import Resident
from shadowcaster.tests.support import make_game


def _make_resident(kind: str, pos=(5, 5)) -> Resident:
    return Resident(position=pos, kind=kind, color=(200, 200, 200))


def _game_in_town(seed: int):
    game = make_game(seed)
    game.start_new_game()
    # Game starts inside the starting town by design; ensure region_type is set
    game.region_type = "town"
    return game


class ResidentBoonTests(unittest.TestCase):

    # --- farmer ---

    def test_farmer_heals_one_hp_when_injured(self):
        game = _game_in_town(1200)
        game.health = game.max_health - 2
        before = game.health
        game.apply_resident_boon(_make_resident("farmer"))
        self.assertEqual(game.health, before + 1)

    def test_farmer_does_nothing_at_full_health(self):
        game = _game_in_town(1201)
        game.health = game.max_health
        game.apply_resident_boon(_make_resident("farmer"))
        self.assertEqual(game.health, game.max_health)

    def test_farmer_boon_only_activates_once(self):
        game = _game_in_town(1202)
        game.health = 1
        game.apply_resident_boon(_make_resident("farmer"))
        hp_after_first = game.health
        game.health = 1
        game.apply_resident_boon(_make_resident("farmer"))
        self.assertEqual(game.health, 1)
        self.assertGreater(hp_after_first, 1)

    # --- vendor ---

    def test_vendor_grants_one_ammo(self):
        game = _game_in_town(1210)
        before = game.ammo
        game.apply_resident_boon(_make_resident("vendor"))
        self.assertEqual(game.ammo, before + 1)

    def test_vendor_boon_only_activates_once(self):
        game = _game_in_town(1211)
        before = game.ammo
        game.apply_resident_boon(_make_resident("vendor"))
        game.apply_resident_boon(_make_resident("vendor"))
        self.assertEqual(game.ammo, before + 1)

    # --- herbalist ---

    def test_herbalist_cleanses_poison(self):
        game = _game_in_town(1220)
        game.player_statuses["poison"] = 3
        game.apply_resident_boon(_make_resident("herbalist"))
        self.assertNotIn("poison", game.player_statuses)

    def test_herbalist_does_nothing_without_status(self):
        game = _game_in_town(1221)
        game.player_statuses.pop("poison", None)
        game.player_statuses.pop("burn", None)
        result = game.apply_resident_boon(_make_resident("herbalist"))
        self.assertTrue(result)
        self.assertNotIn("poison", game.player_statuses)
        self.assertNotIn("burn", game.player_statuses)

    # --- mason ---

    def test_mason_grants_ward_status(self):
        game = _game_in_town(1230)
        game.player_statuses.pop("ward", None)
        game.apply_resident_boon(_make_resident("mason"))
        self.assertIn("ward", game.player_statuses)
        self.assertGreater(game.player_statuses["ward"], 0)

    # --- miller ---

    def test_miller_grants_medkit(self):
        game = _game_in_town(1240)
        before = game.inventory_quantity("medkit")
        game.apply_resident_boon(_make_resident("miller"))
        self.assertEqual(game.inventory_quantity("medkit"), before + 1)

    # --- trapper ---

    def test_trapper_grants_tonic(self):
        game = _game_in_town(1250)
        before = game.inventory_quantity("tonic")
        game.apply_resident_boon(_make_resident("trapper"))
        self.assertEqual(game.inventory_quantity("tonic"), before + 1)

    # --- drover ---

    def test_drover_grants_ammo(self):
        game = _game_in_town(1260)
        before = game.ammo
        game.apply_resident_boon(_make_resident("drover"))
        self.assertEqual(game.ammo, before + 1)

    # --- boon returns False outside a town ---

    def test_resident_boon_does_nothing_outside_town(self):
        game = make_game(1270)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.region_type = "plains"
        result = game.apply_resident_boon(_make_resident("farmer"))
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
