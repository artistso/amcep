"""AMCEP System-Wide Scientific Integrity Audit: Verification Script.

Run with: python -m pytest tests/test_system_audit.py -v
or:        python scripts/verify_audit.py

This script numerically verifies every VERIFIED and FALSIFIED claim from
the audit report (research/system-audit-2026-10-18.md) using exact rational
arithmetic where possible and high-precision floats otherwise.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction


def original_score(rho, T, x, n, E):
    return (rho + T - rho * x**n) / E


def transient_score(rho, T, x, n, E, lam):
    return (T - lam * rho * abs(x) ** n) / E


def cumulative_score(rho, T, x, n, E, lam):
    return (T - lam * rho * (1 - abs(x) ** n)) / E


def test_V001_original_score_algebraically_well_defined():
    """V-001: original score is defined for stated domain."""
    assert math.isfinite(original_score(1.0, 5.0, 0.5, 10, 1.0))
    # At E=0 should raise (we check)
    try:
        original_score(1.0, 5.0, 0.5, 10, 0.0)
        assert False, "E=0 should not produce a finite result"
    except ZeroDivisionError:
        pass
    print("V-001 PASS")


def test_V002_E001_original_sign_defect():
    """V-002 / E-001: Increasing T raises score; increasing rho also raises score (falsifying intended penalty)."""
    rho, T1, T2, x, n, E = 1.0, 5.0, 6.0, 0.5, 10, 1.0
    s1 = original_score(rho, T1, x, n, E)
    s2 = original_score(rho, T2, x, n, E)
    assert s2 > s1, "V-002 FAIL: increasing T should raise score"
    print(f"  V-002 T-monotonicity PASS: S(T=5)={s1:.6f} < S(T=6)={s2:.6f}")

    # Now E-001: increasing rho RAISES score (contradicts claimed penalty)
    rho1, rho2 = 1.0, 2.0
    s_rho1 = original_score(rho1, 5.0, 0.5, 10, 1.0)
    s_rho2 = original_score(rho2, 5.0, 0.5, 10, 1.0)
    assert s_rho2 > s_rho1, "E-001 verification: more rho -> higher score (CONFIRMS defect)"
    print(f"  E-001 SIGN DEFECT CONFIRMED: S(rho=1)={s_rho1:.10f}, S(rho=2)={s_rho2:.10f}")
    print(f"    Greater contradiction yields GREATER score -- this is the decisive falsification.")


def test_V004_concrete_counterexample():
    """V-004: Lean-verified counterexample rho=1,2; T=5; x=1/2; n=10; E=1."""
    s1 = original_score(1, 5, Fraction(1, 2), 10, 1)
    s2 = original_score(2, 5, Fraction(1, 2), 10, 1)
    # With Fractions these are exact rational numbers
    assert s2 > s1
    print(f"  V-004 Lean counterexample exact: S(1)={float(s1):.10f}, S(2)={float(s2):.10f}")


def test_V005_V006_transient_antitone():
    """V-005, V-006: transient score is non-increasing in rho under E>0, lam>=0."""
    for rho1, rho2 in [(1.0, 2.0), (0.0, 5.0), (3.0, 3.0)]:
        for x in [0.5, 0.0, 0.99, -0.5]:
            s1 = transient_score(rho1, 5.0, x, 5, 1.0, 1.0)
            s2 = transient_score(rho2, 5.0, x, 5, 1.0, 1.0)
            assert s2 <= s1 + 1e-15, f"Transient antitone failure at x={x}"
    print("V-005/V-006 PASS: transient score non-increasing in rho")


def test_V007_V008_cumulative_antitone_in_domain():
    """V-007, V-008: cumulative antitone when |x|^n <= 1."""
    for rho1, rho2 in [(1.0, 2.0), (0.0, 5.0)]:
        for x in [0.5, 0.0, 0.99, 1.0, -0.9]:
            n = 5
            assert abs(x)**n <= 1.0 + 1e-15
            s1 = cumulative_score(rho1, 5.0, x, n, 1.0, 1.0)
            s2 = cumulative_score(rho2, 5.0, x, n, 1.0, 1.0)
            assert s2 <= s1 + 1e-15, f"Cumulative antitone failure at x={x}"
    print("V-007/V-008 PASS: cumulative score non-increasing in rho for |x|^n <= 1")


def test_E006_cumulative_reverses_outside_domain():
    """E-006: cumulative penalizes WRONG way when |x| > 1."""
    T, E, lam, x, n = 0.0, 1.0, 1.0, 2.0, 1
    s1 = cumulative_score(1.0, T, x, n, E, lam)
    s2 = cumulative_score(2.0, T, x, n, E, lam)
    assert s2 > s1, "E-006: x=2, n=1 should make cumulative score INCREASE with rho"
    print(f"E-006 CUMULATIVE REVERSAL CONFIRMED: S(rho=1)={s1}, S(rho=2)={s2}")


def test_V011_V012_V013_limit_behavior():
    """V-011, V-012, V-013: limit behavior for |x|<1."""
    rho, T, x, E, lam = 1.0, 5.0, 0.5, 1.0, 1.0
    for n_pow in [10, 50, 100, 500]:
        s_trans = transient_score(rho, T, x, n_pow, E, lam)
        s_cum = cumulative_score(rho, T, x, n_pow, E, lam)
    # At n=500 with x=0.5, x^n = 0.5^500 is effectively 0
    assert abs(s_trans - T/E) < 1e-100, "Transient should converge to T/E"
    assert abs(s_cum - (T - lam*rho)/E) < 1e-100, "Cumulative should converge to (T-lam*rho)/E"
    print(f"V-011/V-012/V-013 PASS: n=500 S_trans={s_trans:.15f} (limit T/E=5.0), S_cum={s_cum:.15f} (limit (T-lam*rho)/E=4.0)")


def test_V014_V015_boundary_behavior():
    """V-014, V-015: x=1 constant residual; x=-1 oscillates."""
    rho = 1.0
    for n in range(0, 20):
        val = rho * (1.0)**n
        assert abs(val - rho) < 1e-15
    for n in range(0, 20):
        expected = rho if n % 2 == 0 else -rho
        val = rho * (-1.0)**n
        assert abs(val - expected) < 1e-15
    print("V-014/V-015 PASS: x=1 constant, x=-1 oscillating")


def test_E003_dimensional_incoherence():
    """E-003: original score changes under coherent T,E scaling."""
    rho, T, x, n, E, k = 0.5, 5.0, 0.5, 2, 2.0, 1000.0
    s_orig = original_score(rho, T, x, n, E)
    s_scaled = original_score(rho, k*T, x, n, k*E)
    # rho is NOT scaled -> score changes
    assert s_orig != s_scaled, "Original score should NOT be invariant when rho is not co-scaled"
    print(f"E-003 DIMENSIONAL INCOHERENCE: original S={s_orig}, S(k*T,k*E)={s_scaled} (changed by {abs(s_orig-s_scaled):.6f})")

    # Transient and cumulative ARE invariant when lam is co-scaled
    lam = 1.0
    s_t = transient_score(rho, T, x, n, E, lam)
    s_t_scaled = transient_score(rho, k*T, x, n, k*E, k*lam)
    s_c = cumulative_score(rho, T, x, n, E, lam)
    s_c_scaled = cumulative_score(rho, k*T, x, n, k*E, k*lam)
    assert abs(s_t - s_t_scaled) < 1e-12
    assert abs(s_c - s_c_scaled) < 1e-12
    print(f"  Candidates ARE coherent: S_trans={s_t} invariant, S_cum={s_c} invariant")


def test_E005_unbounded_near_E_zero():
    """E-005: E>0 does NOT bound the score."""
    T, rho, lam = 1.0, 0.0, 0.0
    scores = []
    for m in [1, 10, 100, 1000]:
        E = 1.0 / m
        s = transient_score(rho, T, 0.5, 10, E, lam)
        scores.append(s)
    assert scores[-1] > 100, "Score should become large as E->0"
    print(f"E-005 UNBOUNDED: E=1 -> S={scores[0]}, E=0.001 -> S={scores[-1]}")


def test_E004_finite_float_not_a_proof():
    """E-004: showing small value at n=20 doesn't prove convergence; x=0.99 takes much longer."""
    x1, x2 = 0.5, 0.99
    n = 20
    v1 = x1**n
    v2 = x2**n
    print(f"E-004 NUMERICAL vs PROOF: at n=20, 0.5^{n}={v1:.2e} (small), 0.99^{n}={v2:.4f} (NOT small, ~0.82)")
    print(f"  n=20 threshold check would MISLEADINGLY suggest convergence for x=0.99 is 'close'")
    # Convergence requires for ALL epsilon, EXISTS N... not a single check


