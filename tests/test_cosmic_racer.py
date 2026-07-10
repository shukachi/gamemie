import unittest
from unittest.mock import MagicMock, patch
from src.games.cosmic_racer_game import CosmicRacerGame


class TestCosmicRacerLogic(unittest.TestCase):
    def setUp(self):
        self.callback = MagicMock()
        mock_window = MagicMock()

        with patch('arcade.get_window', return_value=mock_window):
            self.game = CosmicRacerGame(machine_id="cosmicracer_1", on_finish_callback=self.callback)

    def test_menu_state_by_default(self):
        """Игра должна строго стартовать с экрана меню."""
        self.game.on_show_view()
        self.assertEqual(self.game.state, "menu")
        self.assertEqual(self.game.score, 0)

    def test_laser_gap_by_difficulty(self):
        """Проверка, что на Hard зазор лазеров уже, чем на Easy."""
        self.game.difficulty = "easy"
        self.game._start_game()
        easy_gap = self.game.pipe_gap

        self.game.difficulty = "hard"
        self.game._start_game()
        hard_gap = self.game.pipe_gap

        self.assertGreater(easy_gap, hard_gap)

    def test_bird_gravity_fall(self):
        """Проверка, что птица физически падает вниз под гравитацией."""
        self.game._start_game()
        initial_y = self.game.bird.center_y
        self.game.bird.change_y = 0.0

        self.game.on_update(delta_time=1.0)
        self.assertLess(self.game.bird.center_y, initial_y)
