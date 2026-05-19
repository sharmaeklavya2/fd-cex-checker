"""
Fair division instance: a list of valuations (one per agent) and a list of weights.
"""

from __future__ import annotations

from collections.abc import Sequence
from valuation import Valuation, Rational


class Instance:
    """
    A fair division instance.

    Args:
        valuations: valuations[i] is the Valuation of agent i.
        weights:    weights[i] is the entitlement of agent i (int or Fraction).
                    Defaults to [1, 1, ..., 1] (equal entitlements).
    """

    def __init__(self, valuations: Sequence[Valuation],
                 weights: Sequence[Rational] | None = None) -> None:
        self.valuations = valuations
        self.weights = weights if weights is not None else [1] * len(valuations)
        assert len(self.valuations) > 0, "Instance must have at least one agent"
        assert len(self.valuations) == len(self.weights), \
            "Number of valuations must equal number of weights"
        assert all(w > 0 for w in self.weights), "All weights must be positive"
        m = self.valuations[0].n_items()
        assert all(v.n_items() == m for v in self.valuations), \
            "All valuations must be defined over the same number of items"

    def n_agents(self) -> int:
        return len(self.valuations)

    def n_items(self) -> int:
        return self.valuations[0].n_items()

    def has_equal_entitlements(self) -> bool:
        """True iff all agents have the same weight."""
        return len(set(self.weights)) == 1

    def has_identical_valuations(self) -> bool:
        """
        True iff all agents share the exact same Valuation object.
        When constructing instances with identical valuations, reuse the same
        object so this check works correctly.
        """
        return all(v is self.valuations[0] for v in self.valuations)

    def __repr__(self) -> str:
        if self.has_equal_entitlements():
            return f"Instance(valuations={self.valuations!r})"
        else:
            return f"Instance(valuations={self.valuations!r}, weights={self.weights!r})"
