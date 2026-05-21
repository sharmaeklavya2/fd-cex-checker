"""
Shared utilities for fairness notion implementations.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Iterator
from typing import Callable

from valuation import Rational
from allocation import Allocation
from instance import Instance


AgentCheck = Callable[[Instance, Allocation, int], bool]


def max0(C: Iterable[Rational]) -> Rational:
    """Maximum lower-clamped at 0."""
    return max(0, max(C, default=0))


def all_allocations(n_agents: int, n_items: int) -> Iterator[Allocation]:
    """
    Yield every allocation of n_items items among n_agents agents.
    There are n_agents ** n_items allocations in total; agents may
    receive empty bundles.
    """
    for owner in itertools.product(range(n_agents), repeat=n_items):
        yield Allocation(owner=owner, n_agents=n_agents)


def all_subsets(m: int) -> list[frozenset[int]]:
    """Return all 2^m subsets of {0, ..., m-1} as frozensets."""
    items = range(m)
    return [
        frozenset(S)
        for r in range(m + 1)
        for S in itertools.combinations(items, r)
    ]


def and_notions(checks: Iterable[AgentCheck]) -> AgentCheck:
    """Return a check that holds iff all of the given checks hold."""
    def combined(instance: Instance, allocation: Allocation, i: int) -> bool:
        return all(check(instance, allocation, i) for check in checks)
    return combined


def or_notions(checks: Iterable[AgentCheck]) -> AgentCheck:
    """Return a check that holds iff at least one of the given checks holds."""
    def combined(instance: Instance, allocation: Allocation, i: int) -> bool:
        return any(check(instance, allocation, i) for check in checks)
    return combined
