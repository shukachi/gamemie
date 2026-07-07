"""
Base game class for arcade machines.
Inherit from this to create new mini-games.
"""

from abc import ABC, abstractmethod
import arcade
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class BaseGame(arcade.View, ABC):
    """Base class for all arcade machine games."""

    def __init__(self, game_name: str, machine_id: str, on_finish_callback):
        """
        Args:
            game_name: Display name of the game
            machine_id: Unique identifier for this machine
            on_finish_callback: Callable(score, completed) - called when game ends
        """
        super().__init__()
        self.game_name = game_name
        self.machine_id = machine_id
        self.on_finish_callback = on_finish_callback
        self.score = 0
        self.time_remaining = 60  # Default 60 seconds per game
        self.elapsed_time = 0

    @abstractmethod
    def on_update(self, delta_time: float):
        """Update game logic each frame."""
        pass

    @abstractmethod
    def on_draw(self):
        """Render the game."""
        pass

    def finish_game(self, completed: bool = True):
        """Call this when the game should end."""
        self.on_finish_callback(self.score, completed)
