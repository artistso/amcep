from __future__ import annotations

from dataclasses import replace

import pytest

from src.allocation_benchmark import (
    MODELS,
    AllocationConfig,
    AllocationProject,
    apply_policy,
    bootstrap_mean_interval,
    exact_oracle,
    generate_projects,
    model_score,
    run_grid,
    summarize_grid,
)


def project(
    project_id: int,
    *,
    utility: float,
    cost: int,
    prevalence: float = 0.0,
    severity: float = 0.0,
    persistence_kind: str = "persistent",
    x: float = 0.9,
    depth: int = 1,
    reported_utility: float | None = None,
    reported_prevalence: float | None = None,
    reported_severity: float | None = None,
    attacked: bool = False,
) -> AllocationProject:
    return AllocationProject(
        project_id=project_id,
        persistence_kind=persistence_kind,  # type: ignore[arg-type]
        true_utility=utility,
        cost=cost,
        true_prevalence=prevalence,
        true_severity=severity,
        x=x,
        depth=depth,
        reported_utility=(
            utility if reported_utility is None else reported_utility
        ),
        reported_prevalence=(
            prevalence if reported_prevalence is None else reported_prevalence
        ),
        reported_severity=(
            severity if reported_severity is None else reported_severity
        ),
        attacked=attacked,
    )


def test_generator_is_deterministic_and_separates_persistence_classes() -> None:
    config = AllocationConfig(
        project_count=20,
        attack_rate=0.0,
        observation_noise=0.0,
    )
    first = generate_projects(17, config)
    second = generate_projects(17, config)
    assert first == second
    assert {item.persistence_kind for item in first} == {
        "repairable",
        "persistent",
    }
    for item in first:
        if item.persistence_kind == "repairable":
            assert 0.20 <= item.x <= 0.65
            assert 3 <= item.depth <= 8
            assert item.persistence_multiplier == 0.25
        else:
            assert 0.85 <= item.x <= 0.99
            assert 1 <= item.depth <= 3
            assert item.persistence_multiplier == 1.0


def test_attack_only_targets_persistent_reports() -> None:
    config = AllocationConfig(
        project_count=20,
        attack_rate=1.0,
        observation_noise=0.0,
    )
    projects = generate_projects(19, config)
    persistent = [item for item in projects if item.persistence_kind == "persistent"]
    repairable = [item for item in projects if item.persistence_kind == "repairable"]
    assert persistent and repairable
    assert all(item.attacked for item in persistent)
    assert all(not item.attacked for item in repairable)
    for item in persistent:
        assert item.reported_utility == pytest.approx(
            item.true_utility * (1.0 + config.utility_inflation)
        )
        assert item.reported_rho == pytest.approx(
            item.true_rho * (1.0 - config.risk_underreporting)
        )


def test_exact_oracle_solves_two_constraint_knapsack() -> None:
    config = AllocationConfig(
        project_count=3,
        budget=4,
        risk_budget=4,
        harm_weight=1.0,
        risk_scale=1,
    )
    projects = (
        project(0, utility=8.0, cost=3),
        project(1, utility=5.0, cost=2),
        project(2, utility=5.0, cost=2),
    )
    oracle = exact_oracle(projects, config)
    assert oracle.selected_ids == (1, 2)
    assert oracle.true_value == pytest.approx(10.0)
    assert oracle.cost_used == 4
    assert oracle.true_risk_used == 0


def test_policy_never_exceeds_reported_constraints() -> None:
    config = AllocationConfig(project_count=16)
    projects = generate_projects(23, config)
    oracle = exact_oracle(projects, config)
    for model in MODELS:
        outcome = apply_policy(projects, model, config, oracle)
        assert outcome.cost_used <= config.budget
        assert outcome.observed_risk_used <= config.risk_budget
        assert outcome.selected_count == len(outcome.selected_ids)
        assert outcome.penalized_regret >= 0.0


def test_manipulated_report_can_hide_true_constraint_violation() -> None:
    config = AllocationConfig(
        project_count=2,
        budget=2,
        risk_budget=1,
        harm_weight=4.0,
        risk_scale=10,
        violation_penalty=3.0,
    )
    attacked = project(
        0,
        utility=10.0,
        cost=1,
        prevalence=0.8,
        severity=1.0,
        reported_utility=13.5,
        reported_prevalence=0.08,
        reported_severity=1.0,
        attacked=True,
    )
    benign = project(1, utility=1.0, cost=1)
    projects = (attacked, benign)
    oracle = exact_oracle(projects, config)
    outcome = apply_policy(projects, "task_only", config, oracle)
    assert outcome.observed_risk_used <= config.risk_budget
    assert outcome.true_risk_used > config.risk_budget
    assert outcome.true_risk_excess == 7
    assert not outcome.true_feasible
    assert outcome.attacked_selected == 1
    assert outcome.penalized_regret > 0.0


