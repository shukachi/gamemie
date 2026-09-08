"""
Main lobby scene.
Player walks around and interacts with arcade machines and cashier.
"""

import arcade
import math
import os
from PIL import Image as _PILImage
from config import settings as cfg
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED

def _load_coin_texture():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "assets", "fonts", "coin_static.png",
    )
    try:
        img = _PILImage.open(path).convert("RGBA")
        data = img.load()
        w, h = img.size
        # Replace near-white pixels with transparent
        for y in range(h):
            for x in range(w):
                r, g, b, a = data[x, y]
                if r > 220 and g > 220 and b > 220:
                    data[x, y] = (r, g, b, 0)
        return arcade.Texture(image=img)
    except Exception:
        return None

# Interaction zone centres as fractions of (SCREEN_WIDTH, SCREEN_HEIGHT).
# Measured from fix.png (614×347 screenshot of 1280×720 game).
# 5 machines top row, 5 bottom row — first top-left position is decorative, no zone.
ZONE_POSITIONS = [
    # --- top row (left → right) ---
    (0.180, 0.890),
    (0.343, 0.890),
    (0.505, 0.890),
    (0.625, 0.890),
    (0.810, 0.890),
    # --- bottom row (left → right) ---
    (0.180, 0.120),
    (0.343, 0.120),
    (0.505, 0.120),
    (0.625, 0.120),
    (0.810, 0.120),
]
ZONE_W_FRAC = 0.082  # matches machine sprite width  (~105 px at 1280)
ZONE_H_FRAC = 0.125  # matches machine sprite height (~90 px at 720)
from src.core.player_state import PlayerState
from src.core.leaderboard import Leaderboard
from src.games.registry import GameRegistry
from src.ui.dialogs import ConfirmationDialog, LeaderboardView
from src.ui.player_sprite import PlayerSprite


