# AMCEP Mathematical Audit

**Status:** active falsification record  
**Scope:** the published score equations and the mathematical claims directly implied by them  
**Non-scope:** this document does not certify moral truth, physical law, or solutions to open mathematical problems.

## 1. Source equation

The source materials define

\[
S_n(\rho,T,x,E)=\frac{\rho+T-\rho x^n}{E}
=\frac{T+\rho(1-x^n)}{E}.
\]

The minimum explicit domain needed for ordinary real-valued evaluation is

\[
\rho,T,x,E\in\mathbb R,\qquad n\in\mathbb N,\qquad E\ne 0.
\]

For the intended normalization and contradiction-density interpretation, the executable reference model adopts the stricter engineering domain

\[
\rho\ge 0,\qquad n\ge 0,\qquad E>0.
\]

## 2. Decisive sign defect

For fixed \(T,x,n,E\),

\[
\frac{\partial S_n}{\partial \rho}=\frac{1-x^n}{E}.
\]

Under the stated working regime

\[
E>0,\qquad 0\le x<1,\qquad n>0,
\]

we have \(0\le x^n<1\), hence

\[
\frac{\partial S_n}{\partial \rho}>0.
\]

Therefore increasing contradiction density raises the original score. This falsifies the stated principle that contradiction should reduce the score.

A reproducible counterexample is

\[
T=5,\quad x=\tfrac12,\quad n=10,\quad E=1.
\]

Then

\[
S_n(1,5,\tfrac12,1)=5.9990234375
\]

and

\[
S_n(2,5,\tfrac12,1)=6.998046875.
\]

The second state has more contradiction and a larger score.

## 3. Convergence domain

For fixed finite \(\rho\),

\[
\lim_{n\to\infty}\rho x^n=0
\]

holds exactly when

\[
\rho=0\quad\text{or}\quad |x|<1.
\]

Failure cases:

- \(x=1\), \(\rho\ne0\): the residual is constant.
- \(x=-1\), \(\rho\ne0\): the residual oscillates.
- \(|x|>1\), \(\rho\ne0\): the magnitude diverges.
- \(E=0\): the score is undefined.
- \(E<0\): all intended monotonicity signs reverse.

A floating-point evaluation at one finite depth, including \(n=20\), is not a proof of an infinite limit.

## 4. Dimensional-consistency gate

The numerator adds \(T\) and \(\rho(1-x^n)\). This requires either

\[
[T]=[\rho]
\]

or explicit maps that nondimensionalize both quantities. Until the units, measurement procedures, and scale transformations are defined, the score is an algebraic proposal rather than an empirically interpretable law.

## 5. Competing candidate families

### 5.1 Transient-penalty candidate

\[
S_n^{\mathrm{transient}}=\frac{T-\lambda\rho|x|^n}{E},
\qquad \lambda\ge0.
\]

For \(E>0\),

\[
\frac{\partial S_n^{\mathrm{transient}}}{\partial\rho}
=-\frac{\lambda|x|^n}{E}\le0.
\]

However, for \(|x|<1\),

\[
\lim_{n\to\infty}S_n^{\mathrm{transient}}=\frac{T}{E}.
\]

The contradiction penalty disappears. This is coherent only when \(\rho|x|^n\) represents a genuinely repairable transient residual.

### 5.2 Cumulative-penalty candidate

\[
S_n^{\mathrm{cumulative}}=
\frac{T-\lambda\rho(1-|x|^n)}{E},
\qquad \lambda\ge0.
\]

For \(E>0\),

\[
\frac{\partial S_n^{\mathrm{cumulative}}}{\partial\rho}
=-\frac{\lambda(1-|x|^n)}{E}\le0
\]

whenever \(|x|\le1\). For \(|x|<1\),

\[
\lim_{n\to\infty}S_n^{\mathrm{cumulative}}
=\frac{T-\lambda\rho}{E}.
\]

This preserves a lasting contradiction penalty. It remains a candidate model, not a discovered law.

### 5.3 Bounded output candidate

For cross-system comparison, a bounded transformation may be required:

\[
A_n=\sigma(S_n),\qquad
\sigma(z)=\frac{1}{1+e^{-z}}.
\]

This guarantees \(0<A_n<1\), but does not repair undefined variables, invalid units, or unsupported semantics.

## 6. Axioms required before model selection

Any promoted score must state and test at least:

1. **Domain validity:** all inputs and undefined cases are explicit.
2. **Positive responsiveness:** \(\partial S/\partial T>0\) under declared assumptions.
3. **Contradiction penalty:** \(\partial S/\partial\rho\le0\) under declared assumptions.
4. **Boundedness or justified unboundedness.**
5. **Continuity or an explicit reason for discontinuities.**
6. **Scale behavior:** invariance or covariance under changes of units.
7. **Limit behavior:** the intended meaning of \(n\to\infty\).
8. **Uncertainty propagation:** interval or distributional inputs, not only point estimates.
9. **Identifiability:** distinct parameters must be recoverable from data when empirical claims are made.
10. **Falsifiability:** each claim must include a counterexample condition or rejection test.

## 7. Formal-verification gate

A theorem may be marked `formally-verified` only when the repository contains:

- the exact formal statement;
- every hypothesis;
- a machine-checkable Lean artifact over exact types such as `ℝ`;
- a reproducible build command;
- a passing kernel check in CI;
- no replacement of limits by finite floating-point thresholds.

Model-generated proof text is a proposal. The Lean kernel is the proof authority.

## 8. Current verdicts

| Claim | Verdict |
|---|---|
| Increasing \(T\) raises the original score | Conditionally proved for \(E>0\) |
| Increasing \(\rho\) lowers the original score | Falsified in the intended regime |
| \(\rho x^n\to0\) for all inputs | Falsified |
| A finite Float calculation proves the limit | Falsified |
| The transient repair penalizes contradiction | Conditionally proved |
| The transient repair preserves contradiction forever | Falsified for \(|x|<1\) |
| The cumulative repair has the intended derivative sign | Conditionally proved |
| Either repair is a validated real-world law | Unsupported pending definitions and data |
| AMCEP proves P=NP, Hodge, BSD, or universal moral truth | Unsupported |

## 9. Promotion rule

No equation is promoted because it is elegant, intuitive, or generated by a powerful model. Promotion requires exact definitions, mathematical survival under adversarial testing, formal proof where applicable, empirical superiority to declared baselines, and independent reproducibility.