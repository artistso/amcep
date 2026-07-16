# Fail-closed AMCEP candidate-score contract

## Status

This contract narrows the executable domain of the transient and cumulative candidate scores after the robustness benchmark exposed three distinct failures:

1. the original score is dimensionally inconsistent under the declared unit interpretation;
2. the cumulative candidate can reverse contradiction monotonicity when `|x|^n > 1`;
3. every unbounded score can become arbitrarily large as positive normalization approaches zero.

The contract is an engineering control. It is not evidence that either candidate is empirically valid, morally correct, fair, or physically meaningful.

## Inputs

The application-facing evaluator requires:

- a validated `AMCEPState`;
- an explicit positive `normalization_floor` in the same unit as `E`;
- a persistence policy;
- an explicit positive dimensionless output temperature.

No default normalization floor is supplied because a universal floor would be an unsupported domain claim.

## Persistence policies

### Reject

For positive depth, the evaluator preserves

\[
p_n = |x|^n
\]

and rejects requests with `|x| > 1`. This directly enforces the domain needed for cumulative contradiction monotonicity. At depth zero, persistence is exactly one.

### Squash

The evaluator defines

\[
q(x)=\frac{|x|}{1+|x|},\qquad p_n=q(x)^n.
\]

For finite `x` and nonnegative `n`, `p_n` remains in `[0,1]`. This prevents the cumulative penalty factor `1-p_n` from becoming negative.

This transform is not derived from the original AMCEP materials. It is a bounded candidate map and must be justified separately for every application.

## Contracted scores

\[
S_{\mathrm{transient}}
=\frac{T-\lambda\rho p_n}{E},
\]

\[
S_{\mathrm{cumulative}}
=\frac{T-\lambda\rho(1-p_n)}{E}.
\]

For `E > 0`, `lambda >= 0`, and `0 <= p_n <= 1`, their contradiction derivatives satisfy

\[
\frac{\partial S_{\mathrm{transient}}}{\partial\rho}
=-\frac{\lambda p_n}{E}\le0,
\]

\[
\frac{\partial S_{\mathrm{cumulative}}}{\partial\rho}
=-\frac{\lambda(1-p_n)}{E}\le0.
\]

The contract therefore prevents the known contradiction-reward reversal. It does not determine whether `rho`, `lambda`, or the persistence map are valid measurements.

## Normalization floor

A request is rejected when

\[
E<E_{\min}.
\]

The evaluator does not silently replace `E` with the floor. Silent clamping would change the stated model and conceal the rejected domain.

The floor controls only one known instability. It does not produce a universal score bound unless the numerator is also bounded by independently justified input domains.

## Bounded display transform

For display or downstream ranking, the contracted raw score may be mapped through

\[
B(S)=\frac{1}{1+e^{-S/\tau}},\qquad \tau>0.
\]

This transform is monotone, so it preserves pairwise ordering and the sign of contradiction monotonicity. It compresses magnitude into `(0,1)` but does not calibrate probability, utility, morality, or confidence.

## Unit contract

Under a coherent change of task-value units by positive factor `k`, the contract applies

\[
T'=kT,\quad E'=kE,\quad \lambda'=k\lambda,
\quad E'_{\min}=kE_{\min}.
\]

Dimensionless quantities `rho`, `x`, `n`, persistence policy, and output temperature are unchanged. Both contracted raw scores remain invariant under this transformation.

## Fail-closed behavior

The evaluator rejects:

- nonfinite inputs;
- negative contradiction density;
- negative depth;
- nonpositive normalization;
- negative penalty weight;
- normalization below the declared floor;
- invalid policy names;
- nonpositive or nonfinite output temperature;
- `|x| > 1` under the reject policy at positive depth;
- nonfinite arithmetic results.

A rejected request is not assigned score zero and is not silently repaired.

## Remaining evidence requirements

Before application, the project still needs:

- operational definitions and measurement studies for every input;
- a preregistered decision problem and baseline;
- uncertainty propagation and abstention behavior;
- sensitivity to manipulation and strategic reporting;
- subgroup and distribution-shift analysis;
- independently collected external data;
- independent replication.
