"""Tests for fairness for simple instances."""

from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation

from notions import AgentCheck
from notions.basic import is_mms_to
from notions.aps import is_aps_to
from notions.up_to_one import is_ef1_to, is_prop1_to

import pytest

APPROX_NOTIONS = [is_ef1_to, is_prop1_to, is_mms_to, is_aps_to]


@pytest.mark.parametrize("f", APPROX_NOTIONS)
@pytest.mark.parametrize("n", (2, 3))
@pytest.mark.parametrize("t", (1, -1))
def test_single_item(n: int, t: int, f: AgentCheck) -> None:
    v = AdditiveValuation([t])
    I = Instance([v] * n)
    A = Allocation(owner=[0], n_agents=n)
    for i in range(n):
        assert f(I, A, i)


@pytest.mark.parametrize("a, f", [(1, f) for f in APPROX_NOTIONS]
    + [(3, f) for f in (is_ef1_to, is_mms_to, is_aps_to)])
@pytest.mark.parametrize("t", (1, -1))
def test_two_items(t: int, a: int, f: AgentCheck) -> None:
    v = AdditiveValuation([t*a, t])
    I = Instance([v] * 2)
    A = Allocation(owner=[0, 1], n_agents=2)
    assert f(I, A, 0)
    assert f(I, A, 1)
    # In allocation B, treat agent 0 favorably
    owner = [0, 0] if t == 1 else [1, 1]
    B = Allocation(owner=owner, n_agents=2)
    assert f(I, B, 0)
    assert not f(I, B, 1)


def get_house_car_pen() -> tuple[Instance, Allocation, Allocation]:
    v = AdditiveValuation([100, 10, 1])
    I = Instance([v] * 2)
    better_alloc = Allocation(owner=[0, 1, 1], n_agents=2)
    ok_alloc = Allocation(owner=[0, 1, 0], n_agents=2)
    return (I, better_alloc, ok_alloc)

@pytest.mark.parametrize("f", [is_ef1_to, is_prop1_to])
def test_house_car_pen_weak(f: AgentCheck) -> None:
    I, better_alloc, ok_alloc = get_house_car_pen()
    for i in range(2):
        assert f(I, ok_alloc, i)
        assert f(I, better_alloc, i)

@pytest.mark.parametrize("f", [is_mms_to, is_aps_to])
def test_house_car_pen_strong(f: AgentCheck) -> None:
    I, better_alloc, ok_alloc = get_house_car_pen()
    assert f(I, better_alloc, 0)
    assert f(I, better_alloc, 1)
    assert f(I, ok_alloc, 0)
    assert not f(I, ok_alloc, 1)
