import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.leaderboard import Leaderboard, LeaderboardEntry


class LeaderboardTestBase(unittest.TestCase):
    """Runs each test inside a temp directory so real data files aren't touched."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_cwd = os.getcwd()
        os.chdir(self._tmpdir.name)
        self.lb = Leaderboard()

    def tearDown(self):
        os.chdir(self._orig_cwd)
        self._tmpdir.cleanup()


class TestLeaderboardEntrySerialisation(unittest.TestCase):
    def test_to_dict_round_trip(self):
        entry = LeaderboardEntry("Alice", 500, machine_id="pacman_1", timestamp="2026-07-11T10:00:00")
        data = entry.to_dict()
        restored = LeaderboardEntry.from_dict(data)
        self.assertEqual(restored.name, "Alice")
        self.assertEqual(restored.score, 500)
        self.assertEqual(restored.machine_id, "pacman_1")
        self.assertEqual(restored.timestamp, "2026-07-11T10:00:00")

    def test_from_dict_missing_machine_id_is_none(self):
        data = {'name': 'Bob', 'score': 100}
        entry = LeaderboardEntry.from_dict(data)
        self.assertIsNone(entry.machine_id)


class TestGlobalLeaderboard(LeaderboardTestBase):
    def test_empty_returns_empty_list(self):
        self.assertEqual(self.lb.get_global_leaderboard(), [])

    def test_add_and_retrieve_score(self):
        self.lb.add_global_score("Alice", 300)
        entries = self.lb.get_global_leaderboard()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "Alice")
        self.assertEqual(entries[0].score, 300)

    def test_scores_sorted_descending(self):
        self.lb.add_global_score("Alice", 100)
        self.lb.add_global_score("Bob", 500)
        self.lb.add_global_score("Carol", 300)
        entries = self.lb.get_global_leaderboard()
        scores = [e.score for e in entries]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_limit_is_respected(self):
        for i in range(15):
            self.lb.add_global_score(f"Player{i}", i * 10)
        entries = self.lb.get_global_leaderboard(limit=5)
        self.assertEqual(len(entries), 5)

    def test_top_score_is_first(self):
        self.lb.add_global_score("Low", 10)
        self.lb.add_global_score("High", 9999)
        entries = self.lb.get_global_leaderboard()
        self.assertEqual(entries[0].score, 9999)

    def test_multiple_scores_same_player(self):
        self.lb.add_global_score("Alice", 100)
        self.lb.add_global_score("Alice", 200)
        entries = self.lb.get_global_leaderboard()
        self.assertEqual(len(entries), 2)


class TestMachineLeaderboard(LeaderboardTestBase):
    def test_empty_returns_empty_list(self):
        self.assertEqual(self.lb.get_machine_leaderboard("pacman_1"), [])

    def test_add_and_retrieve_machine_score(self):
        self.lb.add_machine_score("pacman_1", "Alice", 400)
        entries = self.lb.get_machine_leaderboard("pacman_1")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].score, 400)

    def test_machine_scores_are_isolated(self):
        self.lb.add_machine_score("pacman_1", "Alice", 100)
        self.lb.add_machine_score("snake_1", "Bob", 200)
        pacman = self.lb.get_machine_leaderboard("pacman_1")
        snake = self.lb.get_machine_leaderboard("snake_1")
        self.assertEqual(len(pacman), 1)
        self.assertEqual(len(snake), 1)
        self.assertEqual(pacman[0].name, "Alice")
        self.assertEqual(snake[0].name, "Bob")

    def test_machine_id_stored_on_entry(self):
        self.lb.add_machine_score("tetris_1", "Alice", 300)
        entries = self.lb.get_machine_leaderboard("tetris_1")
        self.assertEqual(entries[0].machine_id, "tetris_1")

    def test_global_and_machine_independent(self):
        self.lb.add_global_score("Global", 999)
        self.assertEqual(self.lb.get_machine_leaderboard("pacman_1"), [])


class TestLeaderboardPersistence(LeaderboardTestBase):
    def test_scores_persist_across_instances(self):
        self.lb.add_global_score("Alice", 500)
        lb2 = Leaderboard()
        entries = lb2.get_global_leaderboard()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "Alice")

    def test_corrupted_file_returns_empty(self):
        path = os.path.join(self._tmpdir.name, 'data', 'leaderboards', 'global.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write("not valid json{{{{")
        lb2 = Leaderboard()
        self.assertEqual(lb2.get_global_leaderboard(), [])


if __name__ == '__main__':
    unittest.main()
