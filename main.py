"""
Main entry point for the game.
"""

import os
import arcade
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FPS
from src.ui.loading import LoadingScreen


def _register_resources() -> None:
    BASE = os.path.dirname(os.path.abspath(__file__))
    arcade.resources.add_resource_handle("backgrounds", os.path.join(BASE, "assets", "backgrounds"))
    arcade.resources.add_resource_handle("player", os.path.join(BASE, "assets", "sprites", "player"))
    arcade.resources.add_resource_handle("cashier", os.path.join(BASE, "assets", "sprites", "cashier"))
    arcade.resources.add_resource_handle("sounds", os.path.join(BASE, "assets", "sounds"))
    arcade.resources.add_resource_handle("fonts", os.path.join(BASE, "assets", "fonts"))


def main():
    """Create and run the arcade window."""
    _register_resources()
    cfg.load_settings()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=cfg.FULLSCREEN)
    window.set_update_rate(1 / FPS)

    loading_screen = LoadingScreen()
    window.show_view(loading_screen)

    arcade.run()


if __name__ == "__main__":
    main()
