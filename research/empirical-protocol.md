# AMCEP Empirical Stress-Test Protocol

## Objective

Determine whether any AMCEP score family provides measurable value beyond simpler baselines under declared domains, without conflating numerical output with moral truth.

## Primary hypotheses

- **H1 — Ranking:** an AMCEP candidate ranks outcomes more accurately than declared baselines on a locked test set.
- **H2 — Constraint compliance:** an AMCEP candidate reduces hard-constraint violations without unacceptable loss in task performance.
- **H3 — Robustness:** performance degrades more slowly under noise, contradiction injection, missing data, and distribution shift.
- **H4 — Calibration:** score values correspond to observed frequencies or losses under a declared calibration map.

Failure to reject the relevant null hypothesis leaves the candidate unsupported.

## Candidate models

1. Original source equation, retained only as a falsified control.
2. Transient contradiction penalty.
3. Cumulative contradiction penalty.
4. Bounded logistic transformations of candidates 2 and 3.
5. Ablations with no contradiction term, no recursion term, and fixed normalization.

## Baselines

At minimum:

- task-value-only score;
- linear weighted sum;
- max-min allocation;
- proportional fairness;
- Nash social welfare;
- leximin;
- random feasible allocation;
- domain-specific constrained optimizer.

A candidate must beat simple baselines before comparisons with complex systems are interpreted.

## Phase A — Synthetic ground-truth benchmark

Generate datasets with controlled:

- contradiction prevalence;
- contradiction severity;
- observation noise;
- missingness;
- adversarial injection;
- temporal persistence;
- repairable versus permanent contradictions;
- distribution shift.

Because the generator exposes ground truth, this phase tests identifiability and whether the score responds in the mathematically intended direction.

### Metrics

- rank correlation;
- pairwise ranking accuracy;
- Brier score or log loss when probabilistic;
- expected calibration error;
- false-positive and false-negative rates;
- sensitivity to each parameter;
- worst-case regret;
- constraint-violation rate;
- stability under perturbation.

## Phase B — Resource-allocation benchmark

Use tasks with explicit agents, resources, utilities, feasibility constraints, and protected failure conditions.

Report:

- total welfare;
- minimum welfare;
- Nash social welfare;
- Pareto inefficiency gap;
- envy or justified domain-specific fairness metrics;
- feasibility violations;
- computational cost;
- robustness to misreported inputs.

No single metric is declared equivalent to fairness.

## Phase C — Held-out and adversarial testing

Split data into:

- development set;
- calibration set;
- locked in-distribution test set;
- locked out-of-distribution test set;
- adversarial set.

Model form, parameter ranges, baselines, and primary metrics are frozen before locked evaluation.

## Statistical requirements

Every result must include:

- sample size;
- point estimate;
- confidence or credible interval;
- effect size;
- multiple-comparison correction when applicable;
- random seed manifest;
- raw result artifact;
- exact code revision.

A percentage improvement without denominator, baseline, uncertainty, and raw data is rejected.

## Reproducibility package

Each experiment must emit:

```text
results/<experiment-id>/
  manifest.json
  parameters.json
  metrics.json
  predictions.csv
  environment.txt
  checksums.txt
```

`manifest.json` records the Git commit, dataset revision, command, timestamp, seed, candidate model, and claim IDs under test.

## Promotion criteria

A claim may move to `empirically-supported` only when:

1. the protocol was fixed before locked evaluation;
2. raw artifacts are present;
3. the result is reproducible from a clean environment;
4. the candidate beats relevant simple baselines on primary metrics;
5. failure modes and negative results are reported;
6. the claim is scoped to the tested domain;
7. at least one independent replication is planned before any universal language is used.

## Ethics and governance boundary

The benchmark may evaluate measurable properties such as consistency, constraint satisfaction, calibration, robustness, or welfare under a declared utility model. It does not establish an absolute moral law.