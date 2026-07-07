"""
Loading screen.
Shown at game startup.
"""

import arcade
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

CX = SCREEN_WIDTH // 2
CY = SCREEN_HEIGHT // 2


class LoadingScreen(arcade.View):
    """Loading screen displayed at game startup."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.elapsed_time = 0
        self.duration = 4.0
        self.background_texture = arcade.load_texture(":backgrounds:loading_background.jpg")
        self._music = arcade.load_sound(":sounds:loading_music.mp3")
        self._music_player = None

        self._title_text = arcade.Text(
            "GAMEMIE",
            x=CX, y=CY + 50,
            font_size=40, color=arcade.color.LIGHT_CYAN, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._loading_text = arcade.Text(
            "Loading...",
            x=CX, y=CY,
            font_size=20, color=arcade.color.WHITE,
            anchor_x="center", anchor_y="center",
        )
        self._rights_text = arcade.Text(
            'ALL RIGHTS RESERVED, TM "SSD" ©',
            x=CX, y=CY - 100,
            font_size=15, color=arcade.color.WHITE,
            anchor_x="center", anchor_y="center",
        )

    def on_show_view(self):
        self.elapsed_time = 0
        self._music_player = arcade.play_sound(self._music)

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background_texture,
            arcade.XYWH(CX, CY, SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        self._title_text.draw()
        self._loading_text.draw()
        self._rights_text.draw()

        bar_width = 200
        bar_height = 10
        filled_width = (self.elapsed_time / self.duration) * bar_width
        bar_left = CX - bar_width // 2
        arcade.draw_rect_filled(
            arcade.XYWH(bar_left + filled_width / 2, CY - 50, filled_width, bar_height),
            arcade.color.LIGHT_BLUE
        )
        arcade.draw_rect_outline(
            arcade.XYWH(CX, CY - 50, bar_width, bar_height),
            arcade.color.WHITE, 1
        )

    def on_update(self, delta_time: float):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            if self._music_player:
                arcade.stop_sound(self._music_player)
            from src.ui.lobby import LobbyView
            self.window.show_view(LobbyView())
