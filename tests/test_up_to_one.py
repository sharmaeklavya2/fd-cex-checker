"""Tests for EF1."""

from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation
from notions.up_to_one import is_ef1_to

import pytest


@pytest.mark.parametrize("n", (2, 3))
@pytest.mark.parametrize("t", (1, -1))
def test_single_item(n, t):
    v = AdditiveValuation([t])
    I = Instance([v] * n)
    A = Allocation(owner=[0], n_agents=n)
    for i in range(n):
        assert is_ef1_to(I, A, i)


@pytest.mark.parametrize("a", (1, 3))
@pytest.mark.parametrize("t", (1, -1))
def test_two_id_items(t, a):
    v = AdditiveValuation([t, t*a])
    I = Instance([v] * 2)
    A = Allocation(owner=[0, 1], n_agents=2)
    assert is_ef1_to(I, A, 0)
    assert is_ef1_to(I, A, 1)
    # In allocation B, treat agent 0 favorably
    owner = [0, 0] if t == 1 else [1, 1]
    B = Allocation(owner=owner, n_agents=2)
    assert is_ef1_to(I, B, 0)
    assert not is_ef1_to(I, B, 1)


def test_house_car_pen():
    v = AdditiveValuation([100, 10, 1])
    I = Instance([v] * 2)
    better_alloc = Allocation(owner=[0, 1, 1], n_agents=2)
    ok_alloc = Allocation(owner=[0, 1, 0], n_agents=2)
    for alloc in (better_alloc, ok_alloc):
        for i in range(2):
            assert is_ef1_to(I, alloc, i)
