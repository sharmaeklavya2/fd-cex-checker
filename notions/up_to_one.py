"""
"Up to one item" fairness notions: EF1, PROP1.
"""

from __future__ import annotations

from fractions import Fraction

from instance import Instance
from allocation import Allocation


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

    # max value after removing a chore (if it exists)
    v_own_better = v_own + max(0, max([-v.marginal_loss(c, A_i) for c in A_i], default=0))

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
            v_other_worse = v_other - max(v.marginal_loss(g, A_j) for g in A_j)
            if Fraction(v_own, w[i]) >= Fraction(v_other_worse, w[j]):
                continue

        return False

    return True
