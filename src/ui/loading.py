"""
Loading screen.
Shown at game startup.
"""

import os
import arcade
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class LoadingScreen(arcade.View):
    """Loading screen displayed at game startup."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.elapsed_time = 0
        self.duration = 2.0  # 2 seconds

        bg_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "backgrounds", "loading_background.jpg"
        ))
        self.background_texture = arcade.load_texture(bg_path)

    def on_show(self):
        """Screen initialization."""
        self.elapsed_time = 0

    def on_draw(self):
        """Draw the loading screen."""
        self.clear()

        arcade.draw_texture_rect(
            self.background_texture,
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        arcade.draw_text(
            "GAMEMIE ",
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50,
            font_size=40, color=arcade.color.LIGHT_CYAN, bold=True
        )

        arcade.draw_text(
            "Loading...",
            SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2,
            font_size=20, color=arcade.color.WHITE
        )

        arcade.draw_text(
            "ALL RIGHTS RESERVED, TM \"SSD\" ©",
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100,
            font_size=15, color=arcade.color.WHITE
        )

        # Progress bar
        bar_width = 200
        bar_height = 10
        filled_width = (self.elapsed_time / self.duration) * bar_width
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, filled_width, bar_height),
            arcade.color.LIGHT_BLUE
        )
        arcade.draw_rect_outline(
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, bar_width, bar_height),
            arcade.color.WHITE, 1
        )

    def on_update(self, delta_time: float):
        """Update loading progress."""
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            from src.ui.lobby import LobbyView
            self.window.show_view(LobbyView())
