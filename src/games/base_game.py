"""
Base game class for arcade machines.
Inherit from this to create new mini-games.
"""

import arcade
from abc import ABC, abstractmethod


class BaseGame(ABC, arcade.View):
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

    @abstractmethod
    def on_show(self):
        """Called when the view is shown."""
        pass

    @abstractmethod
    def on_draw(self):
        """Render the game."""
        pass

    @abstractmethod
    def on_update(self, delta_time: float):
        """Update game logic."""
        pass

    def on_key_press(self, key: int, modifiers: int):
        """Handle key press."""
        pass

    def on_key_release(self, key: int, modifiers: int):
        """Handle key release."""
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse press."""
        pass

    def finish_game(self, completed: bool = True):
        """Call this when the game should end."""
        self.on_finish_callback(self.score, completed)
