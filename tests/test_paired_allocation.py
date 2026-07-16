from __future__ import annotations

from dataclasses import replace

import pytest

from src.allocation_benchmark import AllocationConfig, AllocationScenario
from src.paired_allocation import (
    attacked_project_ids,
    latent_fingerprint,
    paired_deltas,
    run_paired_grid,
    summarize_paired_deltas,
)


def test_paired_grid_preserves_latent_projects_and_oracle() -> None:
    config = AllocationConfig(project_count=20)
    scenarios = run_paired_grid((11,), (0.0, 0.25, 0.5, 1.0), config)
    assert len(scenarios) == 4
    reference = scenarios[0]
    reference_fingerprint = latent_fingerprint(reference.projects)
    for scenario in scenarios[1:]:
        assert latent_fingerprint(scenario.projects) == reference_fingerprint
        assert scenario.oracle == reference.oracle


def test_attack_sets_are_nested_for_shared_seed() -> None:
    scenarios = run_paired_grid(
        (19,),
        (0.0, 0.1, 0.25, 0.5, 1.0),
        AllocationConfig(project_count=20),
    )
    attacked_sets = [attacked_project_ids(scenario) for scenario in scenarios]
    assert attacked_sets[0] == frozenset()
    assert all(
        left.issubset(right)
        for left, right in zip(attacked_sets, attacked_sets[1:], strict=True)
    )
    persistent_ids = {
        project.project_id
        for project in scenarios[-1].projects
        if project.persistence_kind == "persistent"
    }
    assert attacked_sets[-1] == persistent_ids


def test_paired_grid_is_deterministic() -> None:
    config = AllocationConfig(project_count=12)
    first = run_paired_grid((101, 102), (0.0, 0.5), config)
    second = run_paired_grid((101, 102), (0.0, 0.5), config)
    assert first == second


def test_paired_delta_shape_and_baseline_exclusion() -> None:
    seeds = (101, 102, 103)
    rates = (0.0, 0.25, 0.5)
    scenarios = run_paired_grid(
        seeds,
        rates,
        AllocationConfig(project_count=10),
    )
    deltas = paired_deltas(scenarios)
    assert len(deltas) == len(seeds) * (len(rates) - 1) * 8
    assert {delta.attack_rate for delta in deltas} == {0.25, 0.5}
    assert {delta.baseline_attack_rate for delta in deltas} == {0.0}


def test_zero_attack_condition_has_no_attacked_projects() -> None:
    scenarios = run_paired_grid(
        (201,),
        (0.0, 1.0),
        AllocationConfig(project_count=20),
    )
    baseline = scenarios[0]
    assert baseline.config.attack_rate == 0.0
    assert not attacked_project_ids(baseline)
    assert all(outcome.attacked_selected == 0 for outcome in baseline.outcomes)


def test_full_attack_changes_at_least_one_policy_outcome() -> None:
    scenarios = run_paired_grid(
        range(300, 310),
        (0.0, 1.0),
        AllocationConfig(project_count=16),
    )
    deltas = paired_deltas(scenarios)
    assert any(delta.delta_penalized_regret != 0.0 for delta in deltas)
    assert any(delta.delta_attacked_selected > 0.0 for delta in deltas)


def test_paired_aggregate_shape_and_interval_order() -> None:
    scenarios = run_paired_grid(
        (401, 402, 403, 404),
        (0.0, 0.25, 0.5),
        AllocationConfig(project_count=10),
    )
    deltas = paired_deltas(scenarios)
    aggregates = summarize_paired_deltas(deltas, resamples=200)
    assert len(aggregates) == 2 * 8
    assert all(aggregate.pairs == 4 for aggregate in aggregates)
    for aggregate in aggregates:
        for interval in (
            aggregate.delta_true_value,
            aggregate.delta_value_gap,
            aggregate.delta_penalized_regret,
            aggregate.delta_feasibility,
            aggregate.delta_true_risk_excess,
            aggregate.delta_attacked_selected,
        ):
            assert interval.low <= interval.mean <= interval.high


def test_paired_aggregate_is_deterministic() -> None:
    scenarios = run_paired_grid(
        (501, 502, 503),
        (0.0, 0.5),
        AllocationConfig(project_count=10),
    )
    deltas = paired_deltas(scenarios)
    first = summarize_paired_deltas(deltas, resamples=200)
    second = summarize_paired_deltas(deltas, resamples=200)
    assert first == second


def test_paired_grid_validation() -> None:
    config = AllocationConfig(project_count=8)
    with pytest.raises(ValueError, match="seed"):
        run_paired_grid((), (0.0, 0.5), config)
    with pytest.raises(ValueError, match="two distinct"):
        run_paired_grid((1,), (0.0,), config)
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        run_paired_grid((1,), (0.0, 1.1), config)


def test_paired_delta_requires_baseline() -> None:
    scenarios = run_paired_grid(
        (601,),
        (0.25, 0.5),
        AllocationConfig(project_count=8),
    )
    with pytest.raises(ValueError, match="missing the baseline"):
        paired_deltas(scenarios, baseline_attack_rate=0.0)


def test_paired_delta_rejects_duplicate_condition() -> None:
    scenarios = run_paired_grid(
        (701,),
        (0.0, 0.5),
        AllocationConfig(project_count=8),
    )
    duplicated: tuple[AllocationScenario, ...] = scenarios + (scenarios[0],)
    with pytest.raises(ValueError, match="duplicate"):
        paired_deltas(duplicated)


def test_paired_delta_rejects_latent_mismatch() -> None:
    scenarios = list(
        run_paired_grid(
            (801,),
            (0.0, 0.5),
            AllocationConfig(project_count=8),
        )
    )
    attacked = scenarios[1]
    changed_project = replace(
        attacked.projects[0],
        true_utility=attacked.projects[0].true_utility + 1.0,
    )
    scenarios[1] = replace(
        attacked,
        projects=(changed_project, *attacked.projects[1:]),
    )
    with pytest.raises(ValueError, match="non-identical"):
        paired_deltas(tuple(scenarios))


def test_empty_delta_summary_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        summarize_paired_deltas(())
