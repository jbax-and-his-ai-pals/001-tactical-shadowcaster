from __future__ import annotations

import unittest

from shadowcaster.tests.support import make_game


class BoardAndPreviewTests(unittest.TestCase):
    def test_notice_board_refresh_preserves_selected_quest_when_possible(self):
        game = make_game(811)
        game.start_new_game()
        game.open_notice_board()
        self.assertGreaterEqual(len(game.notice_board_quests), 2)
        game.notice_board_index = 1
        selected_id = game.notice_board_quests[1].id

        game.refresh_notice_board(keep_selection=True)

        self.assertEqual(game.notice_board_quests[game.notice_board_index].id, selected_id)

    def test_notice_board_confirm_unavailable_for_already_accepted_quest(self):
        game = make_game(812)
        game.start_new_game()
        game.open_notice_board()
        self.assertTrue(game.notice_board_confirm_available())

        game.accept_board_quest(0)

        self.assertFalse(game.notice_board_confirm_available())

    def test_local_debug_world_map_mode_seeds_preview_targets(self):
        game = make_game(813)
        game.start_new_game()
        if game.in_local_region():
            game.leave_local_region()
        game.toggle_world_map()

        game.toggle_world_map_mode()

        self.assertEqual(game.world_map_mode, "local_debug")
        self.assertEqual(len(game.local_debug_target_coords), 25)
        self.assertTrue(game.preview_world_regions)


if __name__ == "__main__":
    unittest.main()
