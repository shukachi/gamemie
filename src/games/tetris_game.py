"""
Tetris game integrated as a BaseGame view.
3 difficulty levels, local leaderboard, proper lobby integration.
"""

import arcade
import random
import json
import os
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
CELL_SIZE = 30
COLS = 10
ROWS = 20

# Поле будет размещено по центру экрана
FIELD_X = (SCREEN_WIDTH - COLS * CELL_SIZE) // 2
FIELD_Y = (SCREEN_HEIGHT - ROWS * CELL_SIZE) // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

SHAPES = {
    'I': [[(0,0), (1,0), (2,0), (3,0)],
          [(0,1), (0,0), (0,-1), (0,-2)]],
    'O': [[(0,0), (1,0), (0,1), (1,1)]],
    'T': [[(0,0), (-1,0), (1,0), (0,1)],
          [(0,0), (0,1), (0,-1), (1,0)],
          [(0,0), (-1,0), (1,0), (0,-1)],
          [(0,0), (0,1), (0,-1), (-1,0)]],
    'S': [[(0,0), (1,0), (0,1), (-1,1)],
          [(0,0), (0,1), (1,0), (1,-1)]],
    'Z': [[(0,0), (-1,0), (0,1), (1,1)],
          [(0,0), (0,1), (-1,0), (-1,-1)]],
    'J': [[(0,0), (-1,0), (1,0), (1,1)],
          [(0,0), (0,1), (0,-1), (1,-1)],
          [(0,0), (-1,0), (1,0), (-1,-1)],
          [(0,0), (0,1), (0,-1), (-1,1)]],
    'L': [[(0,0), (-1,0), (1,0), (-1,1)],
          [(0,0), (0,1), (0,-1), (-1,-1)],
          [(0,0), (-1,0), (1,0), (1,-1)],
          [(0,0), (0,1), (0,-1), (1,1)]]
}

# Уровни сложности: интервал падения (секунд)
DIFFICULTY_SPEEDS = {
    'easy': 0.6,
    'medium': 0.4,
    'hard': 0.2
}

LEADERBOARD_FILE = "data/leaderboards/tetris_leaderboard.json"
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