class ArcadeMachine:
    """Represents an arcade machine in the lobby."""

    def __init__(self, machine_id: str, machine_name: str, x: float, y: float):
        self.machine_id = machine_id
        self.machine_name = machine_name
        self.x = x
        self.y = y
        self.locked = False
        self.broken = False
        self.zone_w = ZONE_W_FRAC * SCREEN_WIDTH
        self.zone_h = ZONE_H_FRAC * SCREEN_HEIGHT
        offset = SCREEN_HEIGHT * 0.13
        text_y = y - offset if y > SCREEN_HEIGHT / 2 else y + offset
        self._play_text = arcade.Text(
            "ИГРАТЬ", x=x, y=text_y,
            color=(144, 238, 144), font_size=22, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._block_text = arcade.Text(
            "BLOCK", x=x, y=text_y,
            color=(220, 50, 50), font_size=22, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._broken_text = arcade.Text(
            "BROKEN", x=x, y=text_y,
            color=(220, 30, 30), font_size=22, bold=True,
            anchor_x="center", anchor_y="center",
        )

    def draw(self, player_x: float, player_y: float, is_near: bool = False):
        if not is_near:
            return
        if self.broken:
            self._broken_text.draw()
        elif self.locked:
            self._block_text.draw()
        else:
            self._play_text.draw()

    def is_player_nearby(self, player_x: float, player_y: float) -> bool:
        """Check if player is inside the rectangular interaction zone."""
        return (abs(player_x - self.x) < self.zone_w / 2 and
                abs(player_y - self.y) < self.zone_h / 2)

    def contains_point(self, x: float, y: float) -> bool:
        return self.is_player_nearby(x, y)


class Cashier:
    """Represents the cashier NPC."""

    DRAW_W = 120
    DRAW_H = 120
    INTERACTION_RANGE = 90

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self._sprite = arcade.Sprite(":cashier:cashier.png")
        self._sprite.center_x = x
        self._sprite.center_y = y
        self._sprite.width = self.DRAW_W
        self._sprite.height = self.DRAW_H
        self._label = arcade.Text(
            "CASHIER", x=x - 22, y=y + self.DRAW_H // 2 + 4,
            color=arcade.color.WHITE, font_size=9, bold=True,
        )

    def draw(self, player_x: float, player_y: float, is_near: bool = False):
        """Draw the cashier sprite with label above."""
        arcade.draw_sprite(self._sprite)
        self._label.color = arcade.color.GREEN if is_near else arcade.color.WHITE
        self._label.draw()

    def is_player_nearby(self, player_x: float, player_y: float) -> bool:
        """Check if player is close enough to interact."""
        distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)
        return distance < self.INTERACTION_RANGE


class LobbyView(arcade.View):
    """Main lobby scene."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK

        self.background_texture = arcade.load_texture(":backgrounds:back_fon_game_club.webp")

        # Player
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_size = 30
        self.player_speed_x = 0
        self.player_speed_y = 0
        self.player_sprite = PlayerSprite(self.player_x, self.player_y)
        self.target_x: float | None = None  # mouse-click walk target
        self.target_y: float | None = None

        # Game state
        self.player_state = PlayerState("Player")
        self.leaderboard = Leaderboard()
        self.registry = GameRegistry()

        # Machines
        self.machines = []
        self._create_machines()

        # Cashier
        self.cashier = Cashier(SCREEN_WIDTH // 12.19, SCREEN_HEIGHT // 5.14)

        # Music
        self.music = arcade.load_sound(":sounds:lobby_music.mp3")
        self.music_settings = arcade.load_sound(":sounds:settings.mp3")
        self.music_player = None
        self.settings_music_player = None

        # Zone entry sound
        self._hm_sound = arcade.load_sound(":sounds:hm_new.mp3")
        self._hm_last_played: float = -999.0  # seconds since lobby start
        self._hm_elapsed: float = 0.0
        self._zones_near_prev: set[str] = set()  # ids of zones player was in last frame
        self._hm_player = None  # keep reference to prevent GC killing playback

        # UI state
        self.show_menu = False
        self.show_global_leaderboard = False

        # Text objects (fast rendering)
        self._score_text = arcade.Text(
            "Score: 0", x=10, y=SCREEN_HEIGHT - 20,
            color=arcade.color.WHITE, font_size=14, bold=True,
        )
        self._instructions_text = arcade.Text(
            "WASD — движение  |  E — взаимодействие",
            x=10, y=10,
            color=arcade.color.LIGHT_GRAY, font_size=10,
        )

        # Coin HUD
        self._coin_texture = _load_coin_texture()
        self._coin_size = 28
        self._coins_text = arcade.Text(
            "x0", x=42, y=SCREEN_HEIGHT - 53,
            color=(255, 215, 80), font_size=13, bold=True,
        )

    def _create_machines(self):
        """Create arcade machines positioned to match the background art."""
        machine_ids = self.registry.get_machine_ids()
        self.player_state.initialize_machines(machine_ids)
        broken_ids = set(machine_ids[-2:])  # last 2 machines are broken

        for i, machine_id in enumerate(machine_ids):
            if i >= len(ZONE_POSITIONS):
                break
            machine_def = self.registry.get_machine(machine_id)
            x_frac, y_frac = ZONE_POSITIONS[i]
            machine = ArcadeMachine(
                machine_id, machine_def['name'],
                x_frac * SCREEN_WIDTH, y_frac * SCREEN_HEIGHT,
            )
            machine.broken = machine_id in broken_ids
            self.machines.append(machine)

    def on_show_view(self):
        if self.settings_music_player:
            arcade.stop_sound(self.settings_music_player)
            self.settings_music_player = None
        if self.music_player:
            self.music_player.play()
        else:
            self.music_player = arcade.play_sound(self.music, loop=True)
        self.music_player.volume = cfg.LOBBY_MUSIC_VOLUME
        self._zones_near_prev = set()

    def on_hide_view(self):
        if self.music_player:
            self.music_player.pause()
        self.settings_music_player = arcade.play_sound(self.music_settings, loop=True)
        self.settings_music_player.volume = cfg.SETTINGS_MUSIC_VOLUME

    def on_draw(self):
        """Render the lobby."""
        self.clear()

        if cfg.POTATO_MODE:
            self._draw_potato()
        else:
            self._draw_normal()

        # Draw UI
        self._score_text.text = f"Score: {self.player_state.total_score}"
        self._score_text.draw()
        self._instructions_text.draw()
        if self.player_state.attempt_active:
            self._coins_text.text = f"x{self.player_state.coins}"
            self._coins_text.draw()
            if self._coin_texture:
                arcade.draw_texture_rect(
                    self._coin_texture,
                    arcade.XYWH(20, SCREEN_HEIGHT - 46, self._coin_size, self._coin_size),
                )

    def _draw_normal(self):
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        for machine in self.machines:
            is_locked = self.player_state.is_machine_locked(machine.machine_id)
            machine.locked = is_locked
            is_near = machine.is_player_nearby(self.player_x, self.player_y)
            machine.draw(self.player_x, self.player_y, is_near)
        cashier_near = self.cashier.is_player_nearby(self.player_x, self.player_y)
        self.cashier.draw(self.player_x, self.player_y, cashier_near)
        self.player_sprite.draw()

    def _draw_potato(self):
        # Purple background
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            (72, 0, 100)
        )
        # Machines as rectangles
        for machine in self.machines:
            is_locked = self.player_state.is_machine_locked(machine.machine_id)
            machine.locked = is_locked
            is_near = machine.is_player_nearby(self.player_x, self.player_y)
            fill = (80, 80, 90) if is_locked else (100, 140, 220)
            arcade.draw_rect_filled(
                arcade.XYWH(machine.x, machine.y, machine.zone_w, machine.zone_h), fill
            )
            arcade.draw_rect_outline(
                arcade.XYWH(machine.x, machine.y, machine.zone_w, machine.zone_h),
                arcade.color.WHITE, 2
            )
            machine.draw(self.player_x, self.player_y, is_near)
        # Cashier as rectangle
        cashier_near = self.cashier.is_player_nearby(self.player_x, self.player_y)
        cw = self.cashier.INTERACTION_RANGE * 1.4
        ch = self.cashier.INTERACTION_RANGE * 1.4
        fill = (230, 200, 0) if cashier_near else (160, 140, 0)
        arcade.draw_rect_filled(
            arcade.XYWH(self.cashier.x, self.cashier.y, cw, ch), fill
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.cashier.x, self.cashier.y, cw, ch), arcade.color.WHITE, 2
        )
        self.cashier._label.color = arcade.color.GREEN if cashier_near else arcade.color.WHITE
        self.cashier._label.draw()
        # Player as white circle
        arcade.draw_circle_filled(self.player_x, self.player_y, 20, arcade.color.WHITE)

    def on_update(self, delta_time: float):
        """Update lobby logic."""
        # Update player position
        # Mouse-click walk-to-target
        if self.target_x is not None:
            dx = self.target_x - self.player_x
            dy = self.target_y - self.player_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 6:
                self.target_x = self.target_y = None
                self.player_speed_x = self.player_speed_y = 0
            else:
                self.player_speed_x = dx / dist
                self.player_speed_y = dy / dist

        self.player_x += self.player_speed_x * PLAYER_SPEED * delta_time
        self.player_y += self.player_speed_y * PLAYER_SPEED * delta_time

        # Clamp player to screen
        self.player_x = max(self.player_size, min(SCREEN_WIDTH - self.player_size, self.player_x))
        self.player_y = max(self.player_size, min(SCREEN_HEIGHT - self.player_size, self.player_y))

        # Sync sprite position and advance animation
        self.player_sprite.x = self.player_x
        self.player_sprite.y = self.player_y
        self.player_sprite.update(delta_time, self.player_speed_x, self.player_speed_y)

        # Zone entry sound (hm.ogg) with 2-second cooldown
        self._hm_elapsed += delta_time
        zones_near_now: set[str] = set()
        for machine in self.machines:
            if machine.is_player_nearby(self.player_x, self.player_y):
                zones_near_now.add(machine.machine_id)
        if self.cashier.is_player_nearby(self.player_x, self.player_y):
            zones_near_now.add("cashier")

        newly_entered = zones_near_now - self._zones_near_prev
        if newly_entered and (self._hm_elapsed - self._hm_last_played) >= 2.0:
            self._hm_player = arcade.play_sound(self._hm_sound, volume=1.0)
            self._hm_last_played = self._hm_elapsed

        self._zones_near_prev = zones_near_now


    def on_key_press(self, key: int, modifiers: int):
        kb = cfg.KEY_BINDINGS
        if key == kb['up']:
            self.player_speed_y = 1
            self.target_x = self.target_y = None
        elif key == kb['down']:
            self.player_speed_y = -1
            self.target_x = self.target_y = None
        elif key == kb['left']:
            self.player_speed_x = -1
            self.target_x = self.target_y = None
        elif key == kb['right']:
            self.player_speed_x = 1
            self.target_x = self.target_y = None
        elif key == kb['interact']:
            self._handle_interaction()
        elif key == arcade.key.H:
            self._hm_player = arcade.play_sound(self._hm_sound, volume=1.0)

    def on_key_release(self, key: int, modifiers: int):
        kb = cfg.KEY_BINDINGS
        if key == kb['up'] or key == kb['down']:
            self.player_speed_y = 0
        elif key == kb['left'] or key == kb['right']:
            self.player_speed_x = 0

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if cfg.MOUSE_CONTROL and button == arcade.MOUSE_BUTTON_LEFT:
            self.target_x = float(x)
            self.target_y = float(y)
            self.player_speed_x = 0
            self.player_speed_y = 0

    def _handle_interaction(self):
        """Handle player interaction with machines or cashier."""
        for machine in self.machines:
            if machine.is_player_nearby(self.player_x, self.player_y):
                if machine.broken:
                    return
                if self.player_state.is_machine_locked(machine.machine_id):
                    return
                if not self.player_state.attempt_active or self.player_state.coins <= 0:
                    return
                self._show_machine_dialog(machine)
                return

        if self.cashier.is_player_nearby(self.player_x, self.player_y):
            self._show_cashier_menu()

    def _show_machine_dialog(self, machine: ArcadeMachine):
        """Show confirmation dialog for a machine."""
        leaderboard_entries = self.leaderboard.get_machine_leaderboard(machine.machine_id)

        def on_confirm():
            self._start_game(machine.machine_id)

        def on_cancel():
            # Раньше здесь был pass, теперь возвращаемся в лобби
            self.window.show_view(self)

        dialog = ConfirmationDialog(
            machine.machine_id, machine.machine_name, leaderboard_entries,
            on_confirm, on_cancel
        )
        self.window.show_view(dialog)

    def _start_game(self, machine_id: str):
        """Start a game on a machine."""
        def on_game_finish(score: int, completed: bool):
            # Coin and attempt are spent regardless of outcome
            self.player_state.spend_attempt(machine_id)
            self.player_state.spend_coin()
            # Accumulate score (even 0 is valid — just didn't score)
            self.player_state.add_score(machine_id, score)
            if score > 0:
                name = self.player_state.player_name or "Player"
                self.leaderboard.add_machine_score(machine_id, name, score)
            self.window.show_view(self)

        game = self.registry.create_game(machine_id, on_game_finish)
        if game:
            self.window.show_view(game)

    def _show_cashier_menu(self):
        from src.ui.controls_dialog import CashierMenuView
        self.window.show_view(CashierMenuView(self.player_state, self.leaderboard, self))