"""
Leaderboard management.
Stores and retrieves scores from JSON files.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class LeaderboardEntry:
    """A single leaderboard entry."""

    def __init__(self, name: str, score: int, machine_id: str = None, timestamp: str = None):
        self.name = name
        self.score = score
        self.machine_id = machine_id  # None for global leaderboard
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'score': self.score,
            'machine_id': self.machine_id,
            'timestamp': self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LeaderboardEntry':
        return LeaderboardEntry(
            name=data['name'],
            score=data['score'],
            machine_id=data.get('machine_id'),
            timestamp=data.get('timestamp')
        )


class Leaderboard:
    """Manages leaderboard data."""

    GLOBAL_PATH = 'data/leaderboards/global.json'
    MACHINE_PATH_TEMPLATE = 'data/leaderboards/machine_{}.json'

    def __init__(self):
        Path('data/leaderboards').mkdir(parents=True, exist_ok=True)

    def get_global_leaderboard(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top scores across all machines."""
        return self._load_leaderboard(self.GLOBAL_PATH, limit)

    def get_machine_leaderboard(self, machine_id: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top scores for a specific machine."""
        path = self.MACHINE_PATH_TEMPLATE.format(machine_id)
        return self._load_leaderboard(path, limit)

    def add_global_score(self, name: str, score: int):
        """Add a score to the global leaderboard."""
        self._add_score(self.GLOBAL_PATH, name, score, machine_id=None)

    def add_machine_score(self, machine_id: str, name: str, score: int):
        """Add a score to a machine-specific leaderboard."""
        path = self.MACHINE_PATH_TEMPLATE.format(machine_id)
        self._add_score(path, name, score, machine_id=machine_id)

    def _add_score(self, path: str, name: str, score: int, machine_id: str = None):
        """Add a score to a leaderboard file."""
        entry = LeaderboardEntry(name, score, machine_id)
        entries = self._load_entries(path)
        entries.append(entry.to_dict())
        entries.sort(key=lambda x: x['score'], reverse=True)
        self._save_entries(path, entries)

    def _load_leaderboard(self, path: str, limit: int) -> List[LeaderboardEntry]:
        """Load leaderboard entries from file, sorted by score."""
        entries = self._load_entries(path)
        entries.sort(key=lambda x: x['score'], reverse=True)
        return [LeaderboardEntry.from_dict(e) for e in entries[:limit]]

    def _load_entries(self, path: str) -> List[Dict[str, Any]]:
        """Load raw entries from file."""
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_entries(self, path: str, entries: List[Dict[str, Any]]):
        """Save raw entries to file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(entries, f, indent=2)
