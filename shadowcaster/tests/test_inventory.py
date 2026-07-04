from __future__ import annotations

import unittest

from shadowcaster.models import GroundItem, Item
from shadowcaster.tests.support import make_game


class InventoryTests(unittest.TestCase):

    # --- medkit / tonic use ---

    def test_use_medkit_heals_player(self):
        game = make_game(200)
        game.start_new_game()
        game.health = 1
        game.add_item("medkit", "Healing Potion", "consumable", (200, 0, 0), "vitality", quantity=1,
                      description="Restores health.")
        game.use_item("medkit")
        expected = min(game.max_health, 1 + game.tuning["medkit_heal"])
        self.assertEqual(game.health, expected)

    def test_use_medkit_does_nothing_at_full_health(self):
        game = make_game(201)
        game.start_new_game()
        game.health = game.max_health
        game.inventory = []
        game.add_item("medkit", "Healing Potion", "consumable", (200, 0, 0), "vitality", quantity=1,
                      description="Restores health.")
        game.use_item("medkit")
        self.assertEqual(game.health, game.max_health)
        self.assertEqual(game.inventory_quantity("medkit"), 1)

    def test_use_tonic_adds_ward_status(self):
        game = make_game(202)
        game.start_new_game()
        game.add_item("tonic", "Ward Tonic", "consumable", (100, 100, 200), "power", quantity=1,
                      description="Clears statuses and grants ward.")
        game.use_item("tonic")
        self.assertIn("ward", game.player_statuses)
        self.assertGreater(game.player_statuses["ward"], 0)

    def test_use_tonic_cleanses_status(self):
        game = make_game(203)
        game.start_new_game()
        game.player_statuses["poison"] = 3
        game.add_item("tonic", "Ward Tonic", "consumable", (100, 100, 200), "power", quantity=1,
                      description="Clears statuses and grants ward.")
        game.use_item("tonic")
        self.assertNotIn("poison", game.player_statuses)

    def test_use_item_removes_when_quantity_reaches_zero(self):
        game = make_game(204)
        game.start_new_game()
        game.health = 1
        game.inventory = []
        game.add_item("medkit", "Healing Potion", "consumable", (200, 0, 0), "vitality", quantity=1,
                      description="Restores health.")
        game.use_item("medkit")
        self.assertEqual(game.inventory_quantity("medkit"), 0)

    # --- equip weapon / armor ---

    def test_equip_weapon_increases_effective_melee(self):
        game = make_game(210)
        game.start_new_game()
        base = game.effective_melee_damage
        game.add_item("warhammer", "Warhammer", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=2, ranged_bonus=0)
        game.equip_item("warhammer")
        self.assertEqual(game.effective_melee_damage, base + 2)

    def test_equip_armor_increases_effective_defense(self):
        game = make_game(211)
        game.start_new_game()
        game.add_item("leather_armor", "Leather Armor", "armor", (200, 200, 200), "armor",
                      defense_bonus=1)
        game.equip_item("leather_armor")
        self.assertEqual(game.effective_defense, 1)

    def test_equipping_second_weapon_replaces_first(self):
        game = make_game(212)
        game.start_new_game()
        game.add_item("dagger", "Dagger", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=1, ranged_bonus=0)
        game.add_item("warhammer", "Warhammer", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=2, ranged_bonus=0)
        game.equip_item("dagger")
        game.equip_item("warhammer")
        dagger = game.inventory_item("dagger")
        hammer = game.inventory_item("warhammer")
        assert dagger is not None and hammer is not None
        self.assertFalse(dagger.equipped)
        self.assertTrue(hammer.equipped)

    def test_unequip_clears_effective_bonus(self):
        game = make_game(213)
        game.start_new_game()
        base = game.effective_melee_damage
        game.add_item("dagger", "Dagger", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=1, ranged_bonus=0)
        game.equip_item("dagger")
        game.equip_item("dagger")
        self.assertEqual(game.effective_melee_damage, base)

    # --- floor item pickup ---

    def test_floor_item_pickup_adds_to_inventory(self):
        game = make_game(220)
        game.start_new_game()
        item = Item(key="spear", name="Spear", category="weapon", color=(200, 200, 200),
                    marker="weapon", melee_bonus=1, ranged_bonus=1)
        ground_item = GroundItem(position=game.player, item=item)
        game.floor_items = [ground_item]
        before = game.inventory_quantity("spear")
        game.collect_floor_items()
        self.assertEqual(game.inventory_quantity("spear"), before + 1)
        self.assertNotIn(ground_item, game.floor_items)

    def test_duplicate_non_consumable_pickup_salvages_to_ammo(self):
        game = make_game(221)
        game.start_new_game()
        game.add_item("spear", "Spear", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=1, ranged_bonus=1)
        item = Item(key="spear", name="Spear", category="weapon", color=(200, 200, 200),
                    marker="weapon", melee_bonus=1, ranged_bonus=1)
        ammo_before = game.ammo
        msg = game.add_ground_item_to_inventory(GroundItem(position=game.player, item=item))
        self.assertIn("salvage", msg.lower())
        self.assertEqual(game.ammo, ammo_before + 1)
        self.assertEqual(game.inventory_quantity("spear"), 1)

    def test_consumable_items_stack_on_add(self):
        game = make_game(222)
        game.start_new_game()
        before = game.inventory_quantity("medkit")
        game.add_item("medkit", "Healing Potion", "consumable", (200, 0, 0), "vitality", quantity=1,
                      description="Restores health.")
        game.add_item("medkit", "Healing Potion", "consumable", (200, 0, 0), "vitality", quantity=2,
                      description="Restores health.")
        self.assertEqual(game.inventory_quantity("medkit"), before + 3)


if __name__ == "__main__":
    unittest.main()
