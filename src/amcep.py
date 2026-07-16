"""Executable AMCEP score models with explicit domains."""

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

    def validate(self) -> None:
        values = (self.rho, self.operator_power, self.x, self.normalization)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("all scalar inputs must be finite")
        if self.rho < 0:
            raise ValueError("rho must be non-negative")
        if self.n < 0:
            raise ValueError("n must be non-negative")
        if self.normalization <= 0:
            raise ValueError("normalization E must be strictly positive")


def original_score(state: AMCEPState) -> float:
    """Return (rho + T - rho*x^n)/E exactly as stated in the source."""
    state.validate()
    return (
        state.rho
        + state.operator_power
        - state.rho * state.x**state.n
    ) / state.normalization


def candidate_score(state: AMCEPState) -> float:
    """Candidate contradiction-penalizing score, not an established theorem."""
    state.validate()
    return (
        state.operator_power - state.rho * abs(state.x) ** state.n
    ) / state.normalization


def residual_converges(rho: float, x: float) -> bool:
    """Whether rho*x^n tends to zero as n tends to infinity."""
    if not (math.isfinite(rho) and math.isfinite(x)):
        raise ValueError("rho and x must be finite")
    return rho == 0 or abs(x) < 1


def original_d_score_d_rho(state: AMCEPState) -> float:
    state.validate()
    return (1 - state.x**state.n) / state.normalization


def candidate_d_score_d_rho(state: AMCEPState) -> float:
    state.validate()
    return -(abs(state.x) ** state.n) / state.normalization
