import arcade
import random
import math
from src.games.base_game import BaseGame
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Внутренние константы и состояния автомата
GROUND_HEIGHT = 50
STATE_MENU = 0
STATE_GAME = 1
STATE_GAME_OVER = 2

PLAYER_SPEED = 9



class FallingItem(arcade.Sprite):
    """Класс для всех полезных падающих предметов (монет, звезд, ключей)."""
    def __init__(self, item_type: str, filename: str, scale: float = 0.5):
        super().__init__(filename, scale=scale)
        self.item_type = item_type  # "bronze", "star", "key", "gold"


class Meteor(arcade.Sprite):
    """Класс для опасных метеоритов со случайной графикой и вращением."""
    def __init__(self, scale: float = 0.5):
        meteor_images = [
            ":resources:images/space_shooter/meteorGrey_big1.png",
            ":resources:images/space_shooter/meteorGrey_big2.png",
            ":resources:images/space_shooter/meteorGrey_big3.png",
            ":resources:images/space_shooter/meteorGrey_big4.png"
        ]
        chosen_img = random.choice(meteor_images)
        super().__init__(chosen_img, scale=scale)
        self.rotation_speed = random.uniform(-3, 3)

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self.angle += self.rotation_speed
class CoineaterGame(BaseGame):
    """Игра Coineater, полностью интегрированная в экосистему Arcade Club."""

    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("Coineater", machine_id, on_finish_callback)
        self.difficulty = "medium"
        self.state = STATE_MENU

        self.hover_start = False
        self.hover_easy = False
        self.hover_medium = False
        self.hover_hard = False

        # Списки спрайтов
        self.background_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        self.meteor_list = arcade.SpriteList()
        self.gui_sprites = arcade.SpriteList()

        self.player = None
        self.lives = 3

        # Параметры режима "Золотой Лихорадки"
        self.gold_mode_timer = 0.0
        self.is_gold_mode = False
        self.hurt_timer = 0.0

        # Предзагрузка встроенных звуков
        self.sound_coin_bronze = arcade.load_sound(":resources:sounds/coin5.wav")
        self.sound_coin_star = arcade.load_sound(":resources:sounds/coin3.wav")
        self.sound_coin_key = arcade.load_sound(":resources:sounds/coin1.wav")
        self.sound_coin_gold = arcade.load_sound(":resources:sounds/coin2.wav")
        self.sound_hurt = arcade.load_sound(":resources:sounds/hurt3.wav")
        self.sound_gameover = arcade.load_sound(":resources:sounds/gameover3.wav")

        # Оптимизация текста под требования хаба
        self.ui_texts = {
            "title": arcade.Text("COINEATER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140, (22, 175, 130, 255), 64, font_name="Arial Black", anchor_x="center", bold=True),
            "start": arcade.Text("НАЖМИТЕ 'E' ИЛИ КЛИКНИТЕ ДЛЯ СТАРТА", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, (150, 150, 150, 255), 18, font_name="Impact", anchor_x="center"),
            "diff_label": arcade.Text("ВЫБЕРИТЕ СЛОЖНОСТЬ:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, (211, 211, 211, 255), 14, font_name="Arial", anchor_x="center", bold=True),
            "easy": arcade.Text("EASY", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 140, (255, 255, 255, 255), 24, font_name="Impact", anchor_x="center"),
            "medium": arcade.Text("MEDIUM", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140, (255, 255, 255, 255), 24, font_name="Impact", anchor_x="center"),
            "hard": arcade.Text("HARD", SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 140, (255, 255, 255, 255), 24, font_name="Impact", anchor_x="center"),
            "score": arcade.Text("0", 75, SCREEN_HEIGHT - 60, (40, 255, 180, 255), 34, font_name="Arial Black", bold=True),
            "lives": arcade.Text("", float(SCREEN_WIDTH - 40), float(SCREEN_HEIGHT - 50), (255, 255, 255, 255), 20, font_name="Arial Black", anchor_x="right", bold=True),
            "gold_rush": arcade.Text("", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 55, (255, 215, 0, 255), 22, font_name="Impact", anchor_x="center"),
            "game_over": arcade.Text("ИГРА ОКОНЧЕНА", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, (255, 100, 100, 255), 52, font_name="Arial Black", anchor_x="center", bold=True),
            "final_score": arcade.Text("", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10, (255, 255, 255, 255), 24, font_name="Impact", anchor_x="center"),
            "restart": arcade.Text("НАЖМИТЕ 'R' ДЛЯ СБРОСА / ESC ДЛЯ ВЫХОДА", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, (211, 211, 211, 255), 16, font_name="Arial", anchor_x="center", bold=True)
        }

        self.fall_speed = 6.8
        self.spawn_cooldown = 0.85
        self.max_x_step = 240
        self.star_chance = 8
        self.key_chance = 3
        self.meteor_chance = 20

        self.spawn_timer = 0.0
        self.last_item_x = SCREEN_WIDTH // 2
        self.left_pressed = False
        self.right_pressed = False

        self.generate_pixel_background()

    def generate_pixel_background(self):
        """Создает процедурный пиксельный градиент."""
        self.background_list = arcade.SpriteList()
        pixel_size = 25
        for y in range(0, SCREEN_HEIGHT, pixel_size):
            for x in range(0, SCREEN_WIDTH, pixel_size):
                height_ratio = y / SCREEN_HEIGHT
                base_g = int(50 + height_ratio * 40)
                noise = random.randint(-12, 12)
                g = max(20, min(140, base_g + noise))
                r = max(5, min(40, int(g * 0.3)))
                b = max(10, min(65, int(g * 0.5)))

                pixel = arcade.SpriteSolidColor(pixel_size, pixel_size, color=(r, g, b, 255))
                pixel.center_x = float(x + pixel_size / 2)
                pixel.center_y = float(y + pixel_size / 2)
                self.background_list.append(pixel)

    def on_show_view(self):
        self.state = STATE_MENU
        self.score = 0
        self.left_pressed = False
        self.right_pressed = False

    def setup_game(self):
        """Инициализация или перезапуск игры под выбранную сложность."""
        self.player_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        self.meteor_list = arcade.SpriteList()
        self.gui_sprites = arcade.SpriteList()

        self.score = 0
        self.spawn_timer = 0.0
        self.gold_mode_timer = 0.0
        self.hurt_timer = 0.0
        self.is_gold_mode = False
        self.last_item_x = SCREEN_WIDTH // 2

        if self.difficulty == "easy":
            self.lives = 3
            self.fall_speed = 4.5
            self.spawn_cooldown = 1.2
            self.max_x_step = 350
            self.star_chance = 15
            self.key_chance = 6
            self.meteor_chance = 12
        elif self.difficulty == "medium":
            self.lives = 2
            self.fall_speed = 6.8
            self.spawn_cooldown = 0.85
            self.max_x_step = 240
            self.star_chance = 8
            self.key_chance = 3
            self.meteor_chance = 22
        else:  # hard
            self.lives = 1
            self.fall_speed = 9.5
            self.spawn_cooldown = 0.55
            self.max_x_step = 160
            self.star_chance = 3
            self.key_chance = 1
            self.meteor_chance = 35

        self.player = arcade.Sprite(":resources:images/enemies/slimeBlock.png", scale=0.75)
        self.player.center_x = float(SCREEN_WIDTH // 2)
        self.player.bottom = float(GROUND_HEIGHT)
        self.player.color = arcade.color.PURPLE_HEART
        self.player_list.append(self.player)

        coin_icon = arcade.Sprite(":resources:images/items/coinSilver.png", scale=0.5)
        coin_icon.center_x = 45.0
        coin_icon.center_y = float(SCREEN_HEIGHT - 45)
        self.gui_sprites.append(coin_icon)
    def spawn_object(self):
        """Генерация предметов на основе весов и шансов сложности."""
        min_x = max(40, self.last_item_x - self.max_x_step)
        max_x = min(SCREEN_WIDTH - 40, self.last_item_x + self.max_x_step)
        obj_x = random.randint(int(min_x), int(max_x))
        self.last_item_x = obj_x

        roll = random.randint(1, 100)

        if roll <= self.meteor_chance:
            meteor = Meteor(scale=0.5)
            meteor.center_x = float(obj_x)
            meteor.top = float(SCREEN_HEIGHT + 40)
            meteor.change_y = -self.fall_speed
            self.meteor_list.append(meteor)
            return

        item_roll = random.randint(1, 100)

        if item_roll <= self.key_chance:
            item = FallingItem("key", ":resources:images/items/keyYellow.png", scale=0.6)
        elif item_roll <= self.key_chance + self.star_chance:
            item = FallingItem("star", ":resources:images/items/star.png", scale=0.6)
        else:
            if self.is_gold_mode:
                item = FallingItem("gold", ":resources:images/items/coinGold.png", scale=0.6)
            else:
                item = FallingItem("bronze", ":resources:images/items/coinBronze.png", scale=0.6)

        item.center_x = float(obj_x)
        item.top = float(SCREEN_HEIGHT + 40)
        item.change_y = -self.fall_speed
        self.item_list.append(item)

    def on_draw(self):
        self.clear()

        # Отрисовка игрового мира
        self.background_list.draw()

        arcade.draw_rect_filled(
            arcade.rect.XYWH(float(SCREEN_WIDTH // 2), float(GROUND_HEIGHT // 2), float(SCREEN_WIDTH),
                             float(GROUND_HEIGHT)),
            color=(30, 160, 120, 255)
        )

        if self.state == STATE_MENU:
            self.ui_texts["title"].draw()
            self.ui_texts["start"].color = (255, 255, 255, 255) if self.hover_start else (150, 150, 150, 255)
            self.ui_texts["start"].draw()
            self.ui_texts["diff_label"].draw()

            self.ui_texts["easy"].color = (255, 230, 100, 255) if self.hover_easy else (
                (255, 255, 255, 255) if self.difficulty == "easy" else (120, 120, 120, 255))
            self.ui_texts["easy"].bold = (self.difficulty == "easy")
            self.ui_texts["easy"].draw()

            self.ui_texts["medium"].color = (255, 230, 100, 255) if self.hover_medium else (
                (255, 255, 255, 255) if self.difficulty == "medium" else (120, 120, 120, 255))
            self.ui_texts["medium"].bold = (self.difficulty == "medium")
            self.ui_texts["medium"].draw()

            self.ui_texts["hard"].color = (255, 230, 100, 255) if self.hover_hard else (
                (255, 255, 255, 255) if self.difficulty == "hard" else (120, 120, 120, 255))
            self.ui_texts["hard"].bold = (self.difficulty == "hard")
            self.ui_texts["hard"].draw()

        elif self.state == STATE_GAME:
            self.item_list.draw()
            self.meteor_list.draw()
            self.player_list.draw()
            self.gui_sprites.draw()

            self.ui_texts["score"].text = f"{self.score}"
            self.ui_texts["score"].draw()

            self.ui_texts["lives"].text = "❤️ " * max(0, self.lives)
            self.ui_texts["lives"].draw()

            if self.is_gold_mode:
                self.ui_texts["gold_rush"].text = f"GOLD RUSH: {math.ceil(self.gold_mode_timer)}s"
                self.ui_texts["gold_rush"].draw()

        elif self.state == STATE_GAME_OVER:
            self.ui_texts["game_over"].draw()
            self.ui_texts["final_score"].text = f"FINAL SCORE: {self.score}"
            self.ui_texts["final_score"].draw()
            self.ui_texts["restart"].draw()
    def on_update(self, delta_time: float):
        if self.state != STATE_GAME:
            return

        # Управление на основе KEY_BINDINGS из конфигурации хаба лобби
        if self.left_pressed and not self.right_pressed:
            self.player.center_x -= PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player.center_x += PLAYER_SPEED

        if self.player.left < 0:
            self.player.left = 0.0
        if self.player.right > SCREEN_WIDTH:
            self.player.right = float(SCREEN_WIDTH)

        self.item_list.update()
        self.meteor_list.update()

        if self.hurt_timer > 0:
            self.hurt_timer -= delta_time
            if self.hurt_timer <= 0:
                self.player.color = arcade.color.PURPLE_HEART

        if self.is_gold_mode:
            self.gold_mode_timer -= delta_time
            if self.gold_mode_timer <= 0:
                self.is_gold_mode = False
                for item in self.item_list:
                    if item.item_type == "gold":
                        item.item_type = "bronze"
                        item.texture = arcade.load_texture(":resources:images/items/coinBronze.png")

        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_cooldown:
            self.spawn_object()
            self.spawn_timer = 0.0

        # Коллизии с полезными вещами
        hit_items = arcade.check_for_collision_with_list(self.player, self.item_list)
        for item in hit_items:
            if item.item_type == "key":
                arcade.play_sound(self.sound_coin_key)
                self.is_gold_mode = True
                self.gold_mode_timer = 15.0
                for screen_item in self.item_list:
                    if screen_item.item_type == "bronze":
                        screen_item.item_type = "gold"
                        screen_item.texture = arcade.load_texture(":resources:images/items/coinGold.png")
            elif item.item_type == "star":
                arcade.play_sound(self.sound_coin_star)
                self.score += 20
            elif item.item_type == "gold":
                arcade.play_sound(self.sound_coin_gold)
                self.score += 5
            else:
                arcade.play_sound(self.sound_coin_bronze)
                self.score += 1

            item.remove_from_sprite_lists()

        # Коллизии с метеоритами
        hit_meteors = arcade.check_for_collision_with_list(self.player, self.meteor_list)
        for meteor in hit_meteors:
            meteor.remove_from_sprite_lists()
            self.lives -= 1

            if self.lives <= 0:
                arcade.play_sound(self.sound_gameover)
                self.state = STATE_GAME_OVER
                self.finish_game(completed=True)
            else:
                arcade.play_sound(self.sound_hurt)
                self.player.color = arcade.color.RED
                self.hurt_timer = 0.2

        # Пропуск монет под землю
        for item in list(self.item_list):
            if item.bottom <= GROUND_HEIGHT:
                if item.item_type in ("bronze", "gold"):
                    self.lives -= 1

                    if self.lives <= 0:
                        arcade.play_sound(self.sound_gameover)
                        self.state = STATE_GAME_OVER
                        self.finish_game(completed=True)
                    else:
                        arcade.play_sound(self.sound_hurt)
                        self.player.color = arcade.color.RED
                        self.hurt_timer = 0.2

                item.remove_from_sprite_lists()

        for meteor in list(self.meteor_list):
            if meteor.bottom <= GROUND_HEIGHT:
                meteor.remove_from_sprite_lists()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.state != STATE_MENU:
            return
        self.hover_start = (SCREEN_WIDTH // 2 - 200 <= x <= SCREEN_WIDTH // 2 + 200) and (
                    SCREEN_HEIGHT // 2 - 10 <= y <= SCREEN_HEIGHT // 2 + 30)

        if SCREEN_HEIGHT // 2 - 160 <= y <= SCREEN_HEIGHT // 2 - 110:
            self.hover_easy = (SCREEN_WIDTH // 2 - 210 <= x <= SCREEN_WIDTH // 2 - 90)
            self.hover_medium = (SCREEN_WIDTH // 2 - 60 <= x <= SCREEN_WIDTH // 2 + 60)
            self.hover_hard = (SCREEN_WIDTH // 2 + 90 <= x <= SCREEN_WIDTH // 2 + 210)
        else:
            self.hover_easy = self.hover_medium = self.hover_hard = False

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.state != STATE_MENU:
            return
        if self.hover_start:
            self.setup_game()
            self.state = STATE_GAME
        elif SCREEN_HEIGHT // 2 - 160 <= y <= SCREEN_HEIGHT // 2 - 110:
            if SCREEN_WIDTH // 2 - 210 <= x <= SCREEN_WIDTH // 2 - 90:
                self.difficulty = "easy"
            elif SCREEN_WIDTH // 2 - 60 <= x <= SCREEN_WIDTH // 2 + 60:
                self.difficulty = "medium"
            elif SCREEN_WIDTH // 2 + 90 <= x <= SCREEN_WIDTH // 2 + 210:
                self.difficulty = "hard"

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.finish_game(completed=False)
            return

        kb = cfg.KEY_BINDINGS
        if self.state == STATE_MENU:
            if key == arcade.key.E:
                self.setup_game()
                self.state = STATE_GAME
        elif self.state == STATE_GAME:
            if key == kb['left']:
                self.left_pressed = True
            elif key == kb['right']:
                self.right_pressed = True
        elif self.state == STATE_GAME_OVER:
            if key == arcade.key.R:
                self.state = STATE_MENU
                self.left_pressed = False
                self.right_pressed = False

    def on_key_release(self, key: int, modifiers: int):
        kb = cfg.KEY_BINDINGS
        if self.state == STATE_GAME:
            if key == kb['left']:
                self.left_pressed = False
            elif key == kb['right']:
                self.right_pressed = False
