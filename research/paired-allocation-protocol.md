# Paired counterfactual allocation protocol

## Purpose

The first constrained-allocation benchmark used independent seed blocks for different attack rates. That design prevented paired within-scenario comparisons. This protocol reuses the same latent projects, observation noise, exact oracle, and random attack draws for every attack-rate condition within each seed.

## Pairing contract

For each base seed and each attack rate:

- the same project count, costs, latent utilities, persistence classes, true contradiction values, `x`, and depth are regenerated;
- the same observation-noise draws are regenerated;
- the same persistent-project attack uniform draws are regenerated;
- the exact latent oracle is unchanged;
- only the threshold applied to the attack uniform draw changes.

Consequently, attacked sets are nested as attack rate increases. The `0` condition is the within-seed baseline.

## Paired estimands

For every policy and attacked condition, the experiment computes attacked minus baseline deltas for:

- true net value;
- exact-oracle value gap;
- violation-penalized regret;
- latent feasibility indicator;
- latent persistent-risk excess;
- attacked projects selected.

Means and deterministic percentile-bootstrap 95% intervals are computed across paired seeds.

## Locked matrix

- 30 seeds beginning at `20260716`;
- attack rates `0`, `0.1`, `0.25`, and `0.5`;
- 16 projects per seed;
- eight policies inherited unchanged from the first allocation benchmark;
- 1,000 bootstrap resamples;
- complete scenarios, paired deltas, aggregate intervals, environment, and checksums retained.

## Integrity checks

The experiment fails when:

- latent project fingerprints differ across attack rates for a seed;
- exact oracle solutions differ across attack rates for a seed;
- attacked sets are not nested by attack rate;
- a seed-rate condition appears twice;
- the zero baseline is absent;
- a paired delta is attempted across non-identical latent scenarios.

## Interpretation boundary

This design supports within-generator counterfactual statements about the declared reporting attack. It does not establish that the attack model, utility function, harm weight, persistence classes, or project distribution represent any real institution. Synthetic paired intervals are not empirical evidence.
