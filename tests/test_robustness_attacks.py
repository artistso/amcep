from __future__ import annotations

import math
from dataclasses import replace

import pytest

from experiments.robustness_attacks import (
    GROUPS,
    MODELS,
    RobustnessCase,
    decimal_score,
    evaluate_matrix,
    float_score,
    generate_group,
    rescale_units,
    severity_monotonicity_violation,
    summarize_group,
    unit_rescaling_error,
)


def base_case() -> RobustnessCase:
    return RobustnessCase(
        prevalence=0.5,
        severity=1.0,
        operator_power=5.0,
        x=0.5,
        depth=2,
        normalization=2.0,
        penalty_weight=3.0,
    )


def test_case_validation_rejects_invalid_domains() -> None:
    with pytest.raises(ValueError):
        replace(base_case(), prevalence=1.1).validate()
    with pytest.raises(ValueError):
        replace(base_case(), severity=-1.0).validate()
    with pytest.raises(ValueError):
        replace(base_case(), depth=-1).validate()
    with pytest.raises(ValueError):
        replace(base_case(), normalization=0.0).validate()
    with pytest.raises(ValueError):
        replace(base_case(), penalty_weight=-1.0).validate()
    with pytest.raises(ValueError):
        replace(base_case(), x=math.inf).validate()


def test_decimal_path_matches_production_path() -> None:
    case = base_case()
    for model in MODELS:
        assert float(decimal_score(case, model)) == pytest.approx(
            float_score(case, model), abs=1e-14
        )


def test_original_fails_coherent_unit_rescaling() -> None:
    case = base_case()
    assert unit_rescaling_error(case, "original", 1000.0) > 0.01
    assert unit_rescaling_error(case, "transient", 1000.0) < 1e-12
    assert unit_rescaling_error(case, "cumulative", 1000.0) < 1e-12


def test_rescale_units_validates_factor_and_fields() -> None:
    transformed = rescale_units(base_case(), 10.0)
    assert transformed.operator_power == 50.0
    assert transformed.normalization == 20.0
    assert transformed.penalty_weight == 30.0
    assert transformed.prevalence == base_case().prevalence
    with pytest.raises(ValueError):
        rescale_units(base_case(), 0.0)


def test_original_rewards_higher_severity_in_intended_domain() -> None:
    case = base_case()
    assert severity_monotonicity_violation(case, "original")
    assert not severity_monotonicity_violation(case, "transient")
    assert not severity_monotonicity_violation(case, "cumulative")
    with pytest.raises(ValueError):
        severity_monotonicity_violation(
            case,
            "original",
            low=2.0,
            high=1.0,
        )


def test_generation_is_deterministic_and_group_specific() -> None:
    first = generate_group("combined", sample_size=20, seed=7)
    second = generate_group("combined", sample_size=20, seed=7)
    assert first == second
    assert all(abs(case.x) >= 0.97 for case in first)
    assert all(case.normalization <= 0.1 for case in first)
    assert all(case.severity >= 1.0 for case in first)
    with pytest.raises(ValueError):
        generate_group("in_distribution", sample_size=1)


def test_group_summary_exposes_expected_structural_failures() -> None:
    cases = generate_group("in_distribution", sample_size=80, seed=11)
    original = summarize_group("in_distribution", "original", cases)
    transient = summarize_group("in_distribution", "transient", cases)
    cumulative = summarize_group("in_distribution", "cumulative", cases)

    assert original.severity_violation_rate == 1.0
    assert original.unit_rescaling_violation_rate > 0.95
    assert transient.severity_violation_rate == 0.0
    assert cumulative.severity_violation_rate == 0.0
    assert transient.unit_rescaling_violation_rate == 0.0
    assert cumulative.unit_rescaling_violation_rate == 0.0
    assert max(
        original.max_decimal_disagreement,
        transient.max_decimal_disagreement,
        cumulative.max_decimal_disagreement,
    ) < 1e-11
    with pytest.raises(ValueError):
        summarize_group("in_distribution", "original", ())


def test_small_normalization_attack_amplifies_scores() -> None:
    regular = generate_group("in_distribution", sample_size=200, seed=5)
    attacked = generate_group("small_E", sample_size=200, seed=5)
    regular_summary = summarize_group(
        "in_distribution",
        "cumulative",
        regular,
    )
    attacked_summary = summarize_group("small_E", "cumulative", attacked)
    assert attacked_summary.p95_abs_score > regular_summary.p95_abs_score * 20


def test_complete_matrix_shape_and_finiteness() -> None:
    summaries = evaluate_matrix(sample_size=20, seed=13)
    assert len(summaries) == len(GROUPS) * len(MODELS)
    assert {(summary.group, summary.model) for summary in summaries} == {
        (group, model) for group in GROUPS for model in MODELS
    }
    assert all(summary.nonfinite_rate == 0.0 for summary in summaries)
