"""
UI components and dialogs.
"""

import arcade
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIALOG_WIDTH, DIALOG_HEIGHT


class ConfirmationDialog(arcade.View):
    """Dialog shown before starting a game."""

    def __init__(self, machine_id: str, machine_name: str, leaderboard_entries: list,
                 on_confirm_callback, on_cancel_callback):
        """
        Args:
            machine_id: ID of the machine
            machine_name: Display name of the machine
            leaderboard_entries: List of top scores for this machine
            on_confirm_callback: Called if player confirms
            on_cancel_callback: Called if player cancels
        """
        super().__init__()
        self.machine_id = machine_id
        self.machine_name = machine_name
        self.leaderboard_entries = leaderboard_entries[:5]  # Top 5
        self.on_confirm_callback = on_confirm_callback
        self.on_cancel_callback = on_cancel_callback
        self.background_color = arcade.color.DARK_GRAY

    def on_show(self):
        """Set background."""
        pass

    def on_draw(self):
        """Draw the dialog."""
        arcade.start_render()

        # Semi-transparent overlay
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 150)
        )

        # Dialog box
        dialog_x = SCREEN_WIDTH // 2
        dialog_y = SCREEN_HEIGHT // 2
        arcade.draw_rectangle_outline(
            dialog_x, dialog_y,
            DIALOG_WIDTH, DIALOG_HEIGHT,
            arcade.color.WHITE, 2
        )
        arcade.draw_rectangle_filled(
            dialog_x, dialog_y,
            DIALOG_WIDTH, DIALOG_HEIGHT,
            arcade.color.DARK_SLATE_GRAY
        )

        # Title
        arcade.draw_text(
            self.machine_name,
            dialog_x - DIALOG_WIDTH // 2 + 20, dialog_y + DIALOG_HEIGHT // 2 - 40,
            font_size=16, color=arcade.color.WHITE, bold=True
        )

        # Leaderboard
        arcade.draw_text(
            "Top Scores:",
            dialog_x - DIALOG_WIDTH // 2 + 20, dialog_y + DIALOG_HEIGHT // 2 - 80,
            font_size=12, color=arcade.color.LIGHT_YELLOW
        )

        y_offset = dialog_y + DIALOG_HEIGHT // 2 - 110
        for i, entry in enumerate(self.leaderboard_entries):
            text = f"{i + 1}. {entry.name}: {entry.score}"
            arcade.draw_text(
                text,
                dialog_x - DIALOG_WIDTH // 2 + 30, y_offset - i * 25,
                font_size=10, color=arcade.color.WHITE
            )

        # Buttons
        button_y = dialog_y - DIALOG_HEIGHT // 2 + 30
        arcade.draw_rectangle_outline(
            dialog_x - 80, button_y,
            60, 30, arcade.color.GREEN, 2
        )
        arcade.draw_text(
            "Play",
            dialog_x - 105, button_y - 8,
            font_size=12, color=arcade.color.GREEN, bold=True
        )

        arcade.draw_rectangle_outline(
            dialog_x + 80, button_y,
            60, 30, arcade.color.RED, 2
        )
        arcade.draw_text(
            "Cancel",
            dialog_x + 55, button_y - 8,
            font_size=12, color=arcade.color.RED, bold=True
        )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle button clicks."""
        dialog_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT // 2 - DIALOG_HEIGHT // 2 + 30

        # Play button
        if dialog_x - 110 < x < dialog_x - 50 and button_y - 15 < y < button_y + 15:
            self.on_confirm_callback()
        # Cancel button
        elif dialog_x + 50 < x < dialog_x + 110 and button_y - 15 < y < button_y + 15:
            self.on_cancel_callback()

    def on_key_press(self, key: int, modifiers: int):
        """Handle keyboard input."""
        if key == arcade.key.ESCAPE:
            self.on_cancel_callback()
        elif key == arcade.key.ENTER:
            self.on_confirm_callback()


class LeaderboardView(arcade.View):
    """Leaderboard display view."""

    def __init__(self, title: str, entries: list, on_close_callback):
        """
        Args:
            title: Title of the leaderboard
            entries: List of LeaderboardEntry objects
            on_close_callback: Called when closing the view
        """
        super().__init__()
        self.title = title
        self.entries = entries
        self.on_close_callback = on_close_callback
        self.background_color = arcade.color.DARK_BLUE_GRAY

    def on_show(self):
        """View initialization."""
        pass

    def on_draw(self):
        """Draw the leaderboard."""
        arcade.start_render()

        arcade.draw_text(
            self.title,
            50, SCREEN_HEIGHT - 50,
            font_size=24, color=arcade.color.WHITE, bold=True
        )

        y = SCREEN_HEIGHT - 120
        for i, entry in enumerate(self.entries):
            text = f"{i + 1}. {entry.name}: {entry.score}"
            arcade.draw_text(
                text,
                100, y - i * 40,
                font_size=14, color=arcade.color.LIGHT_YELLOW
            )

        arcade.draw_text(
            "Press ESC or click to close",
            50, 50,
            font_size=12, color=arcade.color.LIGHT_GRAY
        )

    def on_key_press(self, key: int, modifiers: int):
        """Handle keyboard."""
        if key == arcade.key.ESCAPE:
            self.on_close_callback()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Close on any click."""
        self.on_close_callback()
