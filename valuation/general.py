from collections.abc import Mapping, Set

from .base import Valuation, Rational
from .base import SI_FTYPES


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
