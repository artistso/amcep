import math
import unittest

from src.amcep import (
    AMCEPState,
    candidate_d_score_d_rho,
    candidate_score,
    original_d_score_d_rho,
    original_score,
    residual_converges,
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

    def test_candidate_penalizes_contradiction(self):
        low = AMCEPState(1.0, 5.0, 0.5, 10, 1.0)
        high = AMCEPState(2.0, 5.0, 0.5, 10, 1.0)
        self.assertLess(candidate_score(high), candidate_score(low))
        self.assertLessEqual(candidate_d_score_d_rho(low), 0)

    def test_convergence_domain(self):
        self.assertTrue(residual_converges(1.0, 0.5))
        self.assertTrue(residual_converges(0.0, 2.0))
        self.assertFalse(residual_converges(1.0, 1.0))
        self.assertFalse(residual_converges(1.0, -1.0))
        self.assertFalse(residual_converges(1.0, 1.1))

    def test_normalization_is_domain_constraint(self):
        for invalid in (0.0, -1.0):
            with self.assertRaises(ValueError):
                original_score(AMCEPState(1.0, 5.0, 0.5, 10, invalid))

    def test_nonfinite_inputs_rejected(self):
        with self.assertRaises(ValueError):
            original_score(AMCEPState(math.inf, 5.0, 0.5, 10, 1.0))


if __name__ == "__main__":
    unittest.main()
