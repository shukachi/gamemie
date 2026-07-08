"""
Pac-Man arcade game – integrated BaseGame view.
Adaptive layout, menu background (JPG), heart icons, best score, ghost immunity.
"""

import arcade
import random
import math
import json
import os
from src.games.base_game import BaseGame
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
PACMAN_SPEED = 120
GHOST_SPEED = 90
GHOST_SCARED_SPEED = 60
SCARED_DURATION = 7.0
BLINK_START = 3.0
BLINK_INTERVAL = 0.2
COUNTDOWN_SECONDS = 3

COLOR_WALL = (0, 0, 128)
COLOR_DOT = (255, 255, 200)
COLOR_ENERGIZER = (255, 255, 200)
COLOR_PACMAN = (255, 255, 0)
COLOR_GHOST_COLORS = [
    (255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)
]
COLOR_SCARED = (33, 33, 255)
COLOR_EYES = (255, 255, 255)
COLOR_PUPIL = (0, 0, 0)

FRUIT_TYPES = [
    {"type": "strawberry", "color": (255, 0, 0), "multiplier": 3, "duration": 8.0, "name": "клубника"},
    {"type": "banana", "color": (255, 255, 0), "multiplier": 2, "duration": 12.0, "name": "банан"},
    {"type": "grape", "color": (128, 0, 128), "multiplier": 5, "duration": 5.0, "name": "виноград"}
]

DIRECTIONS = {'RIGHT': (1, 0), 'LEFT': (-1, 0), 'UP': (0, -1), 'DOWN': (0, 1)}

MAPS = {
    'easy': [
        "#############",
        "#...........#",
        "#.#.#.#.#.#.#",
        "#...........#",
        "#.#.#.#.#.#.#",
        "#...........#",
        "#.#.#.#.#.#.#",
        "#...........#",
        "#.#.#.#.#.#.#",
        "#...........#",
        "#############"
    ],
    'medium': [
        "###############",
        "#.............#",
        "#.#.#.#.#.#.#.#",
        "#.##.#.#.#.##.#",
        "#.............#",
        "#.#.#.###.#.#.#",
        "#.#...#.#...#.#",
        "#.#.#.#.#.#.#.#",
        "#.............#",
        "#.##.#.#.#.##.#",
        "#.#.#.#.#.#.#.#",
        "#.............#",
        "###############"
    ],
    'hard': [
        "#################",
        "#...............#",
        "#.#.#.#.#.#.#.#.#",
        "#.##.#.#.#.#.##.#",
        "#................#",
        "#.#.#.###.###.#.#",
        "#.#...#.#.#...#.#",
        "#.#.#.#.#.#.#.#.#",
        "#................#",
        "#.##.#.#.#.#.##.#",
        "#.#.#.###.###.#.#",
        "#.#.....#.....#.#",
        "#................#",
        "#.#.#.#.#.#.#.#.#",
        "#################"
    ]
}

LEADERBOARD_FILE = "data/leaderboards/pacman_leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 10

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
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

def can_move_to(col, row, dcol, drow, map_data):
    new_col = col + dcol
    new_row = row + drow
    if new_col < 0 or new_col >= len(map_data[0]) or new_row < 0 or new_row >= len(map_data):
        return False
    return map_data[new_row][new_col] != '#'

