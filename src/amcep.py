"""Executable AMCEP score models with explicit domains.

These functions are research candidates. They do not establish moral truth,
physical law, or empirical validity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class AMCEPState:
    rho: float
    operator_power: float
    x: float
    n: int
    normalization: float
    penalty_weight: float = 1.0

    def validate(self) -> None:
        values = (
            self.rho,
            self.operator_power,
            self.x,
            self.normalization,
            self.penalty_weight,
        )
        if not all(math.isfinite(v) for v in values):
            raise ValueError("all scalar inputs must be finite")
        if self.rho < 0:
            raise ValueError("rho must be non-negative")
        if self.n < 0:
            raise ValueError("n must be non-negative")
        if self.normalization <= 0:
            raise ValueError("normalization E must be strictly positive")
        if self.penalty_weight < 0:
            raise ValueError("penalty weight lambda must be non-negative")


def original_score(state: AMCEPState) -> float:
    """Return (rho + T - rho*x^n)/E exactly as stated in the source."""
    state.validate()
    return (
        state.rho
        + state.operator_power
        - state.rho * state.x**state.n
    ) / state.normalization


def transient_score(state: AMCEPState) -> float:
    """Return a repairable/transient contradiction-penalty candidate.

    S = (T - lambda*rho*|x|^n)/E.
    For |x| < 1 the contradiction penalty vanishes as n grows.
    """
    state.validate()
    return (
        state.operator_power
        - state.penalty_weight * state.rho * abs(state.x) ** state.n
    ) / state.normalization


def candidate_score(state: AMCEPState) -> float:
    """Backward-compatible alias for :func:`transient_score`."""
    return transient_score(state)


def cumulative_score(state: AMCEPState) -> float:
    """Return a lasting/cumulative contradiction-penalty candidate.

    S = (T - lambda*rho*(1 - |x|^n))/E.
    The intended monotonicity analysis assumes |x| <= 1.
    """
    state.validate()
    persistence = abs(state.x) ** state.n
    return (
        state.operator_power
        - state.penalty_weight * state.rho * (1.0 - persistence)
    ) / state.normalization


def logistic(value: float) -> float:
    """Numerically stable logistic transform with output strictly in (0, 1)."""
    if not math.isfinite(value):
        raise ValueError("logistic input must be finite")
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def bounded_transient_score(state: AMCEPState) -> float:
    """Logistic transform of the transient candidate."""
    return logistic(transient_score(state))


def bounded_cumulative_score(state: AMCEPState) -> float:
    """Logistic transform of the cumulative candidate."""
    return logistic(cumulative_score(state))


def residual_converges(rho: float, x: float) -> bool:
    """Whether rho*x^n tends to zero as n tends to infinity."""
    if not (math.isfinite(rho) and math.isfinite(x)):
        raise ValueError("rho and x must be finite")
    return rho == 0 or abs(x) < 1


def original_d_score_d_rho(state: AMCEPState) -> float:
    state.validate()
    return (1 - state.x**state.n) / state.normalization


def transient_d_score_d_rho(state: AMCEPState) -> float:
    state.validate()
    return -(
        state.penalty_weight * abs(state.x) ** state.n
    ) / state.normalization


def candidate_d_score_d_rho(state: AMCEPState) -> float:
    """Backward-compatible derivative alias for the transient candidate."""
    return transient_d_score_d_rho(state)


def cumulative_d_score_d_rho(state: AMCEPState) -> float:
    state.validate()
    return -(
        state.penalty_weight * (1.0 - abs(state.x) ** state.n)
    ) / state.normalization
