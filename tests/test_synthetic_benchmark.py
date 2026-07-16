from dataclasses import replace

import pytest

from src.synthetic_benchmark import (
    MODEL_NAMES,
    SyntheticConfig,
    contradiction_violation_rate,
    default_scenarios,
    evaluate,
    generate_cases,
)


@pytest.mark.parametrize(
    ("regime", "oracle"),
    (
        ("task_only", "task_only"),
        ("transient", "transient"),
        ("cumulative", "cumulative"),
    ),
)
def test_clean_oracle_matches_its_declared_regime(
    regime: str,
    oracle: str,
) -> None:
    result = evaluate(
        SyntheticConfig(sample_size=80, seed=7, regime=regime)  # type: ignore[arg-type]
    )
    by_model = {metric.model: metric for metric in result.metrics}
    assert by_model[oracle].mae == pytest.approx(0.0, abs=1e-12)
    assert by_model[oracle].rmse == pytest.approx(0.0, abs=1e-12)
    assert by_model[oracle].coverage == 1.0


def test_generation_is_reproducible() -> None:
    config = SyntheticConfig(
        sample_size=40,
        seed=91,
        regime="cumulative",
        noise_std=0.05,
        missing_rate=0.1,
        adversarial_rate=0.2,
    )
    assert generate_cases(config) == generate_cases(config)


def test_original_model_always_violates_contradiction_gate() -> None:
    cases = generate_cases(
        SyntheticConfig(sample_size=60, seed=11, regime="cumulative")
    )
    assert contradiction_violation_rate("original", cases) == 1.0
    assert contradiction_violation_rate("transient", cases) == 0.0
    assert contradiction_violation_rate("cumulative", cases) == 0.0
    assert contradiction_violation_rate("task_only", cases) == 0.0


def test_missing_inputs_cause_abstention_not_zero_imputation() -> None:
    result = evaluate(
        SyntheticConfig(
            sample_size=300,
            seed=13,
            regime="cumulative",
            missing_rate=0.5,
        )
    )
    by_model = {metric.model: metric for metric in result.metrics}
    assert by_model["cumulative"].coverage < 1.0
    assert by_model["cumulative"].observations > 0
    assert by_model["task_only"].coverage >= by_model["cumulative"].coverage


def test_default_sweep_is_fixed_and_crosses_all_regimes() -> None:
    scenarios = default_scenarios(sample_size=20, seed=17)
    assert len(scenarios) == 12
    assert {scenario.regime for scenario in scenarios} == {
        "task_only",
        "transient",
        "cumulative",
    }
    assert len({scenario.seed for scenario in scenarios}) == len(scenarios)


def test_every_model_returns_finite_metrics_when_coverage_exists() -> None:
    result = evaluate(
        SyntheticConfig(
            sample_size=90,
            seed=19,
            regime="transient",
            noise_std=0.05,
            adversarial_rate=0.1,
        )
    )
    assert {metric.model for metric in result.metrics} == set(MODEL_NAMES)
    for metric in result.metrics:
        assert metric.observations > 0
        assert metric.mae is not None
        assert metric.rmse is not None
        assert metric.pairwise_ranking_accuracy is not None


def test_changed_seed_changes_generated_cases() -> None:
    base = SyntheticConfig(sample_size=20, seed=23)
    assert generate_cases(base) != generate_cases(replace(base, seed=24))
