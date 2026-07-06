"""
Main lobby scene.
Player walks around and interacts with arcade machines and cashier.
"""

import arcade
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED

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
        self.zone_w = ZONE_W_FRAC * SCREEN_WIDTH
        self.zone_h = ZONE_H_FRAC * SCREEN_HEIGHT

    def draw(self, player_x: float, player_y: float, is_near: bool = False):
        """Show 'ИГРАТЬ' prompt when player is inside the interaction zone."""
        if not is_near or self.locked:
            return
        offset = SCREEN_HEIGHT * 0.13
        text_y = self.y - offset if self.y > SCREEN_HEIGHT / 2 else self.y + offset
        arcade.draw_text(
            "ИГРАТЬ",
            self.x, text_y,
            font_size=22, color=(144, 238, 144), bold=True,
            anchor_x="center", anchor_y="center",
        )

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

    def draw(self, player_x: float, player_y: float, is_near: bool = False):
        """Draw the cashier sprite with label above."""
        arcade.draw_sprite(self._sprite)

        label_color = arcade.color.YELLOW if is_near else arcade.color.WHITE
        arcade.draw_text(
            "CASHIER",
            self.x - 22, self.y + self.DRAW_H // 2 + 4,
            font_size=9, color=label_color, bold=True
        )

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
        self.player_size = 30  # collision/interaction radius in pixels
        self.player_speed_x = 0
        self.player_speed_y = 0
        self.player_sprite = PlayerSprite(self.player_x, self.player_y)

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
        self.music_player = None

        # UI state
        self.show_menu = False
        self.show_global_leaderboard = False

    def _create_machines(self):
        """Create arcade machines positioned to match the background art."""
        machine_ids = self.registry.get_machine_ids()
        self.player_state.initialize_machines(machine_ids)

        for i, machine_id in enumerate(machine_ids):
            if i >= len(ZONE_POSITIONS):
                break
            machine_def = self.registry.get_machine(machine_id)
            x_frac, y_frac = ZONE_POSITIONS[i]
            machine = ArcadeMachine(
                machine_id, machine_def['name'],
                x_frac * SCREEN_WIDTH, y_frac * SCREEN_HEIGHT,
            )
            self.machines.append(machine)

    def on_show_view(self):
        if not self.music_player:
            self.music_player = arcade.play_sound(self.music, loop=True)

    def on_hide_view(self):
        if self.music_player:
            arcade.stop_sound(self.music_player)
            self.music_player = None

    def on_draw(self):
        """Render the lobby."""
        self.clear()

        # Draw background
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Draw machines
        for machine in self.machines:
            is_locked = self.player_state.is_machine_locked(machine.machine_id)
            machine.locked = is_locked
            is_near = machine.is_player_nearby(self.player_x, self.player_y)
            machine.draw(self.player_x, self.player_y, is_near)

        # Draw cashier
        cashier_near = self.cashier.is_player_nearby(self.player_x, self.player_y)
        self.cashier.draw(self.player_x, self.player_y, cashier_near)

        # Draw player
        self.player_sprite.draw()

        # Draw UI
        arcade.draw_text(
            f"Score: {self.player_state.total_score}",
            10, SCREEN_HEIGHT - 20,
            font_size=14, color=arcade.color.WHITE, bold=True
        )

        # Draw instructions
        arcade.draw_text(
            "WASD — движение  |  E — взаимодействие",
            10, 10,
            font_size=10, color=arcade.color.LIGHT_GRAY
        )

    def on_update(self, delta_time: float):
        """Update lobby logic."""
        # Update player position
        self.player_x += self.player_speed_x * PLAYER_SPEED * delta_time
        self.player_y += self.player_speed_y * PLAYER_SPEED * delta_time

        # Clamp player to screen
        self.player_x = max(self.player_size, min(SCREEN_WIDTH - self.player_size, self.player_x))
        self.player_y = max(self.player_size, min(SCREEN_HEIGHT - self.player_size, self.player_y))

        # Sync sprite position and advance animation
        self.player_sprite.x = self.player_x
        self.player_sprite.y = self.player_y
        self.player_sprite.update(delta_time, self.player_speed_x, self.player_speed_y)

    def on_key_press(self, key: int, modifiers: int):
        """Handle key press."""
        if key == arcade.key.W:
            self.player_speed_y = 1
        elif key == arcade.key.S:
            self.player_speed_y = -1
        elif key == arcade.key.A:
            self.player_speed_x = -1
        elif key == arcade.key.D:
            self.player_speed_x = 1
        elif key == arcade.key.E:
            self._handle_interaction()

    def on_key_release(self, key: int, modifiers: int):
        """Handle key release."""
        if key == arcade.key.W or key == arcade.key.S:
            self.player_speed_y = 0
        elif key == arcade.key.D or key == arcade.key.A:
            self.player_speed_x = 0

    def _handle_interaction(self):
        """Handle player interaction with machines or cashier."""
        # Check machines
        for machine in self.machines:
            if machine.is_player_nearby(self.player_x, self.player_y):
                if not self.player_state.is_machine_locked(machine.machine_id):
                    self._show_machine_dialog(machine)
                return

        # Check cashier
        if self.cashier.is_player_nearby(self.player_x, self.player_y):
            self._show_cashier_menu()
            return

    def _show_machine_dialog(self, machine: ArcadeMachine):
        """Show confirmation dialog for a machine."""
        leaderboard_entries = self.leaderboard.get_machine_leaderboard(machine.machine_id)

        def on_confirm():
            self._start_game(machine.machine_id)

        def on_cancel():
            pass

        dialog = ConfirmationDialog(
            machine.machine_id, machine.machine_name, leaderboard_entries,
            on_confirm, on_cancel
        )
        self.window.show_view(dialog)

    def _start_game(self, machine_id: str):
        """Start a game on a machine."""
        def on_game_finish(score: int, completed: bool):
            if completed:
                self.player_state.add_score(machine_id, score)
                self.player_state.spend_attempt(machine_id)
                self.leaderboard.add_machine_score(machine_id, "Player", score)

                if self.player_state.all_machines_locked():
                    # Submit to global leaderboard
                    self.leaderboard.add_global_score("Player", self.player_state.total_score)

            self.window.show_view(self)

        game = self.registry.create_game(machine_id, on_game_finish)
        if game:
            self.window.show_view(game)

    def _show_cashier_menu(self):
        """Show cashier menu (placeholder)."""
        if self.player_state.all_machines_locked():
            self.player_state.reset_all_attempts()
            print("All attempts reset!")
        else:
            # Show leaderboard or other menu options
            leaderboard_entries = self.leaderboard.get_global_leaderboard()

            def on_close():
                self.window.show_view(self)

            leaderboard_view = LeaderboardView("Club Leaderboard", leaderboard_entries, on_close)
            self.window.show_view(leaderboard_view)