# ----------------------------------------------------------------------
# Game objects
# ----------------------------------------------------------------------
class Pacman:
    def __init__(self, col, row, cell_size, field_left, field_bottom, rows, cols):
        self.col = col
        self.row = row
        self.cell_size = cell_size
        self.field_left = field_left
        self.field_bottom = field_bottom
        self.rows = rows
        self.cols = cols
        self.center_x, self.center_y = self._tile_to_pixel(col, row)
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.mouth_angle = 0
        self.mouth_dir = 1

    def _tile_to_pixel(self, col, row):
        x = self.field_left + (col + 0.5) * self.cell_size
        y = self.field_bottom + (self.rows - 1 - row + 0.5) * self.cell_size
        return x, y

    def update(self, dt, map_data):
        self.mouth_angle += 120 * dt * self.mouth_dir
        if self.mouth_angle > 40:
            self.mouth_angle = 40
            self.mouth_dir = -1
        elif self.mouth_angle < 5:
            self.mouth_angle = 5
            self.mouth_dir = 1

        if self.direction == (0, 0):
            if self.next_direction != (0, 0):
                ndcol, ndrow = self.next_direction
                if can_move_to(self.col, self.row, ndcol, ndrow, map_data):
                    self.direction = self.next_direction
                    self.next_direction = (0, 0)
            if self.direction == (0, 0):
                return

        dcol, drow = self.direction
        target_x, target_y = self._tile_to_pixel(self.col + dcol, self.row + drow)
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        step = PACMAN_SPEED * dt
        if step >= dist:
            self.center_x, self.center_y = target_x, target_y
            self.col += dcol
            self.row += drow
            if not can_move_to(self.col, self.row, dcol, drow, map_data):
                self.direction = (0, 0)
            if self.next_direction != (0, 0):
                ndcol, ndrow = self.next_direction
                if can_move_to(self.col, self.row, ndcol, ndrow, map_data):
                    self.direction = self.next_direction
                    self.next_direction = (0, 0)
        else:
            self.center_x += (dx / dist) * step
            self.center_y += (dy / dist) * step

    def set_next_direction(self, dcol, drow):
        self.next_direction = (dcol, drow)


class Ghost:
    def __init__(self, col, row, color, cell_size, field_left, field_bottom, rows, cols):
        self.home_col = col
        self.home_row = row
        self.col = col
        self.row = row
        self.cell_size = cell_size
        self.field_left = field_left
        self.field_bottom = field_bottom
        self.rows = rows
        self.cols = cols
        self.center_x, self.center_y = self._tile_to_pixel(col, row)
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.color = color
        self.scared = False
        self.respawn_timer = 0.0
        self.force_normal = False

    def _tile_to_pixel(self, col, row):
        x = self.field_left + (col + 0.5) * self.cell_size
        y = self.field_bottom + (self.rows - 1 - row + 0.5) * self.cell_size
        return x, y

    def update(self, dt, scared_mode, map_data):
        effective_scared = scared_mode and not self.force_normal

        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn_timer = 0.0
                possible = []
                for ddc, ddr in [(1,0),(-1,0),(0,1),(0,-1)]:
                    if can_move_to(self.col, self.row, ddc, ddr, map_data):
                        possible.append((ddc, ddr))
                if possible:
                    self.direction = random.choice(possible)
                else:
                    self.direction = (0, 0)
            self.scared = effective_scared
            return

        speed = GHOST_SCARED_SPEED if effective_scared else GHOST_SPEED
        self.scared = effective_scared

        if self.direction == (0, 0):
            return

        dcol, drow = self.direction
        target_x, target_y = self._tile_to_pixel(self.col + dcol, self.row + drow)
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        step = speed * dt
        if step >= dist:
            self.center_x, self.center_y = target_x, target_y
            self.col += dcol
            self.row += drow
            possible = []
            for ddc, ddr in [(1,0),(-1,0),(0,1),(0,-1)]:
                if (ddc == -dcol and ddr == -drow) and len(possible) > 0:
                    continue
                if can_move_to(self.col, self.row, ddc, ddr, map_data):
                    possible.append((ddc, ddr))
            if not possible:
                if can_move_to(self.col, self.row, -dcol, -drow, map_data):
                    possible.append((-dcol, -drow))
            if possible:
                self.direction = random.choice(possible)
            else:
                self.direction = (0, 0)
        else:
            self.center_x += (dx / dist) * step
            self.center_y += (dy / dist) * step

    def reset_to_home(self):
        self.col = self.home_col
        self.row = self.home_row
        self.center_x, self.center_y = self._tile_to_pixel(self.col, self.row)
        self.direction = (0, 0)
        self.respawn_timer = 5.0
        self.scared = False
        self.force_normal = True


