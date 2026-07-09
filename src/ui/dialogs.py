"""
UI components and dialogs.
"""

import arcade
import json
import os
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIALOG_WIDTH, DIALOG_HEIGHT

_BG_STAR_COLOR = (255, 255, 255, 123)
_FG_STAR_COLORS = [
    arcade.color.WHITE,
    arcade.color.BABY_BLUE,
    arcade.color.BUFF,
    arcade.color.ALIZARIN_CRIMSON,
]


_GAME_LB_MAP = {
    'pacman_1':      ('data/leaderboards/pacman_leaderboard.json',      'score'),
    'snake_1':       ('data/leaderboards/snake_leaderboard.json',       'score'),
    'tetris_1':      ('data/leaderboards/tetris_leaderboard.json',      'score'),
    'minesweeper_1': ('data/leaderboards/minesweeper_leaderboard.json', 'time'),
}
_LEVELS = ['easy', 'medium', 'hard']
_LEVEL_LABELS = ['Easy', 'Medium', 'Hard']
_MAX_LB = 10


def _load_game_lb(path: str) -> dict:
    empty = {lv: [] for lv in _LEVELS}
    if not os.path.exists(path):
        return empty
    try:
        with open(path) as f:
            data = json.load(f)
        return {lv: data.get(lv, []) for lv in _LEVELS}
    except Exception:
        return empty


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

    _bg_texture = None

    def __init__(self, machine_id: str, machine_name: str, leaderboard_entries: list,
                 on_confirm_callback, on_cancel_callback):
        super().__init__()
        self.machine_id = machine_id
        self.on_confirm_callback = on_confirm_callback
        self.on_cancel_callback = on_cancel_callback

        if ConfirmationDialog._bg_texture is None:
            path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "assets", "backgrounds", "screen_avt.jpeg",
            )
            ConfirmationDialog._bg_texture = arcade.load_texture(path)

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self._button_y = cy - DIALOG_HEIGHT // 2 + 30

        self._title_text = arcade.Text(
            machine_name, cx, cy + DIALOG_HEIGHT // 2 - 28,
            font_size=18, color=arcade.color.WHITE, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._play_text = arcade.Text(
            "Play", cx - 105, self._button_y - 8,
            font_size=12, color=arcade.color.GREEN, bold=True,
        )
        self._cancel_text = arcade.Text(
            "Cancel", cx + 55, self._button_y - 8,
            font_size=12, color=arcade.color.RED, bold=True,
        )

        self._has_diff_lb = machine_id in _GAME_LB_MAP
        if self._has_diff_lb:
            lb_file, val_key = _GAME_LB_MAP[machine_id]
            self._val_key = val_key
            lb_data = _load_game_lb(lb_file)
            self._build_diff_texts(cx, cy, lb_data)
        else:
            self._build_simple_texts(cx, cy, leaderboard_entries)

    def _build_diff_texts(self, cx, cy, lb_data):
        col_w = DIALOG_WIDTH // 3
        score_y = cy + DIALOG_HEIGHT // 2 - 58
        self._score_header = arcade.Text(
            "Score", cx, score_y,
            font_size=14, color=arcade.color.LIGHT_YELLOW,
            anchor_x="center", anchor_y="center",
        )
        header_y = score_y - 32
        self._col_headers = [
            arcade.Text(
                label,
                (cx - DIALOG_WIDTH // 2) + col_w * i + col_w // 2, header_y,
                font_size=14, color=arcade.color.ORANGE,
                anchor_x="center", anchor_y="center",
            )
            for i, label in enumerate(_LEVEL_LABELS)
        ]
        entry_top = header_y - 26
        self._col_entries = []
        for i, level in enumerate(_LEVELS):
            xc = (cx - DIALOG_WIDTH // 2) + col_w * i + col_w // 2
            entries = lb_data[level]
            col = []
            if not entries:
                col.append(arcade.Text(
                    "Empty", xc, entry_top,
                    font_size=12, color=arcade.color.GRAY,
                    anchor_x="center", anchor_y="center",
                ))
            else:
                for j, e in enumerate(entries[:_MAX_LB]):
                    val = f"{e['time']:.1f}s" if self._val_key == 'time' else str(e['score'])
                    col.append(arcade.Text(
                        f"{j + 1}. {e['name']}: {val}",
                        xc, entry_top - j * 18,
                        font_size=11, color=arcade.color.WHITE,
                        anchor_x="center", anchor_y="center",
                    ))
            self._col_entries.append(col)

    def _build_simple_texts(self, cx, cy, entries):
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
            for i, e in enumerate(entries[:5])
        ]

    def on_draw(self):
        self.clear()
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        arcade.draw_texture_rect(
            self._bg_texture,
            arcade.XYWH(cx, cy, SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        self._title_text.draw()

        if self._has_diff_lb:
            self._score_header.draw()
            for h in self._col_headers:
                h.draw()
            for col in self._col_entries:
                for t in col:
                    t.draw()
        else:
            self._scores_header.draw()
            for t in self._entry_texts:
                t.draw()

        arcade.draw_rect_outline(
            arcade.XYWH(cx - 80, self._button_y, 60, 30), arcade.color.GREEN, 2
        )
        self._play_text.draw()
        arcade.draw_rect_outline(
            arcade.XYWH(cx + 80, self._button_y, 60, 30), arcade.color.RED, 2
        )
        self._cancel_text.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        cx = SCREEN_WIDTH // 2
        by = self._button_y
        if cx - 110 < x < cx - 50 and by - 15 < y < by + 15:
            self.on_confirm_callback()
        elif cx + 50 < x < cx + 110 and by - 15 < y < by + 15:
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
