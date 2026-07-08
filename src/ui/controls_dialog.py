"""Cashier menu, controls / key-binding settings, graphics settings, exit confirm."""
import arcade
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

RESOLUTIONS = [(1280, 720), (1920, 1080), (2560, 1440)]


def _key_label(code: int) -> str:
    for name in dir(arcade.key):
        val = getattr(arcade.key, name)
        if val == code and name.isupper() and not name.startswith('_'):
            return name
    if 32 <= code < 127:
        return chr(code).upper()
    return f"#{code}"


# ─────────────────────────── Cashier Menu ───────────────────────────

class CashierMenuView(arcade.View):

    W = int(SCREEN_WIDTH * 0.30)
    H = int(SCREEN_HEIGHT * 0.68)
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    BTN_H = 44
    BTN_GAP = 12

    def __init__(self, player_state, leaderboard, lobby_view):
        super().__init__()
        self.player_state = player_state
        self.leaderboard = leaderboard
        self.lobby_view = lobby_view
        self._build_buttons()

    def _build_buttons(self):
        labels = ["УПРАВЛЕНИЕ", "ГРАФИКА", "ЗВУК"]
        if self.player_state.all_machines_locked():
            labels.append("СБРОСИТЬ ПОПЫТКИ")
        else:
            labels.append("ТАБЛИЦА ЛИДЕРОВ")
        labels += ["ВЫЙТИ ИЗ ИГРЫ", "ЗАКРЫТЬ"]
        self._buttons = labels

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

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 160)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.W, self.H), (25, 25, 45, 240)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.W, self.H), (180, 140, 60), 2
        )
        self._title_text.draw()
        for i, text_obj in enumerate(self._btn_texts):
            by = self._btn_y(i)
            lbl = self._buttons[i]
            btn_color = (100, 25, 25, 220) if lbl == "ВЫЙТИ ИЗ ИГРЫ" else (60, 50, 30, 200)
            arcade.draw_rect_filled(
                arcade.XYWH(self.CX, by, self.W - 40, self.BTN_H), btn_color
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
                elif lbl == "ГРАФИКА":
                    self.window.show_view(
                        GraphicsView(on_close=lambda: self.window.show_view(self))
                    )
                elif lbl == "ЗВУК":
                    self.window.show_view(
                        SoundView(on_close=lambda: self.window.show_view(self),
                                  lobby_view=self.lobby_view)
                    )
                elif lbl == "ТАБЛИЦА ЛИДЕРОВ":
                    from src.ui.dialogs import LeaderboardView
                    entries = self.leaderboard.get_global_leaderboard()
                    self.window.show_view(
                        LeaderboardView("Club Leaderboard", entries,
                                        lambda: self.window.show_view(self))
                    )
                elif lbl == "СБРОСИТЬ ПОПЫТКИ":
                    self.player_state.reset_all_attempts()
                    self._build_buttons()
                elif lbl == "ВЫЙТИ ИЗ ИГРЫ":
                    self.window.show_view(ExitConfirmView(back_view=self))
                elif lbl == "ЗАКРЫТЬ":
                    self.window.show_view(self.lobby_view)
                return


# ─────────────────────────── Controls View ───────────────────────────

class ControlsView(arcade.View):

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
        self.waiting_for: str | None = None
        self._build_texts()

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
        return self.CY + self.PH // 2 - 90 - idx * self.ROW_H

    def _mouse_y(self) -> float:
        return self._row_y(len(self.ACTIONS)) - 8

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 170)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), (22, 22, 40, 240)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), arcade.color.LIGHT_CYAN, 2
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
        my = self._mouse_y()
        self._mouse_label.draw()
        self._mouse_status.text = "[ ВКЛ ]" if cfg.MOUSE_CONTROL else "[ ВЫКЛ ]"
        self._mouse_status.color = (144, 238, 144) if cfg.MOUSE_CONTROL else arcade.color.LIGHT_GRAY
        self._mouse_status.draw()
        close_y = self.CY - self.PH // 2 + 28
        arcade.draw_rect_filled(arcade.XYWH(self.CX, close_y, 180, 36), (70, 30, 30, 220))
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
        for i, (action, _) in enumerate(self.ACTIONS):
            if abs(x - self.CX) < half_w and abs(y - self._row_y(i)) < 22:
                self.waiting_for = action
                return
        if abs(x - self.CX) < half_w and abs(y - self._mouse_y()) < 22:
            cfg.MOUSE_CONTROL = not cfg.MOUSE_CONTROL
            return
        close_y = self.CY - self.PH // 2 + 28
        if abs(x - self.CX) < 90 and abs(y - close_y) < 18:
            self._close_cb()


