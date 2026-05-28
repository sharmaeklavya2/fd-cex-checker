from valuation import AdditiveValuation
from instance import Instance
from notions.mms import wmms

def test_mms_1() -> None:
    v = AdditiveValuation([7, 7, 6, 6, 5, 5] + [4] * 5)
    I = Instance([v] * 4)
    assert wmms(I, 0) == 14
    Ic = Instance([-v] * 4)
    assert wmms(Ic, 0) == -14


def test_mms_2() -> None:
    v = AdditiveValuation([10, 10, 8, 10, 3, 3, 5, 2])
    I = Instance([v] * 3)
    assert wmms(I, 0) == 16
    Ic = Instance([-v] * 3)
    assert wmms(Ic, 0) == -18

def test_wmms_1() -> None:
    w = [7, 3]
    v = AdditiveValuation([1] * sum(w))
    I = Instance([v] * 2, w)
    assert wmms(I, 0) == w[0]
    assert wmms(I, 1) == w[1]
    Ic = Instance([-v] * 2, w)
    assert wmms(Ic, 0) == -w[0]
    assert wmms(Ic, 1) == -w[1]
