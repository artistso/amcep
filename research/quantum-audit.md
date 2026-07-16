# AMCEP Quantum Audit

## Scope

This document separates analogy, mathematical construction, and physical prediction. These are distinct evidence classes and must not be merged.

## 1. Three levels of quantum language

### Analogy

Terms such as superposition, collapse, entanglement, or decoherence may be used metaphorically only when labeled as analogy. Analogy produces no physical prediction.

### Mathematical construction

A construction must define a Hilbert space, states, operators, domains, dynamics, and observables. Internal mathematical coherence still does not establish physical relevance.

### Physical prediction

A physical claim must specify state preparation, measurement, error model, parameter values, and a prediction that differs quantitatively from an established baseline.

## 2. Unitarity gate

Schrodinger evolution is unitary under appropriate conditions when the Hamiltonian is self-adjoint. Writing

\[
H=H_0+\sum_i\lambda_iV_i
\]

is insufficient. Each term must have a defined operator domain, and the total operator must satisfy the conditions needed for self-adjointness. An arbitrary 'ethical potential' does not automatically preserve unitarity.

## 3. Quantum error-correction gate

For a code projector \(P\) and error set \(\{E_a\}\), the relevant Knill-Laflamme condition is pairwise:

\[
P E_a^\dagger E_b P=c_{ab}P.
\]

A condition involving only one error operator at a time is generally insufficient. Any AMCEP quantum-code claim must identify the code space, error channel, correctable set, recovery operation, and finite performance metric.

## 4. Decoherence claims

'Infinite decoherence time' is unsupported except under explicitly idealized assumptions that make the statement mathematically precise. Real devices require finite noise models and experimentally measured coherence or logical-error rates.

Acceptable metrics include:

- logical error rate per cycle;
- coherence time under a declared channel;
- threshold behavior;
- fidelity with confidence intervals;
- overhead relative to a baseline code.

## 5. Natural-isomorphism defect

A table pairing ethical concepts with quantum concepts is not a natural isomorphism. A natural isomorphism requires two functors between defined categories and an invertible natural transformation whose naturality squares commute.

Without those objects, the claim is an analogy and must be labeled accordingly.

## 6. Experimental protocol gate

A quantum experiment must preregister:

1. hardware or simulator;
2. circuit or Hamiltonian;
3. state preparation;
4. measurement basis;
5. number of shots;
6. noise characterization;
7. baseline model;
8. primary outcome;
9. statistical analysis;
10. raw data and calibration files.

Unsupported percentages are removed from promotion consideration until these artifacts exist.

## 7. Current verdict

The existing quantum material may motivate research questions, but it does not currently establish a new quantum law, a natural isomorphism, guaranteed unitarity, or infinite decoherence time. These claims remain `unsupported` until exact constructions and reproducible experiments exist.