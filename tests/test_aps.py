"""Tests for APS (Any Price Share) fairness."""

from fractions import Fraction

import pytest

from valuation import AdditiveValuation, UnitDemandValuation, GeneralValuation
from notions.utils import all_subsets
from instance import Instance
from allocation import Allocation
from notions.aps import aps_instance, is_aps_to, aps_ge
from notions.mms import wmms


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def inst_2_2() -> Instance:
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
def inst_weighted() -> Instance:
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
    def test_equal_weights(self, inst_2_2: Instance):
        assert aps_instance(inst_2_2, 0) == Fraction(1)
        assert aps_instance(inst_2_2, 1) == Fraction(1)

    def test_unequal_weights(self, inst_weighted: Instance):
        assert aps_instance(inst_weighted, 0) == Fraction(2)
        assert aps_instance(inst_weighted, 1) == Fraction(1)


# ---------------------------------------------------------------------------
# is_aps_to()
# ---------------------------------------------------------------------------

class TestIsApsTo:
    def test_agent_gets_everything_is_fair(self, inst_2_2: Instance):
        # Agent 0 receives both items (value 3 >> APS 1).
        alloc = Allocation(owner=[0, 0], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 0) is True

    def test_agent_gets_nothing_is_not_fair(self, inst_2_2: Instance):
        # Agent 1 receives nothing (value 0 < APS 1).
        alloc = Allocation(owner=[0, 0], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 1) is False

    def test_boundary_value_equals_aps_is_fair(self, inst_2_2: Instance):
        # Agent 1 receives item 1 (value 1 == APS 1): exactly on the boundary.
        # This is the case that a naive `not _lp_feasible(z=value)` check gets wrong.
        alloc = Allocation(owner=[0, 1], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 1) is True

    def test_value_above_aps_is_fair(self, inst_2_2: Instance):
        # Agent 0 receives item 0 (value 2 > APS 1).
        alloc = Allocation(owner=[0, 1], n_agents=2)
        assert is_aps_to(inst_2_2, alloc, 0) is True

    def test_unequal_weights_fair_allocation(self, inst_weighted: Instance):
        # Agent 0 gets {0,1} (value 2 == APS 2), agent 1 gets {2} (value 1 == APS 1).
        alloc = Allocation(owner=[0, 0, 1], n_agents=2)
        assert is_aps_to(inst_weighted, alloc, 0) is True
        assert is_aps_to(inst_weighted, alloc, 1) is True

    def test_unequal_weights_unfair_to_heavy_agent(self, inst_weighted: Instance):
        # Agent 0 gets {0} (value 1 < APS 2): unfair.
        # Agent 1 gets {1,2} (value 2 > APS 1): fair.
        alloc = Allocation(owner=[0, 1, 1], n_agents=2)
        assert is_aps_to(inst_weighted, alloc, 0) is False
        assert is_aps_to(inst_weighted, alloc, 1) is True


class TestOrigApsPaperExamples:
    """
    Examples from the paper "Fair-Share Allocations for Agents with Arbitrary Entitlements"
    by Babaioff, Ezra, Feige (doi:10.1287/moor.2021.0199).
    """
    def test_example1(self):
        # Example 1
        v = AdditiveValuation([2, 1, 1, 1, 0])
        b = Fraction(2, 5)
        known_aps = 2
        for z in range(0, 6):
            assert aps_ge(v, b, z) == (known_aps >= z)

    def test_aps_gt_mms(self):
        # Lemma C.1: additive valuations, n=3, m=15.
        v = AdditiveValuation([5,5,5,7,7,7,11,17,23,23,23,31,31,31,65])
        b = Fraction(1, 3)
        known_aps = 97
        assert aps_ge(v, b, known_aps)
        assert not aps_ge(v, b, known_aps+1)

    def test_ud(self):
        # 3.1.1: for unit demand valuations, APS is value of item of rank ceil(1/b).
        v = UnitDemandValuation([3, 5, 7, 9])
        for b, known_aps in [(0.2, 0), (0.4, 5), (0.6, 7), (1, 9)]:
            assert aps_ge(v, b, known_aps)
            assert not aps_ge(v, b, known_aps+1)

    def test_n2(self):
        # Remark 2: example with submodular valuations
        m = 6
        C = {frozenset({0, 1, 2}), frozenset({0, 4, 5}), frozenset({1, 3, 5}), frozenset({2, 3, 4})}
        values = {}
        for S in all_subsets(m):
            if len(S) == 0:
                values[S] = 0
            elif len(S) == 1:
                values[S] = 1
            elif len(S) == 2:
                values[S] = 4
            elif len(S) == 3 and S not in C:
                values[S] = 5
            else:
                values[S] = 6
        v = GeneralValuation(m, values)
        half = Fraction(1, 2)
        assert aps_ge(v, half, 6)
        assert not aps_ge(v, half, 7)
        instance = Instance([v, v])
        mms = wmms(instance, 0)
        assert mms == 5
