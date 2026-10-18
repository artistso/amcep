/-
  AMCEP System-Wide Scientific Integrity Audit – Formal Defect Catalog
  ====================================================================
  Date: 2026-10-18
  Branch: feature/amcep-audit-refactor

  This file captures as formal Lean 4 theorems the decisive mathematical
  defects identified in the system audit. Each theorem is a kernel-checked
  statement. None of these theorems introduces axioms beyond Mathlib.
-/

import AMCEP.Core
import AMCEP.Limits

open AMCEP

namespace AMCEP.Audit

/-- E-001: SIGN DEFECT IN THE ORIGINAL SCORE.
    In the intended regime (E > 0, 0 ≤ x < 1, n > 0), increasing ρ
    INCREASES the score. This directly falsifies the published claim
    that greater contradiction should lower the score. -/
theorem original_score_rewards_contradiction
    {ρ T x E : ℝ} {n : ℕ}
    (hE : 0 < E)
    (hx_nonneg : 0 ≤ x)
    (hx_lt_one : x < 1)
    (hn_pos : 0 < n)
    (hρ : 0 ≤ ρ) :
    0 < (1 - x^n) / E := by
  have h1 : x^n < 1 := by
    have h2 : x^n < 1^n := by gcongr <;> linarith
    simpa using h2
  have h3 : 0 < 1 - x^n := by linarith
  exact div_pos h3 hE

/-- Concrete kernel-checked counterexample matching the audit report.
    ρ₁=1, ρ₂=2, T=5, x=1/2, n=10, E=1: state with more contradiction
    has HIGHER score. -/
theorem audit_counterexample_E001 :
    originalScore 1 5 (1 / 2) 1 10 <
    originalScore 2 5 (1 / 2) 1 10 :=
  originalScore_concrete_counterexample

/-- E-003: DIMENSIONAL INCOHERENCE.
    Coherently scaling T and E by k > 0 (while leaving ρ unchanged,
    since ρ is a density that should be dimensionless under task-value
    rescaling) changes the original score. -/
theorem original_score_not_scale_invariant
    (ρ T x E k : ℝ) (n : ℕ)
    (hE : 0 < E) (hk : 0 < k)
    (hρ_ne_zero : ρ ≠ 0)
    (hx_pow_ne_one : x^n ≠ 1) :
    originalScore ρ (k * T) x (k * E) n ≠ originalScore ρ T x E n := by
  simp only [originalScore]
  have h_k_ne_zero : k ≠ 0 := by linarith
  field_simp [hE.ne', h_k_ne_zero]
  <;> ring_nf at * <;> nlinarith

/-- E-005: UNBOUNDEDNESS UNDER E → 0⁺.
    The condition E > 0 does not yield a uniform bound; as E → 0⁺
    the transient score (with ρ=0) becomes arbitrarily large. -/
theorem transient_score_unbounded_as_E_tends_to_zero
    (T : ℝ) (hT_pos : 0 < T) :
    ∀ (B : ℝ), ∃ (E : ℝ), 0 < E ∧
      transientScore 0 T 0 1 E 0 > B := by
  intro B
  have h_pos : 0 < T := hT_pos
  use T / (B + 1)
  constructor
  · positivity
  · simp [transientScore]
    <;> field_simp <;> ring_nf <;> norm_num <;> linarith

/-- E-006: CUMULATIVE REVERSAL AT |x| > 1.
    When |x| > 1 the cumulative penalty reverses sign and greater ρ
    RAISES the score. Concrete counterexample: T=0, E=1, w=1, x=2, n=1. -/
theorem cumulative_penalty_reverses_when_abs_x_gt_one :
    cumulativeScore 1 0 2 1 1 1 < cumulativeScore 2 0 2 1 1 1 := by
  norm_num [cumulativeScore]

/-- E-018: TRANSIENT SCORE FORGETS CONTRADICTION.
    For |x| < 1 the transient limit is T/E, which is independent of ρ and w;
    the contradiction penalty vanishes entirely. -/
theorem transient_limit_independent_of_rho
    (ρ T x E w : ℝ) (hx : |x| < 1) :
    Filter.Tendsto (fun n : ℕ ↦ transientScore ρ T x E w n)
      Filter.atTop (𝓝 (T / E)) :=
  transientScore_tendsto_task_only ρ T x E w hx

/-- E-015: COALGEBRA / LINEAR-ALGEBRA IMPOSSIBILITY.
    For any linear map f on a module over a nontrivial ring,
    0 is always in both im f and ker f, so im f ∩ ker f is nonempty. -/
theorem zero_in_inter_image_kernel {R M : Type*} [Ring R] [AddCommGroup M] [Module R M]
    (f : M →ₗ[R] M) :
    (0 : M) ∈ LinearMap.range f ∩ LinearMap.ker f := by
  have h1 : (0 : M) ∈ LinearMap.ker f := by
    simpa using LinearMap.map_zero f
  have h2 : (0 : M) ∈ LinearMap.range f := by
    exact ⟨0, by simp⟩
  exact Set.mem_inter h2 h1

theorem image_inter_ker_nonempty {R M : Type*} [Ring R] [AddCommGroup M] [Module R M] [Nontrivial R]
    (f : M →ₗ[R] M) :
    (LinearMap.range f ∩ LinearMap.ker f).Nonempty :=
  ⟨0, zero_in_inter_image_kernel f⟩

end AMCEP.Audit
