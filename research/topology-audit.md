# AMCEP Topology and Category-Theory Audit

## Scope

This document separates mathematically meaningful local-to-global constructions from unsupported ethical interpretations.

## 1. Cohomology is not automatically ethical consistency

A claim of the form

\[
H^1(E;\mathbb Z)=0
\iff
\text{ethical consistency}
\]

is undefined until both sides are formalized and connected by a theorem.

At minimum, a defensible local-to-global construction requires:

- a topological space, site, or category of contexts;
- a presheaf or sheaf whose sections represent local decisions, constraints, or evidence;
- explicit restriction maps;
- a compatibility condition on overlaps;
- a defined obstruction class;
- a theorem distinguishing existence from uniqueness of a global section.

Ordinary singular cohomology with constant coefficients is not presumed to encode moral consistency.

## 2. Candidate sheaf-theoretic direction

Let \(X\) be a space of decision contexts and \(\mathcal F\) a sheaf whose local sections encode feasible local assignments. A precise research question is:

> Under what assumptions does a compatible family of local sections glue to a global section, and what obstruction prevents gluing?

This can become a legitimate theorem once \(X\), \(\mathcal F\), compatibility, and the obstruction group are defined. It does not establish that the global section is morally correct.

## 3. Existence, uniqueness, and preference are distinct

Even when a global section exists:

- existence does not imply uniqueness;
- uniqueness does not imply optimality;
- optimality under a utility function does not imply universal morality;
- consistency does not imply truth.

Every theorem must state which property it proves.

## 4. Coalgebra condition defect

For a linear map \(\Delta\), zero belongs to both image and kernel:

\[
0\in\operatorname{im}\Delta,
\qquad
0\in\ker\Delta.
\]

Therefore

\[
\operatorname{im}\Delta\cap\ker\Delta\ne\varnothing.
\]

The condition

\[
\operatorname{im}\Delta\cap\ker\Delta=\varnothing
\]

is impossible in the ordinary vector-space setting. Replacing the empty intersection by \(\{0\}\) would create a coherent algebraic condition, but would still not encode nonviolence without an explicit semantic theorem.

## 5. Category-theory requirements

A proposed functor or adjunction must define:

- source and target categories;
- objects and morphisms;
- identity and composition laws;
- functor action on objects and morphisms;
- natural transformations when claimed;
- unit and counit for an adjunction;
- the universal property being satisfied.

A correspondence table between concepts is not a functor. A verbal analogy is not a natural isomorphism. A claimed left adjoint requires a proved hom-set bijection natural in both variables.

## 6. Promotion criteria

A topology or category-theory claim may enter the claim ledger as `conditionally-proved` or `formally-verified` only when:

1. all objects and morphisms are defined;
2. the exact theorem is scoped to those definitions;
3. counterexamples are documented;
4. the proof is complete;
5. any ethical interpretation is separately operationalized and empirically tested.

Until then, such claims remain `proposed` or `unsupported`.