def mat_vec(A, v):
    """Plain Python matrix-vector multiply (3x3)."""
    return [sum(A[i][j] * v[j] for j in range(3)) for i in range(3)]


def test_E015_zero_intersection_impossible():
    """E-015: For any linear map, 0 is always in im(Delta) ∩ ker(Delta).

    Proof: For any linear map Delta on vector space V:
      - Delta(0) = 0  =>  0 ∈ ker(Delta)
      - Delta(0) = 0  =>  0 ∈ im(Delta) (witnessed by preimage 0)
    Hence 0 ∈ im(Delta) ∩ ker(Delta) always. The condition im ∩ ker = ∅
    is impossible in any vector space.
    """
    import random
    random.seed(42)
    for _ in range(20):
        A = [[random.gauss(0, 1) for _ in range(3)] for _ in range(3)]
        zero = [0.0, 0.0, 0.0]
        result = mat_vec(A, zero)
        assert all(abs(r) < 1e-15 for r in result), "A @ 0 must equal 0"
    print("E-015 PASS: 0 always in im ∩ ker for any linear map")


def test_E018_transient_forgets():
    """E-018: transient penalty vanishes asymptotically."""
    rho, T, x, E, lam = 1.0, 5.0, 0.5, 1.0, 1.0
    n = 100
    s = transient_score(rho, T, x, n, E, lam)
    assert abs(s - T/E) < 1e-20, "Transient limit is T/E independent of rho"
    print(f"E-018 TRANSIENT FORGETS: at n=100 S_trans={s:.15f} (same as T/E=5.0 regardless of rho={rho})")


def main():
    print("="*70)
    print("AMCEP SYSTEM AUDIT VERIFICATION SCRIPT")
    print("="*70)
    print()
    test_V001_original_score_algebraically_well_defined()
    print()
    test_V002_E001_original_sign_defect()
    print()
    test_V004_concrete_counterexample()
    print()
    test_V005_V006_transient_antitone()
    print()
    test_V007_V008_cumulative_antitone_in_domain()
    print()
    test_E006_cumulative_reverses_outside_domain()
    print()
    test_V011_V012_V013_limit_behavior()
    print()
    test_V014_V015_boundary_behavior()
    print()
    test_E003_dimensional_incoherence()
    print()
    test_E005_unbounded_near_E_zero()
    print()
    test_E004_finite_float_not_a_proof()
    print()
    test_E015_zero_intersection_impossible()
    print()
    test_E018_transient_forgets()
    print()
    print("="*70)
    print("ALL VERIFICATION TESTS PASSED")
    print("See research/system-audit-2026-10-18.md for full report.")
    print("="*70)


if __name__ == "__main__":
    main()
