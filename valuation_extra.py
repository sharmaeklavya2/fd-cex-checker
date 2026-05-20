"""
Non-additive valuation functions for fair division instances.
"""

from __future__ import annotations

from collections.abc import Sequence, Set, Mapping

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


class GeneralValuation(Valuation):

    def __init__(self, m: int, values: Mapping[frozenset[int], Rational]):
        assert m > 0
        assert values[frozenset()] == 0
        assert len(values) == 2**m
        for S in values.keys():
            for g in S:
                assert g in range(m)
        self._m = m
        self._values = values

        self._func_types = SI_FTYPES if m == 1 else frozenset({'general'})
        marginals_set = set()
        has_neg, has_zero, has_pos = False, False, False
        for S in values.keys():
            rest = set(range(m)) - S
            for g in rest:
                x = values[S | frozenset({g})] - values[S]
                marginals_set.add(x)
                if x > 0:
                    has_pos = True
                elif x < 0:
                    has_neg = True
                else:
                    has_zero = True
        self._marginals_set = marginals_set
        self._marginal_range = (min(marginals_set), max(marginals_set))
        self._signs = (has_neg, has_zero, has_pos)

    def n_items(self) -> int:
        return self._m

    def value(self, subset: Set[int]) -> Rational:
        return self._values[frozenset(subset)]

    def func_types(self) -> frozenset[str]:
        return self._func_types

    def signs(self) -> tuple[bool, bool, bool]:
        return self._signs

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def is_k_val(self, k: int) -> bool:
        return len(self._marginals_set) <= k
