import arcade
import random
import math
from PIL import Image, ImageDraw, ImageFilter
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Базовые константы гонки
MAX_SPEED = 11
ACCELERATION = 0.15
FRICTION = 0.5
CRITICAL_SPEED = 10
TOTAL_LAPS = 5

TRACK_CENTER_X = 500
TRACK_CENTER_Y = 300
STRAIGHT_LENGTH = 300
BASE_RADIUS = 120
LANE_DISTANCE = 30

LANE_COLORS = [
    arcade.color.HOT_PINK,
    arcade.color.CYAN,
    arcade.color.PURPLE,
    arcade.color.NEON_GREEN
]


class Car:
    """Логика движения и физики болида (игрока и ботов)."""
    def __init__(self, start_lane, is_bot=False, bot_color=arcade.color.WHITE, difficulty="medium"):
        self.base_lane = start_lane
        self.current_lane = start_lane
        self.is_bot = is_bot
        self.color = bot_color if is_bot else arcade.color.NEON_GREEN
        self.distance = STRAIGHT_LENGTH / 2
        self.speed = 0.0
        self.lap = 0
        self.stun_timer = 0.0
        self.is_stunned = False
        self.finished = False
        self.x = 0
        self.y = 0
        self.angle = 0.0

        if difficulty == "easy":
            self.bot_target_speed = MAX_SPEED * random.uniform(0.7, 0.75)
            self.max_stun_time = 1.0
        elif difficulty == "hard":
            self.bot_target_speed = MAX_SPEED * random.uniform(1.0, 1.05)
            self.max_stun_time = 0.09
        else:
            self.bot_target_speed = MAX_SPEED * random.uniform(0.85, 0.95)
            self.max_stun_time = 0.3

        if not is_bot:
            self.max_stun_time = 1.0

    def update(self, delta_time, is_pressing_space, total_length):
        if self.is_stunned:
            self.stun_timer -= delta_time
            if self.stun_timer <= 0:
                self.is_stunned = False
            return

        if self.is_bot:
            gas = self.speed < self.bot_target_speed
        else:
            gas = is_pressing_space

        if gas:
            self.speed += ACCELERATION
            if self.speed > MAX_SPEED:
                self.speed = MAX_SPEED
        else:
            self.speed -= FRICTION
            if self.speed < 0:
                self.speed = 0

        if not self.finished:
            self.distance += self.speed

        in_turn = abs(self.x - TRACK_CENTER_X) > (STRAIGHT_LENGTH / 2)

        if in_turn and self.speed > CRITICAL_SPEED:
            self.is_stunned = True
            self.stun_timer = self.max_stun_time
            self.speed = 0.0
            return

        if self.distance >= total_length:
            self.distance -= total_length
            self.lap += 1
            if self.lap >= TOTAL_LAPS:
                self.finished = True
            else:
                self.current_lane = (self.base_lane - self.lap) % 4


