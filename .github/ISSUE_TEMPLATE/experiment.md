---
name: Empirical experiment
description: Preregister a numerical or real-world AMCEP evaluation
title: "Experiment: "
labels: []
assignees:
  - artistso
---

## Claim IDs under test

List the exact ledger claims. Do not create a universal claim from a domain-specific experiment.

## Research question and hypotheses

- Primary hypothesis:
- Null hypothesis:
- Secondary hypotheses:

## Variables and measurement contract

For each variable, state its type, domain, units, observation model, estimator, uncertainty, intervention meaning, missing-data rule, and manipulation risk.

## Candidate models and ablations

List every AMCEP family, parameter range, transformation, and ablation to be evaluated.

## Baselines

Include the simplest credible alternatives capable of falsifying the need for AMCEP.

## Data and split policy

- Generator or dataset revision:
- Development set:
- Calibration set:
- Locked test set:
- Out-of-distribution set:
- Adversarial set:

## Primary metrics

State metrics, aggregation rules, statistical tests, uncertainty intervals, and multiple-comparison treatment before evaluation.

## Reproducibility manifest

- Code commit:
- Environment:
- Seeds:
- Command:
- Expected raw artifacts:
- Checksum method:

## Failure and stopping rules

State what outcome rejects the hypothesis, invalidates the run, or requires a retraction.

## Acceptance criteria

- [ ] Protocol frozen before locked evaluation.
- [ ] Raw outputs retained.
- [ ] Effect sizes and uncertainty reported.
- [ ] Negative results published.
- [ ] Results scoped to the tested distribution.
- [ ] Claim ledger status changed only after artifact validation.