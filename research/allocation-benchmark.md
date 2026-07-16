# AMCEP constrained allocation benchmark

## Evidence class

This benchmark is a deterministic synthetic decision experiment. It tests implementation behavior, decision regret, constraint violations, and strategic-reporting sensitivity under declared assumptions. It does not establish real-world validity, fairness, morality, social welfare, or physical law.

## Decision problem

Each scenario contains a finite set of projects. A policy selects a subset subject to:

- an integer cost budget;
- an integer persistent-risk budget.

The latent objective is

\[
V(A)=\sum_{i\in A}\left(u_i-h\rho_i m_i\right),
\]

where `u_i` is true utility, `h` is a declared harm weight, `rho_i` is true contradiction prevalence times severity, and

\[
m_i=0.25\quad\text{for repairable projects},
\qquad
m_i=1\quad\text{for persistent projects}.
\]

The multiplier is part of the synthetic data-generating process. It is not asserted to be a universal ethical or empirical constant.

## Exact oracle

The benchmark computes the globally optimal feasible subset using dynamic programming for a two-constraint 0/1 knapsack problem. The oracle uses latent utility and latent persistent risk. It is therefore an evaluation reference, not a deployable policy.

## Reported information and manipulation

Policies observe noisy reports rather than latent truth. A persistent project selected for attack:

- inflates reported utility by 35%;
- reduces reported contradiction density by 65% while preserving nonnegative prevalence and severity.

Attacks never alter latent utility, cost, persistence class, or true risk. Policies enforce the budget and risk cap using reported information; evaluation uses latent information. This creates a measurable difference between observed feasibility and true feasibility.

## Compared policies

- `task_only`: reported utility;
- `class_aware`: reported utility minus reported risk times the known synthetic persistence class;
- `linear_penalty`: reported utility minus reported contradiction without persistence class;
- `original`: the source AMCEP score;
- `transient`: the contracted transient candidate;
- `cumulative`: the contracted cumulative candidate;
- bounded transient;
- bounded cumulative.

Every policy ranks positive score margin per unit cost and then admits projects only while reported cost and reported risk remain within their caps.

## Persistence-semantics stress

The generator assigns repairable projects lower `x` and greater depth, and persistent projects higher `x` and lower depth. This exposes an important semantic conflict:

- the transient term `rho*|x|^n` penalizes persistent projects more strongly;
- the cumulative term `rho*(1-|x|^n)` penalizes repairable projects more strongly.

Neither interpretation is accepted in advance. The benchmark measures their decision consequences against the explicit latent objective.

## Metrics

For each policy and attack rate, the benchmark reports:

- true net value;
- value gap relative to the exact oracle;
- penalized regret after true risk excess;
- true feasibility rate;
- true persistent-risk excess;
- number of attacked projects selected.

Means include deterministic percentile-bootstrap 95% intervals across independent seeds.

## Locked experiment

- 16 projects per scenario;
- cost budget 32;
- persistent-risk budget 24;
- 30 seeds beginning at `20260716`;
- attack rates `0`, `0.1`, `0.25`, and `0.5`;
- 1,000 bootstrap resamples;
- complete scenario, project, oracle, and policy records retained;
- environment and SHA-256 checksums retained.

Changing these values after observing results requires a new experiment identifier and new claim-ledger entry.

## Rejection gates

A model is rejected for this decision problem when it systematically produces greater penalized regret or lower true feasibility than a simpler declared baseline with uncertainty intervals that do not support equivalence. A single synthetic benchmark cannot promote a model to `empirically-supported`.

## Remaining external requirements

Application still requires operational measurement definitions, a defensible harm weight, preregistered external data, uncertainty propagation for each observation, subgroup evaluation, legal and ethical review, independent replication, and a deployment-specific abstention policy.
