"""
Epistemic fairness wrapper.

An allocation A is epistemic-F-fair to agent i if there exists a certificate
allocation B with B_i = A_i that is F-fair to agent i.
"""

from __future__ import annotations

import itertools
from typing import Callable, Protocol

from instance import Instance
from allocation import Allocation

AgentCheck = Callable[[Instance, Allocation, int], bool]

class EpistemicAgentCheck(Protocol):
    def __call__(self, instance: Instance, allocation: Allocation, i: int,
                 cert: Allocation | None = None) -> bool: ...

def get_epistemic(check: AgentCheck) -> EpistemicAgentCheck:
    """
    Return the epistemic variant of a per-agent fairness check.

    The returned function returns True iff there exists a certificate
    allocation B with B_i = A_i such that check(instance, B, i) is True.
    It enumerates all ways to distribute M \\ A_i among the other agents.
    """
    def epistemic_check(instance: Instance, allocation: Allocation, i: int, cert: Allocation | None = None) -> bool:
        n = instance.n_agents()
        A_i = allocation.bundle(i)
        remaining = list(instance.all_items() - A_i)
        others = [j for j in range(n) if j != i]

        if cert is not None:
            if cert.bundle(i) != A_i:
                raise ValueError("Invalid epistemic certificate: bundle mismatch")
            if check(instance, cert, i):
                return True
            else:
                raise ValueError("Invalid epistemic certificate: unfair")
        for assignment in itertools.product(others, repeat=len(remaining)):
            bundles: list[set[int]] = [set() for _ in range(n)]
            bundles[i] = set(A_i)
            for item, agent in zip(remaining, assignment):
                bundles[agent].add(item)
            B = Allocation(bundles=bundles, n_agents=n)
            if check(instance, B, i):
                return True
        return False

    return epistemic_check
