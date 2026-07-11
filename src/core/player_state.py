"""
Player state management.
Tracks attempts per machine, accumulated score, coins, and attempt session.
"""

from config.settings import ATTEMPTS_PER_MACHINE


class PlayerState:
    """Manages player progress during a session."""

    def __init__(self, player_name: str = "Player"):
        self.name = player_name
        self.total_score = 0
        self.machine_attempts = {}  # machine_id -> remaining attempts
        self.session_over = False

        self.coins: int = 0
        self.player_name: str = ""        # entered at "Начать попытку"
        self.attempt_active: bool = False

    def initialize_machines(self, machine_ids: list):
        for machine_id in machine_ids:
            self.machine_attempts[machine_id] = ATTEMPTS_PER_MACHINE

    def add_score(self, machine_id: str, points: int):
        self.total_score += points

    def spend_attempt(self, machine_id: str) -> bool:
        if machine_id not in self.machine_attempts:
            return False
        if self.machine_attempts[machine_id] > 0:
            self.machine_attempts[machine_id] -= 1
            return True
        return False

    def spend_coin(self) -> bool:
        if self.coins > 0:
            self.coins -= 1
            return True
        return False

    def get_remaining_attempts(self, machine_id: str) -> int:
        return self.machine_attempts.get(machine_id, 0)

    def is_machine_locked(self, machine_id: str) -> bool:
        return self.get_remaining_attempts(machine_id) == 0

    def all_machines_locked(self) -> bool:
        if not self.machine_attempts:
            return False
        return all(a == 0 for a in self.machine_attempts.values())

    def reset_all_attempts(self):
        for machine_id in self.machine_attempts:
            self.machine_attempts[machine_id] = ATTEMPTS_PER_MACHINE

    def start_attempt(self, name: str, coins: int = 15):
        self.player_name = name
        self.coins = coins
        self.attempt_active = True
        self.total_score = 0
        self.reset_all_attempts()

    def end_attempt(self):
        self.attempt_active = False
        self.total_score = 0

    def end_session(self):
        self.session_over = True
