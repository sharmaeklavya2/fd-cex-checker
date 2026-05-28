"""Tests for properties of valuation functions."""

from valuation import AdditiveValuation


def test_neg():
    v1 = AdditiveValuation([3, 1, 0, -1, -3])
    v2 = AdditiveValuation([-3, -1, 0, 1, 3])
    assert (-v1)._values == v2._values

def test_mul():
    v1 = AdditiveValuation([3, 1, 0, -1, -3])
    v2 = AdditiveValuation([30, 10, 0, -10, -30])
    c = 10
    assert (v1 * c)._values == v2._values
    assert (c * v1)._values == v2._values
