"""
Non-additive valuation functions for fair division instances.
"""

from __future__ import annotations

from collections.abc import Sequence, Set

from valuation import Rational, Valuation, SUBMOD_FTYPES, SI_FTYPES


class UnitDemandValuation(Valuation):
    """
    Unit demand valuation: value(S) = max of values of items in S.
    """

    def __init__(self, values: Sequence[Rational], shift: Rational = 0):
        """
        Args:
            values: values[i] is the value of item i, as int or Fraction.
        """
        assert len(values) > 0
        assert all(x >= 0 for x in values)
        assert shift >= 0
        self._shift = shift
        self._values = list(values)
        self._values_sorted = sorted(values)
        m = len(values)

        if m == 1:
            u0 = shift + values[0]
            self._marginal_range = (u0, u0)
            self._func_types = SI_FTYPES
        else:
            self._marginal_range = (shift, shift + self._values_sorted[-1])
            if shift == 0 or m <= 3:
                self._func_types = SUBMOD_FTYPES | frozenset({'submodCanc', 'cancelable'})
            else:
                self._func_types = SUBMOD_FTYPES

    def n_items(self) -> int:
        return len(self._values)

    def value(self, subset: Set[int]) -> Rational:
        return len(subset) * self._shift + max((self._values[i] for i in subset), default=0)

    def func_types(self) -> frozenset[str]:
        return self._func_types

    def signs(self) -> tuple[bool, bool, bool]:
        if self._shift > 0:
            return (False, False, True)
        v_min, v_max = self._marginal_range
        return (False, v_min == 0, v_max > 0)

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def is_k_val(self, k: int) -> bool:
        v_min, v_max = self._marginal_range
        if k == 1:
            return v_min == v_max
        else:
            raise NotImplementedError('cannot check UnitDemandValuation for bivaluedness')

    def __repr__(self) -> str:
        if self._shift > 0:
            return f"{type(self).__name__}({self._values!r}, shift={self._shift!r})"
        else:
            return f"{type(self).__name__}({self._values!r})"
