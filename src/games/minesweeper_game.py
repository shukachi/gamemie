"""
Minesweeper game integrated as a BaseGame view.
3 difficulty levels, local leaderboard (best time), proper lobby integration.
"""

import arcade
import random
import time
import json
import os
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# ----------------------------------------------------------------------
# Game constants (dynamic per difficulty)
# ----------------------------------------------------------------------
CELL_SIZE = 40          # базовый размер клетки, может быть уменьшен для больших полей

# Цвета
COLOR_HIDDEN = (180, 180, 180)
COLOR_OPENED = (220, 220, 220)
COLOR_MINE = (255, 0, 0)
COLOR_FLAG = (255, 215, 0)
COLOR_GRID = (100, 100, 100)
COLOR_BG = (0, 0, 0)

NUMBER_COLORS = {
    1: (0, 0, 255), 2: (0, 128, 0), 3: (255, 0, 0), 4: (0, 0, 128),
    5: (128, 0, 0), 6: (0, 128, 128), 7: (128, 0, 128), 8: (64, 64, 64)
}

# Сложность: (rows, cols, mines)
DIFFICULTY_CONFIG = {
    'easy':   (9, 9, 10),
    'medium': (12, 12, 20),
    'hard':   (15, 15, 30)
}

LEADERBOARD_FILE = "data/leaderboards/minesweeper_leaderboard.json"
MAX_ENTRIES = 10

def load_local_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE) as f:
                data = json.load(f)
                if all(k in data for k in ('easy','medium','hard')):
                    return data
        except:
            pass
    return {"easy": [], "medium": [], "hard": []}

def save_local_leaderboard(data):
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)


