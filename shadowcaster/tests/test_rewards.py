from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


class RewardTests(unittest.TestCase):

    def _game_with_exploration_reward(self, seed):
        game = make_game(seed)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.exploration_reward_pending = 100
        game.exploration_choice_index = 0
        return game

    # --- exploration reward choices ---

    def test_vitality_choice_increases_max_health(self):
        game = self._game_with_exploration_reward(600)
        before = game.max_health
        amount = game.tuning["full_explore_vitality_bonus"]
        game.exploration_choice_index = 0
        game.apply_exploration_reward_choice()
        self.assertEqual(game.max_health, before + amount)

    def test_vitality_choice_also_heals(self):
        game = self._game_with_exploration_reward(601)
        game.health = 1
        amount = game.tuning["full_explore_vitality_bonus"]
        game.exploration_choice_index = 0
        game.apply_exploration_reward_choice()
        self.assertGreater(game.health, 1)
        self.assertLessEqual(game.health, game.max_health)

    def test_power_choice_increases_melee_damage(self):
        game = self._game_with_exploration_reward(602)
        before = game.melee_damage
        amount = game.tuning["full_explore_power_bonus"]
        game.exploration_choice_index = 1
        game.apply_exploration_reward_choice()
        self.assertEqual(game.melee_damage, before + amount)

    def test_power_choice_increases_ranged_damage(self):
        game = self._game_with_exploration_reward(603)
        before = game.ranged_damage
        amount = game.tuning["full_explore_power_bonus"]
        game.exploration_choice_index = 1
        game.apply_exploration_reward_choice()
        self.assertEqual(game.ranged_damage, before + amount)

    def test_recovery_choice_grants_medkits(self):
        game = self._game_with_exploration_reward(604)
        before = game.inventory_quantity("medkit")
        expected = game.tuning["full_explore_recovery_medkits"]
        game.exploration_choice_index = 2
        game.apply_exploration_reward_choice()
        self.assertEqual(game.inventory_quantity("medkit"), before + expected)

    def test_recovery_choice_grants_tonics(self):
        game = self._game_with_exploration_reward(605)
        before = game.inventory_quantity("tonic")
        expected = game.tuning["full_explore_recovery_tonics"]
        game.exploration_choice_index = 2
        game.apply_exploration_reward_choice()
        self.assertEqual(game.inventory_quantity("tonic"), before + expected)

    def test_reward_clears_pending_after_applied(self):
        game = self._game_with_exploration_reward(606)
        game.exploration_choice_index = 0
        game.apply_exploration_reward_choice()
        self.assertIsNone(game.exploration_reward_pending)

    def test_reward_adds_milestone_to_claimed_set(self):
        game = self._game_with_exploration_reward(607)
        game.exploration_choice_index = 0
        game.apply_exploration_reward_choice()
        self.assertIn(100, game.claimed_exploration_rewards)

    def test_reward_increments_full_clears(self):
        game = self._game_with_exploration_reward(608)
        before = game.full_clears
        game.exploration_choice_index = 0
        game.apply_exploration_reward_choice()
        self.assertEqual(game.full_clears, before + 1)

    # --- has_pending_reward gating ---

    def test_has_pending_reward_true_when_exploration_pending(self):
        game = make_game(620)
        game.start_new_game()
        game.exploration_reward_pending = 100
        self.assertTrue(game.has_pending_reward())

    def test_has_pending_reward_false_when_nothing_pending(self):
        game = make_game(621)
        game.start_new_game()
        game.exploration_reward_pending = None
        game.delve_reward_pending = False
        self.assertFalse(game.has_pending_reward())

    def test_has_pending_reward_true_when_delve_pending(self):
        game = make_game(622)
        game.start_new_game()
        game.delve_reward_pending = True
        self.assertTrue(game.has_pending_reward())

    # --- reward not re-triggered for claimed milestone ---

    def test_claimed_milestone_does_not_reopen_reward(self):
        game = make_game(630)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.claimed_exploration_rewards.add(100)
        game.exploration_progress = 100
        game.check_exploration_rewards()
        self.assertIsNone(game.exploration_reward_pending)


if __name__ == "__main__":
    unittest.main()
