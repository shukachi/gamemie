"""
Example placeholder game.
Demonstrates how to implement a game using BaseGame.
"""

import arcade
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class DemoGame(BaseGame):
    """Simple demo game - catch falling objects."""

    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("Demo Game", machine_id, on_finish_callback)
        self.time_remaining = 30
        self.elapsed_time = 0
        self.background_color = arcade.color.DARK_BLUE_GRAY

    def on_show(self):
        """Game initialization."""
        self.elapsed_time = 0
        self.score = 0

    def on_draw(self):
        """Render the game."""
        arcade.start_render()

        # Draw background
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            self.background_color
        )

        # Draw placeholder text
        arcade.draw_text(
            f"Demo Game - {self.game_name}",
            50, SCREEN_HEIGHT - 50,
            font_size=20, color=arcade.color.WHITE
        )
        arcade.draw_text(
            f"Score: {self.score}",
            50, SCREEN_HEIGHT - 100,
            font_size=16, color=arcade.color.WHITE
        )
        arcade.draw_text(
            f"Time: {max(0, self.time_remaining - self.elapsed_time):.1f}s",
            50, SCREEN_HEIGHT - 150,
            font_size=16, color=arcade.color.WHITE
        )
        arcade.draw_text(
            "Press SPACE to score +10 points",
            SCREEN_WIDTH // 2 - 150, 100,
            font_size=14, color=arcade.color.YELLOW
        )
        arcade.draw_text(
            "Press ESC to exit game",
            SCREEN_WIDTH // 2 - 150, 50,
            font_size=14, color=arcade.color.YELLOW
        )

    def on_update(self, delta_time: float):
        """Update game logic."""
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.time_remaining:
            self.finish_game(True)

    def on_key_press(self, key: int, modifiers: int):
        """Handle input."""
        if key == arcade.key.SPACE:
            self.score += 10
        elif key == arcade.key.ESCAPE:
            self.finish_game(False)
