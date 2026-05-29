from typing import TypeVar
from collections.abc import Hashable, Mapping, Sequence, Set
from collections import Counter

from .base import Rational, Valuation
from .base import ADD_FTYPES, SUBMOD_FTYPES, SI_FTYPES


T = TypeVar('T', bound=Hashable)

class PmrfValuation[T](Valuation):
    """
    Partition Matroid Rank Function Valuation.

    Each item has a color, and we have a capacity for each color.
    If a set S has f[c] items of each color c, then value(S) := sum_c min(f[c], capacity[c]).
    """
    def __init__(self, colors: Sequence[T], *,
            default_cap: int | None = None,
            caps: Mapping[T, int] = {},
            shift: Rational = 0):
        assert len(colors) > 0
        assert default_cap is None or default_cap >= 0
        assert all(x >= 0 for x in caps.values())
        assert shift >= 0
        self._colors = colors
        self._shift = shift

        default_cap_2 = len(colors) if default_cap is None else default_cap
        freq = Counter(colors)
        self._caps = {color: min(count, caps.get(color, default_cap_2)) for color, count in freq.items()}
        self._is_additive = all(cap == 0 or cap == freq[color] for color, cap in self._caps.items())

        total_cap = sum(self._caps.values())
        if total_cap == len(colors):
            self._marginal_range = (1+shift, 1+shift)
        elif total_cap == 0:
            self._marginal_range = (shift, shift)
        else:
            self._marginal_range = (shift, 1+shift)

    def n_items(self) -> int:
        return len(self._colors)

    def value(self, subset: Set[int]) -> Rational:
        freq = Counter([self._colors[x] for x in subset])
        return sum([min(cap, freq[color]) for color, cap in self._caps.items()]) + len(subset) * self._shift

    def marginal_range(self) -> tuple[Rational, Rational]:
        return self._marginal_range

    def signs(self) -> tuple[bool, bool, bool]:
        """Returns (has_neg, has_zero, has_pos): whether any marginal value is negative, zero, or positive, respectively."""
        min_marg, max_marg = self._marginal_range
        return (False, min_marg == 0, max_marg > 0)

    def func_types(self) -> frozenset[str]:
        if len(self._colors) == 1:
            return SI_FTYPES
        elif self._is_additive:
            return ADD_FTYPES
        else:
            return SUBMOD_FTYPES

    def is_k_val(self, k: int) -> bool:
        """True iff there are at most k distinct marginal values."""
        min_marg, max_marg = self._marginal_range
        distinct_vals = 1 if min_marg == max_marg else 2
        return distinct_vals <= k