class CosmicRacersGame(BaseGame):
    """Кольцевые гонки на удержание скорости, полностью адаптированные под хаб."""

    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("Cosmic Racers", machine_id, on_finish_callback)
        self.difficulty = "medium"
        self.state = "menu"  # "menu", "playing", "postgame"

        self.is_space_pressed = False
        self.cars = []
        self.leaderboard_list = []
        self.game_active = True

        self.hover_play = False
        self.car_sprites = {}
        self.draw_list = None
        self.background_list = None

        self._build_buttons()

    def create_abstract_texture(self) -> arcade.Texture:
        """Программно генерирует дымчатый синий градиентный фон в памяти."""
        image = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 30, 80, 255))
        draw = ImageDraw.Draw(image)
        for _ in range(25):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            r = random.randint(150, 350)
            color = (random.randint(0, 50), random.randint(100, 200), random.randint(180, 255), 40)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        blurred_image = image.filter(ImageFilter.GaussianBlur(30))
        return arcade.Texture(blurred_image)

    def _build_buttons(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.menu_buttons = [
            {"label": "Easy", "difficulty": "easy", "x": cx, "y": cy + 60, "w": 200, "h": 46},
            {"label": "Medium", "difficulty": "medium", "x": cx, "y": cy, "w": 200, "h": 46},
            {"label": "Hard", "difficulty": "hard", "x": cx, "y": cy - 60, "w": 200, "h": 46},
        ]
        self.postgame_buttons = [
            {"label": "Play Again", "action": "replay", "x": cx - 110, "y": cy - 80, "w": 160, "h": 44},
            {"label": "Quit to Lobby", "action": "quit", "x": cx + 110, "y": cy - 80, "w": 160, "h": 44},
        ]

    def on_show_view(self):
        self.state = "menu"
        self.score = 0
        self.game_active = True
        self.leaderboard_list = []

    def _start_game(self):
        self.is_space_pressed = False
        self.leaderboard_list = []
        self.game_active = True
        self.draw_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        # Создаем и добавляем процедурный дымчатый фон
        bg_texture = self.create_abstract_texture()
        bg_sprite = arcade.Sprite(bg_texture)
        bg_sprite.center_x = SCREEN_WIDTH // 2
        bg_sprite.center_y = SCREEN_HEIGHT // 2
        self.background_list.append(bg_sprite)

        self.cars = [
            Car(start_lane=3, is_bot=False, difficulty=self.difficulty),
            Car(start_lane=2, is_bot=True, bot_color=arcade.color.ORANGE, difficulty=self.difficulty),
            Car(start_lane=1, is_bot=True, bot_color=arcade.color.BLUE, difficulty=self.difficulty),
            Car(start_lane=0, is_bot=True, bot_color=arcade.color.RED, difficulty=self.difficulty)
        ]

        self.car_sprites = {}
        for car in self.cars:
            sprite = arcade.Sprite(":resources:images/space_shooter/playerShip3_orange.png", scale=0.5)
            sprite.color = car.color
            self.car_sprites[car] = sprite
            self.draw_list.append(sprite)

        self.state = "playing"

    def on_draw(self):
        self.clear()

        if self.state == "menu":
            self._draw_menu()
        elif self.state in ("playing", "postgame"):
            if self.background_list:
                self.background_list.draw()

            # Отрисовка неоновых линий трассы
            for i in range(4):
                radius = BASE_RADIUS + i * LANE_DISTANCE
                lane_color = LANE_COLORS[i]
                arcade.draw_line(TRACK_CENTER_X - STRAIGHT_LENGTH // 2, TRACK_CENTER_Y + radius,
                                 TRACK_CENTER_X + STRAIGHT_LENGTH // 2, TRACK_CENTER_Y + radius, lane_color, 3)
                arcade.draw_line(TRACK_CENTER_X - STRAIGHT_LENGTH // 2, TRACK_CENTER_Y - radius,
                                 TRACK_CENTER_X + STRAIGHT_LENGTH // 2, TRACK_CENTER_Y - radius, lane_color, 3)
                arcade.draw_arc_outline(TRACK_CENTER_X + STRAIGHT_LENGTH // 2, TRACK_CENTER_Y, radius * 2, radius * 2,
                                        lane_color, -90, 90, 4)
                arcade.draw_arc_outline(TRACK_CENTER_X - STRAIGHT_LENGTH // 2, TRACK_CENTER_Y, radius * 2, radius * 2,
                                        lane_color, 90, 270, 4)

            # Белая финишная линия
            arcade.draw_line(TRACK_CENTER_X + STRAIGHT_LENGTH // 2, TRACK_CENTER_Y + BASE_RADIUS - 15,
                             TRACK_CENTER_X + STRAIGHT_LENGTH // 2, TRACK_CENTER_Y + BASE_RADIUS + 4 * LANE_DISTANCE,
                             arcade.color.WHITE, 5)

            if self.draw_list:
                self.draw_list.draw()

            # Вывод интерфейса (HUD) гонки
            player_car = self.cars[0]
            arcade.draw_text(f"Круг: {min(player_car.lap + 1, TOTAL_LAPS)}/{TOTAL_LAPS}", 20, SCREEN_HEIGHT - 40,
                             arcade.color.WHITE, 16, bold=True)
            arcade.draw_text(f"Скорость: {player_car.speed:.1f} / Предел: {CRITICAL_SPEED}", 20, SCREEN_HEIGHT - 70,
                             arcade.color.WHITE, 16)

            if player_car.speed > CRITICAL_SPEED and not player_car.is_stunned:
                arcade.draw_text("ТОРМОЗИ! СЛИШКОМ БЫСТРО!", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, arcade.color.RED,
                                 18, anchor_x="center", bold=True)
            if player_car.is_stunned:
                arcade.draw_text("СТАН! ПОТЕРЯ КОНТРОЛЯ!", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, arcade.color.ORANGE,
                                 20, anchor_x="center", bold=True)

            if self.state == "postgame":
                self._draw_postgame()

    def _draw_menu(self):
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
                                (20, 20, 35))
        arcade.draw_text("COSMIC RACERS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160, arcade.color.WHITE, 44,
                         anchor_x="center", bold=True)
        arcade.draw_text("Выберите сложность для старта гонки", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110,
                         arcade.color.LIGHT_GRAY, 15, anchor_x="center")

        for btn in self.menu_buttons:
            l, r = btn["x"] - btn["w"] // 2, btn["x"] + btn["w"] // 2
            b, t = btn["y"] - btn["h"] // 2, btn["y"] + btn["h"] // 2
            is_current = (self.difficulty == btn["difficulty"])
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, (60, 80, 60) if is_current else (40, 40, 70))
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"].upper(), btn["x"], btn["y"], arcade.color.WHITE, 15, anchor_x="center",
                             anchor_y="center", bold=is_current)

    def _draw_postgame(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        arcade.draw_rect_filled(arcade.XYWH(cx, cy, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 160))
        arcade.draw_rect_filled(arcade.XYWH(cx, cy + 20, 450, 280), (25, 25, 40, 240))
        arcade.draw_rect_outline(arcade.XYWH(cx, cy + 20, 450, 280), arcade.color.WHITE, 2)
        arcade.draw_text("ЗАЕЗД ЗАВЕРШЕН", cx, cy + 110, arcade.color.YELLOW, 26, anchor_x="center", bold=True)

        for idx, car in enumerate(self.leaderboard_list):
            name = "ВЫ (Игрок)" if not car.is_bot else f"Истребитель {idx + 1}"
            arcade.draw_text(f"{idx + 1}. {name}", cx, cy + 50 - (idx * 30), car.color, 16, anchor_x="center")

        for btn in self.postgame_buttons:
            l, r = btn["x"] - btn["w"] // 2, btn["x"] + btn["w"] // 2
            b, t = btn["y"] - btn["h"] // 2, btn["y"] + btn["h"] // 2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, (80, 30, 30) if btn["action"] == "quit" else (30, 70, 30))
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 14, anchor_x="center",
                             anchor_y="center")

    def on_update(self, delta_time: float):
        if self.state != "playing" or not self.game_active:
            return

        all_finished = True
        for car in self.cars:
            radius_car = BASE_RADIUS + car.current_lane * LANE_DISTANCE
            semi_circle = math.pi * radius_car
            total_length = STRAIGHT_LENGTH * 2 + semi_circle * 2

            l_top = STRAIGHT_LENGTH / 2
            l_turn1 = semi_circle
            l_bottom = STRAIGHT_LENGTH
            l_turn2 = l_turn1
            d = car.distance

            # Исправленный расчет тригонометрических углов и траектории из оригинального кода
            if d < l_top:
                car.x = TRACK_CENTER_X + d
                car.y = TRACK_CENTER_Y + radius_car
                car.angle = 180 - 90
            elif d < l_top + l_turn1:
                progress = (d - l_top) / l_turn1
                angle_rad = progress * math.pi
                car.x = TRACK_CENTER_X + (STRAIGHT_LENGTH / 2) + radius_car * math.sin(angle_rad)
                car.y = TRACK_CENTER_Y + radius_car * math.cos(angle_rad)
                car.angle = 180 + math.degrees(angle_rad) - 90
            elif d < l_top + l_turn1 + l_bottom:
                progress_dist = d - (l_top + l_turn1)
                car.x = TRACK_CENTER_X + (STRAIGHT_LENGTH / 2) - progress_dist
                car.y = TRACK_CENTER_Y - radius_car
                car.angle = 0 - 90
            elif d < l_top + l_turn1 + l_bottom + l_turn2:
                progress = (d - (l_top + l_turn1 + l_bottom)) / l_turn2
                angle_rad = progress * math.pi
                car.x = TRACK_CENTER_X - (STRAIGHT_LENGTH / 2) - radius_car * math.sin(angle_rad)
                car.y = TRACK_CENTER_Y - radius_car * math.cos(angle_rad)
                car.angle = math.degrees(angle_rad) - 90
            else:
                progress_dist = d - (l_top + l_turn1 + l_bottom + l_turn2)
                car.x = TRACK_CENTER_X - (STRAIGHT_LENGTH / 2) + progress_dist
                car.y = TRACK_CENTER_Y + radius_car
                car.angle = 180 - 90

            car.update(delta_time, self.is_space_pressed, total_length)

            if car in self.car_sprites:
                sprite = self.car_sprites[car]
                sprite.center_x = car.x
                sprite.center_y = car.y
                sprite.angle = car.angle
                sprite.alpha = 100 if car.is_stunned and int(car.stun_timer * 10) % 2 == 0 else 255

            if car.finished and car not in self.leaderboard_list:
                self.leaderboard_list.append(car)
            if not car.finished:
                all_finished = False

        if all_finished:
            self.game_active = False
            self.state = "postgame"

            player = self.cars[0]
            rank = self.leaderboard_list.index(player) if player in self.leaderboard_list else 3
            self.score = max(0, 1000 - rank * 300)
            self.finish_game(completed=True)

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

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.finish_game(completed=False)
            return

        if self.state == "playing":
            if key == arcade.key.SPACE:
                self.is_space_pressed = True

    def on_key_release(self, key: int, modifiers: int):
        if self.state == "playing":
            if key == arcade.key.SPACE:
                self.is_space_pressed = False
