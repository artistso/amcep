"""Decision-level synthetic benchmark for AMCEP score families.

The benchmark defines an explicit resource-allocation problem with a budget,
a persistent-risk cap, an exact two-constraint knapsack oracle, strategic
reporting attacks, and deterministic uncertainty summaries. Synthetic results
are falsification and software evidence only; they do not establish external
validity, fairness, morality, or physical law.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass, replace
from typing import Literal

from src.amcep import AMCEPState, original_score
from src.safe_scores import (
    SafeScoreContract,
    safe_bounded_cumulative_score,
    safe_bounded_transient_score,
    safe_cumulative_score,
    safe_transient_score,
)

PersistenceKind = Literal["repairable", "persistent"]
AllocationModel = Literal[
    "task_only",
    "class_aware",
    "linear_penalty",
    "original",
    "transient",
    "cumulative",
    "bounded_transient",
    "bounded_cumulative",
]

MODELS: tuple[AllocationModel, ...] = (
    "task_only",
    "class_aware",
    "linear_penalty",
    "original",
    "transient",
    "cumulative",
    "bounded_transient",
    "bounded_cumulative",
)


@dataclass(frozen=True)
class AllocationConfig:
    """Locked generator and decision-policy configuration."""

    project_count: int = 16
    budget: int = 32
    risk_budget: int = 24
    attack_rate: float = 0.25
    utility_inflation: float = 0.35
    risk_underreporting: float = 0.65
    observation_noise: float = 0.05
    harm_weight: float = 4.0
    penalty_weight: float = 4.0
    risk_scale: int = 10
    violation_penalty: float = 3.0
    bounded_temperature: float = 3.0

    def validate(self) -> None:
        if not 2 <= self.project_count <= 20:
            raise ValueError("project_count must be between 2 and 20")
        if self.budget <= 0:
            raise ValueError("budget must be positive")
        if self.risk_budget < 0:
            raise ValueError("risk_budget must be non-negative")
        if self.risk_scale <= 0:
            raise ValueError("risk_scale must be positive")
        for name, value in (
            ("attack_rate", self.attack_rate),
            ("utility_inflation", self.utility_inflation),
            ("risk_underreporting", self.risk_underreporting),
            ("observation_noise", self.observation_noise),
            ("harm_weight", self.harm_weight),
            ("penalty_weight", self.penalty_weight),
            ("violation_penalty", self.violation_penalty),
            ("bounded_temperature", self.bounded_temperature),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not 0.0 <= self.attack_rate <= 1.0:
            raise ValueError("attack_rate must be in [0, 1]")
        if self.utility_inflation < 0.0:
            raise ValueError("utility_inflation must be non-negative")
        if not 0.0 <= self.risk_underreporting < 1.0:
            raise ValueError("risk_underreporting must be in [0, 1)")
        if self.observation_noise < 0.0:
            raise ValueError("observation_noise must be non-negative")
        if self.harm_weight < 0.0 or self.penalty_weight < 0.0:
            raise ValueError("harm and penalty weights must be non-negative")
        if self.violation_penalty < 0.0:
            raise ValueError("violation_penalty must be non-negative")
        if self.bounded_temperature <= 0.0:
            raise ValueError("bounded_temperature must be positive")


@dataclass(frozen=True)
class AllocationProject:
    """One project with latent truth and a potentially manipulated report."""

    project_id: int
    persistence_kind: PersistenceKind
    true_utility: float
    cost: int
    true_prevalence: float
    true_severity: float
    x: float
    depth: int
    reported_utility: float
    reported_prevalence: float
    reported_severity: float
    attacked: bool

    def validate(self) -> None:
        scalars = (
            self.true_utility,
            self.true_prevalence,
            self.true_severity,
            self.x,
            self.reported_utility,
            self.reported_prevalence,
            self.reported_severity,
        )
        if not all(math.isfinite(value) for value in scalars):
            raise ValueError("all project scalars must be finite")
        if self.project_id < 0:
            raise ValueError("project_id must be non-negative")
        if self.persistence_kind not in ("repairable", "persistent"):
            raise ValueError("invalid persistence kind")
        if self.true_utility < 0.0 or self.reported_utility < 0.0:
            raise ValueError("utility must be non-negative")
        if self.cost <= 0:
            raise ValueError("cost must be positive")
        if not 0.0 <= self.true_prevalence <= 1.0:
            raise ValueError("true prevalence must be in [0, 1]")
        if not 0.0 <= self.reported_prevalence <= 1.0:
            raise ValueError("reported prevalence must be in [0, 1]")
        if self.true_severity < 0.0 or self.reported_severity < 0.0:
            raise ValueError("severity must be non-negative")
        if not 0.0 <= self.x < 1.0:
            raise ValueError("allocation persistence proxy x must be in [0, 1)")
        if self.depth < 1:
            raise ValueError("depth must be positive")

    @property
    def true_rho(self) -> float:
        return self.true_prevalence * self.true_severity

    @property
    def reported_rho(self) -> float:
        return self.reported_prevalence * self.reported_severity

    @property
    def persistence_multiplier(self) -> float:
        return 0.25 if self.persistence_kind == "repairable" else 1.0

    def true_net_value(self, harm_weight: float) -> float:
        return self.true_utility - (
            harm_weight * self.true_rho * self.persistence_multiplier
        )

    def true_risk_units(self, risk_scale: int) -> int:
        return math.ceil(
            risk_scale * self.true_rho * self.persistence_multiplier
        )

    def reported_risk_units(self, risk_scale: int) -> int:
        return math.ceil(
            risk_scale * self.reported_rho * self.persistence_multiplier
        )


@dataclass(frozen=True)
class OracleSolution:
    selected_ids: tuple[int, ...]
    true_value: float
    cost_used: int
    true_risk_used: int


@dataclass(frozen=True)
class PolicyOutcome:
    model: AllocationModel
    selected_ids: tuple[int, ...]
    selected_count: int
    attacked_selected: int
    true_value: float
    oracle_value: float
    value_gap: float
    penalized_regret: float
    cost_used: int
    observed_risk_used: int
    true_risk_used: int
    true_risk_excess: int
    true_feasible: bool


@dataclass(frozen=True)
class AllocationScenario:
    seed: int
    config: AllocationConfig
    projects: tuple[AllocationProject, ...]
    oracle: OracleSolution
    outcomes: tuple[PolicyOutcome, ...]


@dataclass(frozen=True)
class MeanInterval:
    mean: float
    low: float
    high: float


@dataclass(frozen=True)
class AggregateOutcome:
    model: AllocationModel
    attack_rate: float
    scenarios: int
    true_value: MeanInterval
    value_gap: MeanInterval
    penalized_regret: MeanInterval
    feasibility_rate: MeanInterval
    true_risk_excess: MeanInterval
    attacked_selected: MeanInterval


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def generate_projects(
    seed: int,
    config: AllocationConfig,
) -> tuple[AllocationProject, ...]:
    """Generate one deterministic repairable-versus-persistent scenario."""

    config.validate()
    rng = random.Random(seed)
    projects: list[AllocationProject] = []
    report_factor = math.sqrt(1.0 - config.risk_underreporting)

    for project_id in range(config.project_count):
        persistence_kind: PersistenceKind = (
            "persistent" if rng.random() < 0.5 else "repairable"
        )
        true_utility = rng.uniform(2.0, 15.0)
        cost = rng.randint(1, 8)
        true_prevalence = rng.uniform(0.05, 0.95)
        true_severity = rng.uniform(0.2, 1.5)

        if persistence_kind == "repairable":
            x = rng.uniform(0.20, 0.65)
            depth = rng.randint(3, 8)
        else:
            x = rng.uniform(0.85, 0.99)
            depth = rng.randint(1, 3)

        reported_utility = max(
            0.0,
            true_utility
            + rng.gauss(0.0, config.observation_noise * true_utility),
        )
        reported_prevalence = _clamp(
            true_prevalence + rng.gauss(0.0, config.observation_noise),
            0.0,
            1.0,
        )
        reported_severity = max(
            0.0,
            true_severity
            + rng.gauss(0.0, config.observation_noise * true_severity),
        )

        attacked = (
            persistence_kind == "persistent"
            and rng.random() < config.attack_rate
        )
        if attacked:
            reported_utility *= 1.0 + config.utility_inflation
            reported_prevalence *= report_factor
            reported_severity *= report_factor

        project = AllocationProject(
            project_id=project_id,
            persistence_kind=persistence_kind,
            true_utility=true_utility,
            cost=cost,
            true_prevalence=true_prevalence,
            true_severity=true_severity,
            x=x,
            depth=depth,
            reported_utility=reported_utility,
            reported_prevalence=reported_prevalence,
            reported_severity=reported_severity,
            attacked=attacked,
        )
        project.validate()
        projects.append(project)

    return tuple(projects)


def _better_oracle_state(
    candidate: tuple[float, tuple[int, ...]],
    incumbent: tuple[float, tuple[int, ...]] | None,
) -> bool:
    if incumbent is None:
        return True
    candidate_value, candidate_ids = candidate
    incumbent_value, incumbent_ids = incumbent
    if candidate_value > incumbent_value + 1e-12:
        return True
    if abs(candidate_value - incumbent_value) <= 1e-12:
        return candidate_ids < incumbent_ids
    return False


def exact_oracle(
    projects: tuple[AllocationProject, ...],
    config: AllocationConfig,
) -> OracleSolution:
    """Solve the exact two-constraint 0/1 allocation problem by dynamic programming."""

    config.validate()
    for project in projects:
        project.validate()

    states: dict[tuple[int, int], tuple[float, tuple[int, ...]]] = {
        (0, 0): (0.0, ())
    }
    for project in projects:
        project_value = project.true_net_value(config.harm_weight)
        project_risk = project.true_risk_units(config.risk_scale)
        next_states = dict(states)
        for (cost_used, risk_used), (value, ids) in states.items():
            new_cost = cost_used + project.cost
            new_risk = risk_used + project_risk
            if new_cost > config.budget or new_risk > config.risk_budget:
                continue
            key = (new_cost, new_risk)
            candidate = (value + project_value, ids + (project.project_id,))
            if _better_oracle_state(candidate, next_states.get(key)):
                next_states[key] = candidate
        states = next_states

    best_key = (0, 0)
    best_state = states[best_key]
    for key, state in states.items():
        if _better_oracle_state(state, best_state):
            best_key = key
            best_state = state
        elif abs(state[0] - best_state[0]) <= 1e-12:
            if key[1] < best_key[1] or (
                key[1] == best_key[1] and key[0] < best_key[0]
            ):
                best_key = key
                best_state = state

    return OracleSolution(
        selected_ids=best_state[1],
        true_value=best_state[0],
        cost_used=best_key[0],
        true_risk_used=best_key[1],
    )


def model_score(
    project: AllocationProject,
    model: AllocationModel,
    config: AllocationConfig,
) -> float:
    """Evaluate one reported project under one declared scoring model."""

    project.validate()
    config.validate()
    if model == "task_only":
        return project.reported_utility
    if model == "class_aware":
        return project.reported_utility - (
            config.penalty_weight
            * project.reported_rho
            * project.persistence_multiplier
        )
    if model == "linear_penalty":
        return project.reported_utility - (
            config.penalty_weight * project.reported_rho
        )

    state = AMCEPState(
        rho=project.reported_rho,
        operator_power=project.reported_utility,
        x=project.x,
        n=project.depth,
        normalization=1.0,
        penalty_weight=config.penalty_weight,
    )
    if model == "original":
        return original_score(state)

    contract = SafeScoreContract(
        normalization_floor=0.5,
        persistence_policy="reject",
        output_temperature=config.bounded_temperature,
    )
    if model == "transient":
        return safe_transient_score(state, contract)
    if model == "cumulative":
        return safe_cumulative_score(state, contract)
    if model == "bounded_transient":
        return safe_bounded_transient_score(state, contract)
    if model == "bounded_cumulative":
        return safe_bounded_cumulative_score(state, contract)
    raise AssertionError(f"unhandled model: {model}")


def _score_margin(score: float, model: AllocationModel) -> float:
    if model in ("bounded_transient", "bounded_cumulative"):
        return score - 0.5
    return score


def apply_policy(
    projects: tuple[AllocationProject, ...],
    model: AllocationModel,
    config: AllocationConfig,
    oracle: OracleSolution | None = None,
) -> PolicyOutcome:
    """Rank by reported score per cost and enforce reported constraints."""

    config.validate()
    for project in projects:
        project.validate()
    if oracle is None:
        oracle = exact_oracle(projects, config)

    ranked: list[tuple[float, float, int, AllocationProject]] = []
    for project in projects:
        score = model_score(project, model, config)
        margin = _score_margin(score, model)
        if margin <= 0.0:
            continue
        ranked.append(
            (margin / project.cost, margin, -project.cost, project)
        )
    ranked.sort(
        key=lambda item: (
            -item[0],
            -item[1],
            -item[2],
            item[3].project_id,
        )
    )

    selected: list[AllocationProject] = []
    cost_used = 0
    observed_risk_used = 0
    for _, _, _, project in ranked:
        candidate_cost = cost_used + project.cost
        candidate_risk = observed_risk_used + project.reported_risk_units(
            config.risk_scale
        )
        if candidate_cost > config.budget:
            continue
        if candidate_risk > config.risk_budget:
            continue
        selected.append(project)
        cost_used = candidate_cost
        observed_risk_used = candidate_risk

    selected_ids = tuple(sorted(project.project_id for project in selected))
    true_value = sum(
        project.true_net_value(config.harm_weight) for project in selected
    )
    true_risk_used = sum(
        project.true_risk_units(config.risk_scale) for project in selected
    )
    true_risk_excess = max(0, true_risk_used - config.risk_budget)
    value_gap = oracle.true_value - true_value
    penalized_value = true_value - (
        config.violation_penalty * true_risk_excess
    )
    penalized_regret = max(0.0, oracle.true_value - penalized_value)

    return PolicyOutcome(
        model=model,
        selected_ids=selected_ids,
        selected_count=len(selected),
        attacked_selected=sum(project.attacked for project in selected),
        true_value=true_value,
        oracle_value=oracle.true_value,
        value_gap=value_gap,
        penalized_regret=penalized_regret,
        cost_used=cost_used,
        observed_risk_used=observed_risk_used,
        true_risk_used=true_risk_used,
        true_risk_excess=true_risk_excess,
        true_feasible=true_risk_excess == 0,
    )


def evaluate_scenario(seed: int, config: AllocationConfig) -> AllocationScenario:
    projects = generate_projects(seed, config)
    oracle = exact_oracle(projects, config)
    outcomes = tuple(
        apply_policy(projects, model, config, oracle) for model in MODELS
    )
    return AllocationScenario(
        seed=seed,
        config=config,
        projects=projects,
        oracle=oracle,
        outcomes=outcomes,
    )


def run_grid(
    seeds: Iterable[int],
    attack_rates: Iterable[float],
    base_config: AllocationConfig | None = None,
) -> tuple[AllocationScenario, ...]:
    """Evaluate a locked Cartesian grid of seeds and attack rates."""

    config = base_config or AllocationConfig()
    config.validate()
    scenarios: list[AllocationScenario] = []
    for attack_index, attack_rate in enumerate(attack_rates):
        if not 0.0 <= attack_rate <= 1.0:
            raise ValueError("every attack rate must be in [0, 1]")
        for seed in seeds:
            scenario_config = replace(config, attack_rate=attack_rate)
            scenarios.append(
                evaluate_scenario(seed + attack_index * 1_000_000, scenario_config)
            )
    return tuple(scenarios)


def bootstrap_mean_interval(
    values: tuple[float, ...],
    *,
    seed: int,
    resamples: int = 1000,
) -> MeanInterval:
    """Return a deterministic percentile-bootstrap interval for the mean."""

    if not values:
        raise ValueError("values must be non-empty")
    if resamples < 100:
        raise ValueError("resamples must be at least 100")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("bootstrap values must be finite")

    mean = sum(values) / len(values)
    if len(values) == 1:
        return MeanInterval(mean=mean, low=mean, high=mean)

    rng = random.Random(seed)
    bootstrap_means = []
    for _ in range(resamples):
        sample_mean = sum(rng.choice(values) for _ in values) / len(values)
        bootstrap_means.append(sample_mean)
    bootstrap_means.sort()
    low_index = math.floor(0.025 * (resamples - 1))
    high_index = math.ceil(0.975 * (resamples - 1))
    return MeanInterval(
        mean=mean,
        low=bootstrap_means[low_index],
        high=bootstrap_means[high_index],
    )


def summarize_grid(
    scenarios: tuple[AllocationScenario, ...],
    *,
    bootstrap_seed: int = 20260716,
    resamples: int = 1000,
) -> tuple[AggregateOutcome, ...]:
    """Aggregate decision metrics by attack rate and model."""

    if not scenarios:
        raise ValueError("scenarios must be non-empty")
    grouped: defaultdict[
        tuple[float, AllocationModel], list[PolicyOutcome]
    ] = defaultdict(list)
    for scenario in scenarios:
        for outcome in scenario.outcomes:
            grouped[(scenario.config.attack_rate, outcome.model)].append(outcome)

    aggregates: list[AggregateOutcome] = []
    for index, ((attack_rate, model), outcomes) in enumerate(
        sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1]))
    ):
        interval_seed = bootstrap_seed + index * 10_000
        aggregates.append(
            AggregateOutcome(
                model=model,
                attack_rate=attack_rate,
                scenarios=len(outcomes),
                true_value=bootstrap_mean_interval(
                    tuple(outcome.true_value for outcome in outcomes),
                    seed=interval_seed + 1,
                    resamples=resamples,
                ),
                value_gap=bootstrap_mean_interval(
                    tuple(outcome.value_gap for outcome in outcomes),
                    seed=interval_seed + 2,
                    resamples=resamples,
                ),
                penalized_regret=bootstrap_mean_interval(
                    tuple(outcome.penalized_regret for outcome in outcomes),
                    seed=interval_seed + 3,
                    resamples=resamples,
                ),
                feasibility_rate=bootstrap_mean_interval(
                    tuple(float(outcome.true_feasible) for outcome in outcomes),
                    seed=interval_seed + 4,
                    resamples=resamples,
                ),
                true_risk_excess=bootstrap_mean_interval(
                    tuple(float(outcome.true_risk_excess) for outcome in outcomes),
                    seed=interval_seed + 5,
                    resamples=resamples,
                ),
                attacked_selected=bootstrap_mean_interval(
                    tuple(float(outcome.attacked_selected) for outcome in outcomes),
                    seed=interval_seed + 6,
                    resamples=resamples,
                ),
            )
        )
    return tuple(aggregates)


def serializable_scenarios(
    scenarios: tuple[AllocationScenario, ...],
) -> list[dict[str, object]]:
    return [asdict(scenario) for scenario in scenarios]


def serializable_aggregates(
    aggregates: tuple[AggregateOutcome, ...],
) -> list[dict[str, object]]:
    return [asdict(aggregate) for aggregate in aggregates]
