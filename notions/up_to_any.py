"""
EFX fairness notion.
"""

from __future__ import annotations

from fractions import Fraction
from collections.abc import Collection
import itertools

from instance import Instance
from valuation import Valuation, Rational
from allocation import Allocation


def get_claimables_goods(v: Valuation, A_out: frozenset[int], A_in: frozenset[int]) -> Collection[frozenset[int]]:
    """
    Get the claimable subsets for a bundle A_out wrt bundle A_in and valuation v over goods.

    v is a valuation function over goods (non-negative marginals).
    A_in and A_out are disjoint sets.
    A set S ⊆ A_out is 'likeable' if v(S | A_in) > 0.
    A set S ⊆ A_out is 'claimable' if it is a minimal likeable set.
    This function returns a collection of likeable sets which includes all claimable sets.

    Note that if v is submodular or if v has positive marginals, claimable sets can only be singletons.
    """
    assert len(A_in & A_out) == 0
    has_neg, _, has_pos = v.signs()
    assert not has_neg
    if not has_pos:
        return []

    # find claimable singletons
    output: list[frozenset[int]] = []
    cl_sings = set()
    for g in A_out:
        S = frozenset((g,))
        if v.marginal_gain(S, A_in) > 0:
            output.append(S)
            cl_sings.add(g)

    remaining = A_out - cl_sings
    if v.marginal_gain(remaining, A_in) == 0:
        # this is true if `not has_zero or "submod" in v.func_types()`
        return output

    for r in range(2, len(remaining)+1):
        for S_tup in itertools.combinations(remaining, r):
            S = frozenset(S_tup)
            if v.marginal_gain(S, A_in) > 0:
                output.append(S)
    return output


def get_disposables_chores(v: Valuation, A_i: frozenset[int]) -> Collection[frozenset[int]]:
    """
    Get the disposable subsets for a bundle A_i and valuation v over chores.

    v is a valuation function over chores (non-positive marginals).
    A set S ⊆ A_i is 'disliked' if v(S | A_i - S) < 0.
    Note that f(X) := -v(X | A_i - X) is monotone in X,
    so if a set is disliked, its supersets are also disliked.
    A set S ⊆ A_i is 'disposable' if it is a minimal disliked set.
    This function returns a collection of disliked sets which includes all disposable sets.

    Note that if v is submodular or if v has negative marginals, disposable sets can only be singletons.
    """
    has_neg, _, has_pos = v.signs()
    assert not has_pos
    if not has_neg:
        return []

    # find disposable singletons
    output: list[frozenset[int]] = []
    d_sings = set()
    for c in A_i:
        S = frozenset((c,))
        if v.marginal_loss(S, A_i) < 0:
            output.append(S)
            d_sings.add(c)

    remaining = A_i - d_sings
    if v.marginal_loss(remaining, A_i) == 0:
        # this is true if `not has_zero or "submod" in v.func_types()`
        return output

    for r in range(2, len(remaining)+1):
        for S_tup in itertools.combinations(remaining, r):
            S = frozenset(S_tup)
            if v.marginal_loss(S, A_i) < 0:
                output.append(S)
    return output


def get_chores_inc_value(v: Valuation, A_i: frozenset[int]) -> Rational:
    """The smallest increment that can be made to a bundle of chores by removing something."""
    disposable_sets = get_disposables_chores(v, A_i)
    return min((-v.marginal_loss(S, A_i) for S in disposable_sets), default=0)


def is_efx_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    n = instance.n_agents()
    A_i = allocation.bundle(i)

    has_neg, _, has_pos = v.signs()
    if has_neg and has_pos:
        raise NotImplementedError("EFX is not implemented for mixed manna.")
    if (not has_neg) and (not has_pos):
        return True  # only zero values in instance

    v_own = v(A_i)

    if has_pos:
        # goods
        for j in range(n):
            A_j = allocation.bundle(j)
            v_other = v(A_j)
            if j == i or Fraction(v_own, w[i]) >= Fraction(v_other, w[j]):
                continue
            claimable_sets = get_claimables_goods(v, A_j, A_i)
            if not claimable_sets:
                continue
            min_mloss = min(v.marginal_loss(S, A_j) for S in claimable_sets)
            if Fraction(v_own, w[i]) < Fraction(v_other - min_mloss, w[j]):
                return False
        return True
    else:
        # chores
        assert has_neg
        if v_own == 0:
            return True
        min_marg_disutil = get_chores_inc_value(v, A_i)
        v_own_better = v_own + min_marg_disutil
        for j in range(n):
            A_j = allocation.bundle(j)
            if Fraction(v_own_better, w[i]) < Fraction(v(A_j), w[j]):
                return False
        return True


def is_propx_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    A_i, M = allocation.bundle(i), instance.all_items()

    v_own = v(A_i)
    PROP = Fraction(w[i] / sum(w)) * v(M)
    if v_own >= PROP:
        return True

    has_neg, _, has_pos = v.signs()
    if has_neg and has_pos:
        raise NotImplementedError("PROPx is not implemented for mixed manna.")
    assert has_neg or has_pos

    if has_pos:
        A_rest = M - A_i
        claimable_sets = get_claimables_goods(v, A_rest, A_i)
        for S in claimable_sets:
            if v_own + v.marginal_gain(S, A_i) <= PROP:
                return False
        return True
    else:
        min_marg_disutil = get_chores_inc_value(v, A_i)
        return v_own + min_marg_disutil > PROP


def is_propm_propavg_to(instance: Instance, allocation: Allocation, i: int) -> tuple[bool, bool]:
    v, w = instance.valuations[i], instance.weights
    A_i, M = allocation.bundle(i), instance.all_items()

    v_own = v(A_i)
    PROP = Fraction(w[i] / sum(w)) * v(M)
    if v_own >= PROP:
        return (True, True)

    has_neg, _, has_pos = v.signs()
    if has_neg and has_pos:
        raise NotImplementedError("PROPm/PROPavg is not implemented for mixed manna.")
    assert has_neg or has_pos

    if has_pos:
        n = instance.n_agents()
        T = []
        for j in range(n):
            if j == i:
                continue
            A_j = allocation.bundle(j)
            claimable_sets = get_claimables_goods(v, A_j, A_i)
            if claimable_sets:
                T.append(min(v.marginal_gain(S, A_i) for S in claimable_sets))
        is_propm = (len(T) == 0 or v_own + max(T) > PROP)
        is_propavg = (len(T) == 0 or v_own + Fraction(sum(T), len(T)) > PROP)
        return (is_propm, is_propavg)
    else:
        min_marg_disutil = get_chores_inc_value(v, A_i)
        result = (v_own + min_marg_disutil > PROP)
        return (result, result)


def is_propm_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    return is_propm_propavg_to(instance, allocation, i)[0]

def is_propavg_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    return is_propm_propavg_to(instance, allocation, i)[1]
