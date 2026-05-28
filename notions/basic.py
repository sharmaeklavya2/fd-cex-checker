"""
Basic fairness notions: EF, PROP.
"""

from __future__ import annotations

from fractions import Fraction

from instance import Instance
from allocation import Allocation


def is_ef_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    vi_own = v(allocation.bundle(i))
    return all(Fraction(vi_own, w[i]) >= Fraction(v(allocation.bundle(j)), w[j])
               for j in range(instance.n_agents()) if j != i)


def is_prop_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    W = sum(w)
    vi_own = v(allocation.bundle(i))
    vi_all = v(instance.all_items())
    return vi_own >= Fraction(w[i], W) * vi_all
