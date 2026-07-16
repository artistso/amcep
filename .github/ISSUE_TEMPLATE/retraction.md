---
name: Claim retraction
description: Retract or materially narrow a published AMCEP claim
title: "Retraction: "
labels: []
assignees:
  - artistso
---

## Claim ID and current statement

Identify the exact ledger entry and copy its current statement and status.

## Reason for retraction

Select and explain every applicable reason:

- [ ] Mathematical counterexample
- [ ] Missing or false assumption
- [ ] Formal proof failure
- [ ] Numerical implementation defect
- [ ] Unreproducible empirical result
- [ ] Data or provenance defect
- [ ] Overgeneralization beyond tested scope
- [ ] Quantum or categorical analogy presented as theorem
- [ ] Other

## Evidence

Link the counterexample, failed verifier output, corrected analysis, raw data, or independent replication.

## Corrected status and wording

- New status:
- Replacement statement:
- Replacement claim ID, when applicable:

## Downstream impact

List affected documentation, code, experiments, deployments, citations, releases, and dependent claims.

## Required actions

- [ ] Update `data/claims.json`.
- [ ] Preserve the original history.
- [ ] Add a changelog entry.
- [ ] Correct the public site.
- [ ] Mark dependent claims for review.
- [ ] Publish a replacement or scope correction.
- [ ] Verify deployment and cache invalidation.

## Non-erasure rule

Retraction changes status and public interpretation. It does not delete the original claim, evidence trail, or reason for correction.