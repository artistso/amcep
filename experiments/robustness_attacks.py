"""Independent robustness attacks for AMCEP score families.

This module deliberately re-implements the score equations with ``Decimal``
instead of calling the production implementation. Agreement checks therefore
exercise an independent arithmetic path. The attacks test software behavior,
unit-rescaling consistency, boundary sensitivity, and contradiction-severity
monotonicity. They do not establish real-world validity or moral truth.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, localcontext
from typing import Literal

from src.amcep import AMCEPState, cumulative_score, original_score, transient_score

ModelName = Literal["original", "transient", "cumulative"]
GroupName = Literal[
    "in_distribution",
    "boundary_x",
    "small_E",
    "high_severity",
    "combined",
]
MODELS: tuple[ModelName, ...] = ("original", "transient", "cumulative")
GROUPS: tuple[GroupName, ...] = (
    "in_distribution",
    "boundary_x",
    "small_E",
    "high_severity",
    "combined",
)


@dataclass(frozen=True)
class RobustnessCase:
    """One fully specified score case with separated prevalence and severity."""

    prevalence: float
    severity: float
    operator_power: float
    x: float
    depth: int
    normalization: float
    penalty_weight: float

    @property
    def effective_contradiction(self) -> float:
        return self.prevalence * self.severity

    def validate(self) -> None:
        scalars = (
            self.prevalence,
            self.severity,
            self.operator_power,
            self.x,
            self.normalization,
            self.penalty_weight,
        )
        if not all(math.isfinite(value) for value in scalars):
            raise ValueError("all scalar inputs must be finite")
        if not 0.0 <= self.prevalence <= 1.0:
            raise ValueError("prevalence must be in [0, 1]")
        if self.severity < 0.0:
            raise ValueError("severity must be non-negative")
        if self.depth < 0:
            raise ValueError("depth must be non-negative")
        if self.normalization <= 0.0:
            raise ValueError("normalization must be strictly positive")
        if self.penalty_weight < 0.0:
            raise ValueError("penalty_weight must be non-negative")


@dataclass(frozen=True)
class GroupSummary:
    group: GroupName
    model: ModelName
    observations: int
    nonfinite_rate: float
    mean_abs_score: float
    p95_abs_score: float
    severity_violation_rate: float
    unit_rescaling_violation_rate: float
    max_unit_rescaling_error: float
    max_decimal_disagreement: float


def _state(case: RobustnessCase) -> AMCEPState:
    case.validate()
    return AMCEPState(
        rho=case.effective_contradiction,
        operator_power=case.operator_power,
        x=case.x,
        n=case.depth,
        normalization=case.normalization,
        penalty_weight=case.penalty_weight,
    )


def float_score(case: RobustnessCase, model: ModelName) -> float:
    """Evaluate through the production implementation."""

    state = _state(case)
    if model == "original":
        return original_score(state)
    if model == "transient":
        return transient_score(state)
    if model == "cumulative":
        return cumulative_score(state)
    raise AssertionError(f"unhandled model: {model}")


def decimal_score(case: RobustnessCase, model: ModelName) -> Decimal:
    """Evaluate independently using high-precision decimal arithmetic."""

    case.validate()
    with localcontext() as context:
        context.prec = 60
        prevalence = Decimal(str(case.prevalence))
        severity = Decimal(str(case.severity))
        rho = prevalence * severity
        operator_power = Decimal(str(case.operator_power))
        x = Decimal(str(case.x))
        normalization = Decimal(str(case.normalization))
        weight = Decimal(str(case.penalty_weight))
        persistence = abs(x) ** case.depth

        if model == "original":
            numerator = rho + operator_power - rho * (x**case.depth)
        elif model == "transient":
            numerator = operator_power - weight * rho * persistence
        elif model == "cumulative":
            numerator = operator_power - weight * rho * (
                Decimal(1) - persistence
            )
        else:
            raise AssertionError(f"unhandled model: {model}")
        return numerator / normalization


def rescale_units(case: RobustnessCase, factor: float) -> RobustnessCase:
    """Change the task-value unit while preserving dimensionless quantities.

    A coherent unit change scales ``T``, ``E``, and the contradiction penalty
    coefficient together. Prevalence, severity, ``x``, and depth are unchanged.
    """

    if not math.isfinite(factor) or factor <= 0.0:
        raise ValueError("factor must be finite and strictly positive")
    return replace(
        case,
        operator_power=case.operator_power * factor,
        normalization=case.normalization * factor,
        penalty_weight=case.penalty_weight * factor,
    )


def unit_rescaling_error(
    case: RobustnessCase,
    model: ModelName,
    factor: float,
) -> float:
    baseline = float_score(case, model)
    transformed = float_score(rescale_units(case, factor), model)
    return abs(transformed - baseline)


def severity_monotonicity_violation(
    case: RobustnessCase,
    model: ModelName,
    *,
    low: float = 0.25,
    high: float = 2.0,
) -> bool:
    """Whether greater contradiction severity strictly increases the score."""

    if not 0.0 <= low < high:
        raise ValueError("require 0 <= low < high")
    low_case = replace(case, severity=low)
    high_case = replace(case, severity=high)
    return float_score(high_case, model) > float_score(low_case, model)


def _quantile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("values must be non-empty")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def generate_group(
    group: GroupName,
    *,
    sample_size: int = 400,
    seed: int = 20260716,
) -> tuple[RobustnessCase, ...]:
    """Generate a deterministic in-distribution or attack-domain group."""

    if sample_size < 2:
        raise ValueError("sample_size must be at least two")
    rng = random.Random(seed)
    cases: list[RobustnessCase] = []

    for _ in range(sample_size):
        prevalence = rng.uniform(0.0, 1.0)
        severity = rng.uniform(0.0, 1.0)
        operator_power = rng.uniform(-2.0, 2.0)
        x = rng.uniform(0.05, 0.95)
        depth = rng.randint(1, 12)
        normalization = rng.uniform(0.5, 2.0)
        penalty_weight = rng.uniform(0.5, 2.0)

        if group in ("boundary_x", "combined"):
            magnitude = rng.uniform(0.97, 1.03)
            x = magnitude if rng.random() < 0.5 else -magnitude
        if group in ("small_E", "combined"):
            normalization = 10 ** rng.uniform(-4.0, -1.0)
        if group in ("high_severity", "combined"):
            severity = rng.uniform(1.0, 10.0)
        if group not in GROUPS:
            raise AssertionError(f"unhandled group: {group}")

        cases.append(
            RobustnessCase(
                prevalence=prevalence,
                severity=severity,
                operator_power=operator_power,
                x=x,
                depth=depth,
                normalization=normalization,
                penalty_weight=penalty_weight,
            )
        )
    return tuple(cases)


def summarize_group(
    group: GroupName,
    model: ModelName,
    cases: tuple[RobustnessCase, ...],
    *,
    unit_factor: float = 1000.0,
    tolerance: float = 1e-10,
) -> GroupSummary:
    if not cases:
        raise ValueError("cases must be non-empty")

    scores = [float_score(case, model) for case in cases]
    finite_scores = [score for score in scores if math.isfinite(score)]
    nonfinite_rate = 1.0 - len(finite_scores) / len(scores)
    absolute_scores = [abs(score) for score in finite_scores]

    rescaling_errors = [
        unit_rescaling_error(case, model, unit_factor) for case in cases
    ]
    decimal_disagreements = [
        abs(float(decimal_score(case, model)) - float_score(case, model))
        for case in cases
    ]
    severity_violations = sum(
        severity_monotonicity_violation(case, model) for case in cases
    )

    return GroupSummary(
        group=group,
        model=model,
        observations=len(cases),
        nonfinite_rate=nonfinite_rate,
        mean_abs_score=sum(absolute_scores) / len(absolute_scores),
        p95_abs_score=_quantile(absolute_scores, 0.95),
        severity_violation_rate=severity_violations / len(cases),
        unit_rescaling_violation_rate=(
            sum(error > tolerance for error in rescaling_errors) / len(cases)
        ),
        max_unit_rescaling_error=max(rescaling_errors),
        max_decimal_disagreement=max(decimal_disagreements),
    )


def evaluate_matrix(
    *,
    sample_size: int = 400,
    seed: int = 20260716,
) -> tuple[GroupSummary, ...]:
    """Evaluate all models across all deterministic attack groups."""

    summaries: list[GroupSummary] = []
    for index, group in enumerate(GROUPS):
        cases = generate_group(group, sample_size=sample_size, seed=seed + index)
        summaries.extend(
            summarize_group(group, model, cases) for model in MODELS
        )
    return tuple(summaries)


def serializable_matrix(
    *,
    sample_size: int = 400,
    seed: int = 20260716,
) -> list[dict[str, object]]:
    return [
        asdict(summary)
        for summary in evaluate_matrix(sample_size=sample_size, seed=seed)
    ]
