"""Tests for properties of valuation functions."""

from valuation import AdditiveValuation, PmrfValuation, BinPackingValuation
from valuation.bin_pack import opt_bin_pack, first_fit_decreasing


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


#=[ Bin packing ]===============================================================

def test_bp_1():
    for n in (4, 5, 6):
        assert opt_bin_pack([1] * n, 3, 3) == 2
        assert first_fit_decreasing([1] * n, 3) == 2

def test_bp_2():
    sizes, cap = [3, 2, 2, 3, 2, 2], 7
    assert first_fit_decreasing(sizes, cap) == 3
    assert opt_bin_pack(sizes, cap, 3) == 2
