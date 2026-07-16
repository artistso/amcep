# AMCEP constrained allocation benchmark: locked findings

## Evidence class

These are deterministic synthetic decision results. They are numerical evidence about the declared generator, oracle, policies, and attack. They are not real-world validation, fairness evidence, moral evidence, social-welfare evidence, or physical evidence.

## Reproducibility record

- Experiment: `amcep-constrained-allocation-v1`
- Pull-request branch head: `d32e0c8211acbdf1b41b1429f7d33c678bd62620`
- GitHub Actions run: `29529947680`
- Runner merge ref recorded in the artifact: `584226cb6f0ac5d6ba15ca2c3c2f2f1e9520e464`
- Artifact ID: `8388216367`
- Artifact digest: `sha256:8030c7f0e7fd8d4f11de2ecb036135d2eb2410b91ad8d2adbe7010f8c6bc2efa`
- Scenarios: 120
- Projects per scenario: 16
- Base seeds per attack-rate block: 30
- Seed derivation: `scenario_seed = base_seed + attack_index * 1,000,000`
- Attack rates: `0`, `0.1`, `0.25`, `0.5`
- Bootstrap resamples: 1,000

The bundle contains the complete configuration, all project reports and latent values, exact-oracle solutions, every policy outcome, aggregate intervals, environment, manifest, and internal SHA-256 checksums. Every checksum passed independently after download.

## Penalized regret

Values are mean penalized regret with deterministic percentile-bootstrap 95% intervals. Lower is better.

| Model | Attack 0 | Attack 0.1 | Attack 0.25 | Attack 0.5 |
|---|---:|---:|---:|---:|
| Class-aware baseline | 3.314 [1.635, 5.554] | 8.089 [4.537, 12.822] | 12.064 [7.962, 16.508] | 15.180 [9.548, 20.928] |
| Linear-penalty baseline | 4.378 [2.040, 6.962] | 9.024 [4.881, 14.190] | 11.014 [6.522, 15.998] | 16.613 [10.487, 22.988] |
| Task-only baseline | 10.650 [5.854, 16.038] | 11.802 [7.389, 16.425] | 16.390 [11.949, 21.184] | 19.533 [13.437, 25.660] |
| Original AMCEP | 9.956 [5.540, 15.175] | 11.266 [6.851, 16.414] | 16.259 [11.911, 20.943] | 19.504 [13.577, 25.579] |
| Transient candidate | 3.468 [1.715, 5.591] | 8.979 [4.843, 14.053] | 12.988 [8.608, 18.143] | 16.883 [11.359, 22.556] |
| Cumulative candidate | 10.527 [6.024, 15.554] | 12.669 [8.406, 17.394] | 16.120 [11.633, 20.925] | 19.075 [13.367, 25.096] |
| Bounded transient | 7.602 [4.604, 11.147] | 10.607 [6.911, 14.932] | 14.666 [10.798, 18.274] | 21.496 [15.690, 27.158] |
| Bounded cumulative | 11.263 [6.867, 16.367] | 14.079 [9.853, 18.628] | 17.137 [12.493, 21.649] | 23.534 [17.876, 29.289] |

At every attack rate, the lowest mean regret among the three simple baselines was lower than the mean regret of every AMCEP formula-based policy. The intervals overlap in several comparisons, especially class-aware versus transient. Therefore this is a point-estimate result for the locked matrix, not evidence of statistical separation or general superiority.

## True feasibility

True feasibility means the selected portfolio satisfied the latent persistent-risk cap, not merely the reported cap.

| Model | Attack 0 | Attack 0.1 | Attack 0.25 | Attack 0.5 |
|---|---:|---:|---:|---:|
| Class-aware baseline | 0.867 | 0.733 | 0.533 | 0.333 |
| Linear-penalty baseline | 0.867 | 0.700 | 0.600 | 0.367 |
| Task-only baseline | 0.867 | 0.567 | 0.333 | 0.233 |
| Original AMCEP | 0.867 | 0.567 | 0.300 | 0.267 |
| Transient candidate | 0.867 | 0.733 | 0.500 | 0.267 |
| Cumulative candidate | 0.900 | 0.567 | 0.333 | 0.333 |
| Bounded transient | 0.833 | 0.767 | 0.367 | 0.333 |
| Bounded cumulative | 0.867 | 0.733 | 0.367 | 0.200 |

Every policy had a lower true-feasibility point estimate in the 0.5 attack block than in the unattacked block. Because attack-rate blocks use independent generated scenarios, this is not a paired causal estimate. The strategic-reporting mechanism nevertheless produced the failure it was designed to expose: reported constraint compliance does not guarantee latent constraint compliance.

## True risk excess

Mean latent risk excess increased from at most `0.233` in the unattacked block to between `4.000` and `4.833` in the 0.5 attack block. The bounded output transform did not prevent manipulation-induced constraint failure.

## Persistence semantics

The transient candidate was consistently closer to the class-aware latent objective than the cumulative candidate on mean penalized regret. This follows the declared generator: persistent projects receive high `x` and low depth, while repairable projects receive low `x` and greater depth.

Under those assignments:

- `rho*|x|^n` penalizes persistent projects more strongly;
- `rho*(1-|x|^n)` penalizes repairable projects more strongly.

The cumulative candidate therefore encodes the opposite persistence semantics from the benchmark's latent objective. This is a generator-specific falsification result, not proof that the transient interpretation is correct in the real world.

## Original equation

The original score was near the task-only baseline across all four blocks and materially worse in mean regret than the class-aware or transient policies. This is consistent with the already-proven sign defect: in the intended `x < 1` regime, the original equation rewards increased reported contradiction rather than penalizing it.

## Bounded transforms

Bounding the output did not improve decision quality automatically. Both bounded candidates had greater mean regret than their raw counterparts at every attack rate. A monotone map can preserve order in exact arithmetic, but the policy uses a fixed positive-margin threshold and score-per-cost ratio; nonlinear compression changes those margins and ratios. Boundedness is therefore a numerical control, not a decision-optimality guarantee.

## Scenario-level baseline comparison

For each scenario, the best regret among task-only, class-aware, and linear-penalty baselines was compared with each formula-based policy:

| Formula policy | Formula better | Tie | Simple baseline better |
|---|---:|---:|---:|
| Original | 1 | 69 | 50 |
| Transient | 3 | 86 | 31 |
| Cumulative | 1 | 60 | 59 |
| Bounded transient | 11 | 37 | 72 |
| Bounded cumulative | 9 | 33 | 78 |

This comparison selects the best baseline separately within each scenario and is therefore descriptive, not a preregistered model-selection procedure.

## Conclusions limited to this benchmark

1. Strategic underreporting defeated reported-risk enforcement for every tested policy.
2. No AMCEP formula-based policy achieved the lowest mean penalized regret in any attack-rate block.
3. The transient candidate aligned better than the cumulative candidate with the benchmark's declared persistent-harm semantics.
4. The original formula remained noncompetitive with simpler contradiction-aware baselines.
5. Bounded output alone did not improve allocation decisions.
6. External application remains unsupported until the measurements, objective, harm weight, constraints, attack model, and data are independently justified and validated.
