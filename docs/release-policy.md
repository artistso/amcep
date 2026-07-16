# AMCEP Release Policy

## Purpose

A release is a reproducible snapshot of software, definitions, claim statuses, and evidence artifacts. A release number is not a scientific certification.

## Versioning

AMCEP uses semantic versioning for repository compatibility:

- **Major:** incompatible claim-schema, API, score-interface, or evidence-governance change.
- **Minor:** compatible candidate model, theorem module, benchmark, dataset, or evidence artifact.
- **Patch:** correction, audit clarification, test expansion, documentation, or non-breaking infrastructure change.

## Required release contents

Every release must identify:

1. exact Git commit;
2. claim-ledger schema version;
3. all claim-status changes;
4. definitions and assumptions changed;
5. proof artifacts added or invalidated;
6. numerical and empirical artifacts added;
7. falsifications and retractions;
8. toolchain and dependency revisions;
9. deployment identifier, when public-site content changes;
10. known limitations and rollback instructions.

## Evidence promotion gates

### Conditionally proved

Requires an exact statement, explicit assumptions, and a reviewable proof. This is not equivalent to formal verification.

### Formally verified

Requires a kernel-checked artifact, pinned formal environment, passing CI, and no `sorry` or convenience axiom that asserts the target.

### Numerically supported

Requires reproducible code, declared parameter range, raw outputs, seeds, and an explicit statement that finite computation does not prove a universal theorem.

### Empirically supported

Requires a preregistered or locked protocol, data provenance, baselines, raw artifacts, effect sizes, uncertainty, failure analysis, and scope limited to the tested domain.

### Falsified or retracted

Requires preservation of the rejected statement, evidence, correction, affected dependencies, and replacement relationship. Retraction never erases history.

## Pre-release checks

```bash
python -m pip install -e '.[dev]'
ruff check src tests
mypy src
pytest --cov=src --cov-report=term-missing
node --check app.js
```

Once Lean is initialized, `lake build` and the no-`sorry` gate become mandatory.

The release candidate must also pass:

- claim-ledger JSON Schema validation;
- uniqueness of claim IDs;
- evidence-artifact requirements for promoted statuses;
- public-site asset checks;
- internal-link and deployment traceability checks;
- review of every unsupported or universal statement.

## Release notes structure

Release notes must separate:

- definitions;
- mathematical proofs;
- formal proofs;
- numerical evidence;
- empirical evidence;
- falsifications;
- retractions;
- infrastructure;
- known limitations.

These sections must not be collapsed into a generic claim that AMCEP was 'verified.'

## Deployment rule

A site URL is reported as live only after an HTTP verification confirms that the deployed content matches the release commit. Reserved project names and undeployed targets are not public releases.

## Rollback rule

Rollback is required when:

- a promoted claim lacks its required evidence artifact;
- schema or CI defects allow invalid promotion;
- the deployed site differs materially from the release commit;
- a security or integrity defect exposes users to misleading results;
- a mathematical or empirical defect invalidates the release's central claims.

Rollback does not remove the defective release from history. It marks the release and related claims with the appropriate correction or retraction.