class MinesweeperGame(BaseGame):
    def __init__(self, machine_id, on_finish_callback):
        super().__init__("Minesweeper", machine_id, on_finish_callback)
        self.difficulty = None
        self.state = "menu"          # "menu", "leaderboard", "playing", "enter_name", "postgame"
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()
        self.postgame_buttons = []

    def _build_menu_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        return [
            {"label": "Easy (9×9, 10 мин)", "difficulty": "easy", "x": cx, "y": cy + 80, "w": 280, "h": 50},
            {"label": "Medium (12×12, 20 мин)", "difficulty": "medium", "x": cx, "y": cy, "w": 280, "h": 50},
            {"label": "Hard (15×15, 30 мин)", "difficulty": "hard", "x": cx, "y": cy - 80, "w": 280, "h": 50},
            {"label": "Leaderboards", "action": "leaderboard", "x": cx, "y": cy - 160, "w": 200, "h": 50},
        ]

    def on_show(self):
        self.state = "menu"
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()

    def _start_game(self):
        diff = self.difficulty or 'easy'
        self.rows, self.cols, self.mines_count = DIFFICULTY_CONFIG[diff]
        # Вычисляем CELL_SIZE так, чтобы поле поместилось в окно с отступами
        max_cell_w = (SCREEN_WIDTH - 100) // self.cols
        max_cell_h = (SCREEN_HEIGHT - 100) // self.rows
        self.cell_size = min(40, max_cell_w, max_cell_h)
        # Центрирование поля
        field_width = self.cols * self.cell_size
        field_height = self.rows * self.cell_size
        self.field_left = (SCREEN_WIDTH - field_width) // 2
        self.field_bottom = (SCREEN_HEIGHT - field_height) // 2

        self.mines = [[False] * self.cols for _ in range(self.rows)]
        self.cell_state = [['hidden'] * self.cols for _ in range(self.rows)]
        self.counts = [[0] * self.cols for _ in range(self.rows)]
        self.game_over = False
        self.win = False
        self.start_time = time.time()   # секундомер
        self.elapsed_time = 0.0

        # Расстановка мин
        placed = 0
        while placed < self.mines_count:
            r = random.randrange(self.rows)
            c = random.randrange(self.cols)
            if not self.mines[r][c]:
                self.mines[r][c] = True
                placed += 1

        # Вычисление чисел
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mines[r][c]:
                    continue
                cnt = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.mines[nr][nc]:
                            cnt += 1
                self.counts[r][c] = cnt

        self.state = "playing"

    # ---------- Игровая логика ----------
    def _reveal(self, r, c):
        if self.cell_state[r][c] != 'hidden':
            return True
        if self.mines[r][c]:
            # Проигрыш – показать все мины
            for rr in range(self.rows):
                for cc in range(self.cols):
                    if self.mines[rr][cc]:
                        self.cell_state[rr][cc] = 'opened'
            self.game_over = True
            return False
        self.cell_state[r][c] = 'opened'
        # Если пустая – заливка
        if self.counts[r][c] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if self.cell_state[nr][nc] == 'hidden':
                            self._reveal(nr, nc)
        self._check_win()
        return True

    def _check_win(self):
        """Победа, когда все безопасные клетки открыты (оставшиеся закрытые — только мины)."""
        closed = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cell_state[r][c] != 'opened':
                    closed += 1
        if closed == self.mines_count:
            self.win = True
            self.game_over = True
            self.elapsed_time = time.time() - self.start_time

    # ---------- Arcade View callbacks ----------
    def on_draw(self):
        self.clear()
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "leaderboard":
            self._draw_leaderboard()
        elif self.state == "enter_name":
            self._draw_name_input()
        elif self.state in ("playing", "postgame"):
            self._draw_game()
            if self.state == "postgame":
                self._draw_postgame_buttons()

    def on_update(self, delta_time):
        if self.state != "playing":
            return
        if self.game_over:
            if self.state == "playing":
                if self.win:
                    # Проверим рекорд
                    if self._is_high_score():
                        self.state = "enter_name"
                        self.entered_name = ""
                    else:
                        self.state = "postgame"
                        self._build_postgame_buttons()
                else:
                    self.state = "postgame"
                    self._build_postgame_buttons()
            return

    def on_key_press(self, key, modifiers):
        # Глобальный выход
        if key == arcade.key.ESCAPE:
            if self.state in ("menu", "leaderboard", "postgame"):
                self.finish_game(False)
            elif self.state == "playing":
                self.finish_game(False)
            elif self.state == "enter_name":
                self.state = "menu"
            return

        if self.state == "playing":
            pass  # клавиатура не используется в игре
        elif self.state == "enter_name":
            self._handle_name_input(key, modifiers)
        elif self.state == "leaderboard":
            if key == arcade.key.BACKSPACE:
                self.state = "menu"

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "menu":
            for btn in self.menu_buttons:
                if btn["x"] - btn["w"]//2 <= x <= btn["x"] + btn["w"]//2 and \
                   btn["y"] - btn["h"]//2 <= y <= btn["y"] + btn["h"]//2:
                    if "difficulty" in btn:
                        self.difficulty = btn["difficulty"]
                        self._start_game()
                    elif btn.get("action") == "leaderboard":
                        self.state = "leaderboard"
                    break
        elif self.state == "playing" and not self.game_over:
            # Определяем клетку
            col = int((x - self.field_left) // self.cell_size)
            row = int((y - self.field_bottom) // self.cell_size)
            if 0 <= col < self.cols and 0 <= row < self.rows:
                if button == arcade.MOUSE_BUTTON_LEFT:
                    self._reveal(row, col)
                elif button == arcade.MOUSE_BUTTON_RIGHT:
                    if self.cell_state[row][col] == 'hidden':
                        self.cell_state[row][col] = 'flagged'
                    elif self.cell_state[row][col] == 'flagged':
                        self.cell_state[row][col] = 'hidden'
        elif self.state == "postgame":
            for btn in self.postgame_buttons:
                if btn["x"] - btn["w"]//2 <= x <= btn["x"] + btn["w"]//2 and \
                   btn["y"] - btn["h"]//2 <= y <= btn["y"] + btn["h"]//2:
                    if btn["action"] == "replay":
                        self._start_game()
                    elif btn["action"] == "quit":
                        self.finish_game(False)
                    break

    def _handle_name_input(self, key, modifiers):
        if key == arcade.key.ENTER:
            name = self.entered_name.strip() or "Player"
            self._add_leaderboard_entry(name)
            self.state = "postgame"
            self._build_postgame_buttons()
        elif key == arcade.key.BACKSPACE:
            self.entered_name = self.entered_name[:-1]
        elif key == arcade.key.SPACE:
            self.entered_name += " "
        elif arcade.key.A <= key <= arcade.key.Z:
            ch = chr(key).upper() if modifiers & arcade.key.MOD_SHIFT else chr(key).lower()
            self.entered_name += ch
        elif arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            self.entered_name += chr(key)

    # ---------- Leaderboard helpers ----------
    def _is_high_score(self):
        entries = self.leaderboard_data.get(self.difficulty, [])
        if len(entries) < MAX_ENTRIES:
            return True
        # Сравниваем время (меньше — лучше)
        worst = max(entries, key=lambda e: e["time"])["time"]
        return self.elapsed_time < worst

    def _add_leaderboard_entry(self, name):
        entries = self.leaderboard_data.get(self.difficulty, [])
        entries.append({"name": name, "time": round(self.elapsed_time, 2)})
        entries.sort(key=lambda e: e["time"])
        self.leaderboard_data[self.difficulty] = entries[:MAX_ENTRIES]
        save_local_leaderboard(self.leaderboard_data)

    # ---------- Отрисовка ----------
    def _draw_menu(self):
        arcade.draw_text("MINESWEEPER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180,
                         arcade.color.YELLOW, 48, anchor_x="center")
        arcade.draw_text("Выберите сложность", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130,
                         arcade.color.WHITE, 20, anchor_x="center")
        for btn in self.menu_buttons:
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_BLUE)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 16,
                             anchor_x="center", anchor_y="center")

    def _draw_leaderboard(self):
        arcade.draw_text("Local Leaderboard (лучшее время)", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
                         arcade.color.YELLOW, 26, anchor_x="center")
        arcade.draw_text("Press BACKSPACE to return", SCREEN_WIDTH // 2, 30,
                         arcade.color.WHITE, 14, anchor_x="center")
        col_w = SCREEN_WIDTH // 3
        levels = ["easy", "medium", "hard"]
        titles = ["Easy", "Medium", "Hard"]
        for i, level in enumerate(levels):
            xc = col_w * i + col_w // 2
            arcade.draw_text(titles[i], xc, SCREEN_HEIGHT - 80, arcade.color.ORANGE, 22, anchor_x="center")
            entries = self.leaderboard_data[level]
            if not entries:
                arcade.draw_text("Empty", xc, SCREEN_HEIGHT - 120, arcade.color.GRAY, 16, anchor_x="center")
            else:
                for j, e in enumerate(entries[:MAX_ENTRIES]):
                    arcade.draw_text(f"{j+1}. {e['name']}: {e['time']:.1f}s",
                                     xc, SCREEN_HEIGHT - 120 - j*20,
                                     arcade.color.WHITE, 14, anchor_x="center")

    def _draw_name_input(self):
        arcade.draw_text("New Record!", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100,
                         arcade.color.GREEN, 22, anchor_x="center")
        arcade.draw_text(f"Time: {self.elapsed_time:.2f}s", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+60,
                         arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Enter name and press ENTER:", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+20,
                         arcade.color.WHITE, 18, anchor_x="center")
        l, r = SCREEN_WIDTH//2-150, SCREEN_WIDTH//2+150
        b, t = SCREEN_HEIGHT//2-20, SCREEN_HEIGHT//2+20
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GRAY)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE)
        arcade.draw_text(self.entered_name, SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                         arcade.color.WHITE, 18, anchor_x="center")

    def _draw_game(self):
        # Отрисовка клеток
        for r in range(self.rows):
            for c in range(self.cols):
                left = self.field_left + c * self.cell_size
                right = left + self.cell_size
                bottom = self.field_bottom + r * self.cell_size
                top = bottom + self.cell_size

                st = self.cell_state[r][c]
                if st == 'hidden':
                    color = COLOR_HIDDEN
                elif st == 'flagged':
                    color = COLOR_FLAG
                else:
                    color = COLOR_OPENED

                arcade.draw_lrbt_rectangle_filled(left + 1, right - 1, bottom + 1, top - 1, color)
                arcade.draw_line(left, bottom, right, bottom, COLOR_GRID, 1)
                arcade.draw_line(left, top, right, top, COLOR_GRID, 1)
                arcade.draw_line(left, bottom, left, top, COLOR_GRID, 1)
                arcade.draw_line(right, bottom, right, top, COLOR_GRID, 1)

                if st == 'opened':
                    if self.mines[r][c]:
                        cx = left + self.cell_size / 2
                        cy = bottom + self.cell_size / 2
                        arcade.draw_circle_filled(cx, cy, self.cell_size // 4, COLOR_MINE)
                    elif self.counts[r][c] > 0:
                        num = self.counts[r][c]
                        color_num = NUMBER_COLORS.get(num, arcade.color.BLACK)
                        arcade.draw_text(str(num),
                                         left + self.cell_size / 2,
                                         bottom + self.cell_size / 2 - self.cell_size//5,
                                         color_num, self.cell_size//2,
                                         anchor_x="center", anchor_y="center")
                elif st == 'flagged':
                    cx = left + self.cell_size / 2
                    cy = bottom + self.cell_size / 2
                    arcade.draw_line(cx - self.cell_size//6, cy - self.cell_size//6,
                                     cx + self.cell_size//6, cy + self.cell_size//6, arcade.color.RED, 2)
                    arcade.draw_line(cx - self.cell_size//6, cy + self.cell_size//6,
                                     cx + self.cell_size//6, cy - self.cell_size//6, arcade.color.RED, 2)

        # Таймер во время игры
        if not self.game_over:
            elapsed = time.time() - self.start_time
            arcade.draw_text(f"Time: {elapsed:.1f}s", 10, SCREEN_HEIGHT - 30,
                             arcade.color.WHITE, 16)
        else:
            if self.win:
                arcade.draw_text(f"WIN! Time: {self.elapsed_time:.2f}s",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                 arcade.color.GREEN, 28, anchor_x="center")
            else:
                arcade.draw_text("GAME OVER",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                 arcade.color.RED, 28, anchor_x="center")

    def _build_postgame_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.postgame_buttons = [
            {"label": "Play Again", "x": cx - 100, "y": cy - 80, "w": 160, "h": 40, "action": "replay"},
            {"label": "Quit to Lobby", "x": cx + 100, "y": cy - 80, "w": 160, "h": 40, "action": "quit"},
        ]

    def _draw_postgame_buttons(self):
        for btn in self.postgame_buttons:
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GREEN)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 14,
                             anchor_x="center", anchor_y="center")