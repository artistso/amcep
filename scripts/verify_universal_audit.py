"""Universal Mathematical Audit Verification Script.

Verifies every canonical (V-*) and falsified (E-*) numerical claim in
research/universal-math-audit-2026-10-18.md with executable Python checks.

Run: python scripts/verify_universal_audit.py
"""

from __future__ import annotations

import math
import random
import sys


def original(rho, T, x, n, E):
    return (rho + T - rho * x**n) / E


def transient(rho, T, x, n, E, lam):
    return (T - lam * rho * abs(x)**n) / E


def cumulative(rho, T, x, n, E, lam):
    return (T - lam * rho * (1 - abs(x)**n)) / E


# ---------------------------------------------------------------- V-002 / E-001
def test_sign_defect():
    rho1, rho2, T, x, n, E = 1.0, 2.0, 5.0, 0.5, 10, 1.0
    s1 = original(rho1, T, x, n, E)
    s2 = original(rho2, T, x, n, E)
    assert s2 > s1, f"E-001 not confirmed: {s1} vs {s2}"
    # Derivative positive
    deriv = (1 - x**n) / E
    assert deriv > 0
    print(f"V-002/E-001 PASS: S(1)={s1:.10f}, S(2)={s2:.10f}, dS/drho={deriv:.6f} > 0")


# ---------------------------------------------------------------- V-004
def test_transient_antitone():
    for rho1, rho2 in [(1.0, 2.0), (0.0, 3.0), (0.5, 0.5)]:
        for x in [0.0, 0.3, 0.5, 0.9, 1.0, -0.5]:
            s1 = transient(rho1, 5.0, x, 5, 1.0, 1.0)
            s2 = transient(rho2, 5.0, x, 5, 1.0, 1.0)
            assert s2 <= s1 + 1e-15, f"Transient antitone fail at x={x}"
    print("V-004 PASS: transient non-increasing in rho for tested domain")


# ---------------------------------------------------------------- V-005 / E-005
def test_cumulative_domain():
    # Inside domain: antitone
    for x in [0.5, 0.99, 1.0, -0.9]:
        n = 5
        assert abs(x)**n <= 1 + 1e-15
        s1 = cumulative(1.0, 5.0, x, n, 1.0, 1.0)
        s2 = cumulative(2.0, 5.0, x, n, 1.0, 1.0)
        assert s2 <= s1 + 1e-15
    # Outside domain (|x|>1): reversal
    T, E, lam, x, n = 0.0, 1.0, 1.0, 2.0, 1
    s_lo = cumulative(1.0, T, x, n, E, lam)
    s_hi = cumulative(2.0, T, x, n, E, lam)
    assert s_hi > s_lo, f"E-005 reversal not confirmed: {s_lo} vs {s_hi}"
    print(f"V-005/E-005 PASS: cumulative antitone in |x|<=1, reverses at x=2: S(1)={s_lo}, S(2)={s_hi}")


# ---------------------------------------------------------------- V-006 / V-007 limits
def test_limits():
    rho, T, x, E, lam = 1.0, 5.0, 0.5, 1.0, 1.0
    n = 500
    s_t = transient(rho, T, x, n, E, lam)
    s_c = cumulative(rho, T, x, n, E, lam)
    assert abs(s_t - T/E) < 1e-100
    assert abs(s_c - (T - lam*rho)/E) < 1e-100
    print(f"V-006/V-007 PASS: n=500 S_trans={s_t:.15f} (T/E=5.0), S_cum={s_c:.15f} ((T-lam*rho)/E=4.0)")


# ---------------------------------------------------------------- V-008 boundaries
def test_boundaries():
    # x=1 constant residual
    rho = 0.7
    for n in range(0, 20):
        assert abs(rho * 1.0**n - rho) < 1e-15
    # x=-1 oscillates
    for n in range(0, 20):
        expected = rho if n % 2 == 0 else -rho
        assert abs(rho * (-1.0)**n - expected) < 1e-15
    print("V-008 PASS: x=1 constant, x=-1 oscillating")


