"""
Base game class for arcade machines.
Inherit from this to create new mini-games.
"""

from abc import ABC, abstractmethod
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class BaseGame(ABC):
    """Base class for all arcade machine games."""

    def __init__(self, game_name: str, machine_id: str, on_finish_callback):
        """
        Args:
            game_name: Display name of the game
            machine_id: Unique identifier for this machine
            on_finish_callback: Callable(score, completed) - called when game ends
        """
        self.game_name = game_name
        self.machine_id = machine_id
        self.on_finish_callback = on_finish_callback
        self.score = 0
        self.time_remaining = 60  # Default 60 seconds per game
        self.running = True
        self.elapsed_time = 0

    @abstractmethod
    def handle_events(self, event: pygame.event.EventType) -> bool:
        """Handle input. Return False to exit game."""
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """Update game logic each frame."""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """Render the game to the screen."""
        pass

    def run(self, screen: pygame.Surface, clock: pygame.time.Clock) -> tuple:
        """Run game loop. Returns (score, completed)."""
        self.running = True
        self.elapsed_time = 0
        fps = 60

        while self.running and self.elapsed_time < self.time_remaining:
            delta_time = clock.tick(fps) / 1000.0
            self.elapsed_time += delta_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.score, False
                if not self.handle_events(event):
                    return self.score, False

            self.update(delta_time)
            self.draw(screen)
            pygame.display.flip()

        return self.score, True

    def finish_game(self, completed: bool = True):
        """Call this when the game should end."""
        self.running = False
