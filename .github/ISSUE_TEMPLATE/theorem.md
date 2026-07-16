---
name: Formal theorem
description: Specify and verify an exact mathematical claim
title: "Formalize: "
labels: []
assignees:
  - artistso
---

## Claim ID

`AMCEP-___-___`

## Exact statement

Write the theorem with all quantifiers, types, domains, and hypotheses.

## Definitions

List every referenced definition and artifact path.

## Assumptions

- Type assumptions:
- Domain assumptions:
- Regularity assumptions:
- Convergence assumptions:
- Unit or scale assumptions:

## Known counterexamples and boundary cases

Document invalid domains, degenerate cases, oscillation, divergence, sign reversals, and undefined expressions.

## Formal environment

- Lean version:
- Mathlib revision:
- Module path:
- Build command:

## Prohibited shortcuts

- No `sorry`.
- No unreviewed axioms that assert the result.
- No `Float` substitute for a real-analysis theorem.
- No finite-depth substitute for a limit.

## Acceptance criteria

- [ ] Exact statement reviewed.
- [ ] Kernel-checked artifact committed.
- [ ] CI passes from a clean environment.
- [ ] Counterexamples are retained.
- [ ] Claim ledger updated only to the justified status.
- [ ] Scope does not exceed the proved theorem.