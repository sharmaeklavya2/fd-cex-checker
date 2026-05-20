"""
Basic fairness notions: EF, PROP, WMMS.
"""

from __future__ import annotations

from fractions import Fraction

from instance import Instance
from allocation import Allocation
from notions.utils import all_allocations


# ---------------------------------------------------------------------------
# EF – envy-freeness
# ---------------------------------------------------------------------------

def is_ef_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    vi_own = v(allocation.bundle(i))
    return all(Fraction(vi_own, w[i]) >= Fraction(v(allocation.bundle(j)), w[j])
               for j in range(instance.n_agents()) if j != i)


# ---------------------------------------------------------------------------
# PROP – proportionality
# ---------------------------------------------------------------------------

def is_prop_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    W = sum(w)
    vi_own = v(allocation.bundle(i))
    vi_all = v(instance.all_items())
    return vi_own >= Fraction(w[i], W) * vi_all


# ---------------------------------------------------------------------------
# MMS – weighted maximin share  [Farhadi et al. 2019]
#
#   WMMS_i = w_i * max_{X ∈ A} min_{j ∈ N} v_i(X_j) / w_j
#
# For equal entitlements this reduces to the standard MMS.
# ---------------------------------------------------------------------------

def wmms(instance: Instance, i: int) -> Fraction:
    """Return agent i's weighted maximin share as an exact Fraction."""
    n = instance.n_agents()
    v = instance.valuations[i]
    w = instance.weights
    best: Fraction | None = None
    for alloc in all_allocations(n, instance.n_items()):
        min_ratio = min(
            Fraction(v(alloc.bundle(j))) / w[j]
            for j in range(n)
        )
        if best is None or min_ratio > best:
            best = min_ratio
    assert best is not None
    return Fraction(w[i]) * best


def is_mms_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v = instance.valuations[i]
    return v(allocation.bundle(i)) >= wmms(instance, i)
