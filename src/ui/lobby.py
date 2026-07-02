"""
Main lobby scene.
Player walks around and interacts with arcade machines and cashier.
"""

import arcade
import math
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, MACHINES_PER_ROW,
    MACHINE_SPACING_X, MACHINE_SPACING_Y, MACHINE_START_X, MACHINE_START_Y
)
from src.core.player_state import PlayerState
from src.core.leaderboard import Leaderboard
from src.games.registry import GameRegistry
from src.ui.dialogs import ConfirmationDialog, LeaderboardView


class ArcadeMachine:
    """Represents an arcade machine in the lobby."""

    SIZE = 60  # Sprite size
    INTERACTION_RANGE = 100

    def __init__(self, machine_id: str, machine_name: str, x: float, y: float):
        self.machine_id = machine_id
        self.machine_name = machine_name
        self.x = x
        self.y = y
        self.locked = False

    def draw(self, player_x: float, player_y: float, is_near: bool = False):
        """Draw the machine."""
        color = arcade.color.RED if self.locked else arcade.color.CYAN
        if is_near:
            color = arcade.color.YELLOW

        arcade.draw_rect_filled(arcade.XYWH(self.x, self.y, self.SIZE, self.SIZE), color)
        arcade.draw_rect_outline(arcade.XYWH(self.x, self.y, self.SIZE, self.SIZE), arcade.color.WHITE, 2)
        arcade.draw_text(
            self.machine_name[:8],
            self.x - 20, self.y - 10,
            font_size=8, color=arcade.color.BLACK
        )

    def is_player_nearby(self, player_x: float, player_y: float) -> bool:
        """Check if player is close enough to interact."""
        distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)
        return distance < self.INTERACTION_RANGE

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside machine."""
        return (abs(x - self.x) < self.SIZE // 2 and
                abs(y - self.y) < self.SIZE // 2)


class Cashier:
    """Represents the cashier NPC."""

    SIZE = 50
    INTERACTION_RANGE = 100

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def draw(self, player_x: float, player_y: float, is_near: bool = False):
        """Draw the cashier."""
        color = arcade.color.MAGENTA if is_near else arcade.color.LIGHT_CORAL
        arcade.draw_rect_filled(arcade.XYWH(self.x, self.y, self.SIZE, self.SIZE), color)
        arcade.draw_rect_outline(arcade.XYWH(self.x, self.y, self.SIZE, self.SIZE), arcade.color.WHITE, 2)
        arcade.draw_text(
            "CASHIER",
            self.x - 25, self.y - 10,
            font_size=8, color=arcade.color.WHITE
        )

    def is_player_nearby(self, player_x: float, player_y: float) -> bool:
        """Check if player is close enough to interact."""
        distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)
        return distance < self.INTERACTION_RANGE


class LobbyView(arcade.View):
    """Main lobby scene."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_BLUE_GRAY

        # Player
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_size = 20
        self.player_speed_x = 0
        self.player_speed_y = 0

        # Game state
        self.player_state = PlayerState("Player")
        self.leaderboard = Leaderboard()
        self.registry = GameRegistry()

        # Machines
        self.machines = []
        self._create_machines()

        # Cashier
        self.cashier = Cashier(100, 100)

        # UI state
        self.show_menu = False
        self.show_global_leaderboard = False

    def _create_machines(self):
        """Create arcade machines in the lobby."""
        machine_ids = self.registry.get_machine_ids()
        self.player_state.initialize_machines(machine_ids)

        for i, machine_id in enumerate(machine_ids):
            machine_def = self.registry.get_machine(machine_id)
            row = i // MACHINES_PER_ROW
            col = i % MACHINES_PER_ROW

            x = MACHINE_START_X + col * MACHINE_SPACING_X
            y = SCREEN_HEIGHT - MACHINE_START_Y - row * MACHINE_SPACING_Y

            machine = ArcadeMachine(machine_id, machine_def['name'], x, y)
            self.machines.append(machine)

    def on_show(self):
        """View initialization."""
        pass

    def on_draw(self):
        """Render the lobby."""
        self.clear()

        # Draw background
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            self.background_color
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
        arcade.draw_circle_filled(self.player_x, self.player_y, self.player_size, arcade.color.GREEN)
        arcade.draw_circle_outline(self.player_x, self.player_y, self.player_size, arcade.color.WHITE, 2)

        # Draw UI
        arcade.draw_text(
            f"Score: {self.player_state.total_score}",
            10, SCREEN_HEIGHT - 20,
            font_size=14, color=arcade.color.WHITE, bold=True
        )

        # Draw instructions
        arcade.draw_text(
            "Arrow keys to move | Press E to interact with nearby machines/cashier",
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

    def on_key_press(self, key: int, modifiers: int):
        """Handle key press."""
        if key == arcade.key.UP:
            self.player_speed_y = 1
        elif key == arcade.key.DOWN:
            self.player_speed_y = -1
        elif key == arcade.key.LEFT:
            self.player_speed_x = -1
        elif key == arcade.key.RIGHT:
            self.player_speed_x = 1
        elif key == arcade.key.E:
            self._handle_interaction()

    def on_key_release(self, key: int, modifiers: int):
        """Handle key release."""
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_speed_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
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
