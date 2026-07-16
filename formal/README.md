# AMCEP Formal Verification Plan

## Authority boundary

Only artifacts accepted by the Lean kernel may support the ledger status `formally-verified`. Language-model output, floating-point evaluation, prose proofs, and successful unit tests belong to different evidence classes.

## Planned module structure

```text
formal/
  lakefile.toml
  lean-toolchain
  AMCEP/
    Domain.lean
    OriginalScore.lean
    Counterexamples.lean
    TransientScore.lean
    CumulativeScore.lean
    Bounds.lean
    Convergence.lean
    Scale.lean
```

The Lean and Mathlib revisions will be pinned in the same pull request that introduces executable Lean code. No version is declared here until the environment is actually initialized and checked in CI.

## First theorem set

### Original equation

1. Define the score over exact real numbers.
2. Prove positive responsiveness to `T` when `E > 0`.
3. Prove that the original score increases with `rho` when `E > 0`, `0 <= x < 1`, and `n > 0`.
4. Record a concrete exact counterexample.

### Convergence

Prove the exact domain for

```text
rho * x^n → 0
```

with natural-number exponent and real parameters. The theorem must distinguish `rho = 0`, `|x| < 1`, boundary cases, oscillation, and divergence.

### Transient candidate

Prove, under explicit hypotheses:

- non-increasing behavior in `rho`;
- limit equal to `T/E` for `|x| < 1`;
- disappearance of the contradiction penalty.

### Cumulative candidate

Prove, under explicit hypotheses:

- non-increasing behavior in `rho` for `|x| <= 1`;
- limit equal to `(T - lambda*rho)/E` for `|x| < 1`;
- boundary behavior at `x = 1` and `x = -1`;
- failure of the intended derivative sign outside the declared domain.

### Bounded transforms

Prove the mathematical logistic transform lies strictly between zero and one for finite real input. Floating-point saturation to exact `0.0` or `1.0` is an implementation effect and must not be confused with the real-analysis theorem.

## Prohibited shortcuts

Formal files must not use:

- `sorry`;
- unreviewed custom axioms introduced to force the result;
- `Float` as a replacement for `Real` theorem statements;
- a finite depth as a replacement for a limit;
- an informal correspondence table as a categorical construction.

## Model-assisted workflow

The registered Hugging Face theorem provers may propose statements and proof scripts. Every proposal must pass this pipeline:

```text
candidate statement
→ assumption audit
→ Lean elaboration
→ kernel check
→ independent counterexample search
→ claim-ledger update
```

Two models producing the same answer does not create independent mathematical verification.

## CI gate

Once initialized, CI must:

1. install the pinned Lean toolchain;
2. restore the Mathlib cache where appropriate;
3. run `lake build`;
4. reject `sorry` and prohibited declarations;
5. attach the verifier result to the exact commit;
6. allow `formally-verified` only when the relevant artifact path exists.