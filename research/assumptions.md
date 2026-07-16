# AMCEP Assumptions and Rejection Gates

AMCEP claims are valid only relative to declared assumptions. Omitted assumptions are treated as unresolved defects, not harmless shorthand.

## Mathematical assumptions

### A1. Exact domain

Every scalar input is finite. Unless a theorem states otherwise:

\[
\rho\ge0,\qquad n\in\mathbb N,\qquad E>0.
\]

### A2. Convergence regime

Any claim using \(x^n\to0\) must assume either \(\rho=0\) or \(|x|<1\). No finite threshold check substitutes for this assumption.

### A3. Unit compatibility

Every addition or subtraction must involve quantities with compatible units or an explicit nondimensionalization.

### A4. Parameter independence

Partial-derivative claims hold only when the remaining variables are fixed. Empirical causal interpretations require a separate identification argument.

### A5. Regularity

Differentiability, continuity, compactness, convexity, self-adjointness, or other regularity conditions must be stated wherever a theorem uses them.

## Empirical assumptions

### E1. Observable construction

Each variable has a declared observation model and estimator.

### E2. Calibration separation

Parameter selection uses training or calibration data only. Final claims use a locked test set.

### E3. Baseline declaration

The comparison set is fixed before evaluation and includes simple baselines capable of falsifying the need for AMCEP.

### E4. Uncertainty reporting

Every reported effect includes uncertainty, sample size, and a test or interval appropriate to the data-generating process.

### E5. Distribution shift

Claims are scoped to the tested distribution unless out-of-distribution performance is measured explicitly.

### E6. Adversarial evaluation

Any score used in allocation, safety, or governance must be tested for manipulation, proxy gaming, and missing-data exploitation.

## Formal-verification assumptions

### F1. Exact theorem statement

Natural-language intent is not a theorem. The formal artifact must state all quantifiers, types, and hypotheses.

### F2. Kernel acceptance

A proof is accepted only if Lean checks it without `sorry`, unsafe axioms introduced for convenience, or replacement by floating-point examples.

### F3. Reproducible environment

The Lean version, Mathlib revision, and build command are pinned.

### F4. Model separation

Outputs from theorem-proving language models are candidate proof scripts. Model confidence is not evidence.

## Topology-specific assumptions

Before any local-to-global ethical theorem is evaluated, the repository must define:

- the underlying topological space or site;
- the relevant sheaf or presheaf;
- objects represented by sections;
- restriction maps;
- the obstruction class;
- whether the theorem concerns existence, uniqueness, or compatibility of global sections.

Ordinary singular cohomology with constant coefficients is not presumed to encode ethical consistency.

## Quantum-specific assumptions

Before any quantum claim is evaluated, the repository must define:

- a Hilbert space;
- operator domains;
- a self-adjoint Hamiltonian for unitary evolution;
- measurable observables;
- a state-preparation and measurement protocol;
- a prediction that differs from an established baseline;
- error-correction assumptions using the pairwise Knill-Laflamme condition.

Conceptual analogy does not satisfy these requirements.

## Immediate rejection gates

A claim is rejected from promotion when any of the following holds:

1. A variable lacks a type or domain.
2. The equation is dimensionally incoherent.
3. A stated monotonicity property has the wrong derivative sign.
4. A limit claim omits its convergence domain.
5. A numerical example is presented as a universal proof.
6. A formal proof contains placeholders or unchecked axioms.
7. An empirical percentage has no raw data and protocol.
8. A quantum claim lacks a measurable physical prediction.
9. A topological claim lacks the relevant sheaf, obstruction, or universal property.
10. A universal claim exceeds the scope of its evidence.