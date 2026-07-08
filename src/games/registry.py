"""
Game registry.
Keeps track of all available arcade machines.
"""

from src.games.pacman_game import PacmanGame
from src.games.snake_game import SnakeGame
from src.games.tetris_game import TetrisGame
from src.games.minesweeper_game import MinesweeperGame   # <-- добавлен
from src.games.demo_game import DemoGame


class GameRegistry:
    """Registry of all arcade machines."""

    MACHINES = [
        # 1 автомат – Pac-Man
        {'id': 'pacman_1', 'name': 'Pac-Man', 'game_class': PacmanGame},

        # 2 автомат – Snake
        {'id': 'snake_1', 'name': 'Snake', 'game_class': SnakeGame},

        # 3 автомат – Tetris
        {'id': 'tetris_1', 'name': 'Tetris', 'game_class': TetrisGame},

        # 4 автомат – Minesweeper
        {'id': 'minesweeper_1', 'name': 'Minesweeper', 'game_class': MinesweeperGame},

        # остальные 6 автоматов – демо-игры
        {'id': 'demo_5', 'name': 'Demo Game 5', 'game_class': DemoGame},
        {'id': 'demo_6', 'name': 'Demo Game 6', 'game_class': DemoGame},
        {'id': 'demo_7', 'name': 'Demo Game 7', 'game_class': DemoGame},
        {'id': 'demo_8', 'name': 'Demo Game 8', 'game_class': DemoGame},
        {'id': 'demo_9', 'name': 'Demo Game 9', 'game_class': DemoGame},
        {'id': 'demo_10', 'name': 'Demo Game 10', 'game_class': DemoGame},
    ]

    @classmethod
    def get_machine_ids(cls):
        return [m['id'] for m in cls.MACHINES]

    @classmethod
    def get_machine(cls, machine_id: str):
        for m in cls.MACHINES:
            if m['id'] == machine_id:
                return m
        return None

    @classmethod
    def create_game(cls, machine_id: str, on_finish_callback):
        machine = cls.get_machine(machine_id)
        if not machine:
            return None
        return machine['game_class'](machine_id, on_finish_callback)