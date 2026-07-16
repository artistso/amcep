from hypothesis import assume, given, strategies as st

from src.amcep import (
    AMCEPState,
    bounded_cumulative_score,
    bounded_transient_score,
    cumulative_score,
    original_score,
    transient_score,
)

finite = st.floats(
    min_value=-1_000_000,
    max_value=1_000_000,
    allow_nan=False,
    allow_infinity=False,
)
non_negative = st.floats(
    min_value=0,
    max_value=1_000_000,
    allow_nan=False,
    allow_infinity=False,
)
positive = st.floats(
    min_value=1e-9,
    max_value=1_000_000,
    allow_nan=False,
    allow_infinity=False,
)
unit_interval = st.floats(
    min_value=0,
    max_value=1,
    allow_nan=False,
    allow_infinity=False,
)


@given(
    rho=non_negative,
    delta=st.floats(
        min_value=0,
        max_value=1_000_000,
        allow_nan=False,
        allow_infinity=False,
    ),
    operator_power=finite,
    x=unit_interval,
    n=st.integers(min_value=0, max_value=100),
    normalization=positive,
    penalty_weight=non_negative,
)
def test_transient_score_never_rewards_more_contradiction(
    rho: float,
    delta: float,
    operator_power: float,
    x: float,
    n: int,
    normalization: float,
    penalty_weight: float,
) -> None:
    low = AMCEPState(
        rho, operator_power, x, n, normalization, penalty_weight
    )
    high = AMCEPState(
        rho + delta, operator_power, x, n, normalization, penalty_weight
    )
    assert transient_score(high) <= transient_score(low)


@given(
    rho=non_negative,
    delta=st.floats(
        min_value=0,
        max_value=1_000_000,
        allow_nan=False,
        allow_infinity=False,
    ),
    operator_power=finite,
    x=unit_interval,
    n=st.integers(min_value=0, max_value=100),
    normalization=positive,
    penalty_weight=non_negative,
)
def test_cumulative_score_never_rewards_more_contradiction_in_domain(
    rho: float,
    delta: float,
    operator_power: float,
    x: float,
    n: int,
    normalization: float,
    penalty_weight: float,
) -> None:
    low = AMCEPState(
        rho, operator_power, x, n, normalization, penalty_weight
    )
    high = AMCEPState(
        rho + delta, operator_power, x, n, normalization, penalty_weight
    )
    assert cumulative_score(high) <= cumulative_score(low)


@given(
    rho=non_negative,
    operator_power=finite,
    x=st.floats(
        min_value=0,
        max_value=0.999999,
        allow_nan=False,
        allow_infinity=False,
    ),
    n=st.integers(min_value=1, max_value=100),
    normalization=positive,
)
def test_original_equation_rewards_more_contradiction_in_intended_regime(
    rho: float,
    operator_power: float,
    x: float,
    n: int,
    normalization: float,
) -> None:
    delta = 1.0
    low = AMCEPState(rho, operator_power, x, n, normalization)
    high = AMCEPState(rho + delta, operator_power, x, n, normalization)
    assert original_score(high) > original_score(low)


@given(
    rho=non_negative,
    operator_power=finite,
    x=finite,
    n=st.integers(min_value=0, max_value=100),
    normalization=positive,
    penalty_weight=non_negative,
)
def test_bounded_scores_remain_in_unit_interval(
    rho: float,
    operator_power: float,
    x: float,
    n: int,
    normalization: float,
    penalty_weight: float,
) -> None:
    state = AMCEPState(
        rho, operator_power, x, n, normalization, penalty_weight
    )
    # Avoid test cases whose finite inputs overflow during exponentiation.
    assume(abs(x) <= 10 or n <= 10)
    transient = bounded_transient_score(state)
    cumulative = bounded_cumulative_score(state)
    assert 0.0 <= transient <= 1.0
    assert 0.0 <= cumulative <= 1.0
