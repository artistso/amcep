# AMCEP — Falsification-First Research Laboratory

AMCEP is being rebuilt as an auditable research program, not advertised as a completed universal theorem.

## Current mathematical status

The source material defines the score

```text
S_n(rho,T,x,E) = (rho + T - rho*x^n)/E.
```

The first audit found a decisive sign defect. For `E > 0`, `0 <= x < 1`, and `n > 0`,

```text
∂S_n/∂rho = (1 - x^n)/E > 0.
```

Therefore increasing the stated contradiction density `rho` raises the score, contrary to the stated monotonicity principle.

The residual `rho*x^n` tends to zero only when `rho = 0` or `|x| < 1`. A finite numerical check at `n = 20` is not a proof of a limit. Executing floating-point examples in Lean is not a proof of AMCEP, P = NP, the Hodge conjecture, BSD, or a moral theory.

## Repository map

- `index.html`, `styles.css`, `app.js` — public interactive audit
- `src/amcep.py` — executable reference model
- `tests/test_amcep.py` — boundary and property tests
- `research/math-audit.md` — claim-by-claim mathematical audit
- `data/audit.json` — machine-readable claim ledger
- `.github/workflows/ci.yml` — validation on every push to `main`
- `llms.txt` — agent-readable project summary

## Candidate repair under test

```text
S*_n(rho,T,x,E) = (T - rho*|x|^n)/E.
```

For `E > 0`, this candidate is non-increasing in `rho`. It remains a model proposal, not an established law; empirical calibration and domain justification are required.

## Local verification

```bash
python -m unittest discover -s tests -v
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Promotion rule

A claim can be called verified only when the repository contains its exact statement, assumptions, proof artifact, reproducible command, independent failure conditions, and a passing verifier result. Numerical examples are labeled numerical examples.
