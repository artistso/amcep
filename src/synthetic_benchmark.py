"""Deterministic synthetic stress tests for AMCEP score families.

The generator exposes its data-generating regime. Results are structural
sanity checks, not evidence that a regime describes the real world.
"""

from __future__ import annotations

import math
import random
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Literal

from src.amcep import AMCEPState, cumulative_score, original_score, transient_score

GroundTruthRegime = Literal["task_only", "transient", "cumulative"]
ModelName = Literal[
    "task_only",
    "linear_penalty",
    "original",
    "transient",
    "cumulative",
]

MODEL_NAMES: tuple[ModelName, ...] = (
    "task_only",
    "linear_penalty",
    "original",
    "transient",
    "cumulative",
)


@dataclass(frozen=True)
class SyntheticConfig:
    """Configuration for one synthetic data-generating scenario."""

    sample_size: int = 300
    seed: int = 20260716
    regime: GroundTruthRegime = "cumulative"
    noise_std: float = 0.0
    missing_rate: float = 0.0
    adversarial_rate: float = 0.0
    penalty_weight: float = 1.0
    depth_min: int = 1
    depth_max: int = 12

    def validate(self) -> None:
        if self.sample_size < 2:
            raise ValueError("sample_size must be at least two")
        if self.depth_min < 1 or self.depth_max < self.depth_min:
            raise ValueError("depth range must satisfy 1 <= min <= max")
        for name, value in (
            ("noise_std", self.noise_std),
            ("missing_rate", self.missing_rate),
            ("adversarial_rate", self.adversarial_rate),
            ("penalty_weight", self.penalty_weight),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.noise_std < 0:
            raise ValueError("noise_std must be non-negative")
        if not 0 <= self.missing_rate <= 1:
            raise ValueError("missing_rate must be in [0, 1]")
        if not 0 <= self.adversarial_rate <= 1:
            raise ValueError("adversarial_rate must be in [0, 1]")
        if self.penalty_weight < 0:
            raise ValueError("penalty_weight must be non-negative")


@dataclass(frozen=True)
class SyntheticCase:
    """Latent ground truth plus potentially corrupted observations."""

    case_id: int
    regime: GroundTruthRegime
    true_rho: float
    true_operator_power: float
    true_x: float
    depth: int
    true_normalization: float
    penalty_weight: float
    target: float
    observed_rho: float | None
    observed_operator_power: float | None
    observed_x: float | None
    observed_normalization: float | None
    adversarially_corrupted: bool
    missing_field: str | None


@dataclass(frozen=True)
class MetricSummary:
    model: ModelName
    observations: int
    coverage: float
    mae: float | None
    rmse: float | None
    pearson_r: float | None
    pairwise_ranking_accuracy: float | None
    calibration_intercept: float | None
    calibration_slope: float | None
    contradiction_violation_rate: float


@dataclass(frozen=True)
class ScenarioResult:
    config: SyntheticConfig
    cases: tuple[SyntheticCase, ...]
    predictions: dict[ModelName, tuple[float | None, ...]]
    metrics: tuple[MetricSummary, ...]


def _ground_truth(
    regime: GroundTruthRegime,
    rho: float,
    operator_power: float,
    x: float,
    depth: int,
    normalization: float,
    penalty_weight: float,
) -> float:
    if regime == "task_only":
        return operator_power / normalization
    if regime == "transient":
        return (
            operator_power - penalty_weight * rho * abs(x) ** depth
        ) / normalization
    if regime == "cumulative":
        return (
            operator_power
            - penalty_weight * rho * (1.0 - abs(x) ** depth)
        ) / normalization
    raise AssertionError(f"unhandled regime: {regime}")


def generate_cases(config: SyntheticConfig) -> tuple[SyntheticCase, ...]:
    """Generate a deterministic dataset with latent and observed variables."""

    config.validate()
    rng = random.Random(config.seed)
    cases: list[SyntheticCase] = []
    observable_names = ("rho", "operator_power", "x", "normalization")

    for case_id in range(config.sample_size):
        rho = rng.uniform(0.0, 1.0)
        operator_power = rng.uniform(-2.0, 2.0)
        x = rng.uniform(0.05, 0.95)
        depth = rng.randint(config.depth_min, config.depth_max)
        normalization = rng.uniform(0.5, 2.0)

        target = _ground_truth(
            config.regime,
            rho,
            operator_power,
            x,
            depth,
            normalization,
            config.penalty_weight,
        )

        observed_rho = min(
            1.0, max(0.0, rho + rng.gauss(0.0, config.noise_std))
        )
        observed_operator_power = operator_power + rng.gauss(
            0.0, config.noise_std
        )
        observed_x = min(
            0.999999,
            max(0.0, x + rng.gauss(0.0, config.noise_std / 2.0)),
        )
        observed_normalization = max(
            1e-6,
            normalization + rng.gauss(0.0, config.noise_std / 4.0),
        )

        adversarial = rng.random() < config.adversarial_rate
        if adversarial:
            observed_rho = 1.0 - observed_rho

        missing_field: str | None = None
        if rng.random() < config.missing_rate:
            missing_field = rng.choice(observable_names)
            if missing_field == "rho":
                observed_rho = None
            elif missing_field == "operator_power":
                observed_operator_power = None
            elif missing_field == "x":
                observed_x = None
            else:
                observed_normalization = None

        cases.append(
            SyntheticCase(
                case_id=case_id,
                regime=config.regime,
                true_rho=rho,
                true_operator_power=operator_power,
                true_x=x,
                depth=depth,
                true_normalization=normalization,
                penalty_weight=config.penalty_weight,
                target=target,
                observed_rho=observed_rho,
                observed_operator_power=observed_operator_power,
                observed_x=observed_x,
                observed_normalization=observed_normalization,
                adversarially_corrupted=adversarial,
                missing_field=missing_field,
            )
        )

    return tuple(cases)


def _state_from_case(case: SyntheticCase) -> AMCEPState | None:
    values = (
        case.observed_rho,
        case.observed_operator_power,
        case.observed_x,
        case.observed_normalization,
    )
    if any(value is None for value in values):
        return None
    rho, operator_power, x, normalization = values
    assert rho is not None
    assert operator_power is not None
    assert x is not None
    assert normalization is not None
    return AMCEPState(
        rho=rho,
        operator_power=operator_power,
        x=x,
        n=case.depth,
        normalization=normalization,
        penalty_weight=case.penalty_weight,
    )


def predict(case: SyntheticCase, model: ModelName) -> float | None:
    """Predict one case; missing required inputs cause explicit abstention."""

    if model == "task_only":
        if (
            case.observed_operator_power is None
            or case.observed_normalization is None
        ):
            return None
        return case.observed_operator_power / case.observed_normalization

    state = _state_from_case(case)
    if state is None:
        return None
    if model == "linear_penalty":
        return (
            state.operator_power - state.penalty_weight * state.rho
        ) / state.normalization
    if model == "original":
        return original_score(state)
    if model == "transient":
        return transient_score(state)
    if model == "cumulative":
        return cumulative_score(state)
    raise AssertionError(f"unhandled model: {model}")


def _paired_values(
    cases: Iterable[SyntheticCase],
    predictions: Iterable[float | None],
) -> tuple[list[float], list[float]]:
    truth: list[float] = []
    predicted: list[float] = []
    for case, prediction in zip(cases, predictions, strict=True):
        if prediction is None:
            continue
        truth.append(case.target)
        predicted.append(prediction)
    return truth, predicted


def _pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2:
        return None
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    dx = [value - mean_x for value in x]
    dy = [value - mean_y for value in y]
    denominator = math.sqrt(
        sum(value * value for value in dx)
        * sum(value * value for value in dy)
    )
    if denominator == 0:
        return None
    return sum(a * b for a, b in zip(dx, dy, strict=True)) / denominator


def _pairwise_ranking_accuracy(
    truth: list[float],
    predicted: list[float],
) -> float | None:
    concordant = 0
    comparable = 0
    for left in range(len(truth)):
        for right in range(left + 1, len(truth)):
            true_delta = truth[left] - truth[right]
            predicted_delta = predicted[left] - predicted[right]
            if true_delta == 0 or predicted_delta == 0:
                continue
            comparable += 1
            if (true_delta > 0) == (predicted_delta > 0):
                concordant += 1
    if comparable == 0:
        return None
    return concordant / comparable


def _calibration(
    predicted: list[float],
    truth: list[float],
) -> tuple[float | None, float | None]:
    """Fit truth = intercept + slope * prediction by ordinary least squares."""

    if len(predicted) < 2:
        return None, None
    mean_predicted = sum(predicted) / len(predicted)
    mean_truth = sum(truth) / len(truth)
    denominator = sum(
        (value - mean_predicted) ** 2 for value in predicted
    )
    if denominator == 0:
        return None, None
    slope = sum(
        (prediction - mean_predicted) * (target - mean_truth)
        for prediction, target in zip(predicted, truth, strict=True)
    ) / denominator
    intercept = mean_truth - slope * mean_predicted
    return intercept, slope


def contradiction_violation_rate(
    model: ModelName,
    cases: Iterable[SyntheticCase],
    *,
    low_rho: float = 0.25,
    high_rho: float = 0.75,
) -> float:
    """Rate at which increasing contradiction strictly increases a score."""

    if not 0 <= low_rho < high_rho <= 1:
        raise ValueError("require 0 <= low_rho < high_rho <= 1")

    violations = 0
    evaluated = 0
    for case in cases:
        base = replace(
            case,
            observed_rho=low_rho,
            observed_operator_power=case.true_operator_power,
            observed_x=case.true_x,
            observed_normalization=case.true_normalization,
            missing_field=None,
        )
        higher = replace(base, observed_rho=high_rho)
        low_score = predict(base, model)
        high_score = predict(higher, model)
        assert low_score is not None and high_score is not None
        evaluated += 1
        if high_score > low_score:
            violations += 1
    return violations / evaluated if evaluated else 0.0


def summarize_model(
    model: ModelName,
    cases: tuple[SyntheticCase, ...],
    predictions: tuple[float | None, ...],
) -> MetricSummary:
    truth, predicted = _paired_values(cases, predictions)
    observations = len(predicted)
    coverage = observations / len(cases)

    if observations == 0:
        mae = None
        rmse = None
    else:
        errors = [
            prediction - target
            for prediction, target in zip(predicted, truth, strict=True)
        ]
        mae = sum(abs(error) for error in errors) / observations
        rmse = math.sqrt(
            sum(error * error for error in errors) / observations
        )

    calibration_intercept, calibration_slope = _calibration(predicted, truth)
    return MetricSummary(
        model=model,
        observations=observations,
        coverage=coverage,
        mae=mae,
        rmse=rmse,
        pearson_r=_pearson(predicted, truth),
        pairwise_ranking_accuracy=_pairwise_ranking_accuracy(truth, predicted),
        calibration_intercept=calibration_intercept,
        calibration_slope=calibration_slope,
        contradiction_violation_rate=contradiction_violation_rate(model, cases),
    )


def evaluate(config: SyntheticConfig) -> ScenarioResult:
    cases = generate_cases(config)
    predictions: dict[ModelName, tuple[float | None, ...]] = {}
    summaries: list[MetricSummary] = []

    for model in MODEL_NAMES:
        model_predictions = tuple(predict(case, model) for case in cases)
        predictions[model] = model_predictions
        summaries.append(summarize_model(model, cases, model_predictions))

    return ScenarioResult(
        config=config,
        cases=cases,
        predictions=predictions,
        metrics=tuple(summaries),
    )


def default_scenarios(
    *,
    sample_size: int = 300,
    seed: int = 20260716,
) -> tuple[SyntheticConfig, ...]:
    """Return a fixed cross-regime stress matrix."""

    scenarios: list[SyntheticConfig] = []
    stresses = (
        (0.0, 0.0, 0.0),
        (0.05, 0.0, 0.0),
        (0.05, 0.10, 0.0),
        (0.05, 0.0, 0.10),
    )
    regimes: tuple[GroundTruthRegime, ...] = (
        "task_only",
        "transient",
        "cumulative",
    )
    scenario_index = 0
    for regime in regimes:
        for noise_std, missing_rate, adversarial_rate in stresses:
            scenarios.append(
                SyntheticConfig(
                    sample_size=sample_size,
                    seed=seed + scenario_index,
                    regime=regime,
                    noise_std=noise_std,
                    missing_rate=missing_rate,
                    adversarial_rate=adversarial_rate,
                )
            )
            scenario_index += 1
    return tuple(scenarios)


def evaluate_sweep(
    scenarios: Iterable[SyntheticConfig],
) -> tuple[ScenarioResult, ...]:
    return tuple(evaluate(config) for config in scenarios)
