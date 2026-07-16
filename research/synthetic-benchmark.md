# AMCEP Synthetic Falsification Benchmark

## Purpose

This benchmark tests whether the executable score families behave as specified under controlled data-generating processes. Because the generator defines the ground truth, the benchmark can detect implementation defects, sign errors, missing-data behavior, calibration failures, and regime dependence.

It does **not** establish that any synthetic regime describes the real world, that an AMCEP score measures morality, or that a candidate should be used for governance or allocation.

## Ground-truth regimes

The benchmark deliberately includes three incompatible regimes.

### Task-only

\[
y=\frac{T}{E}.
\]

Contradiction has no effect. The task-only baseline is the oracle by construction.

### Transient contradiction

\[
y=\frac{T-\lambda\rho|x|^n}{E}.
\]

Contradiction represents a repairable residual that decays with depth when \(|x|<1\). The transient candidate is the oracle by construction.

### Cumulative contradiction

\[
y=\frac{T-\lambda\rho(1-|x|^n)}{E}.
\]

Contradiction represents a lasting accumulated penalty. The cumulative candidate is the oracle by construction.

The presence of multiple regimes is intentional. A model matching the equation used to generate a clean dataset should win. This is a software and identifiability sanity check, not evidence of universal superiority.

## Compared models

1. Task-only baseline: \(T/E\).
2. Linear penalty baseline: \((T-\lambda\rho)/E\).
3. Original source equation.
4. Transient candidate.
5. Cumulative candidate.

## Stress matrix

Each regime is evaluated under:

- clean observation;
- Gaussian observation noise;
- noise plus missing inputs;
- noise plus targeted contradiction corruption.

The default matrix contains twelve deterministic scenarios with distinct recorded seeds.

## Missing-data rule

Missing required inputs produce explicit abstention. They are not silently converted to zero. Coverage is reported as a primary metric.

The task-only model requires only \(T\) and \(E\), so its coverage can exceed models that also require \(\rho\) and \(x\). This is a legitimate complexity cost rather than an error to hide.

## Adversarial corruption

The initial targeted attack replaces observed contradiction density with

\[
\rho_{obs}\leftarrow1-\rho_{obs}.
\]

The latent target remains unchanged. This tests sensitivity to reversed contradiction ordering. Future versions must add severity manipulation, missingness attacks, normalization attacks, and coordinated multi-variable corruption.

## Metrics

For every model and scenario, the benchmark reports:

- observation count;
- coverage;
- mean absolute error;
- root mean squared error;
- Pearson correlation;
- pairwise ranking accuracy;
- linear calibration intercept and slope;
- contradiction monotonicity violation rate.

The monotonicity intervention fixes all latent covariates and changes \(\rho\) from 0.25 to 0.75. A model violates the contradiction gate when its score strictly increases.

## Expected structural outcomes

These are testable software expectations, not empirical conclusions:

- In a clean task-only regime, the task-only model has zero error.
- In a clean transient regime, the transient model has zero error.
- In a clean cumulative regime, the cumulative model has zero error.
- In the generated domain \(0<x<1\) and \(n\ge1\), the original source equation has a contradiction-violation rate of one.
- Transient and cumulative candidates have zero contradiction violations in their declared generated domain.
- Missing inputs reduce coverage rather than creating fabricated zero-valued evidence.

A failure of these expectations indicates an implementation, artifact, or protocol defect.

## Reproducible artifacts

The runner emits:

```text
results/synthetic/<run>/
  manifest.json
  parameters.json
  metrics.json
  predictions.csv
  environment.txt
  checksums.txt
```

The manifest records the experiment identifier, commit, seed, scenario count, model set, claim IDs under test, and interpretation boundary. Checksums cover all other output files.

## Reproduction

```bash
python scripts/run_synthetic_benchmark.py \
  --output-dir results/synthetic/latest \
  --sample-size 300 \
  --seed 20260716
```

## Promotion boundary

Passing this benchmark may justify `numerically-supported` only for the exact implementation properties and synthetic domains tested. It cannot justify `empirically-supported`, `formally-verified`, or universal language.

A real-world promotion requires operational definitions, external data, locked evaluation, accepted baselines, uncertainty, manipulation analysis, and independent replication.