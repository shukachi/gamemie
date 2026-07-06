"""Cashier menu and controls / key-binding settings."""
import arcade
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def _key_label(code: int) -> str:
    """Return a short human-readable name for a key code."""
    for name in dir(arcade.key):
        val = getattr(arcade.key, name)
        if val == code and name.isupper() and not name.startswith('_'):
            return name
    if 32 <= code < 127:
        return chr(code).upper()
    return f"#{code}"


# ─────────────────────────── Cashier Menu ───────────────────────────

class CashierMenuView(arcade.View):
    """Top-level cashier menu shown when the player interacts with the cashier."""

    W = int(SCREEN_WIDTH * 0.30)
    H = int(SCREEN_HEIGHT * 0.52)
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    BTN_H = 44
    BTN_GAP = 14

    def __init__(self, player_state, leaderboard, lobby_view):
        super().__init__()
        self.player_state = player_state
        self.leaderboard = leaderboard
        self.lobby_view = lobby_view
        self._build_buttons()

    # ── helpers ──────────────────────────────────────────────────────

    def _build_buttons(self):
        labels = ["УПРАВЛЕНИЕ"]
        if self.player_state.all_machines_locked():
            labels.append("СБРОСИТЬ ПОПЫТКИ")
        else:
            labels.append("ТАБЛИЦА ЛИДЕРОВ")
        labels.append("ЗАКРЫТЬ")
        self._buttons = labels

        # Pre-build Text objects for the button labels
        self._btn_texts = [
            arcade.Text(lbl, x=self.CX, y=0,
                        color=arcade.color.WHITE, font_size=14, bold=True,
                        anchor_x="center", anchor_y="center")
            for lbl in labels
        ]
        self._title_text = arcade.Text(
            "КАССИР", x=self.CX, y=self.CY + self.H // 2 - 30,
            color=arcade.color.YELLOW, font_size=20, bold=True,
            anchor_x="center", anchor_y="center",
        )

    def _btn_y(self, idx: int) -> float:
        total = len(self._buttons) * (self.BTN_H + self.BTN_GAP) - self.BTN_GAP
        top = self.CY + total / 2 - self.BTN_H / 2
        return top - idx * (self.BTN_H + self.BTN_GAP)

    def _hit(self, x: float, y: float, idx: int) -> bool:
        return abs(x - self.CX) < self.W // 2 - 20 and abs(y - self._btn_y(idx)) < self.BTN_H // 2

    # ── arcade callbacks ─────────────────────────────────────────────

    def on_draw(self):
        self.clear()
        # Dim background
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 160),
        )
        # Panel
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.W, self.H), (25, 25, 45, 240)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.W, self.H), (180, 140, 60), 2
        )

        self._title_text.draw()

        for i, text_obj in enumerate(self._btn_texts):
            by = self._btn_y(i)
            arcade.draw_rect_filled(
                arcade.XYWH(self.CX, by, self.W - 40, self.BTN_H), (60, 50, 30, 200)
            )
            text_obj.y = by
            text_obj.draw()

    def on_key_press(self, key, _mod):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.lobby_view)

    def on_mouse_press(self, x, y, button, _mod):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        for i, lbl in enumerate(self._buttons):
            if self._hit(x, y, i):
                if lbl == "УПРАВЛЕНИЕ":
                    self.window.show_view(
                        ControlsView(on_close=lambda: self.window.show_view(self))
                    )
                elif lbl == "ТАБЛИЦА ЛИДЕРОВ":
                    from src.ui.dialogs import LeaderboardView
                    entries = self.leaderboard.get_global_leaderboard()
                    self.window.show_view(
                        LeaderboardView("Club Leaderboard", entries,
                                        on_close=lambda: self.window.show_view(self))
                    )
                elif lbl == "СБРОСИТЬ ПОПЫТКИ":
                    self.player_state.reset_all_attempts()
                    self._build_buttons()
                elif lbl == "ЗАКРЫТЬ":
                    self.window.show_view(self.lobby_view)
                return


# ─────────────────────────── Controls View ───────────────────────────

