"""
Allocation of items to agents.

Items are integers 0..m-1. Agents are integers 0..n-1.
Two representations are stored internally:
  - owner[j]    = index of the agent who owns item j  (list of length m)
  - bundles[i]  = frozenset of items owned by agent i (list of length n)
"""

from __future__ import annotations

from collections.abc import Sequence, Set


class Allocation:
    """
    An allocation of m items among n agents.

    Exactly one of `owner` or `bundles` must be provided.

    Args:
        owner:    sequence of length m where owner[j] is the agent who owns item j.
                  Requires n_agents to be passed explicitly, since not every
                  agent is guaranteed to appear in the sequence.
        bundles:  sequence of n sets/frozensets where bundles[i] is the set of
                  items owned by agent i. Disjointness is verified.
        n_agents: required when using the owner form; ignored otherwise.
    """

    def __init__(self, *,
                 owner: Sequence[int] | None = None,
                 bundles: Sequence[Set[int]] | None = None,
                 n_agents: int | None = None) -> None:
        if (owner is None) == (bundles is None):
            raise ValueError("Provide exactly one of 'owner' or 'bundles'")

        if owner is not None:
            if n_agents is None:
                raise ValueError("'n_agents' is required when using the owner form")
            assert all(0 <= a < n_agents for a in owner), \
                "All owner entries must be valid agent indices in 0..n_agents-1"
            self._owner: list[int] = list(owner)
            tmp: list[list[int]] = [[] for _ in range(n_agents)]
            for item, agent in enumerate(owner):
                tmp[agent].append(item)
            self._bundles: list[frozenset[int]] = [frozenset(b) for b in tmp]

        else:  # bundles form
            assert bundles is not None  # for type checker
            all_items = [item for b in bundles for item in b]
            all_items_set = set(all_items)
            assert len(all_items) == len(all_items_set), \
                "Bundles must be disjoint"
            m = len(all_items)
            assert all_items_set == set(range(m)), \
                f"Items must be range({m})"
            self._bundles = [frozenset(b) for b in bundles]
            self._owner = [0] * m
            for agent, bundle in enumerate(self._bundles):
                for item in bundle:
                    self._owner[item] = agent

    def n_agents(self) -> int:
        return len(self._bundles)

    def n_items(self) -> int:
        return len(self._owner)

    def bundle(self, agent: int) -> frozenset[int]:
        """Return the set of items owned by `agent`."""
        return self._bundles[agent]

    def owner_of(self, item: int) -> int:
        """Return the agent who owns `item`."""
        return self._owner[item]

    def __repr__(self) -> str:
        return f"Allocation(bundles={self._bundles!r})"
