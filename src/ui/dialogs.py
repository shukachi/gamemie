"""
UI components and dialogs.
"""

import arcade
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIALOG_WIDTH, DIALOG_HEIGHT

_BG_STAR_COLOR = (255, 255, 255, 123)
_FG_STAR_COLORS = [
    arcade.color.WHITE,
    arcade.color.BABY_BLUE,
    arcade.color.BUFF,
    arcade.color.ALIZARIN_CRIMSON,
]


def _make_starfield(batch: arcade.shape_list.ShapeElementList,
                    color=_BG_STAR_COLOR, random_color: bool = False) -> None:
    for _ in range(250):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        w = random.randint(1, 3)
        h = random.randint(1, 2)
        c = random.choice(_FG_STAR_COLORS) if random_color else color
        batch.append(arcade.shape_list.create_rectangle_filled(x, y, w, h, c))


class ConfirmationDialog(arcade.View):
    """Dialog shown before starting a game."""

    def __init__(self, machine_id: str, machine_name: str, leaderboard_entries: list,
                 on_confirm_callback, on_cancel_callback):
        super().__init__()
        self.machine_id = machine_id
        self.on_confirm_callback = on_confirm_callback
        self.on_cancel_callback = on_cancel_callback
        self.background_color = arcade.color.DARK_GRAY

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        button_y = cy - DIALOG_HEIGHT // 2 + 30

        self._title_text = arcade.Text(
            machine_name,
            cx - DIALOG_WIDTH // 2 + 20, cy + DIALOG_HEIGHT // 2 - 40,
            font_size=16, color=arcade.color.WHITE, bold=True,
        )
        self._scores_header = arcade.Text(
            "Top Scores:",
            cx - DIALOG_WIDTH // 2 + 20, cy + DIALOG_HEIGHT // 2 - 80,
            font_size=12, color=arcade.color.LIGHT_YELLOW,
        )
        y0 = cy + DIALOG_HEIGHT // 2 - 110
        self._entry_texts = [
            arcade.Text(
                f"{i + 1}. {e.name}: {e.score}",
                cx - DIALOG_WIDTH // 2 + 30, y0 - i * 25,
                font_size=10, color=arcade.color.WHITE,
            )
            for i, e in enumerate(leaderboard_entries[:5])
        ]
        self._play_text = arcade.Text(
            "Play", cx - 105, button_y - 8,
            font_size=12, color=arcade.color.GREEN, bold=True,
        )
        self._cancel_text = arcade.Text(
            "Cancel", cx + 55, button_y - 8,
            font_size=12, color=arcade.color.RED, bold=True,
        )

    def on_draw(self):
        self.clear()
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        button_y = cy - DIALOG_HEIGHT // 2 + 30

        arcade.draw_rect_filled(
            arcade.XYWH(cx, cy, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 150)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(cx, cy, DIALOG_WIDTH, DIALOG_HEIGHT), arcade.color.DARK_SLATE_GRAY
        )
        arcade.draw_rect_outline(
            arcade.XYWH(cx, cy, DIALOG_WIDTH, DIALOG_HEIGHT), arcade.color.WHITE, 2
        )

        self._title_text.draw()
        self._scores_header.draw()
        for t in self._entry_texts:
            t.draw()

        arcade.draw_rect_outline(
            arcade.XYWH(cx - 80, button_y, 60, 30), arcade.color.GREEN, 2
        )
        self._play_text.draw()
        arcade.draw_rect_outline(
            arcade.XYWH(cx + 80, button_y, 60, 30), arcade.color.RED, 2
        )
        self._cancel_text.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        button_y = cy - DIALOG_HEIGHT // 2 + 30
        if cx - 110 < x < cx - 50 and button_y - 15 < y < button_y + 15:
            self.on_confirm_callback()
        elif cx + 50 < x < cx + 110 and button_y - 15 < y < button_y + 15:
            self.on_cancel_callback()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.on_cancel_callback()
        elif key == arcade.key.ENTER:
            self.on_confirm_callback()


class LeaderboardView(arcade.View):
    """Leaderboard display view."""

    _FG_SPEED = 200
    _BG_SPEED = 80

    def __init__(self, title: str, entries: list, on_close_callback):
        super().__init__()
        self.on_close_callback = on_close_callback

        # Parallax star layers (2 tiles each for seamless loop)
        self._fg1 = arcade.shape_list.ShapeElementList()
        self._fg2 = arcade.shape_list.ShapeElementList()
        self._fg2.center_y = SCREEN_HEIGHT
        self._bg1 = arcade.shape_list.ShapeElementList()
        self._bg2 = arcade.shape_list.ShapeElementList()
        self._bg2.center_y = SCREEN_HEIGHT
        _make_starfield(self._fg1, random_color=True)
        _make_starfield(self._fg2, random_color=True)
        _make_starfield(self._bg1)
        _make_starfield(self._bg2)

        cx = SCREEN_WIDTH // 2
        self._title_text = arcade.Text(
            title, cx, SCREEN_HEIGHT - 48,
            font_size=26, color=(255, 215, 0), bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._entry_texts = [
            arcade.Text(
                f"{i + 1}.  {e.name}  —  {e.score}",
                cx, SCREEN_HEIGHT - 120 - i * 42,
                font_size=15, color=arcade.color.LIGHT_YELLOW,
                anchor_x="center", anchor_y="center",
            )
            for i, e in enumerate(entries)
        ]
        self._hint = arcade.Text(
            "ESC или клик — закрыть",
            cx, 38,
            font_size=11, color=arcade.color.LIGHT_GRAY,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        self._bg1.draw()
        self._bg2.draw()
        self._fg1.draw()
        self._fg2.draw()
        self._title_text.draw()
        for t in self._entry_texts:
            t.draw()
        self._hint.draw()

    def on_update(self, delta_time: float):
        self._fg1.center_y -= self._FG_SPEED * delta_time
        self._fg2.center_y -= self._FG_SPEED * delta_time
        self._bg1.center_y -= self._BG_SPEED * delta_time
        self._bg2.center_y -= self._BG_SPEED * delta_time
        for lst in (self._fg1, self._fg2, self._bg1, self._bg2):
            if lst.center_y < -SCREEN_HEIGHT:
                lst.center_y = SCREEN_HEIGHT

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.on_close_callback()

    def on_mouse_press(self, x, y, button, modifiers):
        self.on_close_callback()
