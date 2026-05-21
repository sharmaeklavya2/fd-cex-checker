"""
EFX fairness notion.
"""

from __future__ import annotations

from fractions import Fraction

from instance import Instance
from allocation import Allocation


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
            if j == i or v_other == 0:
                continue
            removables = [g for g in A_j if v.marginal_gain(g, A_i) > 0]
            if not removables:
                raise NotImplementedError("EFX: Unsupported case (goods). Looks like v is not submodular.")
            min_mloss = min(v.marginal_loss(g, A_j) for g in removables)
            if Fraction(v_own, w[i]) < Fraction(v_other - min_mloss, w[j]):
                return False
        return True
    else:
        # chores
        assert has_neg
        if v_own == 0:
            return True
        min_m_disutil = min(-v.marginal_loss(c, A_i) for c in A_i)
        if min_m_disutil == 0:
            raise NotImplementedError("EFX: Unsupported case (chores). Looks like v is not submodular.")
        v_own_better = v_own + min_m_disutil
        for j in range(n):
            A_j = allocation.bundle(j)
            if Fraction(v_own_better, w[i]) < Fraction(v(A_j), w[j]):
                return False
        return True
