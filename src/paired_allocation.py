"""Paired counterfactual analysis for the AMCEP allocation benchmark.

Every attack-rate condition reuses the same seed, latent projects, observation
noise, and exact oracle. Only the strategic attack threshold changes. This
supports within-scenario deltas and removes the independent-block caveat from
the first allocation benchmark. Synthetic results remain non-empirical.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass, replace

from src.allocation_benchmark import (
    MODELS,
    AllocationConfig,
    AllocationModel,
    AllocationProject,
    AllocationScenario,
    MeanInterval,
    bootstrap_mean_interval,
    evaluate_scenario,
)


@dataclass(frozen=True)
class LatentProjectFingerprint:
    project_id: int
    persistence_kind: str
    true_utility: float
    cost: int
    true_prevalence: float
    true_severity: float
    x: float
    depth: int


@dataclass(frozen=True)
class PairedDelta:
    seed: int
    model: AllocationModel
    baseline_attack_rate: float
    attack_rate: float
    delta_true_value: float
    delta_value_gap: float
    delta_penalized_regret: float
    delta_feasibility: float
    delta_true_risk_excess: float
    delta_attacked_selected: float


@dataclass(frozen=True)
class PairedAggregate:
    model: AllocationModel
    baseline_attack_rate: float
    attack_rate: float
    pairs: int
    delta_true_value: MeanInterval
    delta_value_gap: MeanInterval
    delta_penalized_regret: MeanInterval
    delta_feasibility: MeanInterval
    delta_true_risk_excess: MeanInterval
    delta_attacked_selected: MeanInterval


def latent_fingerprint(
    projects: tuple[AllocationProject, ...],
) -> tuple[LatentProjectFingerprint, ...]:
    """Extract fields that strategic reporting must never change."""

    return tuple(
        LatentProjectFingerprint(
            project_id=project.project_id,
            persistence_kind=project.persistence_kind,
            true_utility=project.true_utility,
            cost=project.cost,
            true_prevalence=project.true_prevalence,
            true_severity=project.true_severity,
            x=project.x,
            depth=project.depth,
        )
        for project in projects
    )


def attacked_project_ids(scenario: AllocationScenario) -> frozenset[int]:
    return frozenset(
        project.project_id for project in scenario.projects if project.attacked
    )


def run_paired_grid(
    seeds: Iterable[int],
    attack_rates: Iterable[float],
    base_config: AllocationConfig | None = None,
) -> tuple[AllocationScenario, ...]:
    """Evaluate every attack rate on identical latent scenarios per seed."""

    config = base_config or AllocationConfig()
    config.validate()
    seed_values = tuple(seeds)
    rate_values = tuple(sorted(set(attack_rates)))
    if not seed_values:
        raise ValueError("at least one seed is required")
    if len(rate_values) < 2:
        raise ValueError("at least two distinct attack rates are required")
    if any(not 0.0 <= rate <= 1.0 for rate in rate_values):
        raise ValueError("attack rates must be in [0, 1]")

    scenarios: list[AllocationScenario] = []
    for seed in seed_values:
        seed_scenarios = tuple(
            evaluate_scenario(seed, replace(config, attack_rate=rate))
            for rate in rate_values
        )
        reference = seed_scenarios[0]
        reference_fingerprint = latent_fingerprint(reference.projects)
        reference_oracle = reference.oracle
        previous_attacked: frozenset[int] = frozenset()

        for scenario in seed_scenarios:
            if latent_fingerprint(scenario.projects) != reference_fingerprint:
                raise AssertionError("paired conditions changed latent projects")
            if scenario.oracle != reference_oracle:
                raise AssertionError("paired conditions changed the exact oracle")
            current_attacked = attacked_project_ids(scenario)
            if not previous_attacked.issubset(current_attacked):
                raise AssertionError("attack sets must be nested by attack rate")
            previous_attacked = current_attacked
            scenarios.append(scenario)

    return tuple(scenarios)


def paired_deltas(
    scenarios: tuple[AllocationScenario, ...],
    *,
    baseline_attack_rate: float = 0.0,
) -> tuple[PairedDelta, ...]:
    """Compute within-seed policy deltas relative to one attack rate."""

    if not scenarios:
        raise ValueError("scenarios must be non-empty")
    grouped: defaultdict[int, dict[float, AllocationScenario]] = defaultdict(dict)
    for scenario in scenarios:
        rate = scenario.config.attack_rate
        if rate in grouped[scenario.seed]:
            raise ValueError("duplicate seed and attack-rate condition")
        grouped[scenario.seed][rate] = scenario

    deltas: list[PairedDelta] = []
    for seed, by_rate in sorted(grouped.items()):
        if baseline_attack_rate not in by_rate:
            raise ValueError(f"seed {seed} is missing the baseline attack rate")
        baseline = by_rate[baseline_attack_rate]
        baseline_outcomes = {
            outcome.model: outcome for outcome in baseline.outcomes
        }
        baseline_fingerprint = latent_fingerprint(baseline.projects)

        for attack_rate, scenario in sorted(by_rate.items()):
            if attack_rate == baseline_attack_rate:
                continue
            if latent_fingerprint(scenario.projects) != baseline_fingerprint:
                raise ValueError("paired delta received non-identical latent projects")
            outcomes = {outcome.model: outcome for outcome in scenario.outcomes}
            for model in MODELS:
                before = baseline_outcomes[model]
                after = outcomes[model]
                deltas.append(
                    PairedDelta(
                        seed=seed,
                        model=model,
                        baseline_attack_rate=baseline_attack_rate,
                        attack_rate=attack_rate,
                        delta_true_value=after.true_value - before.true_value,
                        delta_value_gap=after.value_gap - before.value_gap,
                        delta_penalized_regret=(
                            after.penalized_regret - before.penalized_regret
                        ),
                        delta_feasibility=(
                            float(after.true_feasible)
                            - float(before.true_feasible)
                        ),
                        delta_true_risk_excess=float(
                            after.true_risk_excess - before.true_risk_excess
                        ),
                        delta_attacked_selected=float(
                            after.attacked_selected - before.attacked_selected
                        ),
                    )
                )
    return tuple(deltas)


def summarize_paired_deltas(
    deltas: tuple[PairedDelta, ...],
    *,
    bootstrap_seed: int = 20260716,
    resamples: int = 1000,
) -> tuple[PairedAggregate, ...]:
    """Aggregate paired deltas with percentile-bootstrap mean intervals."""

    if not deltas:
        raise ValueError("deltas must be non-empty")
    grouped: defaultdict[
        tuple[float, float, AllocationModel], list[PairedDelta]
    ] = defaultdict(list)
    for delta in deltas:
        grouped[
            (delta.baseline_attack_rate, delta.attack_rate, delta.model)
        ].append(delta)

    aggregates: list[PairedAggregate] = []
    for index, (key, rows) in enumerate(
        sorted(grouped.items(), key=lambda item: item[0])
    ):
        baseline_rate, attack_rate, model = key
        interval_seed = bootstrap_seed + index * 10_000
        aggregates.append(
            PairedAggregate(
                model=model,
                baseline_attack_rate=baseline_rate,
                attack_rate=attack_rate,
                pairs=len(rows),
                delta_true_value=bootstrap_mean_interval(
                    tuple(row.delta_true_value for row in rows),
                    seed=interval_seed + 1,
                    resamples=resamples,
                ),
                delta_value_gap=bootstrap_mean_interval(
                    tuple(row.delta_value_gap for row in rows),
                    seed=interval_seed + 2,
                    resamples=resamples,
                ),
                delta_penalized_regret=bootstrap_mean_interval(
                    tuple(row.delta_penalized_regret for row in rows),
                    seed=interval_seed + 3,
                    resamples=resamples,
                ),
                delta_feasibility=bootstrap_mean_interval(
                    tuple(row.delta_feasibility for row in rows),
                    seed=interval_seed + 4,
                    resamples=resamples,
                ),
                delta_true_risk_excess=bootstrap_mean_interval(
                    tuple(row.delta_true_risk_excess for row in rows),
                    seed=interval_seed + 5,
                    resamples=resamples,
                ),
                delta_attacked_selected=bootstrap_mean_interval(
                    tuple(row.delta_attacked_selected for row in rows),
                    seed=interval_seed + 6,
                    resamples=resamples,
                ),
            )
        )
    return tuple(aggregates)


def serializable_deltas(deltas: tuple[PairedDelta, ...]) -> list[dict[str, object]]:
    return [asdict(delta) for delta in deltas]


def serializable_aggregates(
    aggregates: tuple[PairedAggregate, ...],
) -> list[dict[str, object]]:
    return [asdict(aggregate) for aggregate in aggregates]
