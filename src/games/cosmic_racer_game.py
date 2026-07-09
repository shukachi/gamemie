import arcade
import random
from src.games.base_game import BaseGame
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Константы физики
GRAVITY = 0.4
FLAP_SPEED = 7.5
PIPE_SPAWN_RATE = 100

# Цвета интерфейса в стиле остальных автоматов клуба
COLOR_MENU_BG = (20, 20, 35)
COLOR_BTN_BG = (40, 40, 70)
COLOR_BTN_OUTLINE = (255, 255, 255)
COLOR_LASER_CORE = (255, 255, 255)


class CosmicRacerGame(BaseGame):
    """Космический Flappy Bird, полностью адаптированный под стандарты Arcade Club."""

    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("CosmicRacer", machine_id, on_finish_callback)

        # Состояния строго по примеру встроенных игр: "menu", "playing", "postgame"
        self.state = "menu"
        self.difficulty = "medium"

        # Списки спрайтов
        self.player_list = arcade.SpriteList()
        self.pipe_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.bird = None

        self.game_over = False
        self.spawn_timer = 0

        # Кнопки для экранов (структура как в Сапере/Тетрисе)
        self.menu_buttons = []
        self.postgame_buttons = []
        self._build_buttons()

        # Звуковые эффекты из встроенных ресурсов
        self.jump_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.game_over_sound = arcade.load_sound(":resources:sounds/explosion1.wav")

    def _build_buttons(self):
        """Сборка геометрии кнопок для меню и финиша."""
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

    @staticmethod
    def create_laser_texture(width: int, height: int) -> arcade.Texture:
        """Программная генерация неоновой текстуры лазера с помощью Pillow."""
        from PIL import Image, ImageDraw
        if height <= 0:
            height = 1

        image = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Сглаженные неоновые слои лазерного луча
        draw.rectangle([2, 0, width - 3, height], fill=(0, 255, 100, 40))
        draw.rectangle([6, 0, width - 7, height], fill=(0, 255, 150, 120))
        draw.rectangle([12, 0, width - 13, height], fill=COLOR_LASER_CORE)

        return arcade.Texture(image)

    def on_show_view(self):
        """Вызывается при переключении на этот автомат."""
        self.state = "menu"
        self.score = 0
        self.game_over = False
        self._build_buttons()

    def _start_game(self):
        """Инициализация игрового процесса."""
        self.player_list = arcade.SpriteList()
        self.pipe_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        self.score = 0
        self.game_over = False
        self.spawn_timer = 0

        # Космический фон
        background = arcade.Sprite(":resources:images/backgrounds/stars.png")
        background.width = SCREEN_WIDTH
        background.height = SCREEN_HEIGHT
        background.center_x = SCREEN_WIDTH // 2
        background.center_y = SCREEN_HEIGHT // 2
        self.background_list.append(background)

        # Конфигурация сложности
        if self.difficulty == "easy":
            self.pipe_speed = 2.5
            self.pipe_gap = 195
        elif self.difficulty == "hard":
            self.pipe_speed = 4.5
            self.pipe_gap = 135
        else:
            self.pipe_speed = 3.5
            self.pipe_gap = 165

        # Спавн космолёта игрока
        self.bird = arcade.Sprite(":resources:images/space_shooter/playerShip3_orange.png", scale=0.5)
        self.bird.center_x = 160
        self.bird.center_y = SCREEN_HEIGHT // 2
        self.bird.change_y = 0
        self.bird.angle = 90
        self.player_list.append(self.bird)

        self.spawn_pipes()
        self.state = "playing"

    def spawn_pipes(self):
        """Генерация препятствий."""
        gap_center = random.randint(160, SCREEN_HEIGHT - 160)
        bottom_pipe_height = gap_center - (self.pipe_gap // 2)
        top_pipe_height = SCREEN_HEIGHT - gap_center - (self.pipe_gap // 2)
        pipe_width = 40

        # Нижнее препятствие
        bottom_texture = self.create_laser_texture(pipe_width, bottom_pipe_height)
        bottom_pipe = arcade.Sprite(bottom_texture)
        bottom_pipe.center_x = SCREEN_WIDTH + 50
        bottom_pipe.bottom = 0
        bottom_pipe.change_x = -self.pipe_speed
        bottom_pipe.passed = False

        # Верхнее препятствие
        top_texture = self.create_laser_texture(pipe_width, top_pipe_height)
        top_pipe = arcade.Sprite(top_texture)
        top_pipe.center_x = SCREEN_WIDTH + 50
        top_pipe.top = SCREEN_HEIGHT
        top_pipe.change_x = -self.pipe_speed

        self.pipe_list.append(bottom_pipe)
        self.pipe_list.append(top_pipe)

    def on_draw(self):
        self.clear()

        if self.state == "menu":
            self._draw_menu()
        elif self.state in ("playing", "postgame"):
            if self.background_list:
                self.background_list.draw()
            self.pipe_list.draw()
            self.player_list.draw()

            # HUD в верхнем левом углу
            arcade.draw_text(f"Score: {self.score}", 20, SCREEN_HEIGHT - 35, arcade.color.WHITE, 16, bold=True)
            arcade.draw_text(f"Difficulty: {self.difficulty.upper()}", 20, SCREEN_HEIGHT - 60, arcade.color.LIGHT_GRAY,
                             12)

            if self.state == "postgame":
                self._draw_postgame()

    def _draw_menu(self):
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
                                COLOR_MENU_BG)
        arcade.draw_text("COSMIC RACER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160, arcade.color.CYAN, 44,
                         anchor_x="center", bold=True)
        arcade.draw_text("Выберите сложность для старта сессии", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110,
                         arcade.color.WHITE, 15, anchor_x="center")

        for btn in self.menu_buttons:
            l, r = btn["x"] - btn["w"] // 2, btn["x"] + btn["w"] // 2
            b, t = btn["y"] - btn["h"] // 2, btn["y"] + btn["h"] // 2

            is_current = (self.difficulty == btn["difficulty"])
            bg_color = (60, 80, 60) if is_current else COLOR_BTN_BG

            arcade.draw_lrbt_rectangle_filled(l, r, b, t, bg_color)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, COLOR_BTN_OUTLINE, 2)
            arcade.draw_text(btn["label"].upper(), btn["x"], btn["y"], arcade.color.WHITE, 15, anchor_x="center",
                             anchor_y="center", bold=is_current)

    def _draw_postgame(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        arcade.draw_rect_filled(arcade.XYWH(cx, cy, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 160))
        arcade.draw_rect_filled(arcade.XYWH(cx, cy + 20, 420, 240), (25, 25, 40, 240))
        arcade.draw_rect_outline(arcade.XYWH(cx, cy + 20, 420, 240), arcade.color.RED, 2)

        arcade.draw_text("GAME OVER", cx, cy + 80, arcade.color.RED, 32, anchor_x="center", bold=True)
        arcade.draw_text(f"Финальный счет: {self.score}", cx, cy + 30, arcade.color.WHITE, 18, anchor_x="center")

        for btn in self.postgame_buttons:
            l, r = btn["x"] - btn["w"] // 2, btn["x"] + btn["w"] // 2
            b, t = btn["y"] - btn["h"] // 2, btn["y"] + btn["h"] // 2
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, (80, 30, 30) if btn["action"] == "quit" else (30, 70, 30))
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, COLOR_BTN_OUTLINE, 2)
            arcade.draw_text(btn["label"], btn["x"], btn["y"], arcade.color.WHITE, 14, anchor_x="center",
                             anchor_y="center")
    def on_update(self, delta_time: float):
        if self.state != "playing":
            return

        # Физика падения космолёта
        self.bird.change_y -= GRAVITY
        self.player_list.update()
        self.pipe_list.update()

        # Интервальный спавн лазеров
        self.spawn_timer += 1
        if self.spawn_timer >= PIPE_SPAWN_RATE:
            self.spawn_pipes()
            self.spawn_timer = 0

        # Коллизия с границами экрана
        if self.bird.bottom <= 0 or self.bird.top >= SCREEN_HEIGHT:
            self._handle_game_over()
            return

        # Проверка пролёта препятствий и начисление очков (list-приведение для безопасности)
        for pipe in list(self.pipe_list):
            if pipe.right < 0:
                pipe.remove_from_sprite_lists()

            if hasattr(pipe, 'passed') and not pipe.passed and pipe.center_x < self.bird.center_x:
                pipe.passed = True
                self.score += 1

        # Коллизия со стенками лазеров
        if arcade.check_for_collision_with_list(self.bird, self.pipe_list):
            self._handle_game_over()

    def _handle_game_over(self):
        arcade.play_sound(self.game_over_sound)
        self.state = "postgame"
        # Передаем набранные очки хабу клуба
        self.finish_game(completed=True)

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.finish_game(completed=False)
            return

        kb = cfg.KEY_BINDINGS
        if self.state == "playing":
            if key == kb['up'] or key == arcade.key.SPACE:
                self.bird.change_y = FLAP_SPEED
                arcade.play_sound(self.jump_sound)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.state == "menu":
            for btn in self.menu_buttons:
                if btn["x"] - btn["w"]//2 <= x <= btn["x"] + btn["w"]//2 and \
                   btn["y"] - btn["h"]//2 <= y <= btn["y"] + btn["h"]//2:
                    self.difficulty = btn["difficulty"]
                    self._start_game()
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
