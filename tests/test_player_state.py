import sys
import os
import unittest
from unittest.mock import patch

# Stub config so we don't need a display
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

with patch.dict('sys.modules', {'config.settings': type(sys)('config.settings')}):
    import config.settings as _cfg
    _cfg.ATTEMPTS_PER_MACHINE = 3

from src.core.player_state import PlayerState


class TestPlayerStateInit(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState("Dima")

    def test_initial_score_is_zero(self):
        self.assertEqual(self.state.total_score, 0)

    def test_initial_coins_is_zero(self):
        self.assertEqual(self.state.coins, 0)

    def test_session_not_over_by_default(self):
        self.assertFalse(self.state.session_over)

    def test_name_stored(self):
        self.assertEqual(self.state.name, "Dima")


class TestInitializeMachines(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()
        self.state.initialize_machines(['m1', 'm2', 'm3'])

    def test_all_machines_get_attempts(self):
        for mid in ['m1', 'm2', 'm3']:
            self.assertEqual(self.state.get_remaining_attempts(mid), 3)

    def test_unknown_machine_returns_zero(self):
        self.assertEqual(self.state.get_remaining_attempts('unknown'), 0)


class TestSpendAttempt(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()
        self.state.initialize_machines(['m1'])

    def test_spend_decrements_by_one(self):
        self.state.spend_attempt('m1')
        self.assertEqual(self.state.get_remaining_attempts('m1'), 2)

    def test_spend_returns_true_when_available(self):
        self.assertTrue(self.state.spend_attempt('m1'))

    def test_spend_returns_false_when_locked(self):
        for _ in range(3):
            self.state.spend_attempt('m1')
        self.assertFalse(self.state.spend_attempt('m1'))

    def test_attempts_dont_go_below_zero(self):
        for _ in range(5):
            self.state.spend_attempt('m1')
        self.assertEqual(self.state.get_remaining_attempts('m1'), 0)

    def test_spend_unknown_machine_returns_false(self):
        self.assertFalse(self.state.spend_attempt('nonexistent'))


class TestMachineLocked(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()
        self.state.initialize_machines(['m1', 'm2'])

    def test_not_locked_initially(self):
        self.assertFalse(self.state.is_machine_locked('m1'))

    def test_locked_after_all_attempts_spent(self):
        for _ in range(3):
            self.state.spend_attempt('m1')
        self.assertTrue(self.state.is_machine_locked('m1'))

    def test_all_machines_locked_false_while_attempts_remain(self):
        self.assertFalse(self.state.all_machines_locked())

    def test_all_machines_locked_true_when_all_spent(self):
        for mid in ['m1', 'm2']:
            for _ in range(3):
                self.state.spend_attempt(mid)
        self.assertTrue(self.state.all_machines_locked())

    def test_all_machines_locked_false_on_empty_dict(self):
        self.assertFalse(PlayerState().all_machines_locked())


class TestAddScore(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()
        self.state.initialize_machines(['m1'])

    def test_score_accumulates(self):
        self.state.add_score('m1', 100)
        self.state.add_score('m1', 50)
        self.assertEqual(self.state.total_score, 150)

    def test_score_from_different_machines_sums(self):
        self.state.initialize_machines(['m1', 'm2'])
        self.state.add_score('m1', 200)
        self.state.add_score('m2', 300)
        self.assertEqual(self.state.total_score, 500)


class TestSpendCoin(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()

    def test_spend_coin_returns_false_when_empty(self):
        self.assertFalse(self.state.spend_coin())

    def test_spend_coin_decrements(self):
        self.state.coins = 5
        self.state.spend_coin()
        self.assertEqual(self.state.coins, 4)

    def test_spend_coin_returns_true_when_available(self):
        self.state.coins = 1
        self.assertTrue(self.state.spend_coin())


class TestResetAttempts(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()
        self.state.initialize_machines(['m1', 'm2'])
        for mid in ['m1', 'm2']:
            for _ in range(3):
                self.state.spend_attempt(mid)

    def test_reset_restores_all_attempts(self):
        self.state.reset_all_attempts()
        for mid in ['m1', 'm2']:
            self.assertEqual(self.state.get_remaining_attempts(mid), 3)

    def test_not_locked_after_reset(self):
        self.state.reset_all_attempts()
        self.assertFalse(self.state.all_machines_locked())


class TestStartAndEndAttempt(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState()
        self.state.initialize_machines(['m1'])
        self.state.add_score('m1', 999)

    def test_start_attempt_sets_name(self):
        self.state.start_attempt("Alice", coins=10)
        self.assertEqual(self.state.player_name, "Alice")

    def test_start_attempt_sets_coins(self):
        self.state.start_attempt("Alice", coins=10)
        self.assertEqual(self.state.coins, 10)

    def test_start_attempt_resets_score(self):
        self.state.start_attempt("Alice")
        self.assertEqual(self.state.total_score, 0)

    def test_start_attempt_marks_active(self):
        self.state.start_attempt("Alice")
        self.assertTrue(self.state.attempt_active)

    def test_end_attempt_marks_inactive(self):
        self.state.start_attempt("Alice")
        self.state.end_attempt()
        self.assertFalse(self.state.attempt_active)

    def test_end_session_marks_session_over(self):
        self.state.end_session()
        self.assertTrue(self.state.session_over)


if __name__ == '__main__':
    unittest.main()
