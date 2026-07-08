"""
Snake game integrated as a BaseGame view.
3 difficulty levels, local leaderboard, proper lobby integration.
Optimized: all arcade.Text objects are pre-created and reused.
Controls synced with lobby key bindings.
Visual: background frame, HUD panel, bordered game field,
light green field with subtle grid, blue snake.
"""

import arcade
import random
import json
import os
from src.games.base_game import BaseGame
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 60) // CELL_SIZE   # оставляем место под HUD
GRID_OFFSET_Y = 60

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

# Настройки сложности (секунд между движениями)
DIFFICULTY_SPEEDS = {
    'easy': 0.18,
    'medium': 0.12,
    'hard': 0.07
}

# Цвета
FIELD_BG_COLOR = (170, 215, 170)     # светлый зеленоватый фон поля
GRID_LINE_COLOR = (130, 170, 130)    # тонкие линии сетки
SNAKE_BODY_COLOR = (0, 130, 255)     # синее тело
SNAKE_HEAD_COLOR = (0, 60, 180)      # тёмно-синяя голова

LEADERBOARD_FILE = "data/leaderboards/snake_leaderboard.json"
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

class SnakeGame(BaseGame):
    def __init__(self, machine_id, on_finish_callback):
        super().__init__("Snake", machine_id, on_finish_callback)
        self.difficulty = None
        self.state = "menu"
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()
        self.postgame_buttons = []
        self.move_interval = 0.18
        self.snake = []
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = [0, 0]
        self.score = 0
        self.game_over = False
        self.time_since_move = 0.0

        # ---------- Предсозданные тексты ----------
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self._menu_title = arcade.Text("SNAKE", cx, cy + 180, arcade.color.YELLOW, 48, anchor_x="center")
        self._menu_subtitle = arcade.Text("Выберите сложность", cx, cy + 130, arcade.color.WHITE, 20, anchor_x="center")

        self._menu_btn_labels = [
            arcade.Text("Easy (slow)", 0, 0, arcade.color.WHITE, 20, anchor_x="center"),
            arcade.Text("Medium", 0, 0, arcade.color.WHITE, 20, anchor_x="center"),
            arcade.Text("Hard (fast)", 0, 0, arcade.color.WHITE, 20, anchor_x="center"),
            arcade.Text("Leaderboards", 0, 0, arcade.color.WHITE, 20, anchor_x="center")
        ]

        self._lb_title = arcade.Text("Local Leaderboard", cx, SCREEN_HEIGHT - 40, arcade.color.YELLOW, 32, anchor_x="center")
        self._lb_hint = arcade.Text("Press BACKSPACE to return", cx, 30, arcade.color.WHITE, 14, anchor_x="center")
        self._lb_level_titles = [
            arcade.Text("Easy", 0, 0, arcade.color.ORANGE, 22, anchor_x="center"),
            arcade.Text("Medium", 0, 0, arcade.color.ORANGE, 22, anchor_x="center"),
            arcade.Text("Hard", 0, 0, arcade.color.ORANGE, 22, anchor_x="center")
        ]
        self._lb_entry_texts = {level: [] for level in ('easy','medium','hard')}
        for level in ('easy','medium','hard'):
            for _ in range(MAX_ENTRIES):
                self._lb_entry_texts[level].append(
                    arcade.Text("", 0, 0, arcade.color.WHITE, 14, anchor_x="center")
                )

        # HUD тексты
        self._score_text = arcade.Text("Score: 0", 0, 0, arcade.color.WHITE, 16)
        self._best_text = arcade.Text("", 0, 0, arcade.color.GOLD, 14)

        self._enter_name_title = arcade.Text("New High Score!", cx, cy + 100, arcade.color.GREEN, 22, anchor_x="center")
        self._enter_name_prompt = arcade.Text("Enter name and press ENTER:", cx, cy + 50, arcade.color.WHITE, 18, anchor_x="center")
        self._entered_name_text = arcade.Text("", cx, cy, arcade.color.WHITE, 18, anchor_x="center")

        self._postgame_title = arcade.Text("", cx, cy + 40, arcade.color.WHITE, 28, anchor_x="center")
        self._postgame_btn_texts = [
            arcade.Text("Play Again", 0, 0, arcade.color.WHITE, 14, anchor_x="center"),
            arcade.Text("Quit to Lobby", 0, 0, arcade.color.WHITE, 14, anchor_x="center")
        ]

        # Параметры компоновки
        self.hud_top = SCREEN_HEIGHT - 50
        self.field_left = 0
        self.field_bottom = 0

    def _build_menu_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        return [
            {"label": "Easy", "difficulty": "easy", "x": cx, "y": cy + 80, "w": 200, "h": 50},
            {"label": "Medium", "difficulty": "medium", "x": cx, "y": cy, "w": 200, "h": 50},
            {"label": "Hard", "difficulty": "hard", "x": cx, "y": cy - 80, "w": 200, "h": 50},
            {"label": "Leaderboards", "action": "leaderboard", "x": cx, "y": cy - 160, "w": 200, "h": 50},
        ]

    def on_show_view(self):
        self.state = "menu"
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()

    def _start_game(self):
        diff = self.difficulty or 'easy'
        self.move_interval = DIFFICULTY_SPEEDS[diff]
        self.snake = [
            [GRID_WIDTH // 2, GRID_HEIGHT // 2],
            [GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2],
            [GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2]
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.time_since_move = 0.0
        self._place_food()
        self.state = "playing"

        field_width = GRID_WIDTH * CELL_SIZE
        field_height = GRID_HEIGHT * CELL_SIZE
        self.field_left = (SCREEN_WIDTH - field_width) // 2
        self.field_bottom = GRID_OFFSET_Y

    def _place_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if [x, y] not in self.snake:
                self.food = [x, y]
                break

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
            return

        if self.next_direction == UP and self.direction != DOWN:
            self.direction = UP
        elif self.next_direction == DOWN and self.direction != UP:
            self.direction = DOWN
        elif self.next_direction == LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif self.next_direction == RIGHT and self.direction != LEFT:
            self.direction = RIGHT

        self.time_since_move += delta_time
        if self.time_since_move < self.move_interval:
            return
        self.time_since_move = 0.0

        head = self.snake[0].copy()
        if self.direction == UP:
            head[1] += 1
        elif self.direction == DOWN:
            head[1] -= 1
        elif self.direction == LEFT:
            head[0] -= 1
        elif self.direction == RIGHT:
            head[0] += 1

        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            self.game_over = True
            self._handle_game_end()
            return

        if head in self.snake:
            self.game_over = True
            self._handle_game_end()
            return

        self.snake.insert(0, head)

        if head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

    def _handle_game_end(self):
        if self._is_high_score():
            self.state = "enter_name"
            self.entered_name = ""
        else:
            self.state = "postgame"
            self._build_postgame_buttons()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.state in ("menu", "leaderboard", "postgame"):
                self.finish_game(False)
            elif self.state == "playing":
                self.finish_game(False)
            elif self.state == "enter_name":
                self.state = "menu"
            return

        if self.state == "playing" and not self.game_over:
            if key == cfg.KEY_BINDINGS['up']:
                self.next_direction = UP
            elif key == cfg.KEY_BINDINGS['down']:
                self.next_direction = DOWN
            elif key == cfg.KEY_BINDINGS['left']:
                self.next_direction = LEFT
            elif key == cfg.KEY_BINDINGS['right']:
                self.next_direction = RIGHT

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

    # ------------------------------------------------------------------
    # Drawing methods
    # ------------------------------------------------------------------
    def _draw_menu(self):
        self._menu_title.draw()
        self._menu_subtitle.draw()
        for i, btn in enumerate(self.menu_buttons):
            l = btn["x"] - btn["w"] // 2
            r = btn["x"] + btn["w"] // 2
            b = btn["y"] - btn["h"] // 2
            t = btn["y"] + btn["h"] // 2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_BLUE)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            lbl = self._menu_btn_labels[i]
            lbl.x = btn["x"]
            lbl.y = btn["y"]
            lbl.draw()

    def _draw_leaderboard(self):
        self._lb_title.draw()
        self._lb_hint.draw()
        col_w = SCREEN_WIDTH // 3
        levels = ["easy", "medium", "hard"]
        for i, level in enumerate(levels):
            xc = col_w * i + col_w // 2
            self._lb_level_titles[i].x = xc
            self._lb_level_titles[i].y = SCREEN_HEIGHT - 80
            self._lb_level_titles[i].draw()
            entries = self.leaderboard_data[level]
            for j in range(MAX_ENTRIES):
                if j < len(entries):
                    e = entries[j]
                    self._lb_entry_texts[level][j].text = f"{j+1}. {e['name']}: {e['score']}"
                    self._lb_entry_texts[level][j].x = xc
                    self._lb_entry_texts[level][j].y = SCREEN_HEIGHT - 120 - j * 20
                    self._lb_entry_texts[level][j].draw()
            if not entries:
                empty_text = arcade.Text("Empty", xc, SCREEN_HEIGHT - 120,
                                         arcade.color.GRAY, 16, anchor_x="center")
                empty_text.draw()

    def _draw_name_input(self):
        self._enter_name_title.draw()
        self._enter_name_prompt.draw()
        l, r = SCREEN_WIDTH//2-150, SCREEN_WIDTH//2+150
        b, t = SCREEN_HEIGHT//2-20, SCREEN_HEIGHT//2+20
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GRAY)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE)
        self._entered_name_text.text = self.entered_name
        self._entered_name_text.x = SCREEN_WIDTH // 2
        self._entered_name_text.y = SCREEN_HEIGHT // 2
        self._entered_name_text.draw()

    def _draw_game(self):
        # Общий фон и внешняя рамка
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (10, 10, 30))
        arcade.draw_lrbt_rectangle_outline(2, SCREEN_WIDTH - 2, 2, SCREEN_HEIGHT - 2,
                                           arcade.color.DARK_GRAY, 4)

        # HUD панель
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH,
                                          self.hud_top, SCREEN_HEIGHT,
                                          (20, 20, 50, 200))
        self._score_text.text = f"Score: {self.score}"
        self._score_text.x = 15
        self._score_text.y = self.hud_top + 30
        self._score_text.draw()

        if self.difficulty and self.leaderboard_data:
            entries = self.leaderboard_data.get(self.difficulty, [])
            if entries:
                best = entries[0]
                self._best_text.text = f"Best: {best['score']} by {best['name']}"
            else:
                self._best_text.text = "Best: --"
            self._best_text.x = 15
            self._best_text.y = self.hud_top + 8
            self._best_text.draw()

        # Рамка игрового поля
        field_left = self.field_left
        field_bottom = self.field_bottom
        field_width = GRID_WIDTH * CELL_SIZE
        field_height = GRID_HEIGHT * CELL_SIZE
        arcade.draw_lrbt_rectangle_outline(field_left - 2, field_left + field_width + 2,
                                           field_bottom - 2, field_bottom + field_height + 2,
                                           arcade.color.YELLOW, 3)

        # Заливка фона поля
        arcade.draw_lrbt_rectangle_filled(field_left, field_left + field_width,
                                          field_bottom, field_bottom + field_height,
                                          FIELD_BG_COLOR)

        # Тонкая сетка
        for y in range(GRID_HEIGHT + 1):
            py = field_bottom + y * CELL_SIZE
            arcade.draw_line(field_left, py, field_left + field_width, py, GRID_LINE_COLOR, 1)
        for x in range(GRID_WIDTH + 1):
            px = field_left + x * CELL_SIZE
            arcade.draw_line(px, field_bottom, px, field_bottom + field_height, GRID_LINE_COLOR, 1)

        # Еда
        fx, fy = self.food
        food_left = field_left + fx * CELL_SIZE
        food_right = food_left + CELL_SIZE
        food_bottom = field_bottom + fy * CELL_SIZE
        food_top = food_bottom + CELL_SIZE
        arcade.draw_lrbt_rectangle_filled(food_left, food_right, food_bottom, food_top, arcade.color.RED)

        # Змейка (синяя)
        for i, (sx, sy) in enumerate(self.snake):
            seg_left = field_left + sx * CELL_SIZE
            seg_right = seg_left + CELL_SIZE
            seg_bottom = field_bottom + sy * CELL_SIZE
            seg_top = seg_bottom + CELL_SIZE
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            arcade.draw_lrbt_rectangle_filled(seg_left, seg_right, seg_bottom, seg_top, color)

        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, 36, anchor_x="center")

    def _build_postgame_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.postgame_buttons = [
            {"label": "Play Again", "x": cx - 100, "y": cy - 80, "w": 160, "h": 40, "action": "replay"},
            {"label": "Quit to Lobby", "x": cx + 100, "y": cy - 80, "w": 160, "h": 40, "action": "quit"},
        ]

    def _draw_postgame_buttons(self):
        self._postgame_title.text = "Game Over"
        self._postgame_title.draw()
        for i, btn in enumerate(self.postgame_buttons):
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GREEN)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            txt = self._postgame_btn_texts[i]
            txt.x = btn["x"]
            txt.y = btn["y"]
            txt.draw()