class ControlsView(arcade.View):
    """Key-binding and mouse-control settings screen."""

    ACTIONS = [
        ('up',       'Вверх'),
        ('down',     'Вниз'),
        ('left',     'Влево'),
        ('right',    'Вправо'),
        ('interact', 'Взаимодействие (E)'),
    ]

    PW = int(SCREEN_WIDTH * 0.46)
    PH = int(SCREEN_HEIGHT * 0.68)
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    ROW_H = 52

    def __init__(self, on_close):
        super().__init__()
        self._close_cb = on_close
        self.waiting_for: str | None = None   # action being remapped
        self._build_texts()

    # ── text construction ─────────────────────────────────────────────

    def _build_texts(self):
        self._title = arcade.Text(
            "НАСТРОЙКИ УПРАВЛЕНИЯ",
            x=self.CX, y=self.CY + self.PH // 2 - 34,
            color=arcade.color.LIGHT_CYAN, font_size=17, bold=True,
            anchor_x="center", anchor_y="center",
        )
        start_y = self.CY + self.PH // 2 - 90
        self._action_labels: list[arcade.Text] = []
        self._key_labels: list[arcade.Text] = []
        for i, (action, label) in enumerate(self.ACTIONS):
            y = start_y - i * self.ROW_H
            self._action_labels.append(arcade.Text(
                label, x=self.CX - self.PW // 2 + 24, y=y,
                color=arcade.color.LIGHT_GRAY, font_size=13,
                anchor_x="left", anchor_y="center",
            ))
            self._key_labels.append(arcade.Text(
                f"[ {_key_label(cfg.KEY_BINDINGS[action])} ]",
                x=self.CX + self.PW // 2 - 24, y=y,
                color=arcade.color.WHITE, font_size=13,
                anchor_x="right", anchor_y="center",
            ))
        mouse_y = start_y - len(self.ACTIONS) * self.ROW_H - 8
        self._mouse_label = arcade.Text(
            "Управление мышью", x=self.CX - self.PW // 2 + 24, y=mouse_y,
            color=arcade.color.LIGHT_GRAY, font_size=13,
            anchor_x="left", anchor_y="center",
        )
        self._mouse_status = arcade.Text(
            "", x=self.CX + self.PW // 2 - 24, y=mouse_y,
            color=arcade.color.WHITE, font_size=13,
            anchor_x="right", anchor_y="center",
        )
        self._close_text = arcade.Text(
            "ЗАКРЫТЬ  (ESC)",
            x=self.CX, y=self.CY - self.PH // 2 + 28,
            color=arcade.color.WHITE, font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )

    def _row_y(self, idx: int) -> float:
        start_y = self.CY + self.PH // 2 - 90
        return start_y - idx * self.ROW_H

    def _mouse_y(self) -> float:
        return self._row_y(len(self.ACTIONS)) - 8

    # ── arcade callbacks ─────────────────────────────────────────────

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 170),
        )
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), (22, 22, 40, 240)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH),
            arcade.color.LIGHT_CYAN, 2,
        )

        self._title.draw()

        for i, (action, _) in enumerate(self.ACTIONS):
            y = self._row_y(i)
            is_waiting = self.waiting_for == action
            if is_waiting:
                arcade.draw_rect_filled(
                    arcade.XYWH(self.CX, y, self.PW - 16, 36), (50, 50, 100, 200)
                )
            self._action_labels[i].draw()
            kl = self._key_labels[i]
            if is_waiting:
                kl.text = "[ нажмите клавишу... ]"
                kl.color = arcade.color.YELLOW
            else:
                kl.text = f"[ {_key_label(cfg.KEY_BINDINGS[action])} ]"
                kl.color = arcade.color.WHITE
            kl.draw()

        # Mouse toggle row
        my = self._mouse_y()
        self._mouse_label.draw()
        if cfg.MOUSE_CONTROL:
            self._mouse_status.text = "[ ВКЛ ]"
            self._mouse_status.color = (144, 238, 144)
        else:
            self._mouse_status.text = "[ ВЫКЛ ]"
            self._mouse_status.color = arcade.color.LIGHT_GRAY
        self._mouse_status.draw()

        # Close button
        close_y = self.CY - self.PH // 2 + 28
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, close_y, 180, 36), (70, 30, 30, 220)
        )
        self._close_text.draw()

    def on_key_press(self, key, _mod):
        if self.waiting_for:
            if key != arcade.key.ESCAPE:
                cfg.KEY_BINDINGS[self.waiting_for] = key
            self.waiting_for = None
            return
        if key == arcade.key.ESCAPE:
            self._close_cb()

    def on_mouse_press(self, x, y, button, _mod):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.waiting_for:
            self.waiting_for = None
            return

        half_w = self.PW // 2

        # Binding rows
        for i, (action, _) in enumerate(self.ACTIONS):
            if abs(x - self.CX) < half_w and abs(y - self._row_y(i)) < 22:
                self.waiting_for = action
                return

        # Mouse toggle
        if abs(x - self.CX) < half_w and abs(y - self._mouse_y()) < 22:
            cfg.MOUSE_CONTROL = not cfg.MOUSE_CONTROL
            return

        # Close button
        close_y = self.CY - self.PH // 2 + 28
        if abs(x - self.CX) < 90 and abs(y - close_y) < 18:
            self._close_cb()
