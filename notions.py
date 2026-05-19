"""
Fairness notions for fair division.

Notions implemented:
    EF   – envy-freeness
    PROP – proportionality
    MMS  – (weighted) maximin share  [Farhadi et al. 2019]
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from collections.abc import Iterator
from typing import Callable

from instance import Instance
from allocation import Allocation

# Type alias for per-agent fairness checks.
AgentCheck = Callable[[Instance, Allocation, int], bool]


# ---------------------------------------------------------------------------
# Helper: enumerate all allocations
# ---------------------------------------------------------------------------

def all_allocations(n_agents: int, n_items: int) -> Iterator[Allocation]:
    """
    Yield every allocation of n_items items among n_agents agents.
    There are n_agents ** n_items allocations in total; agents may
    receive empty bundles.
    """
    for owner in itertools.product(range(n_agents), repeat=n_items):
        yield Allocation(owner=owner, n_agents=n_agents)


# ---------------------------------------------------------------------------
# EF – envy-freeness
# ---------------------------------------------------------------------------

def _is_ef_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    vi_own = v.value(allocation.bundle(i))
    return all(Fraction(vi_own, w[i]) >= Fraction(v.value(allocation.bundle(j)), w[j])
               for j in range(instance.n_agents()) if j != i)


# ---------------------------------------------------------------------------
# PROP – proportionality
# ---------------------------------------------------------------------------

def _is_prop_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v, w = instance.valuations[i], instance.weights
    W = sum(w)
    vi_own = v.value(allocation.bundle(i))
    vi_all = v.value(instance.all_items())
    return vi_own >= Fraction(w[i], W) * vi_all


# ---------------------------------------------------------------------------
# MMS – weighted maximin share  [Farhadi et al. 2019]
#
#   WMMS_i = w_i * max_{X ∈ A} min_{j ∈ N} v_i(X_j) / w_j
#
# For equal entitlements this reduces to the standard MMS.
# ---------------------------------------------------------------------------

def _wmms(instance: Instance, i: int) -> Fraction:
    """Return agent i's weighted maximin share as an exact Fraction."""
    n = instance.n_agents()
    v = instance.valuations[i]
    w = instance.weights
    best: Fraction | None = None
    for alloc in all_allocations(n, instance.n_items()):
        min_ratio = min(
            Fraction(v.value(alloc.bundle(j))) / w[j]
            for j in range(n)
        )
        if best is None or min_ratio > best:
            best = min_ratio
    assert best is not None
    return Fraction(w[i]) * best


def _is_mms_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    v = instance.valuations[i]
    return v.value(allocation.bundle(i)) >= _wmms(instance, i)


# ---------------------------------------------------------------------------
# Registry and top-level dispatcher
# ---------------------------------------------------------------------------

NOTIONS: dict[str, AgentCheck] = {
    'EF':   _is_ef_to,
    'PROP': _is_prop_to,
    'MMS':  _is_mms_to,
}


def is_fair_to(instance: Instance, allocation: Allocation, agent: int, notion: str) -> bool:
    check = NOTIONS.get(notion)
    if check is None:
        raise ValueError(f"Unknown fairness notion: {notion!r}")
    return check(instance, allocation, agent)


def is_fair(instance: Instance, allocation: Allocation, notion: str) -> bool:
    """
    Return True iff `allocation` satisfies `notion` for every agent.

    Raises ValueError for unknown notion names.
    """
    check = NOTIONS.get(notion)
    if check is None:
        raise ValueError(f"Unknown fairness notion: {notion!r}")
    return all(check(instance, allocation, i) for i in range(instance.n_agents()))
