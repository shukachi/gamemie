from src.games.pacman_game import PacmanGame
from src.games.snake_game import SnakeGame
from src.games.tetris_game import TetrisGame
from src.games.minesweeper_game import MinesweeperGame
from src.games.cosmic_racers_game import CosmicRacersGame
from src.games.coineater_game import CoineaterGame
from src.games.cosmic_racer_game import CosmicRacerGame
from src.games.demo_game import DemoGame
from src.games.gravity_grid_game import GravityGridGame


class GameRegistry:
    MACHINES = [
        {'id': 'pacman_1', 'name': 'Pac-Man', 'game_class': PacmanGame},
        {'id': 'snake_1', 'name': 'Snake', 'game_class': SnakeGame},
        {'id': 'tetris_1', 'name': 'Tetris', 'game_class': TetrisGame},
        {'id': 'minesweeper_1', 'name': 'Minesweeper', 'game_class': MinesweeperGame},
        {'id': 'cosmicracers_1', 'name': 'Cosmic Racers', 'game_class': CosmicRacersGame},
        {'id': 'coineater_1', 'name': 'Coineater', 'game_class': CoineaterGame},
        {'id': 'cosmicracer_1', 'name': 'CosmicRacer', 'game_class': CosmicRacerGame},
        {'id': 'gravity_grid_1', 'name': 'Gravity Grid', 'game_class': GravityGridGame},

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
