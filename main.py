"""
Main entry point for the game.
"""

import arcade
import sys
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FPS
from src.ui.loading import LoadingScreen


def main():
    """Create and run the arcade window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_update_rate(1 / FPS)

    loading_screen = LoadingScreen()
    window.show_view(loading_screen)

    arcade.run()


if __name__ == "__main__":
    main()
