"""Tests for fairness for simple instances."""

from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation

from notions import AgentCheck
from notions.basic import is_mms_to
from notions.aps import is_aps_to
from notions.up_to_one import is_ef1_to, is_prop1_to
from notions.up_to_any import is_efx_to, is_propx_to, is_propavg_to, is_propm_to
from notions.epistemic import get_epistemic, get_min_fs

import pytest

APPROX_NOTIONS = [is_ef1_to, is_prop1_to, is_mms_to, is_aps_to,
    is_efx_to, is_propx_to, is_propm_to, is_propavg_to]


@pytest.mark.parametrize("eqEnt, f", [(True, f) for f in APPROX_NOTIONS]
    + [(False, f) for f in (is_ef1_to, is_prop1_to, is_aps_to)])
@pytest.mark.parametrize("n", (2, 3))
@pytest.mark.parametrize("t", (1, -1))
def test_single_item(n: int, t: int, eqEnt: bool, f: AgentCheck) -> None:
    v = AdditiveValuation([t])
    w = [1] * n if eqEnt else [3**i for i in range(n)]
    I = Instance([v] * n, w)
    A = Allocation(owner=[0], n_agents=n)
    for i in range(n):
        assert f(I, A, i)


@pytest.mark.parametrize("a, f", [(1, f) for f in APPROX_NOTIONS]
    + [(3, f) for f in set(APPROX_NOTIONS) - {is_prop1_to}])
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

@pytest.mark.parametrize("f", [is_mms_to, is_aps_to, is_efx_to, is_propm_to, is_propavg_to])
def test_house_car_pen_strong(f: AgentCheck) -> None:
    I, better_alloc, ok_alloc = get_house_car_pen()
    assert f(I, better_alloc, 0)
    assert f(I, better_alloc, 1)
    assert f(I, ok_alloc, 0)
    assert not f(I, ok_alloc, 1)


def get_aids_typhoid_flu() -> tuple[Instance, Allocation, Allocation]:
    v = AdditiveValuation([-100, -10, -1])
    I = Instance([v] * 2)
    better_alloc = Allocation(owner=[1, 0, 0], n_agents=2)
    ok_alloc = Allocation(owner=[1, 0, 1], n_agents=2)
    return (I, better_alloc, ok_alloc)


@pytest.mark.parametrize("f", [is_ef1_to, is_prop1_to])
def test_aids_typhoid_flu_weak(f: AgentCheck) -> None:
    I, better_alloc, ok_alloc = get_aids_typhoid_flu()
    for i in range(2):
        assert f(I, ok_alloc, i)
        assert f(I, better_alloc, i)

@pytest.mark.parametrize("f", [is_mms_to, is_aps_to, is_efx_to, is_propx_to])
def test_aids_typhoid_flu_strong(f: AgentCheck) -> None:
    I, better_alloc, ok_alloc = get_aids_typhoid_flu()
    assert f(I, better_alloc, 0)
    assert f(I, better_alloc, 1)
    assert f(I, ok_alloc, 0)
    assert not f(I, ok_alloc, 1)

APPROX_SHAREY_NOTIONS = [is_mms_to, is_aps_to,
    is_prop1_to, is_propx_to, is_propavg_to, is_propm_to,
    get_epistemic(is_ef1_to), get_epistemic(is_efx_to),
    get_min_fs(is_ef1_to), get_min_fs(is_efx_to)]

def get_myob_alloc(t: int, n: int) -> tuple[Instance, Allocation, Allocation]:
    assert t != 0
    assert n > 2
    if t > 0:
        v = AdditiveValuation([t] * (2*n-1))
        I = Instance([v] * n)
        owner = list(range(n-1)) + [n-1] * n
        A = Allocation(owner=owner, n_agents=n)
        owner2 = [0] + list(range(1, n)) * 2
        cert = Allocation(owner=owner2, n_agents=n)
        return (I, A, cert)
    else:
        v = AdditiveValuation([t] * (n-1)**2)
        I = Instance([v] * n)
        owner = [0] * (n-1) + list(range(1, n-1)) * (n-1)
        A = Allocation(owner=owner, n_agents=n)
        owner2 = [0] * (n-1) + list(range(1, n)) * (n-2)
        cert = Allocation(owner=owner2, n_agents=n)
        return (I, A, cert)

@pytest.mark.parametrize("t", (1, -1))
@pytest.mark.parametrize("f", APPROX_SHAREY_NOTIONS)
def test_myob_sharey(t: int, f: AgentCheck) -> None:
    I, A, _ = get_myob_alloc(t, 3)
    assert f(I, A, 0)

@pytest.mark.parametrize("t", (1, -1))
@pytest.mark.parametrize("f", [is_ef1_to, is_efx_to])
def test_myob_non_sharey(t: int, f: AgentCheck) -> None:
    I, A, cert = get_myob_alloc(t, 3)
    fe = get_epistemic(f)
    fms = get_min_fs(f)
    assert not f(I, A, 0)
    assert fe(I, A, 0, cert)
    assert fms(I, A, 0, cert)