# ─────────────────────────── Graphics View ───────────────────────────

class GraphicsView(arcade.View):

    PW = int(SCREEN_WIDTH * 0.42)
    PH = int(SCREEN_HEIGHT * 0.70)
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    ROW_H = 50

    def __init__(self, on_close):
        super().__init__()
        self._close_cb = on_close
        self._build_texts()

    def _res_y(self, idx: int) -> float:
        start_y = self.CY + self.PH // 2 - 90
        return start_y - idx * self.ROW_H

    def _fullscreen_y(self) -> float:
        return self._res_y(len(RESOLUTIONS)) - 10

    def _potato_y(self) -> float:
        return self._fullscreen_y() - self.ROW_H - 4

    def _close_y(self) -> float:
        return self.CY - self.PH // 2 + 28

    def _build_texts(self):
        self._title = arcade.Text(
            "НАСТРОЙКИ ГРАФИКИ",
            x=self.CX, y=self.CY + self.PH // 2 - 34,
            color=arcade.color.LIGHT_CYAN, font_size=17, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._res_header = arcade.Text(
            "РАЗРЕШЕНИЕ  (требуется перезапуск ↻)",
            x=self.CX - self.PW // 2 + 20, y=self.CY + self.PH // 2 - 60,
            color=arcade.color.LIGHT_GRAY, font_size=11,
            anchor_x="left", anchor_y="center",
        )
        self._res_texts = [
            arcade.Text(
                f"{w} × {h}", x=self.CX, y=self._res_y(i),
                color=arcade.color.WHITE, font_size=13, bold=True,
                anchor_x="center", anchor_y="center",
            )
            for i, (w, h) in enumerate(RESOLUTIONS)
        ]
        self._fs_label = arcade.Text(
            "Полноэкранный режим",
            x=self.CX - self.PW // 2 + 24, y=self._fullscreen_y(),
            color=arcade.color.LIGHT_GRAY, font_size=13,
            anchor_x="left", anchor_y="center",
        )
        self._fs_status = arcade.Text(
            "", x=self.CX + self.PW // 2 - 24, y=self._fullscreen_y(),
            color=arcade.color.WHITE, font_size=13,
            anchor_x="right", anchor_y="center",
        )
        self._potato_label = arcade.Text(
            "Картошка \U0001f954",
            x=self.CX - self.PW // 2 + 24, y=self._potato_y(),
            color=arcade.color.LIGHT_GRAY, font_size=13,
            anchor_x="left", anchor_y="center",
        )
        self._potato_status = arcade.Text(
            "", x=self.CX + self.PW // 2 - 24, y=self._potato_y(),
            color=arcade.color.WHITE, font_size=13,
            anchor_x="right", anchor_y="center",
        )
        self._close_text = arcade.Text(
            "ЗАКРЫТЬ  (ESC)",
            x=self.CX, y=self._close_y(),
            color=arcade.color.WHITE, font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 170)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), (22, 22, 40, 240)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), arcade.color.LIGHT_CYAN, 2
        )
        self._title.draw()
        self._res_header.draw()

        current_res = cfg.RESOLUTION
        for i, (w, h) in enumerate(RESOLUTIONS):
            y = self._res_y(i)
            selected = (w, h) == current_res and not cfg.FULLSCREEN
            row_color = (50, 80, 50, 220) if selected else (40, 40, 60, 180)
            arcade.draw_rect_filled(
                arcade.XYWH(self.CX, y, self.PW - 40, 36), row_color
            )
            t = self._res_texts[i]
            t.color = (144, 238, 144) if selected else arcade.color.WHITE
            t.draw()

        # Fullscreen toggle row
        self._fs_label.draw()
        self._fs_status.text = "[ ВКЛ ]" if cfg.FULLSCREEN else "[ ВЫКЛ ]"
        self._fs_status.color = (144, 238, 144) if cfg.FULLSCREEN else arcade.color.LIGHT_GRAY
        self._fs_status.draw()

        # Potato mode row
        self._potato_label.y = self._potato_y()
        self._potato_status.y = self._potato_y()
        self._potato_label.draw()
        self._potato_status.text = "[ ВКЛ ]" if cfg.POTATO_MODE else "[ ВЫКЛ ]"
        self._potato_status.color = (255, 180, 80) if cfg.POTATO_MODE else arcade.color.LIGHT_GRAY
        self._potato_status.draw()

        # Close button
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self._close_y(), 180, 36), (70, 30, 30, 220)
        )
        self._close_text.draw()

    def on_key_press(self, key, _mod):
        if key == arcade.key.ESCAPE:
            self._close_cb()

    def on_mouse_press(self, x, y, button, _mod):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        half_w = self.PW // 2

        # Resolution rows — save preference, apply on next launch
        for i, (w, h) in enumerate(RESOLUTIONS):
            if abs(x - self.CX) < half_w and abs(y - self._res_y(i)) < 20:
                cfg.RESOLUTION = (w, h)
                cfg.save_settings()
                return

        # Fullscreen toggle — applies immediately
        if abs(x - self.CX) < half_w and abs(y - self._fullscreen_y()) < 22:
            cfg.FULLSCREEN = not cfg.FULLSCREEN
            self.window.set_fullscreen(cfg.FULLSCREEN)
            cfg.save_settings()
            return

        # Potato mode toggle
        if abs(x - self.CX) < half_w and abs(y - self._potato_y()) < 22:
            cfg.POTATO_MODE = not cfg.POTATO_MODE
            cfg.save_settings()
            return

        # Close button
        if abs(x - self.CX) < 90 and abs(y - self._close_y()) < 18:
            self._close_cb()


