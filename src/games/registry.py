"""
Game registry.
Keeps track of all available arcade machines.
"""

from src.games.demo_game import DemoGame


class GameRegistry:
    """Registry of all arcade machines."""

    # Machine definitions
    MACHINES = [
        {'id': f'demo_{i}', 'name': f'Demo Game {i}', 'game_class': DemoGame}
        for i in range(1, 11)
    ]

    @classmethod
    def get_machine_ids(cls):
        """Get all machine IDs."""
        return [m['id'] for m in cls.MACHINES]

    @classmethod
    def get_machine(cls, machine_id: str):
        """Get machine definition by ID."""
        for m in cls.MACHINES:
            if m['id'] == machine_id:
                return m
        return None

    @classmethod
    def create_game(cls, machine_id: str, on_finish_callback):
        """Create a game instance for the given machine."""
        machine = cls.get_machine(machine_id)
        if not machine:
            return None
        return machine['game_class'](machine_id, on_finish_callback)
