"""Fail-closed AMCEP candidate-score contract.

The original score families remain available in :mod:`src.amcep` for audit and
reproduction. This module adds an application-facing contract that rejects or
transforms known unsafe domains explicitly. It does not establish empirical,
ethical, or physical validity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Literal

from src.amcep import AMCEPState, logistic

PersistencePolicy = Literal["reject", "squash"]


class UnsafeDomainError(ValueError):
    """Raised when a score request violates an explicit safety contract."""


@dataclass(frozen=True)
class SafeScoreContract:
    """Domain and output policy for application-facing candidate scores.

    ``normalization_floor`` uses the same unit as ``state.normalization``.
    ``output_temperature`` is dimensionless because the raw score is
    dimensionless. The ``squash`` policy is a modeling choice, not a theorem
    about persistence in any real system.
    """

    normalization_floor: float
    persistence_policy: PersistencePolicy = "reject"
    output_temperature: float = 1.0

    def validate(self) -> None:
        if not math.isfinite(self.normalization_floor):
            raise ValueError("normalization floor must be finite")
        if self.normalization_floor <= 0.0:
            raise ValueError("normalization floor must be strictly positive")
        if self.persistence_policy not in ("reject", "squash"):
            raise ValueError("persistence policy must be 'reject' or 'squash'")
        if not math.isfinite(self.output_temperature):
            raise ValueError("output temperature must be finite")
        if self.output_temperature <= 0.0:
            raise ValueError("output temperature must be strictly positive")

    def rescaled(self, factor: float) -> SafeScoreContract:
        """Return the same contract under a coherent task-value unit change."""

        _validate_scale_factor(factor)
        scaled = replace(
            self,
            normalization_floor=self.normalization_floor * factor,
        )
        scaled.validate()
        return scaled


@dataclass(frozen=True)
class SafeScoreEvaluation:
    """Raw and bounded outputs produced under one validated contract."""

    transient_raw: float
    cumulative_raw: float
    transient_bounded: float
    cumulative_bounded: float
    persistence: float


def _validate_scale_factor(factor: float) -> None:
    if not math.isfinite(factor) or factor <= 0.0:
        raise ValueError("scale factor must be finite and strictly positive")


def _require_finite(value: float, label: str) -> float:
    if not math.isfinite(value):
        raise UnsafeDomainError(f"{label} produced a nonfinite result")
    return value


def _strict_logistic(value: float) -> float:
    """Return a floating result strictly inside the open unit interval."""

    result = logistic(value)
    if result <= 0.0:
        return math.nextafter(0.0, 1.0)
    if result >= 1.0:
        return math.nextafter(1.0, 0.0)
    return result


def rescale_state(state: AMCEPState, factor: float) -> AMCEPState:
    """Coherently change the task-value unit used by ``T``, ``E``, and lambda."""

    state.validate()
    _validate_scale_factor(factor)
    scaled = replace(
        state,
        operator_power=state.operator_power * factor,
        normalization=state.normalization * factor,
        penalty_weight=state.penalty_weight * factor,
    )
    scaled.validate()
    return scaled


def persistence_factor(
    x: float,
    n: int,
    contract: SafeScoreContract,
) -> float:
    """Return a persistence factor in ``[0, 1]`` under an explicit policy.

    ``reject`` preserves ``|x|^n`` but refuses ``|x| > 1`` for positive depth.
    ``squash`` first maps ``|x|`` to ``|x| / (1 + |x|)`` and then raises it to
    ``n``. The latter is total for finite ``x`` and bounded, but is only a
    candidate transform whose external interpretation requires validation.
    """

    contract.validate()
    if not math.isfinite(x):
        raise ValueError("persistence input x must be finite")
    if n < 0:
        raise ValueError("depth n must be non-negative")
    if n == 0:
        return 1.0

    magnitude = abs(x)
    if contract.persistence_policy == "reject":
        if magnitude > 1.0:
            raise UnsafeDomainError(
                "reject policy requires |x| <= 1 for positive depth"
            )
        return magnitude**n

    if magnitude <= 1.0:
        squashed = magnitude / (1.0 + magnitude)
    else:
        squashed = 1.0 / (1.0 + 1.0 / magnitude)
    return squashed**n


def _validate_safe_request(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    state.validate()
    contract.validate()
    if state.normalization < contract.normalization_floor:
        raise UnsafeDomainError(
            "normalization is below the declared positive safety floor"
        )
    return persistence_factor(state.x, state.n, contract)


def _transient_raw(state: AMCEPState, persistence: float) -> float:
    value = (
        state.operator_power
        - state.penalty_weight * state.rho * persistence
    ) / state.normalization
    return _require_finite(value, "transient score")


def _cumulative_raw(state: AMCEPState, persistence: float) -> float:
    value = (
        state.operator_power
        - state.penalty_weight * state.rho * (1.0 - persistence)
    ) / state.normalization
    return _require_finite(value, "cumulative score")


def safe_transient_score(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    """Evaluate the transient candidate under a fail-closed domain contract."""

    persistence = _validate_safe_request(state, contract)
    return _transient_raw(state, persistence)


def safe_cumulative_score(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    """Evaluate the cumulative candidate with non-negative penalty factor."""

    persistence = _validate_safe_request(state, contract)
    return _cumulative_raw(state, persistence)


def safe_transient_d_score_d_rho(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    """Exact rho derivative of the contracted transient candidate."""

    persistence = _validate_safe_request(state, contract)
    value = -(state.penalty_weight * persistence) / state.normalization
    return _require_finite(value, "transient contradiction derivative")


def safe_cumulative_d_score_d_rho(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    """Exact rho derivative of the contracted cumulative candidate."""

    persistence = _validate_safe_request(state, contract)
    value = -(
        state.penalty_weight * (1.0 - persistence)
    ) / state.normalization
    return _require_finite(value, "cumulative contradiction derivative")


def safe_bounded_transient_score(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    """Map the contracted transient score monotonically into ``(0, 1)``."""

    raw = safe_transient_score(state, contract)
    return _strict_logistic(raw / contract.output_temperature)


def safe_bounded_cumulative_score(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> float:
    """Map the contracted cumulative score monotonically into ``(0, 1)``."""

    raw = safe_cumulative_score(state, contract)
    return _strict_logistic(raw / contract.output_temperature)


def evaluate_safe_scores(
    state: AMCEPState,
    contract: SafeScoreContract,
) -> SafeScoreEvaluation:
    """Evaluate both candidate families once under the same validated policy."""

    persistence = _validate_safe_request(state, contract)
    transient_raw = _transient_raw(state, persistence)
    cumulative_raw = _cumulative_raw(state, persistence)
    temperature = contract.output_temperature
    return SafeScoreEvaluation(
        transient_raw=transient_raw,
        cumulative_raw=cumulative_raw,
        transient_bounded=_strict_logistic(transient_raw / temperature),
        cumulative_bounded=_strict_logistic(cumulative_raw / temperature),
        persistence=persistence,
    )
