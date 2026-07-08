"""
Snake game integrated as a BaseGame view.
3 difficulty levels, local leaderboard, proper lobby integration.
"""

import arcade
import random
import math
import json
import os
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Constants
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 60) // CELL_SIZE  # leave room for HUD
GRID_OFFSET_Y = 60

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

# Difficulty settings: move interval in seconds
DIFFICULTY_SPEEDS = {
    'easy': 0.18,
    'medium': 0.12,
    'hard': 0.07
}

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
        self.state = "menu"          # "menu", "playing", "leaderboard", "enter_name", "postgame"
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
        self.win = False
        self.time_since_move = 0.0
        self._place_food()
        self.state = "playing"

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

        # direction lock (no 180 turn)
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
        if self.direction == UP:    head[1] += 1
        elif self.direction == DOWN:  head[1] -= 1
        elif self.direction == LEFT:  head[0] -= 1
        elif self.direction == RIGHT: head[0] += 1

        # wall collision
        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            self.game_over = True
            self._handle_game_end()
            return

        # self collision
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
        # switch to appropriate state
        if self._is_high_score():
            self.state = "enter_name"
            self.pending_score = self.score
            self.entered_name = ""
        else:
            self.state = "postgame"
            self._build_postgame_buttons()

    def on_key_press(self, key, modifiers):
        # Global quit key
        if key == arcade.key.ESCAPE:
            if self.state in ("menu", "leaderboard", "postgame"):
                self.finish_game(False)
            elif self.state == "playing":
                self.finish_game(False)
            elif self.state == "enter_name":
                self.state = "menu"
            return

        if self.state == "playing":
            if not self.game_over:
                if key == arcade.key.UP:    self.next_direction = UP
                elif key == arcade.key.DOWN:  self.next_direction = DOWN
                elif key == arcade.key.LEFT:  self.next_direction = LEFT
                elif key == arcade.key.RIGHT: self.next_direction = RIGHT
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

    # -----------------------------------------------
    # Drawing methods
    # -----------------------------------------------
    def _draw_menu(self):
        arcade.draw_text("SNAKE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180,
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
        # Draw grid area
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                px = x * CELL_SIZE
                py = y * CELL_SIZE + GRID_OFFSET_Y
                arcade.draw_lrbt_rectangle_outline(px, px + CELL_SIZE, py, py + CELL_SIZE,
                                                   arcade.color.DARK_GRAY, 1)

        # Food
        fx, fy = self.food
        food_left = fx * CELL_SIZE
        food_right = food_left + CELL_SIZE
        food_bottom = fy * CELL_SIZE + GRID_OFFSET_Y
        food_top = food_bottom + CELL_SIZE
        arcade.draw_lrbt_rectangle_filled(food_left, food_right, food_bottom, food_top, arcade.color.RED)

        # Snake
        for i, (sx, sy) in enumerate(self.snake):
            seg_left = sx * CELL_SIZE
            seg_right = seg_left + CELL_SIZE
            seg_bottom = sy * CELL_SIZE + GRID_OFFSET_Y
            seg_top = seg_bottom + CELL_SIZE
            color = arcade.color.GREEN if i == 0 else arcade.color.DARK_GREEN
            arcade.draw_lrbt_rectangle_filled(seg_left, seg_right, seg_bottom, seg_top, color)

        # HUD
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 20,
                         arcade.color.WHITE, 16)

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
        arcade.draw_text("Game Over", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40,
                         arcade.color.WHITE, 28, anchor_x="center")
        for btn in self.postgame_buttons:
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GREEN)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 14,
                             anchor_x="center", anchor_y="center")