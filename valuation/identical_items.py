from collections.abc import Mapping, Set, Sequence

from .base import Valuation, Rational
from .base import SI_FTYPES, ADD_FTYPES, SUBADD_FTYPES, SUBMOD_FTYPES, SUPERADD_FTYPES, SUPERMOD_FTYPES
from valuation.unit_demand import UNIT_DEM_FTYPES


def identify_ftype(marginals: Sequence[Rational]) -> frozenset[str]:
    m = len(marginals)
    if m == 1:
        return SI_FTYPES
    if marginals == [marginals[0]] * m:
        return ADD_FTYPES
    elif marginals[0] > 0 and marginals == [marginals[0]] + [0] * (m-1):
        return UNIT_DEM_FTYPES
    elif marginals == sorted(marginals, reverse=True):
        return SUBMOD_FTYPES
    elif marginals == sorted(marginals, reverse=False):
        return SUPERMOD_FTYPES
    values: list[Rational] = [0]
    for x in marginals:
        values.append(values[-1] + x)
    is_subadd, is_superadd = True, True
    for i in range(1, m//2+1):
        if is_subadd or is_superadd:
            for j in range(i, m-i+1):
                if values[i+j] < values[i] + values[j]:
                    is_superadd = False
                elif values[i+j] > values[i] + values[j]:
                    is_subadd = False
    if is_subadd:
        return SUBADD_FTYPES
    elif is_superadd:
        return SUPERADD_FTYPES
    else:
        return frozenset({'general'})


class IdenticalItemsValuation(Valuation):
    """
    v(S) = a[|S|] for some sequence a.
    Note that len(a) should be m+1 for m items, and a[0] must be 0.
    """
    def __init__(self, values: Sequence[Rational]):
        assert len(values) > 0
        assert values[0] == 0
        self._values: Sequence[Rational] = list(values)
        self._m = len(values) - 1
        marginals = [values[i+1] - values[i] for i in range(self._m)]
        self._marginals_set = frozenset(marginals)
        self._marginal_range = (min(marginals), max(marginals))
        self._func_types = identify_ftype(marginals)

    def n_items(self) -> int:
        return self._m

    def value_list(self) -> Sequence[Rational]:
        return self._values

    def value(self, subset: Set[int]) -> Rational:
        return self._values[len(subset)]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._values!r})"

    def func_types(self) -> frozenset[str]:
        return self._func_types

    def signs(self) -> tuple[bool, bool, bool]:
        min_marg, max_marg = self._marginal_range
        return (min_marg < 0, 0 in self._marginals_set, max_marg > 0)

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def is_k_val(self, k: int) -> bool:
        return len(self._marginals_set) <= k