# ─────────────────────────── Sound View ───────────────────────────

class SoundView(arcade.View):

    PW = int(SCREEN_WIDTH * 0.50)
    PH = int(SCREEN_HEIGHT * 0.44)
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    ROW_H = 64
    BAR_W = 160
    BAR_H = 16
    BAR_LEFT_OFF = 10   # bar left edge = CX + BAR_LEFT_OFF

    TRACKS = [
        ('LOBBY_MUSIC_VOLUME',    'Музыка лобби'),
        ('SETTINGS_MUSIC_VOLUME', 'Музыка настроек'),
    ]

    def __init__(self, on_close, lobby_view):
        super().__init__()
        self._close_cb = on_close
        self._lobby = lobby_view
        self._build_texts()

    def _row_y(self, idx: int) -> float:
        return self.CY + self.PH // 2 - 90 - idx * self.ROW_H

    def _close_y(self) -> float:
        return self.CY - self.PH // 2 + 32

    def _bl(self) -> float:
        return self.CX + self.BAR_LEFT_OFF

    def _build_texts(self):
        self._title = arcade.Text(
            "НАСТРОЙКИ ЗВУКА",
            x=self.CX, y=self.CY + self.PH // 2 - 34,
            color=arcade.color.LIGHT_CYAN, font_size=17, bold=True,
            anchor_x="center", anchor_y="center",
        )
        bl = self._bl()
        self._row_labels = []
        self._pct_texts = []
        self._arrow_l = []
        self._arrow_r = []
        for i in range(len(self.TRACKS)):
            y = self._row_y(i)
            _, name = self.TRACKS[i]
            self._row_labels.append(arcade.Text(
                name, x=self.CX - self.PW // 2 + 24, y=y,
                color=arcade.color.LIGHT_GRAY, font_size=13,
                anchor_x="left", anchor_y="center",
            ))
            self._pct_texts.append(arcade.Text(
                "  0%", x=bl + self.BAR_W + 58, y=y,
                color=arcade.color.WHITE, font_size=13,
                anchor_x="right", anchor_y="center",
            ))
            self._arrow_l.append(arcade.Text(
                "◀", x=bl - 20, y=y,
                color=arcade.color.WHITE, font_size=14,
                anchor_x="center", anchor_y="center",
            ))
            self._arrow_r.append(arcade.Text(
                "▶", x=bl + self.BAR_W + 20, y=y,
                color=arcade.color.WHITE, font_size=14,
                anchor_x="center", anchor_y="center",
            ))
        self._close_text = arcade.Text(
            "ЗАКРЫТЬ  (ESC)",
            x=self.CX, y=self._close_y(),
            color=arcade.color.WHITE, font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )

    def _get_vol(self, idx: int) -> float:
        return getattr(cfg, self.TRACKS[idx][0])

    def _set_vol(self, idx: int, vol: float) -> None:
        vol = max(0.0, min(1.0, round(vol, 2)))
        setattr(cfg, self.TRACKS[idx][0], vol)
        if idx == 0 and self._lobby.music_player:
            self._lobby.music_player.volume = vol
        elif idx == 1 and self._lobby.settings_music_player:
            self._lobby.settings_music_player.volume = vol
        cfg.save_settings()

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 170)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), (22, 22, 40, 240)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), arcade.color.LIGHT_CYAN, 2
        )
        self._title.draw()
        bl = self._bl()
        for i in range(len(self.TRACKS)):
            y = self._row_y(i)
            vol = self._get_vol(i)
            filled = vol * self.BAR_W
            bar_cx = bl + self.BAR_W / 2
            # bar background
            arcade.draw_rect_filled(
                arcade.XYWH(bar_cx, y, self.BAR_W, self.BAR_H), (40, 40, 60, 200)
            )
            # filled portion
            if filled > 0:
                arcade.draw_rect_filled(
                    arcade.XYWH(bl + filled / 2, y, filled, self.BAR_H), (80, 160, 255, 220)
                )
            arcade.draw_rect_outline(
                arcade.XYWH(bar_cx, y, self.BAR_W, self.BAR_H), arcade.color.LIGHT_GRAY, 1
            )
            self._row_labels[i].draw()
            self._arrow_l[i].draw()
            self._arrow_r[i].draw()
            self._pct_texts[i].text = f"{int(vol * 100):3d}%"
            self._pct_texts[i].draw()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self._close_y(), 180, 36), (70, 30, 30, 220)
        )
        self._close_text.draw()

    def on_key_press(self, key, _mod):
        if key == arcade.key.ESCAPE:
            self._close_cb()

    def on_mouse_press(self, x, y, button, _mod):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        bl = self._bl()
        for i in range(len(self.TRACKS)):
            ry = self._row_y(i)
            if abs(y - ry) > 22:
                continue
            if abs(x - (bl - 20)) < 16:
                self._set_vol(i, self._get_vol(i) - 0.05)
                return
            if abs(x - (bl + self.BAR_W + 20)) < 16:
                self._set_vol(i, self._get_vol(i) + 0.05)
                return
            if bl <= x <= bl + self.BAR_W:
                self._set_vol(i, (x - bl) / self.BAR_W)
                return
        if abs(x - self.CX) < 90 and abs(y - self._close_y()) < 18:
            self._close_cb()


