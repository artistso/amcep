import AMCEP.Core

open Filter Topology

namespace AMCEP

/-- Powers of `|x|` tend to zero when `|x| < 1`. -/
theorem abs_pow_tendsto_zero {x : ℝ} (hx : |x| < 1) :
    Tendsto (fun n : ℕ ↦ |x| ^ n) atTop (𝓝 0) :=
  tendsto_pow_atTop_nhds_zero_of_lt_one (abs_nonneg x) hx

/-- The signed residual tends to zero throughout the strict unit interval. -/
theorem residual_tendsto_zero {ρ x : ℝ} (hx : |x| < 1) :
    Tendsto (fun n : ℕ ↦ ρ * x ^ n) atTop (𝓝 0) := by
  have hpow : Tendsto (fun n : ℕ ↦ x ^ n) atTop (𝓝 0) :=
    tendsto_pow_atTop_nhds_zero_of_abs_lt_one hx
  simpa using (tendsto_const_nhds.mul hpow)

/-- The residual is identically zero when `ρ = 0`, regardless of `x`. -/
theorem residual_tendsto_zero_of_rho_zero (x : ℝ) :
    Tendsto (fun n : ℕ ↦ (0 : ℝ) * x ^ n) atTop (𝓝 0) := by
  simpa using (tendsto_const_nhds : Tendsto (fun _ : ℕ ↦ (0 : ℝ)) atTop (𝓝 0))

/-- The transient score forgets contradiction when `|x| < 1`. -/
theorem transientScore_tendsto_task_only
    (ρ T x E w : ℝ) (hx : |x| < 1) :
    Tendsto (fun n : ℕ ↦ transientScore ρ T x E w n) atTop (𝓝 (T / E)) := by
  have hpow : Tendsto (fun n : ℕ ↦ |x| ^ n) atTop (𝓝 0) :=
    abs_pow_tendsto_zero hx
  have hscaled :
      Tendsto (fun n : ℕ ↦ w * ρ * |x| ^ n) atTop (𝓝 0) := by
    simpa [mul_assoc] using
      ((tendsto_const_nhds.mul tendsto_const_nhds).mul hpow)
  have hnum :
      Tendsto (fun n : ℕ ↦ T - w * ρ * |x| ^ n) atTop (𝓝 T) := by
    simpa using tendsto_const_nhds.sub hscaled
  simpa [transientScore, div_eq_mul_inv] using
    hnum.mul (tendsto_const_nhds :
      Tendsto (fun _ : ℕ ↦ E⁻¹) atTop (𝓝 E⁻¹))

/-- The cumulative score retains the limiting contradiction penalty when `|x| < 1`. -/
theorem cumulativeScore_tendsto_lasting_penalty
    (ρ T x E w : ℝ) (hx : |x| < 1) :
    Tendsto (fun n : ℕ ↦ cumulativeScore ρ T x E w n) atTop
      (𝓝 ((T - w * ρ) / E)) := by
  have hpow : Tendsto (fun n : ℕ ↦ |x| ^ n) atTop (𝓝 0) :=
    abs_pow_tendsto_zero hx
  have honeSub :
      Tendsto (fun n : ℕ ↦ 1 - |x| ^ n) atTop (𝓝 1) := by
    simpa using tendsto_const_nhds.sub hpow
  have hscaled :
      Tendsto (fun n : ℕ ↦ w * ρ * (1 - |x| ^ n)) atTop (𝓝 (w * ρ)) := by
    simpa [mul_assoc] using
      ((tendsto_const_nhds.mul tendsto_const_nhds).mul honeSub)
  have hnum :
      Tendsto (fun n : ℕ ↦ T - w * ρ * (1 - |x| ^ n)) atTop
        (𝓝 (T - w * ρ)) := by
    simpa using tendsto_const_nhds.sub hscaled
  simpa [cumulativeScore, div_eq_mul_inv] using
    hnum.mul (tendsto_const_nhds :
      Tendsto (fun _ : ℕ ↦ E⁻¹) atTop (𝓝 E⁻¹))

/-- At `x = 1`, a nonzero residual remains constant rather than tending to zero. -/
theorem residual_at_one (ρ : ℝ) (n : ℕ) :
    ρ * (1 : ℝ) ^ n = ρ := by
  simp

/-- At `x = -1`, every even-index residual equals `ρ`. -/
theorem residual_at_neg_one_even (ρ : ℝ) (n : ℕ) :
    ρ * (-1 : ℝ) ^ (2 * n) = ρ := by
  simp [pow_mul]

/-- At `x = -1`, every odd-index residual equals `-ρ`. -/
theorem residual_at_neg_one_odd (ρ : ℝ) (n : ℕ) :
    ρ * (-1 : ℝ) ^ (2 * n + 1) = -ρ := by
  simp [pow_add, pow_mul]

end AMCEP
