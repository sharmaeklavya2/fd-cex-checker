from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation
from counterexample import Counterexample

COUNTEREXAMPLES = []

v_sym = AdditiveValuation([10, 20, 30])  # shared by agents 0 and 2
v_1   = AdditiveValuation([20, 10, 30])

COUNTEREXAMPLES.append(Counterexample(
    # PROP does not imply EF.
    # Agent 0 meets her proportional share but envies agent 2's bundle.
    id         = 'prop-not-ef-1',
    instance   = Instance([v_sym, v_1, v_sym]),
    allocation = Allocation(bundles=[{1}, {0}, {2}]),
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'EF',
))
