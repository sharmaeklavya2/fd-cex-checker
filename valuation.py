"""
Valuation functions for fair division instances.

Items are represented as integers 0 .. n_items-1.
Values are int or fractions.Fraction; floats are not supported.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from fractions import Fraction
from collections.abc import Sequence, Set

Rational = int | Fraction


class Valuation(ABC):
    """Abstract base class for valuation functions over sets of items."""

    @abstractmethod
    def n_items(self) -> int:
        """Number of items in the ground set."""
        ...

    @abstractmethod
    def value(self, subset: Set[int]) -> Rational:
        """Value of a set of items."""
        ...

    def marginal(self, item: int, subset: Set[int]) -> Rational:
        """Marginal value of adding `item` to `subset`. Item must not be in subset."""
        assert item not in subset
        return self.value(subset | {item}) - self.value(subset)

    @abstractmethod
    def func_types(self) -> frozenset[str]:
        """
        The set of function-type labels that apply to this valuation.
        Returns the same frozenset object on every call.
        """
        ...

    @abstractmethod
    def signs(self) -> tuple[bool, bool, bool]:
        """
        Returns (has_neg, has_zero, has_pos): whether any marginal value is
        negative, zero, or positive respectively. Exact for this instance.
        """
        ...

    @abstractmethod
    def marginal_range(self) -> tuple[Rational, Rational]:
        """
        Returns (min_marginal, max_marginal): the minimum and maximum marginal
        values across all items and all subsets. Exact for this instance.
        """
        ...

    @abstractmethod
    def is_k_val(self, k: int) -> bool:
        """True iff there are at most k distinct marginal values."""
        ...


# =============================================================================
# Concrete valuation classes
# =============================================================================

class AdditiveValuation(Valuation):
    """
    Additive valuation: value(S) = sum of values of items in S.

    For additive valuations the marginal of item i is always values[i],
    independent of the set. Additive implies submodular, supermodular,
    subadditive, and superadditive.
    """

    _FUNC_TYPES = frozenset({
        'general', 'subadd', 'superadd', 'xos', 'submod', 'supermod',
        'cancelable', 'submodCanc', 'additive',
    })
    _FUNC_TYPES_SINGLE_ITEM = _FUNC_TYPES | frozenset({'unitDemand', 'singleItem'})

    def __init__(self, values: Sequence[Rational]):
        """
        Args:
            values: values[i] is the value of item i, as int or Fraction.
        """
        self._values = list(values)
        self._value_set = frozenset(self._values)
        self._func_types = (self._FUNC_TYPES_SINGLE_ITEM if len(self._values) == 1
                            else self._FUNC_TYPES)
        self._marginal_range = (
            (min(self._values), max(self._values)) if self._values else (0, 0)
        )

    def n_items(self) -> int:
        return len(self._values)

    def value(self, subset: Set[int]) -> Rational:
        return sum(self._values[i] for i in subset)  # sum of empty sequence is 0

    def marginal(self, item: int, subset: Set[int]) -> Rational:
        """O(1) override: marginal of item i is always values[i]."""
        assert item not in subset
        return self._values[item]

    def func_types(self) -> frozenset[str]:
        return self._func_types

    def signs(self) -> tuple[bool, bool, bool]:
        return (
            any(v < 0 for v in self._values),
            any(v == 0 for v in self._values),
            any(v > 0 for v in self._values),
        )

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def is_k_val(self, k: int) -> bool:
        return len(self._value_set) <= k

    def __repr__(self) -> str:
        return f"AdditiveValuation({self._values!r})"
