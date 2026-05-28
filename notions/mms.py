from fractions import Fraction
from collections.abc import Iterable, Sequence, Set

from valuation import AdditiveValuation, Rational, Valuation
from instance import Instance
from allocation import Allocation
from notions.utils import all_allocations


def update_partition_sums(Xset: Set[tuple[Rational, ...]], y: Rational) -> set[tuple[Rational, ...]]:
    Yset = set()
    for X in Xset:
        for j, x in enumerate(X):
            Y = list(X)
            Y[j] = x + y
            Y.sort()
            Yset.add(tuple(Y))
    return Yset


def get_partition_sums(a: Iterable[Rational], n: int) -> set[tuple[Rational, ...]]:
    Xset: set[tuple[Rational, ...]] = {(0,) * n}
    for x in a:
        Xset = update_partition_sums(Xset, x)
    return Xset

# ---------------------------------------------------------------------------
# MMS – weighted maximin share  [Farhadi et al. 2019]
#
#   WMMS_i = w_i * max_{X ∈ A} min_{j ∈ N} v_i(X_j) / w_j
#
# For equal entitlements this reduces to the standard MMS.
# ---------------------------------------------------------------------------

def neg_flip(a: Sequence[Rational]) -> Sequence[Rational]:
    """Let a = a_negative + a_nonneg. Return a_nonneg + reversed(a_negative)."""
    a_negative = [x for x in a if x < 0]
    a_negative.reverse()
    a_nonneg = [x for x in a if x >= 0]
    return a_nonneg + list(a_negative)


def additive_wmms_by_wi(v: AdditiveValuation, w: Sequence[Rational]) -> Rational:
    n = len(w)
    w2 = sorted(w)
    best: Fraction | None = None
    for X in get_partition_sums(v.value_list(), n):
        # assert sorted(X) == X
        X_neg_flipped = neg_flip(X)
        min_ratio = min(Fraction(x, w2[j]) for j, x in enumerate(X_neg_flipped))
        if best is None or min_ratio > best:
            best = min_ratio
    assert best is not None
    return best


def general_wmms_by_wi(v: Valuation, w: Sequence[Rational]) -> Fraction:
    n = len(w)
    best: Fraction | None = None
    for alloc in all_allocations(n, v.n_items()):
        min_ratio = min(Fraction(v(alloc.bundle(j)), w[j]) for j in range(n))
        if best is None or min_ratio > best:
            best = min_ratio
    assert best is not None
    return best


def wmms(instance: Instance, i: int) -> Rational:
    v = instance.valuations[i]
    w = instance.weights
    if isinstance(v, AdditiveValuation):
        return additive_wmms_by_wi(v, w) * w[i]
    else:
        return general_wmms_by_wi(v, w) * w[i]


def is_mms_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v = instance.valuations[i]
    return v(allocation.bundle(i)) >= wmms(instance, i)
