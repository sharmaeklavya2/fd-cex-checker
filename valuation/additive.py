from __future__ import annotations

from collections.abc import Sequence, Set

from .base import Valuation, Rational
from .base import SI_FTYPES, ADD_FTYPES


class AdditiveValuation(Valuation):
    """
    Additive valuation: value(S) = sum of values of items in S.

    For additive valuations the marginal of item i is always values[i],
    independent of the set. Additive implies submodular, supermodular,
    subadditive, and superadditive.
    """

    def __init__(self, values: Sequence[Rational]):
        """
        Args:
            values: values[i] is the value of item i, as int or Fraction.
        """
        self._values = list(values)
        self._value_set = frozenset(self._values)
        self._func_types = (SI_FTYPES if len(self._values) == 1 else ADD_FTYPES)
        self._marginal_range = (
            (min(self._values), max(self._values)) if self._values else (0, 0)
        )

    def value_list(self) -> Sequence[Rational]:
        return self._values

    def n_items(self) -> int:
        return len(self._values)

    def value(self, subset: Set[int]) -> Rational:
        return sum(self._values[i] for i in subset)  # sum of empty sequence is 0

    def marginal_gain(self, X: Set[int], S: Set[int]) -> Rational:
        return self.value(X)

    def marginal_loss(self, X: Set[int], S: Set[int]) -> Rational:
        return self.value(X)

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

    def __pos__(self) -> AdditiveValuation:
        return self

    def __neg__(self) -> AdditiveValuation:
        return AdditiveValuation([-x for x in self._values])

    def __mul__(self, c: object) -> AdditiveValuation:
        if isinstance(c, Rational):
            return AdditiveValuation([x*c for x in self._values])
        else:
            return NotImplemented

    def __rmul__(self, c: object) -> AdditiveValuation:
        if isinstance(c, Rational):
            return AdditiveValuation([x*c for x in self._values])
        else:
            return NotImplemented
