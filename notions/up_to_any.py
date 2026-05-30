"""
EFX fairness notion.
"""

from __future__ import annotations

from fractions import Fraction
from collections.abc import Collection
import itertools

from instance import Instance
from .utils import all_subsets
from valuation import Valuation, Rational
from allocation import Allocation


def get_claimables_goods(v: Valuation, A_out: frozenset[int], A_in: frozenset[int]) -> Collection[frozenset[int]]:
    """
    Get the claimable subsets for a bundle A_out wrt bundle A_in and valuation v.

    v is a valuation function. A_in and A_out are disjoint sets.
    A set S ⊆ A_out is 'likeable' if v(S | A_in) > 0.
    A set S ⊆ A_out is 'claimable' if it is a minimal likeable set or if some items in A_out may be chores.
    This function returns a collection of likeable sets which includes all claimable sets.

    Note that if v is submodular or if v has positive marginals, claimable sets can only be singletons.
    """
    assert len(A_in & A_out) == 0
    has_neg, _, has_pos = v.signs()
    if not has_pos:
        return []

    output: list[frozenset[int]] = []

    if has_neg:
        for S in all_subsets(A_out):
            if v.marginal_gain(S, A_in) > 0:
                output.append(S)
        return output

    # now we are in the goods-only setting

    # find claimable singletons
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

    v is a valuation function.
    A set S ⊆ A_i is 'disliked' if v(S | A_i - S) < 0.
    If all items are chores, then f(X) := -v(X | A_i - X) is monotone in X,
    so if a set is disliked, its supersets are also disliked.
    A set S ⊆ A_i is 'disposable' if it is a minimal disliked set or if some items may be goods.
    This function returns a collection of disliked sets which includes all disposable sets.

    Note that if v is submodular or if v has negative marginals, disposable sets can only be singletons.
    """
    has_neg, _, has_pos = v.signs()
    if not has_neg:
        return []

    output: list[frozenset[int]] = []

    if has_pos:
        for S in all_subsets(A_i):
            if v.marginal_loss(S, A_i) < 0:
                output.append(S)
        return output

    # now we are in the chores-only setting

    # find disposable singletons
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
    if not (has_neg or has_pos):
        return True  # only zero values in instance

    v_own = v(A_i)

    # get value of bundle after removing smallest chore
    min_marg_disutil = get_chores_inc_value(v, A_i)
    assert min_marg_disutil >= 0
    v_own_better = v_own + min_marg_disutil

    for j in range(n):
        A_j = allocation.bundle(j)
        v_other = v(A_j)
        if j == i or Fraction(v_own, w[i]) >= Fraction(v_other, w[j]):  # envy-free
            continue
        if min_marg_disutil > 0 and Fraction(v_own_better, w[i]) < Fraction(v_other, w[j]):  # chores check
            return False
        claimable_sets = get_claimables_goods(v, A_j, A_i)
        if not claimable_sets:
            continue
        min_mloss = min(v.marginal_loss(S, A_j) for S in claimable_sets)
        if Fraction(v_own, w[i]) < Fraction(v_other - min_mloss, w[j]):
            return False
    return True


def is_propx_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    A_i, M = allocation.bundle(i), instance.all_items()

    v_own = v(A_i)
    PROP = Fraction(w[i], sum(w)) * v(M)
    if v_own >= PROP:
        return True

    has_neg, _, has_pos = v.signs()
    assert has_neg or has_pos

    min_marg_disutil = get_chores_inc_value(v, A_i)
    # chores condition
    if min_marg_disutil > 0 and v_own + min_marg_disutil <= PROP:
        return False
    # goods condition
    claimable_sets = get_claimables_goods(v, M - A_i, A_i)
    for S in claimable_sets:
        if v_own + v.marginal_gain(S, A_i) <= PROP:
            return False
    return True


def is_propm_propavg_to(instance: Instance, allocation: Allocation, i: int) -> tuple[bool, bool]:
    v, w = instance.valuations[i], instance.weights
    A_i, M = allocation.bundle(i), instance.all_items()

    v_own = v(A_i)
    PROP = Fraction(w[i], sum(w)) * v(M)
    if v_own >= PROP:
        return (True, True)

    has_neg, _, has_pos = v.signs()
    assert has_neg or has_pos

    # chores condition
    min_marg_disutil = get_chores_inc_value(v, A_i)
    if min_marg_disutil > 0 and v_own + min_marg_disutil <= PROP:
        return (False, False)
    # goods condition
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


def is_propm_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    return is_propm_propavg_to(instance, allocation, i)[0]

def is_propavg_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    return is_propm_propavg_to(instance, allocation, i)[1]
