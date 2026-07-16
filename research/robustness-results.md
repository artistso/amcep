# AMCEP robustness benchmark: locked findings

## Evidence class

These are deterministic numerical and software-verification results from the locked synthetic attack matrix. They are not real-world validation, moral evidence, fairness evidence, or physical evidence.

## Reproducibility record

- Source branch head: `9558b09e666a7483f57edf8e07bb6ffb9602ed88`
- GitHub Actions run: `29526877523`
- Pull-request merge ref recorded by the runner: `d9fe7776c33ec891e7344bddfe01e97b85f4c9df`
- Artifact: `amcep-robustness-d9fe7776c33ec891e7344bddfe01e97b85f4c9df`
- GitHub artifact digest: `sha256:b43904274ec58926ac1c75330c834e618e96a58936b167fc0a708de1b85db3db`
- Locked seed: `20260716`
- Cases: 400 per group
- Groups: in-distribution, persistence boundary, small normalization, high severity, combined
- Models: original, transient, cumulative

The artifact contains `manifest.json`, `metrics.json`, `environment.txt`, and `checksums.txt`. All internal SHA-256 checks passed in CI.

## Decisive findings

### Original equation

In the in-distribution regime (`0.05 <= x <= 0.95`, `1 <= n <= 12`, `E >= 0.5`):

- contradiction-severity violation rate: **1.0000**;
- coherent unit-rescaling violation rate: **1.0000**;
- 95th-percentile absolute score: **2.481293**.

Thus every locked in-domain case rewarded increased contradiction severity, and every locked case changed under the coherent task-value unit transformation used by this benchmark.

The exact rescaling counterexample used by the unit test is

\[
\rho=0.5,\quad T=5,\quad x=0.5,\quad n=2,\quad E=2,\quad k=1000.
\]

The original score changes from `2.6875` to `2.5001875` when `T` and `E` are both multiplied by `k`. This is an exact dimensional-consistency failure under the declared unit interpretation.

### Transient candidate

Across all five groups:

- contradiction-severity violation rate: **0.0000**;
- coherent unit-rescaling violation rate: **0.0000**.

This does not make the transient candidate generally valid. For `|x| > 1`, its penalty magnitude grows with depth rather than converging, and all unbounded variants remain sensitive to small positive normalization.

### Cumulative candidate

In the in-distribution regime:

- contradiction-severity violation rate: **0.0000**;
- coherent unit-rescaling violation rate: **0.0000**.

At the persistence boundary, where `|x|` was sampled from `[0.97, 1.03]`:

- contradiction-severity violation rate: **0.4725**.

Under the combined attack:

- contradiction-severity violation rate: **0.4825**.

This is the expected failure outside the theorem domain. When `|x|^n > 1`, the factor `1 - |x|^n` is negative, so the cumulative penalty reverses sign and greater contradiction raises the score. The candidate therefore requires an enforced domain `|x|^n <= 1` or a separately justified bounded persistence transform.

An exact counterexample is

\[
T=0,\quad E=1,\quad \lambda=1,\quad x=2,\quad n=1,
\]

for which the cumulative score equals `rho`; increasing `rho` from `1` to `2` increases the score from `1` to `2`.

### Small-normalization attack

The 95th-percentile absolute scores changed as follows:

| Model | In-distribution | Small positive E | Combined attack |
|---|---:|---:|---:|
| Original | 2.481293 | 6362.043036 | 10452.591636 |
| Transient | 2.341853 | 6122.928978 | 20489.369771 |
| Cumulative | 2.535909 | 6685.256782 | 7422.490836 |

The condition `E > 0` is sufficient for algebraic definition but not numerical robustness. Any applied model requires a justified lower bound, uncertainty treatment, abstention policy, or bounded transformation.

### Independent arithmetic path

The maximum absolute disagreement between the production float implementation and the independent 60-digit `Decimal` implementation was:

- in-distribution: at most `8.881784197001252e-16`;
- boundary attack: at most `1.3322676295501878e-15`;
- small-normalization attack: at most `3.637978807091713e-12`;
- high-severity attack: at most `3.552713678800501e-15`;
- combined attack: at most `4.547473508864641e-11`.

The larger absolute differences occur where score magnitudes are thousands to tens of thousands. This supports implementation agreement on the locked matrix only; it does not validate the equations.

## Required model changes before application

1. The original score must not be used as a contradiction-penalizing or dimensionally coherent applied score.
2. The cumulative candidate must enforce its persistence domain or replace raw `|x|^n` with a justified bounded persistence map.
3. Every unbounded score must specify a defensible normalization floor and behavior near that floor.
4. External validity still requires preregistered real data, declared baselines, uncertainty intervals, and independent replication.