def test_transient_and_cumulative_reverse_persistence_semantics() -> None:
    config = AllocationConfig(project_count=2, penalty_weight=4.0)
    repairable = project(
        0,
        utility=10.0,
        cost=1,
        prevalence=0.5,
        severity=1.0,
        persistence_kind="repairable",
        x=0.3,
        depth=5,
    )
    persistent = project(
        1,
        utility=10.0,
        cost=1,
        prevalence=0.5,
        severity=1.0,
        persistence_kind="persistent",
        x=0.95,
        depth=1,
    )
    assert model_score(persistent, "transient", config) < model_score(
        repairable, "transient", config
    )
    assert model_score(repairable, "cumulative", config) < model_score(
        persistent, "cumulative", config
    )
    assert model_score(repairable, "class_aware", config) > model_score(
        persistent, "class_aware", config
    )


def test_original_score_rewards_more_reported_contradiction() -> None:
    config = AllocationConfig(project_count=2)
    low = project(
        0,
        utility=5.0,
        cost=1,
        prevalence=0.2,
        severity=1.0,
        x=0.5,
        depth=2,
    )
    high = replace(
        low,
        project_id=1,
        true_prevalence=0.8,
        reported_prevalence=0.8,
    )
    assert model_score(high, "original", config) > model_score(
        low, "original", config
    )


def test_bounded_models_remain_in_open_unit_interval() -> None:
    config = AllocationConfig(project_count=2)
    candidate = project(
        0,
        utility=15.0,
        cost=1,
        prevalence=0.9,
        severity=1.5,
        x=0.99,
        depth=3,
    )
    for model in ("bounded_transient", "bounded_cumulative"):
        score = model_score(candidate, model, config)
        assert 0.0 < score < 1.0


def test_bootstrap_interval_is_deterministic_and_ordered() -> None:
    values = (1.0, 2.0, 3.0, 4.0)
    first = bootstrap_mean_interval(values, seed=7, resamples=200)
    second = bootstrap_mean_interval(values, seed=7, resamples=200)
    assert first == second
    assert first.low <= first.mean <= first.high
    assert first.mean == pytest.approx(2.5)
    with pytest.raises(ValueError):
        bootstrap_mean_interval((), seed=1)
    with pytest.raises(ValueError):
        bootstrap_mean_interval(values, seed=1, resamples=99)


def test_grid_and_aggregate_shapes_are_locked() -> None:
    seeds = (101, 102, 103)
    attack_rates = (0.0, 0.5)
    config = AllocationConfig(project_count=8, budget=16, risk_budget=12)
    scenarios = run_grid(seeds, attack_rates, config)
    assert len(scenarios) == len(seeds) * len(attack_rates)
    assert {scenario.config.attack_rate for scenario in scenarios} == set(
        attack_rates
    )
    assert all(len(scenario.outcomes) == len(MODELS) for scenario in scenarios)

    aggregates = summarize_grid(scenarios, resamples=200)
    assert len(aggregates) == len(attack_rates) * len(MODELS)
    assert all(aggregate.scenarios == len(seeds) for aggregate in aggregates)
    assert all(
        aggregate.feasibility_rate.low
        <= aggregate.feasibility_rate.mean
        <= aggregate.feasibility_rate.high
        for aggregate in aggregates
    )


def test_invalid_config_and_project_domains_fail() -> None:
    invalid_configs = (
        AllocationConfig(project_count=1),
        AllocationConfig(budget=0),
        AllocationConfig(risk_budget=-1),
        AllocationConfig(attack_rate=1.1),
        AllocationConfig(risk_underreporting=1.0),
        AllocationConfig(bounded_temperature=0.0),
    )
    for config in invalid_configs:
        with pytest.raises(ValueError):
            config.validate()

    invalid_project = project(0, utility=1.0, cost=1)
    with pytest.raises(ValueError):
        replace(invalid_project, x=1.0).validate()
    with pytest.raises(ValueError):
        replace(invalid_project, cost=0).validate()
    with pytest.raises(ValueError):
        replace(invalid_project, reported_prevalence=1.1).validate()
