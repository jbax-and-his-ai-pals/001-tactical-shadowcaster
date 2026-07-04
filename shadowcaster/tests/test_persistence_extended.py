from __future__ import annotations

import unittest
from pathlib import Path

from shadowcaster.game import Game
from shadowcaster.models import Quest
from shadowcaster.persistence import load_game, save_game
from shadowcaster.tests.support import make_game

_SAVE_PATH = Path(__file__).parent.parent.parent / "tmp_test_persistence_extended.json"


def _roundtrip(game) -> "Game":
    save_game(game, _SAVE_PATH)
    data = load_game(_SAVE_PATH)
    restored = make_game()
    restored.apply_loaded_state(data)
    return restored


class PersistenceExtendedTests(unittest.TestCase):

    def test_save_load_preserves_health(self):
        game = make_game(1100)
        game.start_new_game()
        game.health = max(1, game.max_health - 3)
        restored = _roundtrip(game)
        self.assertEqual(restored.health, game.health)

    def test_save_load_preserves_max_health(self):
        game = make_game(1101)
        game.start_new_game()
        game.max_health += 5
        game.health = game.max_health
        restored = _roundtrip(game)
        self.assertEqual(restored.max_health, game.max_health)

    def test_save_load_preserves_gold(self):
        game = make_game(1102)
        game.start_new_game()
        game.gold = 42
        restored = _roundtrip(game)
        self.assertEqual(restored.gold, 42)

    def test_save_load_preserves_ammo(self):
        game = make_game(1103)
        game.start_new_game()
        game.ammo = 17
        restored = _roundtrip(game)
        self.assertEqual(restored.ammo, 17)

    def test_save_load_preserves_world_seed(self):
        game = make_game(1104)
        game.start_new_game()
        restored = _roundtrip(game)
        self.assertEqual(restored.world_seed, game.world_seed)

    def test_save_load_preserves_total_monsters_killed(self):
        game = make_game(1105)
        game.start_new_game()
        game.total_monsters_killed = 13
        restored = _roundtrip(game)
        self.assertEqual(restored.total_monsters_killed, 13)

    def test_save_load_preserves_inventory_items(self):
        game = make_game(1106)
        game.start_new_game()
        game.inventory = []
        game.add_item("medkit", "Healing Potion", "consumable", (200, 0, 0), "vitality",
                      quantity=3, description="Restores health.")
        restored = _roundtrip(game)
        self.assertEqual(restored.inventory_quantity("medkit"), 3)

    def test_save_load_preserves_equipped_weapon(self):
        game = make_game(1107)
        game.start_new_game()
        game.add_item("dagger", "Dagger", "weapon", (200, 200, 200), "weapon",
                      melee_bonus=1, ranged_bonus=0)
        game.equip_item("dagger")
        restored = _roundtrip(game)
        item = restored.inventory_item("dagger")
        self.assertIsNotNone(item)
        assert item is not None
        self.assertTrue(item.equipped)

    def test_save_load_preserves_active_quests(self):
        game = make_game(1108)
        game.start_new_game()
        quest = Quest(
            id="persist_test_quest",
            kind="delivery",
            from_world_pos=(0, 0),
            to_world_pos=(2, 0),
            to_town_hint="East",
            item_key="parcel",
            item_name="Parcel",
            description="Test parcel delivery.",
            reward_gold=5,
            status="active",
        )
        game.active_quests.append(quest)
        restored = _roundtrip(game)
        ids = [q.id for q in restored.active_quests]
        self.assertIn("persist_test_quest", ids)

    def test_save_load_preserves_melee_and_ranged_damage(self):
        game = make_game(1109)
        game.start_new_game()
        game.melee_damage += 2
        game.ranged_damage += 1
        original_melee = game.melee_damage
        original_ranged = game.ranged_damage
        restored = _roundtrip(game)
        self.assertEqual(restored.melee_damage, original_melee)
        self.assertEqual(restored.ranged_damage, original_ranged)

    def test_save_load_preserves_player_statuses(self):
        game = make_game(1110)
        game.start_new_game()
        game.player_statuses["ward"] = 5
        restored = _roundtrip(game)
        self.assertIn("ward", restored.player_statuses)
        self.assertEqual(restored.player_statuses["ward"], 5)


if __name__ == "__main__":
    unittest.main()
