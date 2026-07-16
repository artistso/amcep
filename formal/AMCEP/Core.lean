import Mathlib

namespace AMCEP

/-- The original AMCEP score exactly as stated in the source materials. -/
def originalScore (ρ T x E : ℝ) (n : ℕ) : ℝ :=
  (ρ + T - ρ * x ^ n) / E

/-- A transient contradiction-penalty candidate. -/
def transientScore (ρ T x E λ : ℝ) (n : ℕ) : ℝ :=
  (T - λ * ρ * |x| ^ n) / E

/-- A cumulative contradiction-penalty candidate. -/
def cumulativeScore (ρ T x E λ : ℝ) (n : ℕ) : ℝ :=
  (T - λ * ρ * (1 - |x| ^ n)) / E

/-- Exact difference identity for changing contradiction density in the original score. -/
theorem originalScore_sub_originalScore
    (ρ₁ ρ₂ T x E : ℝ) (n : ℕ) :
    originalScore ρ₂ T x E n - originalScore ρ₁ T x E n =
      (ρ₂ - ρ₁) * (1 - x ^ n) / E := by
  unfold originalScore
  ring

/-- Exact difference identity for changing operator power in the original score. -/
theorem originalScore_operatorPower_sub
    (ρ T₁ T₂ x E : ℝ) (n : ℕ) :
    originalScore ρ T₂ x E n - originalScore ρ T₁ x E n =
      (T₂ - T₁) / E := by
  unfold originalScore
  ring

/-- Increasing operator power strictly increases the original score when `E > 0`. -/
theorem originalScore_strictMono_operatorPower
    {ρ T₁ T₂ x E : ℝ} {n : ℕ}
    (hT : T₁ < T₂) (hE : 0 < E) :
    originalScore ρ T₁ x E n < originalScore ρ T₂ x E n := by
  have hdiff :
      0 < originalScore ρ T₂ x E n - originalScore ρ T₁ x E n := by
    rw [originalScore_operatorPower_sub]
    exact div_pos (sub_pos.mpr hT) hE
  linarith

/-- The original score strictly rewards more contradiction whenever `x^n < 1`. -/
theorem originalScore_strictMono_rho
    {ρ₁ ρ₂ T x E : ℝ} {n : ℕ}
    (hρ : ρ₁ < ρ₂) (hE : 0 < E) (hx : x ^ n < 1) :
    originalScore ρ₁ T x E n < originalScore ρ₂ T x E n := by
  have hdiff :
      0 < originalScore ρ₂ T x E n - originalScore ρ₁ T x E n := by
    rw [originalScore_sub_originalScore]
    exact div_pos (mul_pos (sub_pos.mpr hρ) (sub_pos.mpr hx)) hE
  linarith

/-- A concrete exact counterexample to the intended contradiction penalty. -/
theorem originalScore_concrete_counterexample :
    originalScore 1 5 (1 / 2) 1 10 <
      originalScore 2 5 (1 / 2) 1 10 := by
  norm_num [originalScore]

/-- Exact difference identity for the transient candidate. -/
theorem transientScore_sub_transientScore
    (ρ₁ ρ₂ T x E λ : ℝ) (n : ℕ) :
    transientScore ρ₂ T x E λ n - transientScore ρ₁ T x E λ n =
      (-(λ * (ρ₂ - ρ₁) * |x| ^ n)) / E := by
  unfold transientScore
  ring

/-- The transient candidate never rewards more contradiction under its declared domain. -/
theorem transientScore_antitone_rho
    {ρ₁ ρ₂ T x E λ : ℝ} {n : ℕ}
    (hρ : ρ₁ ≤ ρ₂) (hE : 0 < E) (hλ : 0 ≤ λ) :
    transientScore ρ₂ T x E λ n ≤ transientScore ρ₁ T x E λ n := by
  have hterm : 0 ≤ λ * (ρ₂ - ρ₁) * |x| ^ n := by
    exact mul_nonneg
      (mul_nonneg hλ (sub_nonneg.mpr hρ))
      (pow_nonneg (abs_nonneg x) n)
  have hdiff :
      transientScore ρ₂ T x E λ n - transientScore ρ₁ T x E λ n ≤ 0 := by
    rw [transientScore_sub_transientScore, div_eq_mul_inv]
    exact mul_nonpos_of_nonpos_of_nonneg
      (neg_nonpos.mpr hterm)
      (le_of_lt (inv_pos.mpr hE))
  linarith

/-- Exact difference identity for the cumulative candidate. -/
theorem cumulativeScore_sub_cumulativeScore
    (ρ₁ ρ₂ T x E λ : ℝ) (n : ℕ) :
    cumulativeScore ρ₂ T x E λ n - cumulativeScore ρ₁ T x E λ n =
      (-(λ * (ρ₂ - ρ₁) * (1 - |x| ^ n))) / E := by
  unfold cumulativeScore
  ring

/-- The cumulative candidate never rewards more contradiction when `|x|^n ≤ 1`. -/
theorem cumulativeScore_antitone_rho
    {ρ₁ ρ₂ T x E λ : ℝ} {n : ℕ}
    (hρ : ρ₁ ≤ ρ₂) (hE : 0 < E) (hλ : 0 ≤ λ)
    (hx : |x| ^ n ≤ 1) :
    cumulativeScore ρ₂ T x E λ n ≤ cumulativeScore ρ₁ T x E λ n := by
  have hterm : 0 ≤ λ * (ρ₂ - ρ₁) * (1 - |x| ^ n) := by
    exact mul_nonneg
      (mul_nonneg hλ (sub_nonneg.mpr hρ))
      (sub_nonneg.mpr hx)
  have hdiff :
      cumulativeScore ρ₂ T x E λ n - cumulativeScore ρ₁ T x E λ n ≤ 0 := by
    rw [cumulativeScore_sub_cumulativeScore, div_eq_mul_inv]
    exact mul_nonpos_of_nonpos_of_nonneg
      (neg_nonpos.mpr hterm)
      (le_of_lt (inv_pos.mpr hE))
  linarith

/-- At `x = 1`, the transient candidate retains its full contradiction penalty. -/
theorem transientScore_at_one
    (ρ T E λ : ℝ) (n : ℕ) :
    transientScore ρ T 1 E λ n = (T - λ * ρ) / E := by
  simp [transientScore]

/-- At `x = 1`, the cumulative candidate applies no accumulated penalty. -/
theorem cumulativeScore_at_one
    (ρ T E λ : ℝ) (n : ℕ) :
    cumulativeScore ρ T 1 E λ n = T / E := by
  simp [cumulativeScore]

end AMCEP