# ─────────────────────────── Exit Confirm ───────────────────────────

class ExitConfirmView(arcade.View):

    PW = int(SCREEN_WIDTH * 0.38)
    PH = int(SCREEN_HEIGHT * 0.26)
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2

    def __init__(self, back_view):
        super().__init__()
        self._back_view = back_view
        self._question = arcade.Text(
            "Вы точно хотите выйти из игры?",
            x=self.CX, y=self.CY + 30,
            color=arcade.color.WHITE, font_size=14, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._yes_text = arcade.Text(
            "ДА", x=self.CX - 60, y=self.CY - 28,
            color=arcade.color.WHITE, font_size=14, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._no_text = arcade.Text(
            "НЕТ", x=self.CX + 60, y=self.CY - 28,
            color=arcade.color.WHITE, font_size=14, bold=True,
            anchor_x="center", anchor_y="center",
        )

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 180)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), (30, 20, 20, 245)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.CX, self.CY, self.PW, self.PH), (200, 80, 80), 2
        )
        self._question.draw()
        arcade.draw_rect_filled(arcade.XYWH(self.CX - 60, self.CY - 28, 90, 38), (120, 30, 30, 220))
        arcade.draw_rect_filled(arcade.XYWH(self.CX + 60, self.CY - 28, 90, 38), (40, 60, 40, 220))
        self._yes_text.draw()
        self._no_text.draw()

    def on_key_press(self, key, _mod):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self._back_view)

    def on_mouse_press(self, x, y, button, _mod):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if abs(x - (self.CX - 60)) < 45 and abs(y - (self.CY - 28)) < 19:
            arcade.exit()
        elif abs(x - (self.CX + 60)) < 45 and abs(y - (self.CY - 28)) < 19:
            self.window.show_view(self._back_view)
