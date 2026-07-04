from __future__ import annotations

import unittest

from shadowcaster.models import Quest
from shadowcaster.tests.support import make_game


def _make_quest(**kwargs):
    defaults = dict(
        id="q1", kind="delivery",
        from_world_pos=(0, 0), to_world_pos=(1, 0),
        to_town_hint="East", item_key="parcel", item_name="Parcel",
        description="Test quest.", reward_gold=5, status="active",
    )
    defaults.update(kwargs)
    return Quest(**defaults)


def _complete_quest(game, quest):
    quest.status = "complete"
    game.active_quests.append(quest)


class QuestExtendedTests(unittest.TestCase):

    # --- quest_target_label ---

    def test_quest_target_label_includes_region_name(self):
        game = make_game(2300)
        game.start_new_game()
        quest = _make_quest(from_world_pos=(0, 0), to_world_pos=(1, 0),
                            target_region_name="Dustfall")
        label = game.quest_target_label(quest)
        self.assertIn("Dustfall", label)

    def test_quest_target_label_includes_direction(self):
        game = make_game(2301)
        game.start_new_game()
        quest = _make_quest(from_world_pos=(0, 0), to_world_pos=(1, 0),
                            target_region_name="Dustfall")
        label = game.quest_target_label(quest)
        self.assertIn("east", label.lower())

    def test_quest_target_label_north_for_negative_y(self):
        game = make_game(2302)
        game.start_new_game()
        quest = _make_quest(from_world_pos=(0, 0), to_world_pos=(0, -1),
                            target_region_name="Frost Edge")
        label = game.quest_target_label(quest)
        self.assertIn("north", label.lower())

    # --- chain_reward_label ---

    def test_chain_reward_label_medkit(self):
        game = make_game(2310)
        game.start_new_game()
        label = game.chain_reward_label("medkit")
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    def test_chain_reward_label_tonic(self):
        game = make_game(2311)
        game.start_new_game()
        label = game.chain_reward_label("tonic")
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    def test_chain_reward_label_unknown_key_returns_fallback(self):
        game = make_game(2312)
        game.start_new_game()
        label = game.chain_reward_label("nonexistent_key")
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    # --- chain_objective_label ---

    def test_chain_objective_label_hunt(self):
        game = make_game(2320)
        game.start_new_game()
        label = game.chain_objective_label("hunt")
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    def test_chain_objective_label_survey(self):
        game = make_game(2321)
        game.start_new_game()
        label = game.chain_objective_label("survey")
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    # --- chain_mid_message ---

    def test_chain_mid_message_with_landmark(self):
        game = make_game(2330)
        game.start_new_game()
        game.region_name = "Testtown"
        msg = game.chain_mid_message("Old Ruins", "Dustfall")
        self.assertIn("Old Ruins", msg)
        self.assertIn("Dustfall", msg)

    def test_chain_mid_message_without_landmark(self):
        game = make_game(2331)
        game.start_new_game()
        game.region_name = "Testtown"
        msg = game.chain_mid_message(None, "Dustfall")
        self.assertIn("Dustfall", msg)
        self.assertNotIn("None", msg)

    # --- town_prosperity_score and attitude ---

    def test_town_prosperity_zero_with_no_completed_quests(self):
        game = make_game(2340)
        game.start_new_game()
        game.active_quests = []
        score = game.town_prosperity_score(game.world_position)
        self.assertEqual(score, 0)

    def test_town_prosperity_increases_with_completed_delivery(self):
        game = make_game(2341)
        game.start_new_game()
        quest = _make_quest(kind="delivery", from_world_pos=game.world_position,
                            to_world_pos=(1, 0), status="complete")
        _complete_quest(game, quest)
        score = game.town_prosperity_score(game.world_position)
        self.assertGreater(score, 0)

    def test_town_attitude_label_wary_at_zero(self):
        game = make_game(2342)
        game.start_new_game()
        game.active_quests = []
        label = game.town_attitude_label(game.world_position)
        self.assertEqual(label, "Wary")

    def test_town_attitude_label_welcome_at_three(self):
        game = make_game(2343)
        game.start_new_game()
        # Complete 3 delivery quests at this coord to reach score 3
        for i in range(3):
            quest = Quest(
                id=f"d{i}", kind="delivery",
                from_world_pos=game.world_position, to_world_pos=(1, 0),
                to_town_hint="East", item_key="parcel", item_name="Parcel",
                description=".", reward_gold=2, status="complete",
            )
            game.active_quests.append(quest)
        label = game.town_attitude_label(game.world_position)
        self.assertIn(label, ("Welcome", "Trusted", "Beloved"))

    # --- town_service_bonus_tier ---

    def test_service_bonus_tier_zero_with_no_quests(self):
        game = make_game(2350)
        game.start_new_game()
        game.active_quests = []
        tier = game.town_service_bonus_tier(game.world_position)
        self.assertEqual(tier, 0)

    def test_service_bonus_tier_one_at_score_six(self):
        game = make_game(2351)
        game.start_new_game()
        for i in range(6):
            quest = Quest(
                id=f"d{i}", kind="delivery",
                from_world_pos=game.world_position, to_world_pos=(1, 0),
                to_town_hint="East", item_key="parcel", item_name="Parcel",
                description=".", reward_gold=2, status="complete",
            )
            game.active_quests.append(quest)
        tier = game.town_service_bonus_tier(game.world_position)
        self.assertGreaterEqual(tier, 1)

    # --- scout_objective_met ---

    def test_scout_objective_met_at_target_with_no_landmark(self):
        game = make_game(2360)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        quest = _make_quest(
            kind="scout", to_world_pos=game.world_position,
            target_landmark_name="",
        )
        self.assertTrue(game.scout_objective_met(quest))

    def test_scout_objective_not_met_at_wrong_position(self):
        game = make_game(2361)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        quest = _make_quest(kind="scout", to_world_pos=(99, 99))
        self.assertFalse(game.scout_objective_met(quest))

    # --- completed_quest_counts ---

    def test_completed_quest_counts_empty_with_no_quests(self):
        game = make_game(2370)
        game.start_new_game()
        game.active_quests = []
        counts = game.completed_quest_counts()
        self.assertEqual(sum(counts.values()), 0)

    def test_completed_quest_counts_tallies_by_kind(self):
        game = make_game(2371)
        game.start_new_game()
        for kind in ("delivery", "scout", "scout"):
            q = Quest(
                id=f"q_{kind}_{id}", kind=kind,
                from_world_pos=(0, 0), to_world_pos=(1, 0),
                to_town_hint="E", item_key="", item_name="",
                description=".", reward_gold=1, status="complete",
            )
            game.active_quests.append(q)
        counts = game.completed_quest_counts()
        self.assertEqual(counts["delivery"], 1)
        self.assertEqual(counts["scout"], 2)


if __name__ == "__main__":
    unittest.main()
