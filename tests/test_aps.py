"""Tests for APS (Any Price Share) fairness."""

from fractions import Fraction

import pytest

from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation
from notions.aps import aps, is_aps_to


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def inst_2_2():
    """2 agents, equal weights, item values [2, 1].

    Budget = 1/2 for each agent.
    Candidate z values: 0, 1, 2, 3.
      z=3: S_z = {{0,1}}. x_{01}=1 (norm) but x_{01}=1/2 (item 0). Infeasible.
      z=2: S_z = {{0},{0,1}}. x_0+x_{01}=1 vs x_0+x_{01}=1/2. Infeasible.
      z=1: S_z = {{0},{1},{0,1}}. x_0=x_1=1/2 satisfies all constraints. Feasible.
    APS = 1.
    """
    v = AdditiveValuation([2, 1])
    return Instance([v, v])


@pytest.fixture
def inst_weighted():
    """2 agents, weights [2, 1], item values [1, 1, 1].

    Budget_0 = 2/3, budget_1 = 1/3.

    APS_0 = 2: z=2, S_z = all pairs and the triple.
      x_{01}=x_{02}=x_{12}=1/3 covers each item at rate 2/3. Feasible.
    APS_1 = 1: z=1, S_z = all non-empty subsets.
      x_{0}=x_{1}=x_{2}=1/3 covers each item at rate 1/3. Feasible.
    """
    v = AdditiveValuation([1, 1, 1])
    return Instance([v, v], weights=[2, 1])


# ---------------------------------------------------------------------------
# aps()
# ---------------------------------------------------------------------------

class TestApsValue:
    def test_equal_weights(self, inst_2_2):
        assert aps(inst_2_2, 0) == Fraction(1)
        assert aps(inst_2_2, 1) == Fraction(1)

    def test_unequal_weights(self, inst_weighted):
        assert aps(inst_weighted, 0) == Fraction(2)
        assert aps(inst_weighted, 1) == Fraction(1)


# ---------------------------------------------------------------------------
# is_aps_to()
# ---------------------------------------------------------------------------

class TestIsApsTo:
    def test_agent_gets_everything_is_fair(self, inst_2_2):
        # Agent 0 receives both items (value 3 >> APS 1).
        alloc = Allocation(owner=[0, 0], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 0) is True

    def test_agent_gets_nothing_is_not_fair(self, inst_2_2):
        # Agent 1 receives nothing (value 0 < APS 1).
        alloc = Allocation(owner=[0, 0], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 1) is False

    def test_boundary_value_equals_aps_is_fair(self, inst_2_2):
        # Agent 1 receives item 1 (value 1 == APS 1): exactly on the boundary.
        # This is the case that a naive `not _lp_feasible(z=value)` check gets wrong.
        alloc = Allocation(owner=[0, 1], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 1) is True

    def test_value_above_aps_is_fair(self, inst_2_2):
        # Agent 0 receives item 0 (value 2 > APS 1).
        alloc = Allocation(owner=[0, 1], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 0) is True

    def test_unequal_weights_fair_allocation(self, inst_weighted):
        # Agent 0 gets {0,1} (value 2 == APS 2), agent 1 gets {2} (value 1 == APS 1).
        alloc = Allocation(owner=[0, 0, 1], n_agents=2)
        assert is_aps_to(inst_weighted, alloc, 0) is True
        assert is_aps_to(inst_weighted, alloc, 1) is True

    def test_unequal_weights_unfair_to_heavy_agent(self, inst_weighted):
        # Agent 0 gets {0} (value 1 < APS 2): unfair.
        # Agent 1 gets {1,2} (value 2 > APS 1): fair.
        alloc = Allocation(owner=[0, 1, 1], n_agents=2)
        assert is_aps_to(inst_weighted, alloc, 0) is False
        assert is_aps_to(inst_weighted, alloc, 1) is True
