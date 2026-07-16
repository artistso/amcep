import math
import unittest

from src.amcep import (
    AMCEPState,
    bounded_cumulative_score,
    bounded_transient_score,
    candidate_d_score_d_rho,
    candidate_score,
    cumulative_d_score_d_rho,
    cumulative_score,
    logistic,
    original_d_score_d_rho,
    original_score,
    residual_converges,
    transient_score,
)


class TestAMCEPMathAudit(unittest.TestCase):
    def test_source_example_is_reproducible(self):
        state = AMCEPState(1.0, 5.0, 0.5, 10, 1.0)
        self.assertAlmostEqual(original_score(state), 5.9990234375)

    def test_original_sign_defect(self):
        low = AMCEPState(1.0, 5.0, 0.5, 10, 1.0)
        high = AMCEPState(2.0, 5.0, 0.5, 10, 1.0)
        self.assertGreater(original_score(high), original_score(low))
        self.assertGreater(original_d_score_d_rho(low), 0)

    def test_transient_candidate_penalizes_contradiction(self):
        low = AMCEPState(1.0, 5.0, 0.5, 10, 1.0)
        high = AMCEPState(2.0, 5.0, 0.5, 10, 1.0)
        self.assertLess(transient_score(high), transient_score(low))
        self.assertLess(candidate_score(high), candidate_score(low))
        self.assertLessEqual(candidate_d_score_d_rho(low), 0)

    def test_cumulative_candidate_penalizes_contradiction(self):
        for x in (0.0, 0.25, 0.5, 0.9, 1.0):
            low = AMCEPState(1.0, 5.0, x, 10, 1.0)
            high = AMCEPState(2.0, 5.0, x, 10, 1.0)
            self.assertLessEqual(cumulative_score(high), cumulative_score(low))
            self.assertLessEqual(cumulative_d_score_d_rho(low), 0)

    def test_cumulative_derivative_reverses_outside_declared_domain(self):
        state = AMCEPState(1.0, 5.0, 1.1, 10, 1.0)
        self.assertGreater(cumulative_d_score_d_rho(state), 0)

    def test_transient_candidate_forgets_penalty(self):
        state = AMCEPState(4.0, 5.0, 0.5, 100, 1.0, 2.0)
        self.assertAlmostEqual(transient_score(state), 5.0, places=12)

    def test_cumulative_candidate_preserves_penalty(self):
        state = AMCEPState(4.0, 5.0, 0.5, 100, 1.0, 2.0)
        self.assertAlmostEqual(cumulative_score(state), -3.0, places=12)

    def test_penalty_weight_zero_matches_task_only_baseline(self):
        state = AMCEPState(10.0, 5.0, 0.5, 4, 2.0, 0.0)
        self.assertEqual(transient_score(state), 2.5)
        self.assertEqual(cumulative_score(state), 2.5)

    def test_convergence_domain(self):
        self.assertTrue(residual_converges(1.0, 0.5))
        self.assertTrue(residual_converges(0.0, 2.0))
        self.assertFalse(residual_converges(1.0, 1.0))
        self.assertFalse(residual_converges(1.0, -1.0))
        self.assertFalse(residual_converges(1.0, 1.1))

    def test_bounded_scores_are_in_open_unit_interval(self):
        states = [
            AMCEPState(0.0, 0.0, 0.0, 0, 1.0),
            AMCEPState(100.0, 1000.0, 0.5, 10, 0.1, 10.0),
            AMCEPState(100.0, -1000.0, 0.5, 10, 0.1, 10.0),
        ]
        for state in states:
            for value in (
                bounded_transient_score(state),
                bounded_cumulative_score(state),
            ):
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_logistic_is_stable_at_extreme_inputs(self):
        self.assertEqual(logistic(1000.0), 1.0)
        self.assertEqual(logistic(-1000.0), 0.0)
        self.assertEqual(logistic(0.0), 0.5)

    def test_normalization_is_domain_constraint(self):
        for invalid in (0.0, -1.0):
            with self.assertRaises(ValueError):
                original_score(AMCEPState(1.0, 5.0, 0.5, 10, invalid))

    def test_negative_penalty_weight_rejected(self):
        with self.assertRaises(ValueError):
            transient_score(AMCEPState(1.0, 5.0, 0.5, 10, 1.0, -1.0))

    def test_nonfinite_inputs_rejected(self):
        with self.assertRaises(ValueError):
            original_score(AMCEPState(math.inf, 5.0, 0.5, 10, 1.0))
        with self.assertRaises(ValueError):
            logistic(math.nan)


if __name__ == "__main__":
    unittest.main()
