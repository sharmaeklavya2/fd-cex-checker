"""
Epistemic fairness wrapper.

An allocation A is epistemic-F-fair to agent i if there exists a certificate
allocation B with B_i = A_i that is F-fair to agent i.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterator
from typing import Protocol

from instance import Instance
from allocation import Allocation
from notions.utils import all_allocations, AgentCheck

class EpistemicAgentCheck(Protocol):
    def __call__(self, instance: Instance, allocation: Allocation, i: int,
                 cert: Allocation | None = None) -> bool: ...

def get_reallocations(allocation: Allocation, i: int) -> Iterator[Allocation]:
    """
    Yield all allocations B with B_i = allocation.bundle(i).

    Items outside bundle i are distributed in every possible way
    among the other n-1 agents.
    """
    n, m = allocation.n_agents(), allocation.n_items()
    A_i = allocation.bundle(i)
    remaining = list(set(range(m)) - A_i)
    others = [j for j in range(n) if j != i]

    for assignment in itertools.product(others, repeat=len(remaining)):
        bundles: list[set[int]] = [set() for _ in range(n)]
        bundles[i] = set(A_i)
        for item, agent in zip(remaining, assignment):
            bundles[agent].add(item)
        yield Allocation(bundles=bundles, n_agents=n)


def get_epistemic(check: AgentCheck) -> EpistemicAgentCheck:
    """
    Return the epistemic variant of a per-agent fairness check.

    The returned function returns True iff there exists a certificate
    allocation B with B_i = A_i such that check(instance, B, i) is True.
    It enumerates all ways to distribute M \\ A_i among the other agents.
    """
    def epistemic_check(instance: Instance, allocation: Allocation, i: int, cert: Allocation | None = None) -> bool:
        if cert is not None:
            A_i = allocation.bundle(i)
            if cert.bundle(i) != A_i:
                raise ValueError("Invalid epistemic certificate: bundle mismatch")
            elif check(instance, cert, i):
                return True
            else:
                raise ValueError("Invalid epistemic certificate: unfair")
        else:
            return any(check(instance, B, i) for B in get_reallocations(allocation, i))

    return epistemic_check


def get_min_fs(check: AgentCheck) -> EpistemicAgentCheck:
    """
    Return the min-share variant of a per-agent fairness check.

    The returned function returns True iff there exists a certificate
    allocation B with v_i(B_i) ≤ v_i(A_i) such that check(instance, B, i) is True.
    """
    def min_fs_check(instance: Instance, allocation: Allocation, i: int, cert: Allocation | None = None) -> bool:
        v = instance.valuations[i]
        v_own = v(allocation.bundle(i))
        if cert is not None:
            if v(cert.bundle(i)) > v_own:
                raise ValueError("Invalid minfs certificate: bundle gained value")
            elif check(instance, cert, i):
                return True
            else:
                raise ValueError("Invalid minfs certificate: unfair")
        else:
            n, m = allocation.n_agents(), allocation.n_items()
            for B in all_allocations(n, m):
                if v(B.bundle(i)) <= v_own and check(instance, B, i):
                    return True
            return False

    return min_fs_check
