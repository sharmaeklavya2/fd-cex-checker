import math
from fractions import Fraction
from collections.abc import Sequence, Set

from .base import Rational, Valuation
from .base import SI_FTYPES, ADD_FTYPES, SUBADD_FTYPES


def first_fit_decreasing(sizes: Sequence[Rational], cap: Rational) -> int:
    """Pack items by FFD. Returns number of bins used."""
    fills: list[Rational] = []
    for s in sorted(sizes, reverse=True):
        placed = False
        for i in range(len(fills)):
            if fills[i] + s <= cap:
                fills[i] += s
                placed = True
                break
        if not placed:
            fills.append(s)
    return len(fills)


def opt_bin_pack(sizes: Sequence[Rational], cap: Rational, ub: int) -> int | None:
    """
    Sorted-tuple bin-packing DP.

    Searches for a packing of `sizes` using strictly fewer than `ub` bins.
    State = sorted tuple of current bin fill levels.
    Returns the minimum number of bins found, or None if none exists.
    """
    states: set[tuple[Rational, ...]] = {()}
    for s in sizes:
        new_states: set[tuple[Rational, ...]] = set()
        for state in states:
            # place in an existing bin
            for j, fill in enumerate(state):
                if fill + s <= cap:
                    lst = list(state)
                    lst[j] += s
                    new_states.add(tuple(sorted(lst)))
            # open a new bin, but only if it keeps us under ub bins
            if len(state) + 1 < ub:
                new_states.add(tuple(sorted(state + (s,))))
        states = new_states
    if not states:
        return None
    return min(len(state) for state in states)


class BinPackingValuation(Valuation):
    """
    Bin packing valuation: value(S) = minimum number of capacity-C bins
    needed to pack the items in S, where item i has size sizes[i].

    The valuation is monotone non-decreasing and subadditive.
    """

    def __init__(self, sizes: Sequence[Rational], cap: Rational, shift: Rational = 0):
        assert cap > 0, "capacity must be positive"
        assert len(sizes) > 0, "must have at least one item"
        assert all(0 < s <= cap for s in sizes), "all sizes must be in (0, cap]"
        assert shift >= 0
        self._sizes = list(sizes)
        self._cap = cap
        self._shift = shift
        self._m = len(sizes)
        self._cache: dict[frozenset[int], Rational] = {}

        # Marginal minus shift is always in {0, 1}.
        # min marginal (minus shift) = 0 iff some pair of items fits in a single bin together.
        if self._m == 1:
            self._marginal_range = (1+shift, 1+shift)
        else:
            sorted_sizes = sorted(sizes)
            any_pair_fits = (sorted_sizes[0] + sorted_sizes[1] <= cap)
            self._marginal_range = (shift if any_pair_fits else 1+shift, 1+shift)

    def n_items(self) -> int:
        return self._m

    def value(self, subset: Set[int]) -> Rational:
        key = frozenset(subset)
        if key in self._cache:
            return self._cache[key]
        result = self._compute_bins(key) + len(key) * self._shift
        self._cache[key] = result
        return result

    def _compute_bins(self, subset: frozenset[int]) -> int:
        if not subset:
            return 0
        sizes = [self._sizes[i] for i in sorted(subset)]
        cap = self._cap

        lb = math.ceil(Fraction(sum(sizes), cap))  # lower bound
        ub = first_fit_decreasing(sizes, cap)  # upper bound
        if lb == ub:
            return lb

        # Search for a packing with strictly fewer than ub bins.
        result = opt_bin_pack(sizes, cap, ub)
        return ub if result is None else result

    def signs(self) -> tuple[bool, bool, bool]:
        min_marg, _ = self._marginal_range
        return (False, min_marg == 0, True)

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def is_k_val(self, k: int) -> bool:
        min_marg, max_marg = self._marginal_range
        distinct = 1 if min_marg == max_marg else 2
        return distinct <= k

    def func_types(self) -> frozenset[str]:
        min_marg, max_marg = self._marginal_range
        if self._m == 1:
            return SI_FTYPES
        elif min_marg == max_marg:
            return ADD_FTYPES
        else:
            return SUBADD_FTYPES

    def __repr__(self) -> str:
        if self._shift > 0:
            return f"{type(self).__name__}({self._sizes!r}, cap={self._cap!r}, shift={self._shift!r})"
        else:
            return f"{type(self).__name__}({self._sizes!r}, cap={self._cap!r})"
