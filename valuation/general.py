from collections.abc import Collection, Mapping, Set
import itertools

from .base import Valuation, Rational
from .base import SI_FTYPES, ADD_FTYPES, UNIT_DEM_FTYPES, SUBMOD_FTYPES, SUBADD_FTYPES, SUPERMOD_FTYPES, SUPERADD_FTYPES


def get_marginals(m: int, values: Mapping[frozenset[int], Rational]) -> Set[Rational]:
    """
    `values` maps all subsets of range(m) to a number.
    Find the set of all marginal values.
    """
    marginals_set = set()
    for S in values.keys():
        rest = set(range(m)) - S
        for g in rest:
            x = values[S | frozenset({g})] - values[S]
            marginals_set.add(x)
    return marginals_set


def all_subsets(a: Collection[int]) -> list[frozenset[int]]:
    """Return all 2^m subsets of {0, ..., m-1} as frozensets."""
    m = len(a)
    return [frozenset(S) for r in range(m + 1) for S in itertools.combinations(a, r)]


def get_ftypes(m: int, values: Mapping[frozenset[int], Rational]) -> frozenset[str]:
    """
    `values` maps all subsets of range(m) to a number.
    Identify the type of valuation function (submodular, superadditive, etc.)
    """
    if m == 1:
        return SI_FTYPES

    v_sing = [values[frozenset((g,))] for g in range(m)]
    is_additive, is_unit_dem = True, True
    for S, vS in values.items():
        v_sing_2 = [v_sing[g] for g in S]
        if vS != sum(v_sing_2):
            is_additive = False
        if vS < 0 or vS != max(v_sing_2, default=0):
            is_unit_dem = False
    if is_additive:
        return ADD_FTYPES
    elif is_unit_dem:
        return UNIT_DEM_FTYPES

    all_items = frozenset(range(m))
    is_submod, is_supermod = True, True
    for S in values.keys():
        if not (is_submod or is_supermod):
            continue
        if len(S) > m-2:
            continue
        for g1, g2 in itertools.combinations(all_items - S, 2):
            diff = values[S | frozenset((g1,))] + values[S | frozenset((g2,))] - values[S | frozenset((g1, g2))] - values[S]
            if diff < 0:
                is_submod = False
            elif diff > 0:
                is_supermod = False
    if is_submod:
        return SUBMOD_FTYPES
    elif is_supermod:
        return SUPERMOD_FTYPES

    is_subadd, is_superadd = True, True
    for S in values.keys():
        if not (is_subadd or is_superadd):
            break
        for T in all_subsets(all_items - S):
            if not (is_subadd or is_superadd):
                break
            ST = S | T
            diff = values[S] + values[T] - values[ST]
            if diff < 0:
                is_subadd = False
            if diff > 0:
                is_superadd = False
    if is_subadd:
        return SUBADD_FTYPES
    elif is_superadd:
        return SUPERADD_FTYPES
    else:
        return frozenset(('general',))


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

        self._func_types = get_ftypes(m, values)
        self._marginals_set = get_marginals(m, values)
        self._marginal_range = (min(self._marginals_set), max(self._marginals_set))

    def n_items(self) -> int:
        return self._m

    def value(self, subset: Set[int]) -> Rational:
        return self._values[frozenset(subset)]

    def func_types(self) -> frozenset[str]:
        return self._func_types

    def signs(self) -> tuple[bool, bool, bool]:
        min_marg, max_marg = self._marginal_range
        return (min_marg < 0, 0 in self._marginals_set, max_marg > 0)

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def is_k_val(self, k: int) -> bool:
        return len(self._marginals_set) <= k
