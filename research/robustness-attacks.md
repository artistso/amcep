# AMCEP robustness attacks, tranche 1

## Status

This protocol tests structural and numerical behavior of three AMCEP score families. It is not evidence of moral truth, fairness, physical law, or real-world predictive validity.

## Operational split

The benchmark separates contradiction prevalence `p` from contradiction severity `s` and defines

\[
\rho_{\mathrm{eff}} = p s.
\]

This exposes an assumption hidden when a single scalar `rho` represents both quantities.

## Attacks

### Coherent unit rescaling

A task-value unit change applies

\[
T'=kT,\qquad E'=kE,\qquad \lambda'=k\lambda,
\]

while `p`, `s`, `x`, and `n` remain dimensionless. The transient and cumulative candidates are invariant. The original equation generally changes because it adds dimensionless `rho` directly to `T`.

### Severity intervention

Severity is increased from `0.25` to `2.0` while all other inputs remain fixed. A contradiction-penalizing score must not increase. In the intended `E > 0`, `|x| < 1`, `n > 0` domain, the original formula rewards higher severity; the two candidates do not.

### Persistence-boundary shift

`|x|` is moved from `[0.05, 0.95]` to `[0.97, 1.03]`, with both signs, exposing the transition between decay, boundary behavior, oscillation, and growth.

### Small-normalization stress

`E` is moved from `[0.5, 2.0]` to a log-uniform interval from `10^-4` to `10^-1`. All three unbounded score families can become arbitrarily sensitive as positive `E` approaches zero. Domain validity is not numerical robustness.

### High-severity distribution shift

Severity is moved from `[0, 1]` to `[1, 10]` without changing the equations after results are observed.

### Independent arithmetic path

Every score is independently reimplemented with 60-digit `Decimal` arithmetic and compared case by case with the production float implementation. Agreement validates arithmetic implementation only.

## Locked matrix

Five deterministic groups are evaluated for each score family: in-distribution, persistence boundary, small normalization, high severity, and all attacks combined. CI uses 400 cases per group and seed `20260716`.

Metrics include non-finite output rate, mean and 95th-percentile absolute score, severity monotonicity violations, coherent unit-rescaling violations, maximum rescaling error, and maximum float-versus-Decimal disagreement.

## Interpretation gates

- Passing arithmetic agreement is software evidence, not model evidence.
- Surviving these attacks leaves a model as a candidate.
- Small-`E` amplification requires an application-level domain, uncertainty policy, clipping rule, or bounded transformation.
- Synthetic findings cannot promote a claim to `empirically-supported`.
- Negative findings remain public and the locked seed and ranges cannot be changed post hoc.
