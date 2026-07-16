# AMCEP Formal Verification

## Authority boundary

Only exact propositions accepted by the pinned Lean kernel may support the ledger status `formally-verified`. Language-model output, floating-point evaluation, prose proofs, and successful unit tests remain separate evidence classes.

## Pinned environment

```text
Lean:    v4.32.0
Mathlib: v4.32.0
Package: formal/
Build:   lake build
```

The GitHub Actions workflow installs the pinned toolchain, resolves the pinned Mathlib revision, rejects `sorry` and `admit` in the AMCEP theorem modules, runs `lake build`, and preserves diagnostic logs.

## Current module structure

```text
formal/
  lakefile.lean
  lean-toolchain
  AMCEP.lean
  AMCEP/
    Core.lean
    Limits.lean
```

## Kernel-checked theorem set

### Original equation

The library defines the source score over exact real numbers:

```text
originalScore rho T x E n = (rho + T - rho*x^n) / E
```

It proves:

- the exact score difference produced by changing `rho`;
- the exact score difference produced by changing `T`;
- strict increase in `T` when `E > 0`;
- strict increase in `rho` when `rho1 < rho2`, `E > 0`, and `x^n < 1`;
- an exact counterexample at `rho1 = 1`, `rho2 = 2`, `T = 5`, `x = 1/2`, `n = 10`, and `E = 1`.

The contradiction-penalty principle for the original equation is therefore formally falsified in that domain.

### Residual limits

The library proves:

- `rho*x^n` tends to zero for real `rho` and `x` when `|x| < 1`;
- the residual is identically zero when `rho = 0`;
- at `x = 1`, the residual remains constant;
- at `x = -1`, even-index residuals equal `rho` and odd-index residuals equal `-rho`.

The complete biconditional classification

```text
rho*x^n -> 0 iff rho = 0 or |x| < 1
```

is not yet promoted to `formally-verified`; the current files prove the positive domain and exact boundary identities but do not yet contain the complete converse for every `|x| > 1` case.

### Transient candidate

The library defines

```text
transientScore rho T x E w n = (T - w*rho*|x|^n) / E
```

and proves:

- non-increasing behavior in `rho` for `E > 0` and `w >= 0`;
- convergence to `T/E` when `|x| < 1`;
- the resulting disappearance of the contradiction penalty in that limit;
- exact behavior at `x = 1`.

### Cumulative candidate

The library defines

```text
cumulativeScore rho T x E w n = (T - w*rho*(1 - |x|^n)) / E
```

and proves:

- non-increasing behavior in `rho` for `E > 0`, `w >= 0`, and `|x|^n <= 1`;
- convergence to `(T - w*rho)/E` when `|x| < 1`;
- exact behavior at `x = 1`.

These are mathematical properties of candidate functions. They do not establish empirical validity or moral authority.

## Reproduction

From the repository root:

```bash
cd formal
lake update
lake exe cache get
lake build
```

The CI verifier result is attached to the exact pull-request commit. A claim is promoted only when `data/claims.json` names the exact theorem artifact supporting it.

## Prohibited shortcuts

Formal files must not use:

- `sorry`;
- `admit`;
- unreviewed custom axioms introduced to force a result;
- `Float` as a replacement for `Real` theorem statements;
- a finite depth as a replacement for a limit;
- an informal correspondence table as a categorical construction.

## Model-assisted workflow

The registered Hugging Face theorem provers may propose statements and proof scripts. Every proposal must pass:

```text
candidate statement
→ assumption audit
→ Lean elaboration
→ kernel check
→ counterexample search
→ claim-ledger update
```

Agreement between multiple language models is not independent mathematical verification.

## Remaining formal work

- prove the full residual-convergence biconditional;
- prove divergence for `|x| > 1` when `rho != 0`;
- add bounded-transform real-analysis theorems;
- add scale and dimensional-consistency theorems once units are formally represented;
- separate the current modules into narrower domain, counterexample, candidate, and bounds modules as the theorem library grows.
