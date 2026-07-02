"""
Loading screen.
Shown at game startup.
"""

import arcade
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class LoadingScreen(arcade.View):
    """Loading screen displayed at game startup."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_BLUE_GRAY
        self.elapsed_time = 0
        self.duration = 2.0  # 2 seconds

    def on_show(self):
        """Screen initialization."""
        self.elapsed_time = 0

    def on_draw(self):
        """Draw the loading screen."""
        arcade.start_render()

        arcade.draw_text(
            "ARCADE CLUB",
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50,
            font_size=40, color=arcade.color.LIGHT_CYAN, bold=True
        )

        arcade.draw_text(
            "Loading...",
            SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2,
            font_size=20, color=arcade.color.WHITE
        )

        # Progress bar
        bar_width = 200
        bar_height = 10
        filled_width = (self.elapsed_time / self.duration) * bar_width
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
            filled_width, bar_height,
            arcade.color.LIGHT_BLUE
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
            bar_width, bar_height,
            arcade.color.WHITE, 1
        )

    def on_update(self, delta_time: float):
        """Update loading progress."""
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            from src.ui.lobby import LobbyView
            self.window.show_view(LobbyView())
