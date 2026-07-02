"""
Template file for creating new arcade games.
Copy this file and rename it to create your own game.
"""

import arcade
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MyCustomGame(BaseGame):
    """Your custom arcade game implementation."""

    def __init__(self, machine_id: str, on_finish_callback):
        """
        Args:
            machine_id: Unique ID for this arcade machine
            on_finish_callback: Function called when game ends with signature:
                               on_finish_callback(score: int, completed: bool)
        """
        super().__init__("My Custom Game", machine_id, on_finish_callback)
        self.time_remaining = 60  # Set game duration in seconds
        self.elapsed_time = 0
        self.background_color = arcade.color.DARK_BLUE_GRAY

    def on_show(self):
        """Called when the view is shown. Initialize game here."""
        self.elapsed_time = 0
        self.score = 0

    def on_draw(self):
        """Render your game here."""
        self.clear()

        # Draw background
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            self.background_color
        )

        # TODO: Draw your game elements here

        # Draw HUD
        arcade.draw_text(
            f"Score: {self.score}",
            50, SCREEN_HEIGHT - 50,
            font_size=16, color=arcade.color.WHITE
        )
        arcade.draw_text(
            f"Time: {max(0, self.time_remaining - self.elapsed_time):.1f}s",
            50, SCREEN_HEIGHT - 100,
            font_size=16, color=arcade.color.WHITE
        )

    def on_update(self, delta_time: float):
        """Update your game logic here."""
        self.elapsed_time += delta_time

        # TODO: Update game state here

        # End game when time runs out
        if self.elapsed_time >= self.time_remaining:
            self.finish_game(True)

    def on_key_press(self, key: int, modifiers: int):
        """Handle key presses."""
        if key == arcade.key.ESCAPE:
            self.finish_game(False)
        # TODO: Handle your game controls here

    def on_key_release(self, key: int, modifiers: int):
        """Handle key releases."""
        # TODO: Handle key release events
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse clicks."""
        # TODO: Handle mouse input here
        pass
