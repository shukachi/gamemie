"""
Player state management.
Tracks attempts per machine and accumulated score.
"""

from config.settings import ATTEMPTS_PER_MACHINE


class PlayerState:
    """Manages player progress during a session."""

    def __init__(self, player_name: str = "Player"):
        self.name = player_name
        self.total_score = 0
        self.machine_attempts = {}  # machine_id -> remaining attempts
        self.session_over = False

    def initialize_machines(self, machine_ids: list):
        """Initialize attempts for all machines."""
        for machine_id in machine_ids:
            self.machine_attempts[machine_id] = ATTEMPTS_PER_MACHINE

    def add_score(self, machine_id: str, points: int):
        """Add points to total score."""
        self.total_score += points

    def spend_attempt(self, machine_id: str) -> bool:
        """Spend one attempt on a machine. Returns True if attempt was available."""
        if machine_id not in self.machine_attempts:
            return False
        if self.machine_attempts[machine_id] > 0:
            self.machine_attempts[machine_id] -= 1
            return True
        return False

    def get_remaining_attempts(self, machine_id: str) -> int:
        """Get remaining attempts for a machine."""
        return self.machine_attempts.get(machine_id, 0)

    def is_machine_locked(self, machine_id: str) -> bool:
        """Check if a machine is locked (no attempts left)."""
        return self.get_remaining_attempts(machine_id) == 0

    def all_machines_locked(self) -> bool:
        """Check if all machines are locked."""
        if not self.machine_attempts:
            return False
        return all(attempts == 0 for attempts in self.machine_attempts.values())

    def reset_all_attempts(self):
        """Reset all attempts (via cashier)."""
        for machine_id in self.machine_attempts:
            self.machine_attempts[machine_id] = ATTEMPTS_PER_MACHINE

    def end_session(self):
        """End the current session."""
        self.session_over = True
