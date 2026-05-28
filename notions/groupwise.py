"""
Groupwise fairness wrapper.

An allocation A is groupwise-F-fair to agent i if for every set S of other
agents, the restriction of A to the agents S ∪ {i} and their items is F-fair
to agent i (renumbered to 0).
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence, Set

from valuation import AdditiveValuation, Valuation, Rational
from instance import Instance
from allocation import Allocation
from notions.utils import AgentCheck


# ---------------------------------------------------------------------------
# Restricted valuation
# ---------------------------------------------------------------------------

class RestrictedValuation(Valuation):
    """
    A valuation restricted to a subset of items, with items renumbered 0..k-1.

    Args:
        base:     the original valuation.
        item_map: item_map[k] is the original item index for new item k.
    """

    def __init__(self, base: Valuation, item_map: Sequence[int]) -> None:
        self._base = base
        self._item_map = item_map
        self._m = len(item_map)

    def _to_orig(self, subset: Set[int]) -> frozenset[int]:
        return frozenset(self._item_map[k] for k in subset)

    def n_items(self) -> int:
        return self._m

    def value(self, subset: Set[int]) -> Rational:
        return self._base.value(self._to_orig(subset))

    def func_types(self) -> frozenset[str]:
        # Structural properties (submodularity, additivity, …) are preserved under item restriction.
        return self._base.func_types()

    def signs(self) -> tuple[bool, bool, bool]:
        raise NotImplementedError(f"{type(self).__name__}: `signs` is not implemented")

    def marginal_range(self) -> tuple[Rational, Rational]:
        raise NotImplementedError(f"{type(self).__name__}: `marginals` is not implemented")

    def is_k_val(self, k: int) -> bool:
        raise NotImplementedError(f"{type(self).__name__}: `is_k_val` is not implemented")


def get_restricted_valuation(v: Valuation, item_map: Sequence[int]) -> Valuation:
    if isinstance(v, AdditiveValuation):
        values = v.value_list()
        return AdditiveValuation([values[g] for g in item_map])
    else:
        return RestrictedValuation(v, item_map)


# ---------------------------------------------------------------------------
# Restricted instance/allocation
# ---------------------------------------------------------------------------

def get_restricted_alloc(instance: Instance, allocation: Allocation, agents: Sequence[int]
        ) -> tuple[Instance, Allocation]:
    """
    Given an instance I, allocation A, and a sequence of agents, return an
    (instance, allocation) pair restricted to those agents and the items
    ∪_{j ∈ agents} A_j.

    Agent agents[k] is renumbered to k.  Items are renumbered 0, 1, … in sorted order.
    """
    n, m = instance.n_agents(), instance.n_items()
    assert allocation.n_agents() == n
    assert allocation.n_items() == m
    assert len(agents) == len(set(agents)), "agents must be distinct"
    assert all(0 <= j < n for j in agents)

    # Item renumbering: collect all items held by agents in the group
    all_orig_items = sorted(set().union(*(allocation.bundle(j) for j in agents)))
    item_map = all_orig_items          # new item index -> original item index
    item_inv = {orig: new for new, orig in enumerate(item_map)}

    # Build restricted instance
    new_valuations = [get_restricted_valuation(instance.valuations[j], item_map) for j in agents]
    new_weights = [instance.weights[j] for j in agents]
    new_instance = Instance(new_valuations, new_weights)

    # Build restricted allocation (bundles renumbered)
    new_bundles = [frozenset(item_inv[item] for item in allocation.bundle(j)) for j in agents]
    new_allocation = Allocation(bundles=new_bundles)

    return (new_instance, new_allocation)


# ---------------------------------------------------------------------------
# Groupwise decorator
# ---------------------------------------------------------------------------

def get_groupwise(check: AgentCheck) -> AgentCheck:
    """
    Return the groupwise variant of a per-agent fairness check.

    The returned function returns True iff for every non-empty subset S of
    other agents, check holds for agent 0 in the restriction of the instance
    and allocation to agents [i] + sorted(S).
    """
    def groupwise_check(instance: Instance, allocation: Allocation, i: int) -> bool:
        others = [j for j in range(instance.n_agents()) if j != i]
        for r in range(1, len(others) + 1):
            for S in itertools.combinations(others, r):
                r_instance, r_alloc = get_restricted_alloc(instance, allocation, [i] + list(S))
                if not check(r_instance, r_alloc, 0):
                    return False
        return True

    return groupwise_check


def get_pairwise(check: AgentCheck) -> AgentCheck:
    """
    Return the pairwise variant of a per-agent fairness check.

    The returned function returns True iff for every other agent j, check holds
    for agent 0 in the restriction of the instance and allocation to agents [i, j].
    """
    def pairwise_check(instance: Instance, allocation: Allocation, i: int) -> bool:
        for j in range(instance.n_agents()):
            if j == i:
                continue
            r_instance, r_alloc = get_restricted_alloc(instance, allocation, [i, j])
            if not check(r_instance, r_alloc, 0):
                return False
        return True

    return pairwise_check
