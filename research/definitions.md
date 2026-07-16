# AMCEP Definitions and Measurement Contract

This document fixes the minimum information required before an AMCEP variable may be used in a theorem, simulation, or empirical claim.

## Status vocabulary

- **Defined:** syntax, mathematical type, domain, units, and measurement rule are explicit.
- **Operationalized:** an executable estimator maps observations to the variable.
- **Calibrated:** estimator behavior is quantified against reference data.
- **Validated:** the variable predicts or measures the intended construct on held-out data.

No variable is treated as validated merely because it appears in an equation.

## Core variables

| Symbol | Working name | Mathematical type | Provisional domain | Units | Current status |
|---|---|---:|---:|---|---|
| \(\rho\) | contradiction density | real scalar | \([0,\infty)\) | undefined | syntactically defined only |
| \(T\) | operator power / task value | real scalar | application-specific | undefined | syntactically defined only |
| \(x\) | recursion or persistence factor | real scalar | model-specific; convergence often requires \(|x|<1\) | dimensionless unless justified otherwise | syntactically defined only |
| \(n\) | recursion depth / time index | natural number | \(\mathbb N\) | steps | defined |
| \(E\) | normalization or resource term | positive real scalar | \((0,\infty)\) | must match numerator scaling | syntactically defined only |
| \(\lambda\) | contradiction penalty weight | non-negative real scalar | \([0,\infty)\) | chosen to make numerator dimensionally coherent | proposed |
| \(S\) | unbounded score | real scalar | \(\mathbb R\) | numerator units divided by \(E\) units | proposed |
| \(A\) | bounded transformed score | real scalar | typically \((0,1)\) | dimensionless | proposed |

## Required variable record

Each application must add a record containing:

1. **Semantic definition:** what the variable means in that application.
2. **Mathematical type:** scalar, vector, probability, measure, graph statistic, or other exact object.
3. **Domain:** all valid values and excluded values.
4. **Units:** physical, monetary, temporal, or explicitly dimensionless.
5. **Observation model:** what raw observations are available.
6. **Estimator:** the deterministic or statistical map from observations to the variable.
7. **Uncertainty:** interval, posterior, standard error, or other error model.
8. **Intervention semantics:** what it means to deliberately change the variable.
9. **Manipulation resistance:** how gaming or adversarial input is detected.
10. **Missing-data rule:** reject, impute, marginalize, or mark unknown.

## Contradiction density candidates

No single definition of \(\rho\) is currently accepted. Candidate operationalizations must be tested separately.

### Pairwise logical inconsistency

For a finite claim set \(C\), define a contradiction graph \(G_C\) whose vertices are claims and whose edges represent formally established inconsistency. A basic density is

\[
\rho_{\mathrm{pair}}=
\frac{2|E(G_C)|}{|C|(|C|-1)}
\]

when \(|C|\ge2\).

This measures pairwise contradiction frequency, not severity, causal importance, or higher-order inconsistency.

### Weighted contradiction loss

Given contradiction indicators \(c_i\in\{0,1\}\) and non-negative weights \(w_i\),

\[
\rho_{\mathrm{weighted}}=
\frac{\sum_i w_i c_i}{\sum_i w_i}
\]

provided \(\sum_iw_i>0\).

Weights must be fixed before test-set evaluation or estimated using a declared training protocol.

### Probabilistic inconsistency

For probabilistic beliefs, contradiction cannot be reduced automatically to binary edges. Candidate measures may use proper scoring rules, coherence violations, or distance to a consistent probability polytope. The chosen metric must be named and justified.

## Operator power / task value candidates

\(T\) must not combine welfare, performance, safety, truth, and moral preference without an explicit multi-objective aggregation rule.

Candidate constructions include:

- expected utility under a declared utility function;
- task success probability;
- negative calibrated loss;
- vector-valued objectives with Pareto analysis rather than scalarization;
- constrained optimization objective with safety constraints kept separate.

## Normalization term

\(E\) may represent resources, exposure, energy, population, or a pure scale parameter, but these meanings are not interchangeable. The repository must reject any application that does not declare:

- why division by \(E\) is appropriate;
- why \(E>0\);
- whether rescaling \(E\) changes rankings;
- whether \(E\) is observed or chosen;
- whether uncertainty in \(E\) is propagated.

## Dimensional-consistency rule

Addition and subtraction in the numerator require compatible units. Every application must either prove

\[
[T]=[\lambda\rho P_n]
\]

or document an explicit nondimensionalization map. A model failing this gate is rejected before empirical testing.

## Unknowns are first-class values

Missing or undefined quantities must not be silently replaced by zero. Implementations should return an explicit invalid or indeterminate result when the measurement contract is not met.