class TetrisGame(BaseGame):
    def __init__(self, machine_id, on_finish_callback):
        super().__init__("Tetris", machine_id, on_finish_callback)
        self.difficulty = None
        self.state = "menu"          # "menu", "leaderboard", "playing", "enter_name", "postgame"
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()
        self.postgame_buttons = []

    def _build_menu_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        return [
            {"label": "Easy", "difficulty": "easy", "x": cx, "y": cy + 80, "w": 200, "h": 50},
            {"label": "Medium", "difficulty": "medium", "x": cx, "y": cy, "w": 200, "h": 50},
            {"label": "Hard", "difficulty": "hard", "x": cx, "y": cy - 80, "w": 200, "h": 50},
            {"label": "Leaderboards", "action": "leaderboard", "x": cx, "y": cy - 160, "w": 200, "h": 50},
        ]

    def on_show(self):
        self.state = "menu"
        self.score = 0
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()

    def _start_game(self):
        diff = self.difficulty or 'easy'
        self.drop_interval = DIFFICULTY_SPEEDS[diff]
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.paused = False
        self.time_since_drop = 0.0
        self.next_piece_type = random.choice(list(SHAPES.keys()))
        self._spawn_piece()
        self.state = "playing"

    def _spawn_piece(self):
        self.current_type = self.next_piece_type
        self.next_piece_type = random.choice(list(SHAPES.keys()))
        self.current_x = COLS // 2 - 1
        self.current_y = ROWS - 1
        self.current_rotation = 0
        if not self._valid_position():
            self.game_over = True

    def _valid_position(self, x=None, y=None, rotation=None):
        if x is None: x = self.current_x
        if y is None: y = self.current_y
        if rotation is None: rotation = self.current_rotation
        shape = SHAPES[self.current_type][rotation % len(SHAPES[self.current_type])]
        for dx, dy in shape:
            col = x + dx
            row = y + dy
            if col < 0 or col >= COLS or row < 0:
                return False
            if row >= ROWS:
                continue
            if self.grid[row][col] is not None:
                return False
        return True

    def _lock_piece(self):
        shape = SHAPES[self.current_type][self.current_rotation % len(SHAPES[self.current_type])]
        for dx, dy in shape:
            col = self.current_x + dx
            row = self.current_y + dy
            if 0 <= row < ROWS and 0 <= col < COLS:
                self.grid[row][col] = self.current_type
        self._clear_lines()
        self._spawn_piece()

    def _clear_lines(self):
        lines_cleared = 0
        row = 0
        while row < ROWS:
            if all(cell is not None for cell in self.grid[row]):
                del self.grid[row]
                self.grid.append([None for _ in range(COLS)])
                lines_cleared += 1
            else:
                row += 1
        if lines_cleared > 0:
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(lines_cleared, lines_cleared * 200)

    def _move(self, dx, dy):
        if self.game_over or self.paused:
            return False
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        if self._valid_position(x=new_x, y=new_y):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False

    def _rotate(self):
        if self.game_over or self.paused:
            return
        new_rotation = (self.current_rotation + 1) % len(SHAPES[self.current_type])
        if self._valid_position(rotation=new_rotation):
            self.current_rotation = new_rotation

    def _drop_to_bottom(self):
        if self.game_over or self.paused:
            return
        while self._valid_position(y=self.current_y - 1):
            self.current_y -= 1
        self._lock_piece()

    def _is_high_score(self):
        entries = self.leaderboard_data.get(self.difficulty, [])
        if len(entries) < MAX_ENTRIES:
            return True
        lowest = min(entries, key=lambda e: e["score"])["score"]
        return self.score > lowest

    def _add_leaderboard_entry(self, name):
        entries = self.leaderboard_data.get(self.difficulty, [])
        entries.append({"name": name, "score": self.score})
        entries.sort(key=lambda e: e["score"], reverse=True)
        self.leaderboard_data[self.difficulty] = entries[:MAX_ENTRIES]
        save_local_leaderboard(self.leaderboard_data)

    # ------------------------------------------------------------
    # Arcade View callbacks
    # ------------------------------------------------------------
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
                if self._is_high_score():
                    self.state = "enter_name"
                    self.entered_name = ""
                else:
                    self.state = "postgame"
                    self._build_postgame_buttons()
            return
        if self.paused:
            return

        self.time_since_drop += delta_time
        if self.time_since_drop >= self.drop_interval:
            self.time_since_drop = 0.0
            if not self._move(0, -1):
                self._lock_piece()

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
            if self.game_over:
                return
            if key == arcade.key.P:
                self.paused = not self.paused
            elif self.paused:
                return
            elif key == arcade.key.LEFT:
                self._move(-1, 0)
            elif key == arcade.key.RIGHT:
                self._move(1, 0)
            elif key == arcade.key.DOWN:
                self._move(0, -1)
            elif key == arcade.key.UP:
                self._rotate()
            elif key == arcade.key.SPACE:
                self._drop_to_bottom()
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

    # ------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------
    def _draw_menu(self):
        arcade.draw_text("TETRIS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180,
                         arcade.color.YELLOW, 48, anchor_x="center")
        arcade.draw_text("Выберите сложность", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130,
                         arcade.color.WHITE, 20, anchor_x="center")
        for btn in self.menu_buttons:
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_BLUE)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 20,
                             anchor_x="center", anchor_y="center")

    def _draw_leaderboard(self):
        arcade.draw_text("Local Leaderboard", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
                         arcade.color.YELLOW, 32, anchor_x="center")
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
                    arcade.draw_text(f"{j+1}. {e['name']}: {e['score']}",
                                     xc, SCREEN_HEIGHT - 120 - j*20,
                                     arcade.color.WHITE, 14, anchor_x="center")

    def _draw_name_input(self):
        arcade.draw_text("New High Score!", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100,
                         arcade.color.GREEN, 22, anchor_x="center")
        arcade.draw_text("Enter name and press ENTER:", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+50,
                         arcade.color.WHITE, 18, anchor_x="center")
        l, r = SCREEN_WIDTH//2-150, SCREEN_WIDTH//2+150
        b, t = SCREEN_HEIGHT//2-20, SCREEN_HEIGHT//2+20
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GRAY)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE)
        arcade.draw_text(self.entered_name, SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                         arcade.color.WHITE, 18, anchor_x="center")

    def _draw_game(self):
        # Рамка поля
        left = FIELD_X
        right = FIELD_X + COLS * CELL_SIZE
        bottom = FIELD_Y
        top = FIELD_Y + ROWS * CELL_SIZE
        arcade.draw_line(left, bottom, right, bottom, GRAY, 2)
        arcade.draw_line(left, top, right, top, GRAY, 2)
        arcade.draw_line(left, bottom, left, top, GRAY, 2)
        arcade.draw_line(right, bottom, right, top, GRAY, 2)

        # Зафиксированные клетки
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] is not None:
                    self._draw_cell(col, row, COLORS[self.grid[row][col]])

        # Текущая фигура
        if not self.game_over and not self.paused:
            shape = SHAPES[self.current_type][self.current_rotation % len(SHAPES[self.current_type])]
            for dx, dy in shape:
                col = self.current_x + dx
                row = self.current_y + dy
                if row >= ROWS:
                    continue
                self._draw_cell(col, row, COLORS[self.current_type])

        # Панель предпросмотра и счёт
        next_x = FIELD_X + COLS * CELL_SIZE + 40
        next_y = SCREEN_HEIGHT - 120
        arcade.draw_text("Next:", next_x, next_y + 60, WHITE, 14)
        shape_next = SHAPES[self.next_piece_type][0]
        for dx, dy in shape_next:
            px = next_x + dx * CELL_SIZE
            py = next_y + dy * CELL_SIZE
            self._draw_cell_absolute(px, py, COLORS[self.next_piece_type])
        arcade.draw_text(f"Score: {self.score}", next_x, next_y - 50, WHITE, 16)

        if self.game_over:
            arcade.draw_text("GAME OVER",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.RED, 30, anchor_x="center")
        elif self.paused:
            arcade.draw_text("PAUSED",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.YELLOW, 30, anchor_x="center")

    def _draw_cell(self, col, row, color):
        left = FIELD_X + col * CELL_SIZE + 1
        right = left + CELL_SIZE - 2
        bottom = FIELD_Y + row * CELL_SIZE + 1
        top = bottom + CELL_SIZE - 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)

    def _draw_cell_absolute(self, x, y, color):
        left = x + 1
        right = x + CELL_SIZE - 1
        bottom = y + 1
        top = y + CELL_SIZE - 1
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)

    def _build_postgame_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.postgame_buttons = [
            {"label": "Play Again", "x": cx - 100, "y": cy - 80, "w": 160, "h": 40, "action": "replay"},
            {"label": "Quit to Lobby", "x": cx + 100, "y": cy - 80, "w": 160, "h": 40, "action": "quit"},
        ]

    def _draw_postgame_buttons(self):
        arcade.draw_text("Game Over", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40,
                         arcade.color.WHITE, 28, anchor_x="center")
        for btn in self.postgame_buttons:
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GREEN)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 14,
                             anchor_x="center", anchor_y="center")