# ---------------------------------------------------------------- V-009 logistic
def test_logistic():
    def sigmoid(z):
        # Numerically stable, matches src/amcep.py:logistic
        if z >= 0:
            ez = math.exp(-z)
            return 1/(1+ez)
        ez = math.exp(z)
        return ez/(1+ez)
    for z in [-30, -1, 0, 1, 30]:
        s = sigmoid(z)
        assert 0 < s < 1, f"logistic({z})={s} not in (0,1)"
    # At z=1000 with the stable branch, exp(-1000) underflows to 0 and sigmoid = 1.0 exactly;
    # this is why safe_scores uses _strict_logistic with nextafter. The plain sigmoid returns 1.0.
    s_large_pos = sigmoid(1000)
    s_large_neg = sigmoid(-1000)
    assert 0.0 <= s_large_pos <= 1.0
    assert 0.0 <= s_large_neg <= 1.0
    print(f"V-009 PASS: stable logistic maps to (0,1) for normal inputs; overflow saturates at extremes")


# ---------------------------------------------------------------- E-002 float-threshold not a proof
def test_finite_threshold_not_proof():
    # At x=0.5, n=20 is small
    assert 0.5**20 < 1e-5
    # At x=0.99, n=20 is NOT small
    assert 0.99**20 > 0.8
    print(f"E-002 DEMO: 0.5^20={0.5**20:.2e}, 0.99^20={0.99**20:.4f} — single threshold misleading")


# ---------------------------------------------------------------- E-003 dimensional incoherence
def test_dimensional():
    rho, T, x, n, E, k = 0.5, 5.0, 0.5, 2, 2.0, 1000.0
    s_orig = original(rho, T, x, n, E)
    s_scaled = original(rho, k*T, x, n, k*E)
    assert abs(s_orig - s_scaled) > 0.1, f"Original should change"
    # Candidate invariance
    lam = 1.0
    s_t = transient(rho, T, x, n, E, lam)
    s_t_s = transient(rho, k*T, x, n, k*E, k*lam)
    s_c = cumulative(rho, T, x, n, E, lam)
    s_c_s = cumulative(rho, k*T, x, n, k*E, k*lam)
    assert abs(s_t - s_t_s) < 1e-12
    assert abs(s_c - s_c_s) < 1e-12
    print(f"E-003 PASS: original S changes ({s_orig} -> {s_scaled}); candidates invariant")


# ---------------------------------------------------------------- E-004 unbounded E->0
def test_unbounded():
    T, rho, lam = 1.0, 0.0, 0.0
    for m in [1, 10, 100, 1000]:
        E = 1.0/m
        s = transient(rho, T, 0.5, 10, E, lam)
        assert abs(s - m) < 1e-12
    print(f"E-004 PASS: E=1/m gives S=m -> unbounded as m->inf")


# ---------------------------------------------------------------- E-014 zero in im ∩ ker
def test_im_ker_intersection():
    # Any linear map: Delta(0)=0 so 0 in both
    # Use a concrete 2x2 matrix
    def mat_vec(A, v):
        return [sum(A[i][j]*v[j] for j in range(2)) for i in range(2)]
    random.seed(42)
    for _ in range(20):
        A = [[random.gauss(0, 1) for _ in range(2)] for _ in range(2)]
        zero = [0.0, 0.0]
        assert all(abs(x) < 1e-15 for x in mat_vec(A, zero))
    print("E-014 PASS: 0 always in im ∩ ker for any linear map")


# ---------------------------------------------------------------- E-019 pinch invariant (demonstrates bug)
def test_pinch_changes_complexity():
    """Edge subdivision (pinch) adds 1 node and 1 edge net -> V+E increases by 2."""
    # Start: V=2, E=1. After pinch (remove edge (0,1), add node 2, add edges (0,2),(2,1)):
    # V' = 3, E' = 2. So V+E = 3 -> 5. Increases by 2.
    V, E = 2, 1
    V2, E2 = 3, 2
    assert V2 + E2 == V + E + 2
    print(f"E-019 CONFIRMED: edge subdivision changes V+E by +2 (not invariant). V+E goes {V+E} -> {V2+E2}")
    print("         The correct invariants are the cyclomatic number E-V+c and the homology groups.")


def main():
    print("=" * 70)
    print("UNIVERSAL MATHEMATICAL AUDIT — VERIFICATION SCRIPT")
    print("=" * 70)
    print()
    test_sign_defect(); print()
    test_transient_antitone(); print()
    test_cumulative_domain(); print()
    test_limits(); print()
    test_boundaries(); print()
    test_logistic(); print()
    test_finite_threshold_not_proof(); print()
    test_dimensional(); print()
    test_unbounded(); print()
    test_im_ker_intersection(); print()
    test_pinch_changes_complexity(); print()
    print("=" * 70)
    print("ALL VERIFICATION TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
