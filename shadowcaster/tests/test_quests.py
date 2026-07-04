from __future__ import annotations

import unittest

from shadowcaster.models import Quest
from shadowcaster.tests.support import make_game


def _delivery_quest(from_pos=(0, 0), to_pos=(1, 0), gold=5):
    return Quest(
        id="test_delivery",
        kind="delivery",
        from_world_pos=from_pos,
        to_world_pos=to_pos,
        to_town_hint="East",
        item_key="parcel",
        item_name="Parcel",
        description="Deliver a parcel.",
        reward_gold=gold,
        status="active",
    )


def _scout_quest(from_pos=(0, 0), to_pos=(1, 0)):
    return Quest(
        id="test_scout",
        kind="scout",
        from_world_pos=from_pos,
        to_world_pos=to_pos,
        to_town_hint="East",
        item_key="",
        item_name="",
        description="Scout a region.",
        reward_gold=4,
        status="active",
        origin_town_name="Testville",
    )


def _bounty_quest(from_pos=(0, 0), to_pos=(1, 0), target_count=2):
    return Quest(
        id="test_bounty",
        kind="bounty",
        from_world_pos=from_pos,
        to_world_pos=to_pos,
        to_town_hint="East",
        item_key="",
        item_name="",
        description="Hunt enemies.",
        reward_gold=6,
        status="active",
        target_count=target_count,
        origin_town_name="Testville",
    )


class QuestTests(unittest.TestCase):

    # --- accept from notice board ---

    def test_accept_delivery_quest_adds_to_active_quests(self):
        game = make_game(900)
        game.start_new_game()
        game.open_notice_board()
        delivery_idx = next(
            i for i, q in enumerate(game.notice_board_quests) if q.kind == "delivery"
        )
        before = len(game.active_quests)
        game.accept_board_quest(delivery_idx)
        self.assertEqual(len(game.active_quests), before + 1)
        self.assertEqual(game.active_quests[-1].kind, "delivery")

    def test_accept_delivery_quest_adds_item_to_inventory(self):
        game = make_game(901)
        game.start_new_game()
        game.open_notice_board()
        delivery_idx = next(
            i for i, q in enumerate(game.notice_board_quests) if q.kind == "delivery"
        )
        quest_template = game.notice_board_quests[delivery_idx]
        game.accept_board_quest(delivery_idx)
        self.assertGreater(game.inventory_quantity(quest_template.item_key), 0)

    def test_cannot_accept_already_accepted_quest(self):
        game = make_game(902)
        game.start_new_game()
        game.open_notice_board()
        delivery_idx = next(
            i for i, q in enumerate(game.notice_board_quests) if q.kind == "delivery"
        )
        game.accept_board_quest(delivery_idx)
        count_after_first = len(game.active_quests)
        game.accept_board_quest(delivery_idx)
        self.assertEqual(len(game.active_quests), count_after_first)

    # --- delivery completion ---

    def test_delivery_completes_when_at_destination_town(self):
        game = make_game(910)
        game.start_new_game()
        quest = _delivery_quest(from_pos=(0, 0), to_pos=game.world_position)
        game.active_quests.append(quest)
        game.region_type = "town"
        game.check_quest_completion()
        self.assertEqual(quest.status, "complete")

    def test_delivery_grants_gold_on_completion(self):
        game = make_game(911)
        game.start_new_game()
        quest = _delivery_quest(from_pos=(0, 0), to_pos=game.world_position, gold=7)
        game.active_quests.append(quest)
        game.region_type = "town"
        gold_before = game.gold
        game.check_quest_completion()
        self.assertEqual(game.gold, gold_before + 7)

    def test_delivery_removes_quest_item_on_completion(self):
        game = make_game(912)
        game.start_new_game()
        quest = _delivery_quest(from_pos=(0, 0), to_pos=game.world_position)
        game.active_quests.append(quest)
        game.add_item("parcel", "Parcel", "quest", (200, 200, 200), "quest")
        game.region_type = "town"
        game.check_quest_completion()
        self.assertEqual(game.inventory_quantity("parcel"), 0)

    def test_delivery_does_not_complete_at_wrong_town(self):
        game = make_game(913)
        game.start_new_game()
        quest = _delivery_quest(from_pos=(0, 0), to_pos=(99, 99))
        game.active_quests.append(quest)
        game.region_type = "town"
        game.check_quest_completion()
        self.assertEqual(quest.status, "active")

    # --- scout quest ---

    def test_scout_quest_advances_stage_at_target(self):
        game = make_game(920)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        target_pos = game.world_position
        quest = _scout_quest(from_pos=(99, 99), to_pos=target_pos)
        game.active_quests.append(quest)
        game.check_quest_completion()
        self.assertEqual(quest.stage, 1)

    def test_scout_quest_completes_on_return_to_origin(self):
        game = make_game(921)
        game.start_new_game()
        target_pos = game.world_position
        quest = _scout_quest(from_pos=target_pos, to_pos=(99, 99))
        quest.stage = 1
        game.active_quests.append(quest)
        game.region_type = "town"
        game.check_quest_completion()
        self.assertEqual(quest.status, "complete")

    # --- bounty quest ---

    def test_bounty_quest_advances_stage_at_target_region(self):
        game = make_game(930)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        target = game.world_position
        quest = _bounty_quest(from_pos=(99, 99), to_pos=target, target_count=2)
        game.active_quests.append(quest)
        game.check_quest_completion()
        self.assertEqual(quest.stage, 1)

    # --- abandon ---

    def test_abandon_removes_quest_from_active(self):
        game = make_game(940)
        game.start_new_game()
        quest = _delivery_quest()
        game.active_quests.append(quest)
        game.abandon_quest(quest)
        self.assertNotIn(quest, game.active_quests)

    # --- active_delivery_quest helper ---

    def test_active_delivery_quest_returns_active_delivery(self):
        game = make_game(950)
        game.start_new_game()
        quest = _delivery_quest()
        quest.status = "active"
        game.active_quests = [quest]
        self.assertEqual(game.active_delivery_quest(), quest)

    def test_active_delivery_quest_returns_none_when_absent(self):
        game = make_game(951)
        game.start_new_game()
        game.active_quests = []
        self.assertIsNone(game.active_delivery_quest())


if __name__ == "__main__":
    unittest.main()