# ----------------------------------------------------------------------
# Main Game View
# ----------------------------------------------------------------------
class PacmanGame(BaseGame):
    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("Pac-Man", machine_id, on_finish_callback)
        self.difficulty = None
        self.map_data = None
        self.rows = 0
        self.cols = 0
        self.dots = []
        self.energizers = []
        self.walls = []
        self.fruits = []
        self.pacman = None
        self.ghosts = []
        self.score = 0
        self.lives = 3
        self.scared_timer = 0.0
        self.boost_multiplier = 1.0
        self.boost_timer = 0.0
        self.boost_fruit_name = ""
        self.game_over = False
        self.win = False
        self.blink_timer = 0.0
        self.blink_on = True

        self.state = "menu"
        self.leaderboard_data = load_local_leaderboard()
        self.pending_score = 0
        self.entered_name = ""
        self.menu_buttons = self._build_menu_buttons()
        self.postgame_buttons = []
        self.countdown_timer = 0.0

        # Layout
        self.cell_size = 1
        self.field_left = 0
        self.field_bottom = 0
        self.hud_top = 0

        # ---------- ЗАГРУЗКА ФОНА МЕНЮ (JPG) ----------
        try:
            self.menu_bg = arcade.load_texture(":backgrounds:pacman_menu_bg.jpg")
            print("Pac-Man menu background loaded successfully.")
        except Exception as e:
            print(f"WARNING: Could not load Pac-Man menu background: {e}")
            self.menu_bg = None

        # ---------- Text objects ----------
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self._menu_title = arcade.Text("PAC-MAN", cx, cy + 180,
                                       arcade.color.YELLOW, 48, anchor_x="center")
        self._menu_subtitle = arcade.Text("Выберите сложность", cx, cy + 130,
                                          arcade.color.WHITE, 20, anchor_x="center")
        self._lb_title = arcade.Text("Local Leaderboard", cx, SCREEN_HEIGHT - 40,
                                     arcade.color.YELLOW, 32, anchor_x="center")
        self._lb_hint = arcade.Text("Press BACKSPACE to return", cx, 30,
                                    arcade.color.WHITE, 14, anchor_x="center")
        self._lb_level_titles = [
            arcade.Text("Easy", 0, 0, arcade.color.ORANGE, 22, anchor_x="center"),
            arcade.Text("Medium", 0, 0, arcade.color.ORANGE, 22, anchor_x="center"),
            arcade.Text("Hard", 0, 0, arcade.color.ORANGE, 22, anchor_x="center")
        ]
        self._score_text = arcade.Text("Score: 0", 0, 0, arcade.color.WHITE, 16)
        self._best_score_text = arcade.Text("Best: --", 0, 0, arcade.color.GOLD, 14)
        self._boost_text = arcade.Text("", 0, 0, arcade.color.GREEN, 14)
        self._countdown_text = arcade.Text("", cx, cy, arcade.color.YELLOW, 72, anchor_x="center")
        self._enter_name_title = arcade.Text("New High Score!", cx, cy + 100,
                                             arcade.color.GREEN, 22, anchor_x="center")
        self._enter_name_prompt = arcade.Text("Enter name and press ENTER:", cx, cy + 50,
                                              arcade.color.WHITE, 18, anchor_x="center")
        self._entered_name_text = arcade.Text("", cx, cy, arcade.color.WHITE, 18, anchor_x="center")
        self._postgame_title = arcade.Text("", cx, cy + 40, arcade.color.WHITE, 28, anchor_x="center")
        self._postgame_button_texts = [
            arcade.Text("Play Again", 0, 0, arcade.color.WHITE, 14, anchor_x="center"),
            arcade.Text("Quit to Lobby", 0, 0, arcade.color.WHITE, 14, anchor_x="center")
        ]

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
        """Вызывается при каждом показе view. Сбрасываем состояние в меню."""
        self.state = "menu"
        self.score = 0
        self.lives = 3
        self.win = False
        self.game_over = False
        self.leaderboard_data = load_local_leaderboard()
        self.menu_buttons = self._build_menu_buttons()

    def on_draw(self):
        self.clear()
        # Фон меню для всех экранов, кроме игровых
        if self.state in ("menu", "leaderboard", "enter_name", "postgame"):
            if self.menu_bg:
                arcade.draw_texture_rect(self.menu_bg,
                                         arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                                     SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                # Чёрный фон, если изображение не загружено
                arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0))

        if self.state == "menu":
            self._draw_menu()
        elif self.state == "leaderboard":
            self._draw_leaderboard()
        elif self.state == "enter_name":
            self._draw_name_input()
        elif self.state in ("countdown", "playing", "win", "postgame"):
            self._draw_game()
            if self.state == "countdown":
                self._draw_countdown()
            if self.state == "postgame":
                self._draw_postgame_buttons()

    def on_update(self, delta_time):
        if self.state == "countdown":
            self.countdown_timer -= delta_time
            if self.countdown_timer <= 0:
                self.countdown_timer = 0
                self.state = "playing"
            return
        elif self.state == "playing":
            self._update_playing(delta_time)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.state in ("menu", "leaderboard", "postgame", "countdown"):
                self.finish_game(False)
            elif self.state == "playing":
                self.finish_game(False)
            elif self.state == "enter_name":
                self.state = "menu"
            return

        if self.state == "menu":
            pass
        elif self.state == "leaderboard":
            if key == arcade.key.BACKSPACE:
                self.state = "menu"
        elif self.state == "enter_name":
            self._handle_name_input(key, modifiers)
        elif self.state == "playing":
            self._handle_playing_input(key)
        elif self.state == "postgame":
            pass
        elif self.state == "countdown":
            pass

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

    def _compute_layout(self):
        HUD_HEIGHT = 50
        MARGIN = 20
        area_width = SCREEN_WIDTH - 2 * MARGIN
        area_height = SCREEN_HEIGHT - HUD_HEIGHT - 2 * MARGIN
        cell_w = area_width / self.cols
        cell_h = area_height / self.rows
        self.cell_size = min(cell_w, cell_h)
        field_width = self.cols * self.cell_size
        field_height = self.rows * self.cell_size
        self.field_left = (SCREEN_WIDTH - field_width) / 2
        self.field_bottom = MARGIN + (area_height - field_height) / 2
        self.hud_top = SCREEN_HEIGHT - HUD_HEIGHT

    def _start_game(self):
        diff = self.difficulty or 'easy'
        self.map_data = MAPS[diff]
        self.rows = len(self.map_data)
        self.cols = len(self.map_data[0])

        self._compute_layout()

        self.dots = [[False]*self.cols for _ in range(self.rows)]
        self.energizers = [[False]*self.cols for _ in range(self.rows)]
        self.walls = [[False]*self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.map_data[r][c] == '#':
                    self.walls[r][c] = True
                else:
                    self.dots[r][c] = True

        energizer_positions = [(1,1), (self.cols-2,1), (1,self.rows-2), (self.cols-2,self.rows-2)]
        for c, r in energizer_positions:
            if not self.walls[r][c]:
                self.dots[r][c] = False
                self.energizers[r][c] = True

        pac_col, pac_row = self.cols // 2, self.rows - 2
        self.dots[pac_row][pac_col] = False
        self.pacman = Pacman(pac_col, pac_row, self.cell_size,
                             self.field_left, self.field_bottom, self.rows, self.cols)

        self.ghosts = []
        ghost_homes = [
            (self.cols//2 - 1, self.rows//2),
            (self.cols//2, self.rows//2),
            (self.cols//2 - 1, self.rows//2 - 1),
            (self.cols//2 + 1, self.rows//2 - 1)
        ]
        valid_homes = []
        for gc, gr in ghost_homes:
            if not self.walls[gr][gc]:
                valid_homes.append((gc, gr))
            else:
                for dc, dr in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nc, nr = gc+dc, gr+dr
                    if 0 <= nc < self.cols and 0 <= nr < self.rows and not self.walls[nr][nc]:
                        valid_homes.append((nc, nr))
                        break
        for i, (gc, gr) in enumerate(valid_homes[:4]):
            color = COLOR_GHOST_COLORS[i % len(COLOR_GHOST_COLORS)]
            ghost = Ghost(gc, gr, color, self.cell_size,
                          self.field_left, self.field_bottom, self.rows, self.cols)
            self.ghosts.append(ghost)
            self.dots[gr][gc] = False

        available = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.dots[r][c] and not self.walls[r][c] and not self.energizers[r][c]:
                    if c == pac_col and r == pac_row:
                        continue
                    if any((c == gc and r == gr) for gc, gr in valid_homes):
                        continue
                    available.append((c, r))
        random.shuffle(available)
        self.fruits = []
        for i in range(min(3, len(available))):
            col, row = available[i]
            fruit_info = FRUIT_TYPES[i % len(FRUIT_TYPES)]
            self.fruits.append({
                "col": col, "row": row,
                "type": fruit_info["type"],
                "multiplier": fruit_info["multiplier"],
                "duration": fruit_info["duration"],
                "color": fruit_info["color"],
                "name": fruit_info["name"]
            })
            self.dots[row][col] = False

        self.score = 0
        self.lives = 3
        self.scared_timer = 0.0
        self.boost_multiplier = 1.0
        self.boost_timer = 0.0
        self.blink_timer = 0.0
        self.blink_on = True
        self.game_over = False
        self.win = False
        self.countdown_timer = COUNTDOWN_SECONDS
        self.state = "countdown"

    def _update_playing(self, dt):
        if self.game_over or self.win:
            if self.state == "playing":
                if self.win and self._is_high_score():
                    self.state = "enter_name"
                    self.pending_score = self.score
                    self.entered_name = ""
                else:
                    self.state = "postgame"
                    self._build_postgame_buttons()
            return

        if self.boost_timer > 0:
            self.boost_timer -= dt
            if self.boost_timer <= 0:
                self.boost_timer = 0
                self.boost_multiplier = 1
                self.boost_fruit_name = ""

        scared = self.scared_timer > 0
        if scared:
            self.scared_timer -= dt
            if self.scared_timer <= 0:
                self.scared_timer = 0
                scared = False
                for ghost in self.ghosts:
                    ghost.force_normal = False
            if self.scared_timer <= BLINK_START:
                self.blink_timer += dt
                while self.blink_timer >= BLINK_INTERVAL:
                    self.blink_timer -= BLINK_INTERVAL
                    self.blink_on = not self.blink_on
            else:
                self.blink_on = True
        else:
            self.blink_on = True

        self.pacman.update(dt, self.map_data)
        col, row = self.pacman.col, self.pacman.row

        if self.dots[row][col]:
            self.dots[row][col] = False
            self.score += int(10 * self.boost_multiplier)
        if self.energizers[row][col]:
            self.energizers[row][col] = False
            self.score += int(50 * self.boost_multiplier)
            self.scared_timer = SCARED_DURATION
            scared = True
            self.blink_timer = 0.0
            self.blink_on = True
            for ghost in self.ghosts:
                ghost.force_normal = False
        for fruit in self.fruits[:]:
            if fruit["col"] == col and fruit["row"] == row:
                self.fruits.remove(fruit)
                self.boost_multiplier = fruit["multiplier"]
                self.boost_timer = fruit["duration"]
                self.boost_fruit_name = fruit["name"]
                self.score += int(100 * self.boost_multiplier)
                break

        for ghost in self.ghosts:
            ghost.update(dt, scared, self.map_data)

        for ghost in self.ghosts:
            dist = math.hypot(self.pacman.center_x - ghost.center_x,
                              self.pacman.center_y - ghost.center_y)
            if dist < self.cell_size * 0.7:
                if scared and not ghost.force_normal:
                    self.score += int(200 * self.boost_multiplier)
                    ghost.reset_to_home()
                elif not scared:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self._reset_positions()
                    break

        if not self.game_over and not self.win:
            remaining = sum(row.count(True) for row in self.dots) + \
                        sum(row.count(True) for row in self.energizers) + len(self.fruits)
            if remaining == 0:
                self.win = True

    def _reset_positions(self):
        pac_col, pac_row = self.cols // 2, self.rows - 2
        self.pacman.col = pac_col
        self.pacman.row = pac_row
        self.pacman.center_x, self.pacman.center_y = self.pacman._tile_to_pixel(pac_col, pac_row)
        self.pacman.direction = (0, 0)
        self.pacman.next_direction = (0, 0)
        for ghost in self.ghosts:
            ghost.reset_to_home()
        self.scared_timer = 0
        self.blink_timer = 0
        self.blink_on = True
        self.boost_timer = 0
        self.boost_multiplier = 1
        for ghost in self.ghosts:
            ghost.force_normal = False

    def _is_high_score(self):
        entries = self.leaderboard_data.get(self.difficulty, [])
        if len(entries) < MAX_LEADERBOARD_ENTRIES:
            return True
        lowest = min(entries, key=lambda x: x["score"])["score"]
        return self.score > lowest

    def _add_leaderboard_entry(self, name):
        entries = self.leaderboard_data.get(self.difficulty, [])
        entries.append({"name": name, "score": self.score})
        entries.sort(key=lambda x: x["score"], reverse=True)
        self.leaderboard_data[self.difficulty] = entries[:MAX_LEADERBOARD_ENTRIES]
        save_local_leaderboard(self.leaderboard_data)

    def _handle_playing_input(self, key):
        if key == cfg.KEY_BINDINGS['up']:
            self.pacman.set_next_direction(*DIRECTIONS['UP'])
        elif key == cfg.KEY_BINDINGS['down']:
            self.pacman.set_next_direction(*DIRECTIONS['DOWN'])
        elif key == cfg.KEY_BINDINGS['left']:
            self.pacman.set_next_direction(*DIRECTIONS['LEFT'])
        elif key == cfg.KEY_BINDINGS['right']:
            self.pacman.set_next_direction(*DIRECTIONS['RIGHT'])

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
        for btn in self.menu_buttons:
            l = btn["x"] - btn["w"] // 2
            r = btn["x"] + btn["w"] // 2
            b = btn["y"] - btn["h"] // 2
            t = btn["y"] + btn["h"] // 2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_BLUE)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            label = arcade.Text(btn["label"], btn["x"], btn["y"],
                                arcade.color.WHITE, 20,
                                anchor_x="center", anchor_y="center")
            label.draw()

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
            if not entries:
                empty_text = arcade.Text("Empty", xc, SCREEN_HEIGHT - 120,
                                         arcade.color.GRAY, 16, anchor_x="center")
                empty_text.draw()
            else:
                for j, e in enumerate(entries[:MAX_LEADERBOARD_ENTRIES]):
                    text = arcade.Text(f"{j+1}. {e['name']}: {e['score']}",
                                       xc, SCREEN_HEIGHT - 120 - j*20,
                                       arcade.color.WHITE, 14, anchor_x="center")
                    text.draw()

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
        # Фон игры
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (10, 10, 30))
        arcade.draw_lrbt_rectangle_outline(2, SCREEN_WIDTH - 2, 2, SCREEN_HEIGHT - 2,
                                           arcade.color.DARK_GRAY, 4)

        # HUD
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
                self._best_score_text.text = f"Best: {best['score']} by {best['name']}"
            else:
                self._best_score_text.text = "Best: --"
            self._best_score_text.x = 15
            self._best_score_text.y = self.hud_top + 8
            self._best_score_text.draw()

        if self.boost_timer > 0 and self.boost_multiplier > 1:
            self._boost_text.text = f"x{self.boost_multiplier} {self.boost_fruit_name} {self.boost_timer:.1f}s"
            self._boost_text.x = SCREEN_WIDTH - 150
            self._boost_text.y = self.hud_top + 30
            self._boost_text.draw()

        heart_x = SCREEN_WIDTH - 30
        heart_y = self.hud_top + 15
        for i in range(self.lives):
            self._draw_heart(heart_x - i * 25, heart_y, 8)

        # Рамка поля
        field_left = self.field_left
        field_bottom = self.field_bottom
        field_width = self.cols * self.cell_size
        field_height = self.rows * self.cell_size
        arcade.draw_lrbt_rectangle_outline(field_left - 2, field_left + field_width + 2,
                                           field_bottom - 2, field_bottom + field_height + 2,
                                           arcade.color.YELLOW, 3)

        # Стены
        for r in range(self.rows):
            for c in range(self.cols):
                if self.walls[r][c]:
                    cx = field_left + (c + 0.5) * self.cell_size
                    cy = field_bottom + (self.rows - 1 - r + 0.5) * self.cell_size
                    left = cx - self.cell_size / 2
                    right = cx + self.cell_size / 2
                    bottom = cy - self.cell_size / 2
                    top = cy + self.cell_size / 2
                    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, COLOR_WALL)

        # Точки и энерджайзеры
        for r in range(self.rows):
            for c in range(self.cols):
                cx = field_left + (c + 0.5) * self.cell_size
                cy = field_bottom + (self.rows - 1 - r + 0.5) * self.cell_size
                if self.dots[r][c]:
                    arcade.draw_circle_filled(cx, cy, self.cell_size * 0.15, COLOR_DOT)
                if self.energizers[r][c]:
                    arcade.draw_circle_filled(cx, cy, self.cell_size * 0.3, COLOR_ENERGIZER)

        # Фрукты
        for fruit in self.fruits:
            cx = field_left + (fruit["col"] + 0.5) * self.cell_size
            cy = field_bottom + (self.rows - 1 - fruit["row"] + 0.5) * self.cell_size
            self._draw_fruit(fruit["type"], cx, cy, self.cell_size * 0.5)

        # Призраки
        for ghost in self.ghosts:
            gx, gy = ghost.center_x, ghost.center_y
            if ghost.scared:
                if self.scared_timer <= BLINK_START and not self.blink_on:
                    color = ghost.color
                else:
                    color = COLOR_SCARED
            else:
                color = ghost.color
            arcade.draw_circle_filled(gx, gy, self.cell_size * 0.4, color)
            e_off = self.cell_size * 0.15
            arcade.draw_circle_filled(gx - e_off, gy + e_off, self.cell_size * 0.12, COLOR_EYES)
            arcade.draw_circle_filled(gx + e_off, gy + e_off, self.cell_size * 0.12, COLOR_EYES)
            p_off = self.cell_size * 0.04
            dxd, dyd = ghost.direction if ghost.direction != (0, 0) else (1, 0)
            arcade.draw_circle_filled(gx - e_off + dxd * p_off, gy + e_off + dyd * p_off,
                                      self.cell_size * 0.05, COLOR_PUPIL)
            arcade.draw_circle_filled(gx + e_off + dxd * p_off, gy + e_off + dyd * p_off,
                                      self.cell_size * 0.05, COLOR_PUPIL)

        # Пакман
        if self.pacman:
            px, py = self.pacman.center_x, self.pacman.center_y
            dcol, drow = self.pacman.direction
            if dcol == 1: base_angle = 0
            elif dcol == -1: base_angle = 180
            elif drow == 1: base_angle = 270
            elif drow == -1: base_angle = 90
            else: base_angle = 0
            mouth = self.pacman.mouth_angle
            arcade.draw_arc_filled(px, py, self.cell_size * 0.8, self.cell_size * 0.8,
                                   COLOR_PACMAN, start_angle=base_angle + mouth,
                                   end_angle=base_angle + 360 - mouth)
            eye_angle = math.radians(base_angle)
            eye_x = px + math.cos(eye_angle) * self.cell_size * 0.25
            eye_y = py + math.sin(eye_angle) * self.cell_size * 0.25
            arcade.draw_circle_filled(eye_x, eye_y, self.cell_size * 0.08, COLOR_PUPIL)

    def _draw_heart(self, x, y, size):
        arcade.draw_arc_filled(x - size * 0.5, y + size * 0.5, size, size,
                               arcade.color.RED, 0, 180)
        arcade.draw_arc_filled(x + size * 0.5, y + size * 0.5, size, size,
                               arcade.color.RED, 0, 180)
        arcade.draw_triangle_filled(x - size, y + size * 0.3,
                                    x + size, y + size * 0.3,
                                    x, y - size * 0.7,
                                    arcade.color.RED)

    def _draw_countdown(self):
        if self.countdown_timer > 0:
            number = math.ceil(self.countdown_timer)
            self._countdown_text.text = str(number)
        else:
            self._countdown_text.text = "GO!"
        self._countdown_text.x = SCREEN_WIDTH // 2
        self._countdown_text.y = SCREEN_HEIGHT // 2
        self._countdown_text.draw()

    def _draw_fruit(self, fruit_type, cx, cy, size):
        if fruit_type == "strawberry":
            arcade.draw_triangle_filled(cx, cy - size * 0.6, cx - size * 0.5, cy + size * 0.2,
                                        cx + size * 0.5, cy + size * 0.2, (255, 0, 0))
            arcade.draw_lrbt_rectangle_filled(cx - size * 0.15, cx + size * 0.15,
                                              cy + size * 0.2, cy + size * 0.5, (0, 200, 0))
            arcade.draw_circle_filled(cx - size * 0.15, cy - size * 0.1, size * 0.08, (255, 255, 0))
            arcade.draw_circle_filled(cx + size * 0.15, cy - size * 0.1, size * 0.08, (255, 255, 0))
        elif fruit_type == "banana":
            arcade.draw_ellipse_filled(cx, cy, size * 0.9, size * 0.4, (255, 255, 0), tilt_angle=30)
            arcade.draw_circle_filled(cx - size * 0.35, cy - size * 0.15, size * 0.08, (139, 69, 19))
            arcade.draw_circle_filled(cx + size * 0.35, cy + size * 0.15, size * 0.08, (139, 69, 19))
        elif fruit_type == "grape":
            arcade.draw_circle_filled(cx, cy + size * 0.2, size * 0.2, (128, 0, 128))
            arcade.draw_circle_filled(cx - size * 0.2, cy - size * 0.15, size * 0.2, (128, 0, 128))
            arcade.draw_circle_filled(cx + size * 0.2, cy - size * 0.15, size * 0.2, (128, 0, 128))
            arcade.draw_line(cx, cy + size * 0.4, cx, cy + size * 0.6, (0, 200, 0), 2)

    def _build_postgame_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.postgame_buttons = [
            {"label": "Play Again", "x": cx - 100, "y": cy - 80, "w": 160, "h": 40, "action": "replay"},
            {"label": "Quit to Lobby", "x": cx + 100, "y": cy - 80, "w": 160, "h": 40, "action": "quit"},
        ]

    def _draw_postgame_buttons(self):
        self._postgame_title.text = "Game Over" if not self.win else "You Win!"
        self._postgame_title.draw()
        for i, btn in enumerate(self.postgame_buttons):
            l, r = btn["x"] - btn["w"]//2, btn["x"] + btn["w"]//2
            b, t = btn["y"] - btn["h"]//2, btn["y"] + btn["h"]//2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_GREEN)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            txt = self._postgame_button_texts[i]
            txt.x = btn["x"]
            txt.y = btn["y"]
            txt.draw()