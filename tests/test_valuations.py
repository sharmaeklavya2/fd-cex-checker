"""Tests for properties of valuation functions."""

from valuation import AdditiveValuation
from valuation_extra import PmrfValuation


def test_neg():
    v1 = AdditiveValuation([3, 1, 0, -1, -3])
    v2 = AdditiveValuation([-3, -1, 0, 1, 3])
    assert (-v1).value_list() == v2.value_list()

def test_mul():
    v1 = AdditiveValuation([3, 1, 0, -1, -3])
    v2 = AdditiveValuation([30, 10, 0, -10, -30])
    c = 10
    assert (v1 * c).value_list() == v2.value_list()
    assert (c * v1).value_list() == v2.value_list()

def test_uniform_matroid():
    v = PmrfValuation([42] * 10, default_cap=5)
    assert v(set(range(3, 6))) == 3
    assert v(set(range(2, 8))) == 5

def test_distinct_colors():
    v = PmrfValuation('rrrrggggbbbb', default_cap=1)
    assert v({0,1,4}) == 2
