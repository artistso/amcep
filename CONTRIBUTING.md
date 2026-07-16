# Contributing to AMCEP

AMCEP accepts contributions that make claims more precise, more testable, or easier to falsify. Contributions that strengthen rhetoric without strengthening evidence are rejected.

## Branch and pull-request policy

- `main` is the public, deployable research record.
- Experimental work belongs on a branch.
- Claim-changing work enters through a pull request.
- Negative results, counterexamples, and retractions remain visible.

## Required pull-request information

A claim-changing pull request must state:

1. claim IDs affected;
2. exact statements before and after;
3. assumptions added, removed, or narrowed;
4. counterexamples examined;
5. evidence artifacts added;
6. commands used to reproduce results;
7. known failure conditions;
8. whether the change is mathematical, numerical, empirical, analogical, or physical.

## Evidence boundaries

- A calculation is not a theorem.
- A theorem is not an empirical validation.
- An empirical result is not a universal law.
- A conceptual analogy is not a natural isomorphism.
- Language-model agreement is not independent verification.

## Local checks

```bash
python -m pip install -e '.[dev]'
ruff check src tests
mypy src
pytest --cov=src --cov-report=term-missing
node --check app.js
```

All checks must pass before merge.

## Claim ledger changes

Any claim status change must update `data/claims.json` and pass `data/claims.schema.json` validation.

Promotion requirements:

- `conditionally-proved`: exact assumptions and proof are present.
- `formally-verified`: a kernel-checked formal artifact is present.
- `numerically-supported`: reproducible numerical artifacts are present.
- `empirically-supported`: preregistered protocol, data, code, and uncertainty are present.
- `falsified`: a valid counterexample or rejecting result is documented.

## Formal verification

Lean contributions must use exact types, state all hypotheses, compile without `sorry`, and avoid convenience axioms that merely assert the target. Generated proof scripts are reviewed like any other untrusted contribution.

## Empirical work

Empirical pull requests must include:

- dataset or generator revision;
- locked evaluation protocol;
- baselines;
- seeds;
- raw outputs;
- effect sizes and uncertainty;
- failure analysis;
- exact code revision.

## Scope discipline

No contribution may claim that AMCEP solves an open mathematical problem, establishes universal morality, or predicts new physics unless the exact claim has the corresponding complete evidence class and independent review.