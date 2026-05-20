from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation
from counterexample import Counterexample

COUNTEREXAMPLES = []

v_single = AdditiveValuation([1])

COUNTEREXAMPLES.append(Counterexample(
    # MMS does not imply PROP.
    # With 2 agents and 1 good, MMS = 0 for both agents, so any allocation is MMS.
    # But the agent who receives nothing gets 0 < 1/2 = PROP threshold.
    id         = 'mms-not-prop-1',
    instance   = Instance([v_single, v_single]),
    allocation = Allocation(bundles=[{0}, set()]),
    witness    = 1,
    satisfies  = 'MMS',
    violates   = 'PROP',
))

v_sym  = AdditiveValuation([10, 20, 30])   # shared by agents 0 and 2
v_1    = AdditiveValuation([20, 10, 30])

COUNTEREXAMPLES.append(Counterexample(
    # PROP does not imply EF (goods).
    # Agent 0 meets her proportional share but envies agent 2's bundle.
    id         = 'prop-not-ef-1',
    instance   = Instance([v_sym, v_1, v_sym]),
    allocation = Allocation(bundles=[{1}, {0}, {2}]),
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'EF',
))

v_sym_c = AdditiveValuation([-30, -20, -10])  # shared by agents 0 and 2
v_1_c   = AdditiveValuation([-20, -30, -10])

COUNTEREXAMPLES.append(Counterexample(
    # PROP does not imply EF (chores).
    # Agent 0 meets her proportional share but envies agent 2's bundle.
    id         = 'prop-not-ef-2',
    instance   = Instance([v_sym_c, v_1_c, v_sym_c]),
    allocation = Allocation(bundles=[{1}, {0}, {2}]),
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'EF',
))
