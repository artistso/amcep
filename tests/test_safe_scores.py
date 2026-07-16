from __future__ import annotations

import math
from typing import cast

import pytest

from src.amcep import AMCEPState
from src.safe_scores import (
    PersistencePolicy,
    SafeScoreContract,
    UnsafeDomainError,
    evaluate_safe_scores,
    persistence_factor,
    rescale_state,
    safe_bounded_cumulative_score,
    safe_bounded_transient_score,
    safe_cumulative_d_score_d_rho,
    safe_cumulative_score,
    safe_transient_d_score_d_rho,
    safe_transient_score,
)


def base_state() -> AMCEPState:
    return AMCEPState(
        rho=0.5,
        operator_power=5.0,
        x=0.5,
        n=2,
        normalization=2.0,
        penalty_weight=3.0,
    )


def reject_contract() -> SafeScoreContract:
    return SafeScoreContract(
        normalization_floor=0.25,
        persistence_policy="reject",
        output_temperature=1.5,
    )


def squash_contract() -> SafeScoreContract:
    return SafeScoreContract(
        normalization_floor=0.25,
        persistence_policy="squash",
        output_temperature=1.5,
    )


def test_reject_policy_preserves_in_domain_power() -> None:
    state = base_state()
    contract = reject_contract()
    assert persistence_factor(state.x, state.n, contract) == pytest.approx(0.25)
    assert safe_transient_score(state, contract) == pytest.approx(2.3125)
    assert safe_cumulative_score(state, contract) == pytest.approx(1.9375)


def test_reject_policy_fails_closed_outside_persistence_domain() -> None:
    state = AMCEPState(
        rho=1.0,
        operator_power=0.0,
        x=1.0001,
        n=1,
        normalization=1.0,
    )
    with pytest.raises(UnsafeDomainError, match=r"\|x\| <= 1"):
        safe_cumulative_score(state, reject_contract())


def test_depth_zero_has_exact_persistence_one() -> None:
    for policy in ("reject", "squash"):
        contract = SafeScoreContract(
            normalization_floor=0.1,
            persistence_policy=policy,
        )
        assert persistence_factor(1e300, 0, contract) == 1.0


def test_squash_policy_is_total_and_bounded_for_finite_x() -> None:
    contract = squash_contract()
    for x in (-1e300, -2.0, -1.0, 0.0, 1.0, 2.0, 1e300):
        persistence = persistence_factor(x, 7, contract)
        assert 0.0 <= persistence <= 1.0


def test_normalization_floor_rejects_without_clamping() -> None:
    contract = SafeScoreContract(normalization_floor=1.0)
    at_floor = AMCEPState(
        rho=0.0,
        operator_power=2.0,
        x=0.5,
        n=1,
        normalization=1.0,
    )
    below_floor = AMCEPState(
        rho=0.0,
        operator_power=2.0,
        x=0.5,
        n=1,
        normalization=0.999,
    )
    assert safe_transient_score(at_floor, contract) == 2.0
    with pytest.raises(UnsafeDomainError, match="below"):
        safe_transient_score(below_floor, contract)


def test_squash_derivatives_never_reward_more_contradiction() -> None:
    contract = squash_contract()
    for x in (-1e100, -2.0, -1.0, 0.0, 1.0, 2.0, 1e100):
        state = AMCEPState(
            rho=0.5,
            operator_power=1.0,
            x=x,
            n=5,
            normalization=2.0,
            penalty_weight=3.0,
        )
        assert safe_transient_d_score_d_rho(state, contract) <= 0.0
        assert safe_cumulative_d_score_d_rho(state, contract) <= 0.0


def test_coherent_unit_rescaling_preserves_safe_raw_scores() -> None:
    state = base_state()
    contract = reject_contract()
    factor = 1000.0
    scaled_state = rescale_state(state, factor)
    scaled_contract = contract.rescaled(factor)

    assert safe_transient_score(scaled_state, scaled_contract) == pytest.approx(
        safe_transient_score(state, contract), abs=1e-14
    )
    assert safe_cumulative_score(scaled_state, scaled_contract) == pytest.approx(
        safe_cumulative_score(state, contract), abs=1e-14
    )


def test_bounded_outputs_are_strictly_between_zero_and_one() -> None:
    contract = squash_contract()
    for operator_power in (-1e6, -10.0, 0.0, 10.0, 1e6):
        state = AMCEPState(
            rho=2.0,
            operator_power=operator_power,
            x=10.0,
            n=4,
            normalization=1.0,
            penalty_weight=3.0,
        )
        transient = safe_bounded_transient_score(state, contract)
        cumulative = safe_bounded_cumulative_score(state, contract)
        assert 0.0 < transient < 1.0
        assert 0.0 < cumulative < 1.0


def test_combined_evaluation_matches_individual_functions() -> None:
    state = base_state()
    contract = squash_contract()
    evaluation = evaluate_safe_scores(state, contract)
    assert evaluation.transient_raw == pytest.approx(
        safe_transient_score(state, contract)
    )
    assert evaluation.cumulative_raw == pytest.approx(
        safe_cumulative_score(state, contract)
    )
    assert evaluation.transient_bounded == pytest.approx(
        safe_bounded_transient_score(state, contract)
    )
    assert evaluation.cumulative_bounded == pytest.approx(
        safe_bounded_cumulative_score(state, contract)
    )


def test_squashed_cumulative_score_approaches_lasting_penalty() -> None:
    state = AMCEPState(
        rho=2.0,
        operator_power=5.0,
        x=100.0,
        n=10000,
        normalization=2.0,
        penalty_weight=3.0,
    )
    expected = (5.0 - 3.0 * 2.0) / 2.0
    assert safe_cumulative_score(state, squash_contract()) == pytest.approx(
        expected,
        abs=1e-12,
    )


def test_contract_and_scale_validation() -> None:
    invalid_policy = SafeScoreContract(
        normalization_floor=1.0,
        persistence_policy=cast(PersistencePolicy, "clip"),
    )
    for contract in (
        SafeScoreContract(normalization_floor=0.0),
        SafeScoreContract(normalization_floor=math.inf),
        SafeScoreContract(normalization_floor=1.0, output_temperature=0.0),
        SafeScoreContract(normalization_floor=1.0, output_temperature=math.nan),
        invalid_policy,
    ):
        with pytest.raises(ValueError):
            contract.validate()

    with pytest.raises(ValueError):
        rescale_state(base_state(), 0.0)
    with pytest.raises(ValueError):
        reject_contract().rescaled(math.inf)


def test_persistence_rejects_nonfinite_or_negative_depth() -> None:
    with pytest.raises(ValueError):
        persistence_factor(math.inf, 1, reject_contract())
    with pytest.raises(ValueError):
        persistence_factor(0.5, -1, reject_contract())
