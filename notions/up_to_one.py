"""
"Up to one item" fairness notions: EF1, PROP1.
"""

from __future__ import annotations

from fractions import Fraction

from valuation import Valuation, Rational
from instance import Instance
from allocation import Allocation
from notions.utils import max0


def max_disutil_of_some_chore(v: Valuation, S: frozenset[int]) -> Rational:
    """Returns the maximum disutility across chores in S (0 if S has no chores)."""
    return max0(-v.marginal_loss({c}, S) for c in S)


def is_ef1_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    """
    Return True iff agent i is EF1-fair under the given allocation.

    Agent i is EF1-fair wrt agent j if any of the following hold:
      (1) i does not envy j,
      (2) removing some g from A_j eliminates i's envy of j,
      (3) removing some c from A_i eliminates i's envy of j.
    """
    v, w = instance.valuations[i], instance.weights
    A_i = allocation.bundle(i)
    v_own = v(A_i)
    v_own_better = v_own + max_disutil_of_some_chore(v, A_i)

    for j in range(instance.n_agents()):
        if j == i:
            continue
        A_j = allocation.bundle(j)
        v_other = v(A_j)

        # Conditions 1 and 3: no envy up to a chore
        if Fraction(v_own_better, w[i]) >= Fraction(v_other, w[j]):
            continue

        # Condition 2: no envy up to a good
        if A_j:
            v_other_worse = v_other - max0(v.marginal_loss({g}, A_j) for g in A_j)
            if Fraction(v_own, w[i]) >= Fraction(v_other_worse, w[j]):
                continue

        return False

    return True


def is_prop1_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    """
    Return True iff agent i is PROP1-fair under the given allocation.

    Agent i is PROP1-fair if any of the following hold:
      (1) i gets her PROP share,
      (2) adding some g from M - A_i makes agent i super-PROP-sat,
      (3) removing some c from A_i makes agent i super-PROP-sat.
    """
    v, w = instance.valuations[i], instance.weights
    PROP = Fraction(w[i], sum(w)) * v(instance.all_items())
    A_i = allocation.bundle(i)

    v_own = v(A_i)
    if v_own >= PROP:
        return True

    v_own_minus_c = v_own + max_disutil_of_some_chore(v, A_i)
    if v_own_minus_c > PROP:
        return True

    outside = instance.all_items() - A_i
    v_own_plus_g = v_own + max0(v.marginal_gain({g}, A_i) for g in outside)
    return v_own_plus_g > PROP
