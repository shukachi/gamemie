import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock arcade and all game modules before they are imported so no display is needed.
_arcade_mock = MagicMock()
_game_mocks = {
    'arcade': _arcade_mock,
    'src.games.pacman_game': MagicMock(),
    'src.games.snake_game': MagicMock(),
    'src.games.tetris_game': MagicMock(),
    'src.games.minesweeper_game': MagicMock(),
    'src.games.cosmic_racers_game': MagicMock(),
    'src.games.coineater_game': MagicMock(),
    'src.games.cosmic_racer_game': MagicMock(),
    'src.games.demo_game': MagicMock(),
}

# Give each mock module a realistic game class attribute
_game_mocks['src.games.pacman_game'].PacmanGame = MagicMock()
_game_mocks['src.games.snake_game'].SnakeGame = MagicMock()
_game_mocks['src.games.tetris_game'].TetrisGame = MagicMock()
_game_mocks['src.games.minesweeper_game'].MinesweeperGame = MagicMock()
_game_mocks['src.games.cosmic_racers_game'].CosmicRacersGame = MagicMock()
_game_mocks['src.games.coineater_game'].CoineaterGame = MagicMock()
_game_mocks['src.games.cosmic_racer_game'].CosmicRacerGame = MagicMock()
_game_mocks['src.games.demo_game'].DemoGame = MagicMock()

with patch.dict('sys.modules', _game_mocks):
    from src.games.registry import GameRegistry

EXPECTED_IDS = [
    'pacman_1', 'snake_1', 'tetris_1', 'minesweeper_1',
    'cosmicracers_1', 'coineater_1', 'cosmicracer_1',
    'demo_8', 'demo_9', 'demo_10',
]


class TestGetMachineIds(unittest.TestCase):
    def test_returns_all_ten_ids(self):
        self.assertEqual(len(GameRegistry.get_machine_ids()), 10)

    def test_contains_expected_ids(self):
        ids = GameRegistry.get_machine_ids()
        for mid in EXPECTED_IDS:
            self.assertIn(mid, ids)

    def test_ids_are_unique(self):
        ids = GameRegistry.get_machine_ids()
        self.assertEqual(len(ids), len(set(ids)))


class TestGetMachine(unittest.TestCase):
    def test_returns_dict_for_known_id(self):
        machine = GameRegistry.get_machine('pacman_1')
        self.assertIsNotNone(machine)
        self.assertEqual(machine['id'], 'pacman_1')
        self.assertEqual(machine['name'], 'Pac-Man')

    def test_returns_none_for_unknown_id(self):
        self.assertIsNone(GameRegistry.get_machine('does_not_exist'))

    def test_machine_dict_has_required_keys(self):
        for mid in EXPECTED_IDS:
            machine = GameRegistry.get_machine(mid)
            self.assertIn('id', machine)
            self.assertIn('name', machine)
            self.assertIn('game_class', machine)

    def test_all_ids_resolvable(self):
        for mid in EXPECTED_IDS:
            self.assertIsNotNone(GameRegistry.get_machine(mid),
                                 msg=f"Machine '{mid}' not found in registry")


class TestCreateGame(unittest.TestCase):
    def test_returns_none_for_unknown_id(self):
        result = GameRegistry.create_game('nonexistent', None)
        self.assertIsNone(result)

    def test_creates_game_for_valid_id(self):
        callback = MagicMock()
        game = GameRegistry.create_game('pacman_1', callback)
        self.assertIsNotNone(game)

    def test_create_game_calls_constructor_with_machine_id(self):
        callback = MagicMock()
        GameRegistry.create_game('snake_1', callback)
        machine = GameRegistry.get_machine('snake_1')
        machine['game_class'].assert_called_once_with('snake_1', callback)

    def test_create_game_passes_callback(self):
        callback = MagicMock()
        GameRegistry.create_game('tetris_1', callback)
        machine = GameRegistry.get_machine('tetris_1')
        _, kwargs_or_args = machine['game_class'].call_args[0], machine['game_class'].call_args
        # callback is the second positional argument
        self.assertIn(callback, machine['game_class'].call_args[0])


if __name__ == '__main__':
    unittest.main()
