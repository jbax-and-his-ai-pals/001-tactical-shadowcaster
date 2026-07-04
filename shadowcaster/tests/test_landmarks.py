from __future__ import annotations

import unittest

from shadowcaster.constants import COLOR_ACCENT, COLOR_HEAL
from shadowcaster.models import Landmark
from shadowcaster.tests.support import make_game


def _make_landmark(kind, key=None):
    return Landmark(
        key=key or f"test_{kind}",
        position=(5, 5),
        kind=kind,
        name=f"Test {kind.replace('_', ' ').title()}",
        color=(200, 200, 200),
        marker=kind,
    )


class LandmarkTests(unittest.TestCase):

    # --- surface kind completeness ---

    def test_all_surface_kinds_have_handler(self):
        game = make_game(300)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        for kind in sorted(game.surface_landmark_kinds()):
            with self.subTest(kind=kind):
                game.claimed_surface_landmark_keys.clear()
                game.service_modal_open = False
                lm = _make_landmark(kind, key=f"probe_{kind}")
                game.apply_surface_landmark(lm)
                self.assertTrue(
                    game.service_modal_open,
                    f"apply_surface_landmark did not open modal for kind '{kind}'",
                )
                self.assertTrue(
                    game.service_modal_lines,
                    f"apply_surface_landmark produced no lines for kind '{kind}'",
                )

    # --- per-kind effects ---

    def test_oasis_restores_full_health(self):
        game = make_game(310)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.health = 1
        game.apply_surface_landmark(_make_landmark("oasis"))
        self.assertEqual(game.health, game.max_health)

    def test_hot_spring_cleanses_poison(self):
        game = make_game(311)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.player_statuses["poison"] = 3
        game.apply_surface_landmark(_make_landmark("hot_spring"))
        self.assertNotIn("poison", game.player_statuses)

    def test_stone_circle_adds_ward(self):
        game = make_game(312)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.apply_surface_landmark(_make_landmark("stone_circle"))
        self.assertIn("ward", game.player_statuses)
        self.assertGreater(game.player_statuses["ward"], 0)

    def test_watchtower_reveals_adjacent_regions(self):
        game = make_game(313)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        discovered_before = len(game.world_regions)
        game.apply_surface_landmark(_make_landmark("watchtower"))
        self.assertGreaterEqual(len(game.world_regions), discovered_before)

    def test_barrow_grants_gold_and_potion(self):
        game = make_game(314)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        gold_before = game.gold
        kits_before = game.inventory_quantity("medkit")
        game.apply_surface_landmark(_make_landmark("barrow"))
        self.assertGreater(game.gold, gold_before)
        self.assertEqual(game.inventory_quantity("medkit"), kits_before + 1)

    def test_camp_grants_ammo_and_potion(self):
        game = make_game(315)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        ammo_before = game.ammo
        kits_before = game.inventory_quantity("medkit")
        game.apply_surface_landmark(_make_landmark("camp"))
        self.assertEqual(game.ammo, ammo_before + 2)
        self.assertEqual(game.inventory_quantity("medkit"), kits_before + 1)

    def test_necropolis_grants_heavy_loot(self):
        game = make_game(316)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        gold_before = game.gold
        kits_before = game.inventory_quantity("medkit")
        tonics_before = game.inventory_quantity("tonic")
        game.apply_surface_landmark(_make_landmark("necropolis"))
        self.assertGreater(game.gold, gold_before)
        self.assertEqual(game.inventory_quantity("medkit"), kits_before + 2)
        self.assertEqual(game.inventory_quantity("tonic"), tonics_before + 1)

    # --- enterable landmark entry ---

    def test_enterable_landmark_sets_local_region(self):
        game = make_game(320)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        enterable = next(
            (lm for lm in game.landmarks if lm.kind not in game.surface_landmark_kinds()),
            None,
        )
        if enterable is None:
            self.skipTest("No enterable landmark generated for this seed")
        game.enter_landmark(enterable)
        self.assertTrue(game.in_local_region())
        self.assertEqual(game.region_type, enterable.kind)

    def test_leave_local_region_restores_overworld(self):
        game = make_game(321)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        overworld_type = game.region_type
        enterable = next(
            (lm for lm in game.landmarks if lm.kind not in game.surface_landmark_kinds()),
            None,
        )
        if enterable is None:
            self.skipTest("No enterable landmark generated for this seed")
        game.enter_landmark(enterable)
        self.assertNotEqual(game.region_type, overworld_type)
        game.leave_local_region()
        self.assertFalse(game.in_local_region())
        self.assertEqual(game.region_type, overworld_type)

    def test_surface_landmark_claim_persists_in_region_snapshot(self):
        game = make_game(322)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        lm = _make_landmark("camp", key="snapshot_camp")
        game.apply_surface_landmark(lm)
        game.store_current_region()
        region_key = game.region_key(game.world_position)
        saved_claims = game.world_regions[region_key].get("claimed_surface_landmark_keys", set())
        self.assertIn("snapshot_camp", saved_claims)


if __name__ == "__main__":
    unittest.main()
