import unittest
from unittest.mock import MagicMock, patch
from src.games.coineater_game import CoineaterGame, STATE_MENU, STATE_GAME


class TestCoineaterLogic(unittest.TestCase):
    def setUp(self):
        """Создаем заглушку для callback и инстанс игры с патчем контекста Arcade."""
        self.callback = MagicMock()
        mock_window = MagicMock()

        with patch('arcade.get_window', return_value=mock_window):
            self.game = CoineaterGame(machine_id="coineater_1", on_finish_callback=self.callback)

    def test_initial_state(self):
        """Проверка дефолтных настроек игры при запуске."""
        self.assertEqual(self.game.state, STATE_MENU)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_gold_mode)

    def test_difficulty_setup_easy(self):
        """Проверка правильности назначения жизней для Easy."""
        self.game.difficulty = "easy"
        self.game.setup_game()
        self.assertEqual(self.game.lives, 3)
        self.assertGreater(self.game.spawn_cooldown, 1.0)

    def test_difficulty_setup_hard(self):
        """Проверка жестких ограничений жизней для Hard."""
        self.game.difficulty = "hard"
        self.game.setup_game()
        self.assertEqual(self.game.lives, 1)

    def test_gold_mode_activation(self):
        """Проверка работы таймера золотой лихорадки."""
        self.game.setup_game()
        self.game.state = STATE_GAME
        self.game.is_gold_mode = True
        self.game.gold_mode_timer = 15.0

        self.game.on_update(delta_time=1.0)
        self.assertEqual(self.game.gold_mode_timer, 14.0)
