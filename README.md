# AMCEP — Falsification-First Research Laboratory

AMCEP is being rebuilt as an auditable research program. It is **not** presented as a completed universal theorem, a physical law, a moral authority, or a solution to an open mathematical problem.

## Current mathematical status

The source material defines

```text
S_n(rho, T, x, E) = (rho + T - rho*x^n) / E.
```

For `E > 0`, `0 <= x < 1`, and `n > 0`,

```text
∂S_n/∂rho = (1 - x^n) / E > 0.
```

Increasing the stated contradiction density `rho` therefore **raises** the original score. This falsifies the stated contradiction-penalty principle in the intended regime.

The residual `rho*x^n` tends to zero only when `rho = 0` or `|x| < 1`. A finite calculation at `n = 20` does not prove an infinite limit. Floating-point execution in Lean does not prove AMCEP, P = NP, the Hodge conjecture, the Birch and Swinnerton-Dyer conjecture, quantum validity, or universal moral truth.

## Competing candidates under test

### Transient contradiction penalty

```text
S_transient = (T - lambda*rho*|x|^n) / E
```

This is non-increasing in `rho` for `E > 0` and `lambda >= 0`. For `|x| < 1`, however, the penalty vanishes as `n` grows.

### Cumulative contradiction penalty

```text
S_cumulative = (T - lambda*rho*(1 - |x|^n)) / E
```

For `E > 0`, `lambda >= 0`, and `|x| <= 1`, this is non-increasing in `rho`. For `|x| < 1`, its limiting contradiction penalty remains `lambda*rho/E`.

Neither candidate is an established real-world law. Model selection requires operational definitions, unit consistency, preregistered benchmarks, comparison with simple baselines, and independent reproduction.

## Repository map

- `index.html`, `styles.css`, `app.js` — public interactive audit
- `src/amcep.py` — executable original, transient, cumulative, and bounded models
- `tests/test_amcep.py` — numerical boundary tests
- `tests/test_properties.py` — property-based adversarial tests
- `tests/test_claim_ledger.py` — evidence-status enforcement
- `research/math-audit.md` — mathematical audit and competing model families
- `research/definitions.md` — variable and measurement contract
- `research/assumptions.md` — explicit assumptions and rejection gates
- `research/empirical-protocol.md` — preregistered benchmark structure
- `research/topology-audit.md` — topology, sheaf, and category-theory requirements
- `research/quantum-audit.md` — quantum construction and experiment requirements
- `data/claims.schema.json` — machine-readable claim schema
- `data/claims.json` — claim, evidence, falsifier, and status ledger
- `models/model-registry.json` — Hugging Face roles and verification boundaries
- `formal/README.md` — Lean formalization plan
- `.github/workflows/ci.yml` — validation on every pull request and main-branch push
- `llms.txt` — agent-readable project summary

## Evidence statuses

The ledger uses controlled statuses:

```text
proposed
defined
conditionally-proved
formally-verified
numerically-supported
empirically-supported
falsified
retracted
unsupported
```

`formally-verified` requires a kernel-checked formal artifact. `empirically-supported` requires a reproducible empirical artifact. Model confidence, rhetorical strength, and numerical examples cannot promote a claim.

## Local verification

```bash
python -m pip install -e '.[dev]'
ruff check src tests
mypy src
pytest --cov=src --cov-report=term-missing
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Hugging Face research stack

The model registry assigns separate roles to theorem-proving, retrieval, and contradiction-triage models. Model output is always provisional:

```text
model proposal
→ exact claim and assumptions
→ executable or Lean artifact
→ automated verification
→ adversarial review
→ ledger promotion
```

The Lean kernel—not a language model—is the proof authority.

## Contribution rule

Experimental changes belong on branches and enter `main` through pull requests. Every claim-changing pull request must identify:

- the exact claim IDs affected;
- assumptions added or removed;
- counterexamples considered;
- tests and formal artifacts;
- empirical artifacts, when applicable;
- rollback or falsification conditions.

## Promotion rule

A claim may be promoted only when the repository contains its exact statement, domain, assumptions, proof or data artifact, reproducible command, independent failure conditions, and passing verifier result. Negative results and falsifications remain public.