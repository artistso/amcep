# Changelog

All material AMCEP changes are recorded by evidence class. A new equation, proof, numerical result, empirical result, falsification, and retraction are not interchangeable change types.

## Unreleased

### Definitions

- Added operational-definition and measurement-contract requirements for AMCEP variables.

### Mathematical analysis

- Recorded the contradiction-sign defect in the original score.
- Restricted the residual convergence claim to its valid domain.
- Added transient and cumulative contradiction-penalty candidates as research proposals.

### Formal verification

- Added a Lean formalization plan.
- No claim is currently promoted to `formally-verified` by this changelog.

### Numerical verification

- Added boundary tests, competing score implementations, and property-based testing.

### Empirical research

- Added a preregistered synthetic and resource-allocation benchmark structure.
- No reported real-world percentage is currently promoted to `empirically-supported`.

### Falsifications

- Original contradiction-penalty monotonicity claim is falsified in the intended regime.
- Universal residual convergence is falsified.
- Finite floating-point threshold checks are rejected as proofs of limits.
- The transient repair is shown to forget contradiction when `|x| < 1`.

### Retractions and unsupported claims

- P versus NP, Hodge, Birch and Swinnerton-Dyer, universal morality, natural-isomorphism, guaranteed unitarity, and infinite-decoherence claims remain unsupported unless exact independent evidence is added.

### Governance

- Added claim-ledger schema and status controls.
- Added contribution rules, pull-request requirements, issue templates, and release policy.

## Versioning convention

AMCEP uses semantic versioning for repository interfaces and evidence governance:

- **MAJOR:** incompatible schema, equation-interface, or evidence-policy change.
- **MINOR:** new candidate model, theorem module, benchmark, or evidence artifact that preserves compatibility.
- **PATCH:** correction, test expansion, documentation clarification, or non-breaking audit update.

A version number never certifies scientific truth. Evidence statuses remain controlled by `data/claims.json`.