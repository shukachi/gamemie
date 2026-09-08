import arcade
import random
import math
import pyglet.math as pmath
from src.games.base_game import BaseGame
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Настройки игрового поля (виртуальная сетка лабиринта)
GRID_SIZE = 40
GRID_ROWS = 13
GRID_COLS = 13

# Базовые коэффициенты физики
BOUNCE_RESTITUTION = 0.4


class NeonParticle:
    """Улучшенные частицы шлейфа с динамическим размером и закручиванием."""

    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = list(color)  # [R, G, B, A]
        self.size = size
        self.base_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.rotation_phase = random.uniform(0, math.pi * 2)

    def update(self, delta_time):
        self.rotation_phase += delta_time * 5.0
        spiral_x = math.sin(self.rotation_phase) * 0.2
        spiral_y = math.cos(self.rotation_phase) * 0.2

        self.x += self.vx + spiral_x
        self.y += self.vy + spiral_y
        self.lifetime -= delta_time

        ratio = max(0.0, self.lifetime / self.max_lifetime)
        self.size = self.base_size * ratio
        if len(self.color) >= 4:
            self.color[3] = int(255 * ratio)


class GravityGridGame(BaseGame):
    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("Gravity Grid", machine_id, on_finish_callback)
        self.state = "menu"
        self.difficulty = "medium"

        # Центрирование лабиринта
        self.field_w = GRID_COLS * GRID_SIZE
        self.field_h = GRID_ROWS * GRID_SIZE
        self.field_center_x = SCREEN_WIDTH // 2
        self.field_center_y = SCREEN_HEIGHT // 2

        # Системы частиц, тряски и анимации
        self.particles = []
        self.bg_stars = []  # Эффект глубокого космоса на бэкграунде
        self.animation_time = 0.0
        self.screen_shake = 0.0
        self.elapsed_time = 0.0
        self.time_remaining = 60.0

        self.current_rotation = 0.0
        self.target_rotation = 0.0
        self.gravity_dir = 0

        # Позиция и динамический радиус игрока
        self._player_x_val = 0.0
        self._player_y_val = 0.0
        self.player_vx = 0.0
        self.player_vy = 0.0
        self.player_radius = 14.0

        # Баланс сложности
        self.gravity_force = 0.35
        self.max_speed = 12.0
        self.chip_value = 50
        self.max_chips_on_map = 3

        # Сетка объектов (1=стена, 2=чип, 3=лазерная ловушка)
        self.grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]

        self._build_buttons()
        self._generate_bg_stars()

        # Аудиоэффекты
        self.sound_gravity = arcade.load_sound(":resources:sounds/laser1.wav")
        self.sound_collect = arcade.load_sound(":resources:sounds/coin1.wav")
        self.sound_fail = arcade.load_sound(":resources:sounds/explosion1.wav")

    def _generate_bg_stars(self):
        """Создает матрицу мерцающих звезд для создания эффекта глубины."""
        self.bg_stars.clear()
        for _ in range(45):
            self.bg_stars.append({
                "x": random.uniform(self.field_center_x - self.field_w / 2, self.field_center_x + self.field_w / 2),
                "y": random.uniform(self.field_center_y - self.field_h / 2, self.field_center_y + self.field_h / 2),
                "size": random.uniform(1.0, 2.5),
                "speed": random.uniform(0.1, 0.4),
                "alpha": random.randint(50, 180)
            })

    def _build_buttons(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.menu_buttons = [
            {"label": "Easy Grid", "difficulty": "easy", "x": cx, "y": cy + 60, "w": 220, "h": 46},
            {"label": "Medium Grid", "difficulty": "medium", "x": cx, "y": cy, "w": 220, "h": 46},
            {"label": "Hardcore Grid", "difficulty": "hard", "x": cx, "y": cy - 60, "w": 220, "h": 46},
        ]
        self.postgame_buttons = [
            {"label": "Try Again", "action": "replay", "x": cx - 110, "y": cy - 80, "w": 160, "h": 44},
            {"label": "To Lobby", "action": "quit", "x": cx + 110, "y": cy - 80, "w": 160, "h": 44},
        ]

    def on_show(self):
        self.state = "menu"
        self.score = 0
        self.elapsed_time = 0.0
        self.animation_time = 0.0

    def _spawn_single_chip_randomly(self):
        empty_cells = []
        for r in range(1, GRID_ROWS - 1):
            for c in range(1, GRID_COLS - 1):
                if self.grid[r][c] == 0:
                    empty_cells.append((r, c))

        if empty_cells:
            r, c = random.choice(empty_cells)
            self.grid[r][c] = 2

    def _generate_level(self):
        self.grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]

        if self.difficulty == "easy":
            self.player_radius = 15.0
            self.gravity_force = 0.35
            self.max_speed = 10.0
            self.chip_value = 50
            self.max_chips_on_map = 3
        elif self.difficulty == "medium":
            self.player_radius = 11.0
            self.gravity_force = 0.65
            self.max_speed = 15.0
            self.chip_value = 150
            self.max_chips_on_map = 2
        else:  # hard
            self.player_radius = 7.5
            self.gravity_force = 1.15
            self.max_speed = 22.0
            self.chip_value = 400
            self.max_chips_on_map = 1

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if r == 0 or r == GRID_ROWS - 1 or c == 0 or c == GRID_COLS - 1:
                    self.grid[r][c] = 1

        walls = [(2, 2), (2, 3), (2, 4), (2, 10), (3, 6), (4, 6), (4, 8), (5, 2), (6, 4), (6, 5), (6, 6), (6, 8),
                 (7, 10), (8, 2), (8, 3), (8, 8), (9, 6), (10, 4), (10, 8), (10, 9), (10, 10)]
        for r, c in walls:
            if r < GRID_ROWS and c < GRID_COLS:
                self.grid[r][c] = 1

        if self.difficulty in ("medium", "hard"):
            lasers = [(4, 2), (8, 10), (5, 8)]
            for r, c in lasers:
                self.grid[r][c] = 3

        if self.difficulty == "hard":
            self.grid[4][6] = 3
            self.grid[8][6] = 3

        for _ in range(self.max_chips_on_map):
            self._spawn_single_chip_randomly()

        self._player_x_val = float(self.field_center_x)
        self._player_y_val = float(self.field_center_y)
        self.player_vx = 0.0
        self.player_vy = 0.0
        self.gravity_dir = 0
        self.target_rotation = 0.0
        self.current_rotation = 0.0
        self.particles.clear()
        self._generate_bg_stars()

    def _start_game(self):
        self.score = 0
        self.elapsed_time = 0.0
        self.screen_shake = 0.0
        self._generate_level()
        self.state = "playing"

    def _resolve_grid_collisions(self):
        local_x = self._player_x_val - (self.field_center_x - self.field_w / 2)
        local_y = self._player_y_val - (self.field_center_y - self.field_h / 2)

        current_col = int(local_x // GRID_SIZE)
        current_row = int(local_y // GRID_SIZE)

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = current_row + dr
                c = current_col + dc
                if not (0 <= r < GRID_ROWS and 0 <= c < GRID_COLS):
                    continue

                cell_type = self.grid[r][c]
                if cell_type == 0:
                    continue

                cell_x = (self.field_center_x - self.field_w / 2) + c * GRID_SIZE + GRID_SIZE / 2
                cell_y = (self.field_center_y - self.field_h / 2) + r * GRID_SIZE + GRID_SIZE / 2

                closest_x = max(cell_x - GRID_SIZE / 2, min(self._player_x_val, cell_x + GRID_SIZE / 2))
                closest_y = max(cell_y - GRID_SIZE / 2, min(self._player_y_val, cell_y + GRID_SIZE / 2))

                dist_x = self._player_x_val - closest_x
                dist_y = self._player_y_val - closest_y
                distance = math.hypot(dist_x, dist_y)

                if distance < self.player_radius:
                    if cell_type == 1:  # Стены
                        if distance == 0: continue
                        overlap = self.player_radius - distance
                        nx = dist_x / distance
                        ny = dist_y / distance

                        self._player_x_val += nx * overlap
                        self._player_y_val += ny * overlap

                        dot_product = self.player_vx * nx + self.player_vy * ny
                        if dot_product < 0:
                            bounce = BOUNCE_RESTITUTION * 1.4 if self.difficulty == "hard" else BOUNCE_RESTITUTION
                            self.player_vx -= (1.0 + bounce) * dot_product * nx
                            self.player_vy -= (1.0 + bounce) * dot_product * ny
                            if math.hypot(self.player_vx, self.player_vy) > 1.5:
                                shake_add = 2.5 if self.difficulty == "hard" else 1.2
                                self.screen_shake = min(8.0, self.screen_shake + shake_add)

                    elif cell_type == 2:  # Чип
                        self.grid[r][c] = 0
                        arcade.play_sound(self.sound_collect)
                        self.score += self.chip_value

                        for _ in range(16):
                            self.particles.append(NeonParticle(
                                cell_x, cell_y, random.uniform(-5, 5), random.uniform(-5, 5),
                                (255, 230, 50, 255), random.uniform(3, 6), random.uniform(0.4, 0.9)
                            ))

                        self._spawn_single_chip_randomly()

                    elif cell_type == 3:  # Лазер
                        arcade.play_sound(self.sound_fail)
                        minus_score = 150 if self.difficulty == "hard" else 75
                        self.score = max(0, self.score - minus_score)
                        self.screen_shake = 9.0
                        self.player_vx *= -1.5
                        self.player_vy *= -1.5

    def on_update(self, delta_time: float):
        if self.state != "playing":
            return

        self.elapsed_time += delta_time
        self.animation_time += delta_time
        if self.elapsed_time >= self.time_remaining:
            self.state = "postgame"
            self.finish_game(completed=True)
            return

        if self.screen_shake > 0:
            self.screen_shake -= delta_time * 5.0
        else:
            self.screen_shake = 0.0

        self.current_rotation += (self.target_rotation - self.current_rotation) * 0.12

        # Движение фоновых звезд
        for s in self.bg_stars:
            s["y"] -= s["speed"]
            if s["y"] < self.field_center_y - self.field_h / 2:
                s["y"] = self.field_center_y + self.field_h / 2
                s["x"] = random.uniform(self.field_center_x - self.field_w / 2, self.field_center_x + self.field_w / 2)

        # Сила гравитации
        if self.gravity_dir == 0:
            self.player_vy -= self.gravity_force
        elif self.gravity_dir == 1:
            self.player_vx += self.gravity_force
        elif self.gravity_dir == 2:
            self.player_vy += self.gravity_force
        elif self.gravity_dir == 3:
            self.player_vx -= self.gravity_force

        self.player_vx = max(-self.max_speed, min(self.max_speed, self.player_vx))
        self.player_vy = max(-self.max_speed, min(self.max_speed, self.player_vy))

        # Субшаги против туннелирования
        steps = max(1, int(math.ceil(math.hypot(self.player_vx, self.player_vy) / 3.0)))
        for _ in range(steps):
            self._player_x_val += self.player_vx / steps
            self._player_y_val += self.player_vy / steps
            self._resolve_grid_collisions()

        # Пассивный спавн частиц из ядер чипов
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == 2 and random.random() < 0.08:
                    cx = (self.field_center_x - self.field_w / 2) + c * GRID_SIZE + GRID_SIZE / 2
                    cy = (self.field_center_y - self.field_h / 2) + r * GRID_SIZE + GRID_SIZE / 2
                    self.particles.append(NeonParticle(
                        cx, cy, random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6),
                        (255, 255, 100, 150), random.uniform(1.5, 3.5), random.uniform(0.5, 1.0)
                    ))

        # Генерация шлейфа за игроком
        if math.hypot(self.player_vx, self.player_vy) > 0.5:
            p_color = (255, 60, 255, 200) if self.difficulty == "hard" else (0, 240, 255, 200)
            self.particles.append(NeonParticle(
                self._player_x_val, self._player_y_val,
                -self.player_vx * 0.15 + random.uniform(-0.2, 0.2),
                -self.player_vy * 0.15 + random.uniform(-0.2, 0.2),
                p_color, random.uniform(2.5, float(self.player_radius * 0.9)), random.uniform(0.4, 0.7)
            ))

        for p in list(self.particles):
            p.update(delta_time)
            if p.lifetime <= 0:
                self.particles.remove(p)

    def on_draw(self):
        self.clear()

        if self.state == "menu":
            self._draw_menu()
            return

        shake_x = random.uniform(-self.screen_shake, self.screen_shake)
        shake_y = random.uniform(-self.screen_shake, self.screen_shake)

        arcade.get_window().current_view.view_matrix = pmath.Mat4.from_translation(pmath.Vec3(shake_x, shake_y, 0))

        # Улучшенный глубокий фон лабиринта
        bg_base = (14, 8, 22, 255) if self.difficulty == "hard" else (8, 10, 22, 255)
        arcade.draw_rect_filled(
            arcade.rect.XYWH(float(self.field_center_x), float(self.field_center_y), float(self.field_w),
                             float(self.field_h)), bg_base)

        # Отрисовка мерцающих звезд космоса
        for s in self.bg_stars:
            pulsing_alpha = int(s["alpha"] * (0.7 + math.sin(self.animation_time * 4.0 + s["x"]) * 0.3))
            arcade.draw_circle_filled(float(s["x"]), float(s["y"]), float(s["size"]),
                                      (100, 180, 255, max(10, min(255, pulsing_alpha))))

        # Анимационные фазы
        pulse_wall = float(GRID_SIZE - 2) + math.sin(self.animation_time * 6.0) * 1.5
        pulse_laser = 4.0 + math.sin(self.animation_time * 12.0) * 1.5

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cell_type = self.grid[r][c]
                x = (self.field_center_x - self.field_w / 2) + c * GRID_SIZE + GRID_SIZE / 2
                y = (self.field_center_y - self.field_h / 2) + r * GRID_SIZE + GRID_SIZE / 2

                if cell_type == 1:  # Кибер-стены
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(float(x), float(y), float(GRID_SIZE - 2), float(GRID_SIZE - 2)),
                        (18, 26, 60, 255))
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(float(x), float(y), float(GRID_SIZE - 8), float(GRID_SIZE - 8)),
                        (10, 16, 40, 255))
                    b_color = (255, 60, 80, 255) if self.difficulty == "hard" else (0, 220, 255, 255)
                    arcade.draw_rect_outline(arcade.rect.XYWH(float(x), float(y), pulse_wall, pulse_wall), b_color, 2)
                elif cell_type == 2:  # Чипы
                    rot_angle = self.animation_time * 90.0
                    arcade.draw_circle_filled(float(x), float(y), 13.0, (255, 215, 0, 45))
                    arcade.draw_rect_filled(arcade.rect.XYWH(float(x), float(y), 10.0, 10.0), (255, 255, 120, 255),
                                            tilt_angle=rot_angle)
                    arcade.draw_circle_filled(float(x), float(y), 3.5, (255, 255, 255, 255))
                elif cell_type == 3:  # Лазеры
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(float(x), float(y), float(GRID_SIZE), float(pulse_laser * 2.0)),
                        (255, 0, 50, 45))
                    arcade.draw_rect_filled(arcade.rect.XYWH(float(x), float(y), float(GRID_SIZE), 8.0),
                                            (255, 0, 0, 140))
                    arcade.draw_rect_filled(arcade.rect.XYWH(float(x), float(y), float(GRID_SIZE), 2.5),
                                            (255, 230, 230, 255))

        # Отрисовка частиц
        for p in self.particles:
            col_tuple = (int(p.color[0]), int(p.color[1]), int(p.color[2]), int(p.color[3]))
            arcade.draw_circle_filled(float(p.x), float(p.y), float(p.size), col_tuple)

        # Игрок
        r, g, b = (255, 0, 255) if self.difficulty == "hard" else (0, 255, 255)
        arcade.draw_circle_filled(float(self._player_x_val), float(self._player_y_val), self.player_radius * 1.7,
                                  (r, g, b, 50))
        arcade.draw_circle_filled(float(self._player_x_val), float(self._player_y_val), self.player_radius * 1.15,
                                  (r, g, b, 150))
        arcade.draw_circle_filled(float(self._player_x_val), float(self._player_y_val),
                                  max(3.0, self.player_radius * 0.6), (255, 255, 255, 255))

        arcade.get_window().current_view.view_matrix = pmath.Mat4()

        # UI Панель
        arcade.draw_text(f"SCORE: {self.score}", 40.0, float(SCREEN_HEIGHT - 50), arcade.color.NEON_GREEN, 22,
                         bold=True, font_name="Impact")
        arcade.draw_text(f"TIME: {max(0.0, self.time_remaining - self.elapsed_time):.1f}s", float(SCREEN_WIDTH - 280),
                         float(SCREEN_HEIGHT - 50), arcade.color.CYAN, 18, bold=True)

        arr = ["ВНИЗ ↓", "ВПРАВО →", "ВВЕРХ ↑", "ВЛЕВО ←"][self.gravity_dir]
        arcade.draw_text(f"GRAVITY: {arr} (x{self.gravity_force:.2f})", 40.0, float(SCREEN_HEIGHT - 90),
                         arcade.color.ORANGE, 15, bold=True)
        arcade.draw_text(f"CHIP VALUE: +{self.chip_value} pts", 40.0, float(SCREEN_HEIGHT - 120), arcade.color.YELLOW,
                         12, bold=True)

        if self.state == "postgame":
            self._draw_postgame()

    def _draw_menu(self):
        arcade.draw_rect_filled(
            arcade.rect.XYWH(float(SCREEN_WIDTH // 2), float(SCREEN_HEIGHT // 2), float(SCREEN_WIDTH),
                             float(SCREEN_HEIGHT)), (15, 10, 25))
        arcade.draw_text("GRAVITY GRID", float(SCREEN_WIDTH // 2), float(SCREEN_HEIGHT // 2 + 160), arcade.color.CYAN,
                         52, anchor_x="center", bold=True, font_name="Impact")
        arcade.draw_text("Улучшенная неоновая графика и динамический космос!", float(SCREEN_WIDTH // 2),
                         float(SCREEN_HEIGHT // 2 + 110), arcade.color.LIGHT_GRAY, 14, anchor_x="center")

        for btn in self.menu_buttons:
            l, r = btn["x"] - btn["w"] // 2, btn["x"] + btn["w"] // 2
            b, t = btn["y"] - btn["h"] // 2, btn["y"] + btn["h"] // 2
            is_current = (self.difficulty == btn["difficulty"])
            arcade.draw_lrbt_rectangle_filled(float(l), float(r), float(b), float(t),
                                              (60, 40, 80) if is_current else (30, 25, 45))
            arcade.draw_lrbt_rectangle_outline(float(l), float(r), float(b), float(t), arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"].upper(), float(btn["x"]), float(btn["y"]), arcade.color.WHITE, 14,
                             anchor_x="center", anchor_y="center", bold=is_current)

    def _draw_postgame(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        arcade.draw_rect_filled(arcade.rect.XYWH(float(cx), float(cy), float(SCREEN_WIDTH), float(SCREEN_HEIGHT)),
                                (0, 0, 0, 180))
        arcade.draw_rect_filled(arcade.rect.XYWH(float(cx), float(cy + 20), 440.0, 240.0), (20, 15, 30, 240))
        arcade.draw_rect_outline(arcade.rect.XYWH(float(cx), float(cy + 20), 440.0, 240.0), arcade.color.NEON_GREEN, 2)

        arcade.draw_text("СЕССИЯ ОКОНЧЕНА", float(cx), float(cy + 80), arcade.color.YELLOW, 28, anchor_x="center",
                         bold=True)
        arcade.draw_text(f"Итоговый счет: {self.score}", float(cx), float(cy + 25), arcade.color.WHITE, 18,
                         anchor_x="center")

        for btn in self.postgame_buttons:
            l, r = btn["x"] - btn["w"] // 2, btn["x"] + btn["w"] // 2
            b, t = btn["y"] - btn["h"] // 2, btn["y"] + btn["h"] // 2
            is_current = (self.difficulty == btn["difficulty"])
            arcade.draw_lrbt_rectangle_filled(float(l), float(r), float(b), float(t),
                                              (30, 65, 45) if btn["action"] == "replay" else (75, 30, 35))
            arcade.draw_lrbt_rectangle_outline(float(l), float(r), float(b), float(t), arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], float(btn["x"]), float(btn["y"]), arcade.color.WHITE, 14, anchor_x="center",
                             anchor_y="center")

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.finish_game(completed=False)
            return

        if self.state != "playing":
            return

        kb = cfg.KEY_BINDINGS
        old_dir = self.gravity_dir

        if key == kb['down']:
            self.gravity_dir = 0
            self.target_rotation = 0.0
        elif key == kb['right']:
            self.gravity_dir = 1
            self.target_rotation = 90.0
        elif key == kb['up']:
            self.gravity_dir = 2
            self.target_rotation = 180.0
        elif key == kb['left']:
            self.gravity_dir = 3
            self.target_rotation = 270.0

        if old_dir != self.gravity_dir:
            arcade.play_sound(self.sound_gravity)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.state == "menu":
            for btn in self.menu_buttons:
                if btn["x"] - btn["w"] // 2 <= x <= btn["x"] + btn["w"] // 2 and \
                        btn["y"] - btn["h"] // 2 <= y <= btn["y"] + btn["h"] // 2:
                    self.difficulty = btn["difficulty"]
                    self._start_game()
                    break
        elif self.state == "postgame":
            for btn in self.postgame_buttons:
                if btn["x"] - btn["w"] // 2 <= x <= btn["x"] + btn["w"] // 2 and \
                        btn["y"] - btn["h"] // 2 <= y <= btn["y"] + btn["h"] // 2:
                    if btn["action"] == "replay":
                        self._start_game()
                    elif btn["action"] == "quit":
                        self.finish_game(False)
                        break
