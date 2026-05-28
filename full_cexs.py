from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation
from counterexample import Counterexample

COUNTEREXAMPLES = []

for t, witness, label in [(1, 1, 'goods'), (-1, 0, 'chores')]:
    v = AdditiveValuation([t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:single-item:' + label,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0}, set()]),
        witness    = witness,
        satisfies  = 'APS+PROPx',
        violates   = 'PROP',
    ))

# n=3, m=5 goods each of value 1. Agent 2 gets 3 goods, agents 0 and 1 get 1 each.
v = AdditiveValuation([1] * 5)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:share-vs-envy-goods',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0}, {1}, {2, 3, 4}]),
    witness    = 0,
    satisfies  = 'APS+PROPx',
    violates   = 'EF1',
))

# n=3, m=4 chores each of disutility 1. Agents 0 and 1 get 2 chores each, agent 2 gets none.
v = AdditiveValuation([-1] * 4)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:share-vs-envy-chores',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0, 1}, {2, 3}, set()]),
    witness    = 0,
    satisfies  = 'APS+EEFX',
    violates   = 'EF1',
))

# EEF does not imply EF1.
# 3 agents, 12 items. v_i = t * f_i where t in {-1, 1} and:
#   f1: [a,a,b,b,b,b,b,b,a,a,a,a]
#   f2: [a,a,a,a,a,a,b,b,b,b,b,b]
#   f3: [b,b,b,b,a,a,a,a,a,a,b,b]
# Allocation A = ({0,1,2,3}, {4,5,6,7}, {8,9,10,11}). Witness = 0 (EF1-envies agent 1 for t=1, agent 2 for t=-1).

_alloc_eef_not_ef1 = Allocation(bundles=[{0,1,2,3}, {4,5,6,7}, {8,9,10,11}])
for (a, b, t, label) in [(1, 3, 1, 'positive-bival'), (0, 1, 1, 'binary'), (1, 3, -1, 'negative-bival'), (0, 1, -1, 'negBinary')]:
    v1 = t * AdditiveValuation([a,a,b,b,b,b,b,b,a,a,a,a])
    v2 = t * AdditiveValuation([a,a,a,a,a,a,b,b,b,b,b,b])
    v3 = t * AdditiveValuation([b,b,b,b,a,a,a,a,a,a,b,b])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:eef-not-ef1:' + label,
        instance   = Instance([v1, v2, v3]),
        allocation = _alloc_eef_not_ef1,
        witness    = 0,
        satisfies  = 'EEF',
        violates   = 'EF1',
    ))

# PROP does not imply MEFS (goods).
# 3 agents, 3 goods. Allocation: agent 0 gets {1}, agent 1 gets {0}, agent 2 gets {2}.
v1 = AdditiveValuation([10, 20, 30])
v2 = AdditiveValuation([20, 10, 30])
v3 = AdditiveValuation([10, 20, 30])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:prop-not-mefs-goods',
    instance   = Instance([v1, v2, v3]),
    allocation = Allocation(bundles=[{1}, {0}, {2}]),
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'MEFS',
))

# PROP does not imply MEFS (chores).
# 3 agents, 3 chores. Allocation: agent 0 gets {1}, agent 1 gets {0}, agent 2 gets {2}.
v1 = AdditiveValuation([-30, -20, -10])
v2 = AdditiveValuation([-20, -30, -10])
v3 = AdditiveValuation([-30, -20, -10])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:prop-not-mefs-chores',
    instance   = Instance([v1, v2, v3]),
    allocation = Allocation(bundles=[{1}, {0}, {2}]),
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'MEFS',
))

# MEFS does not imply EEF (goods).
# 3 agents, 6 goods. Allocation: agent 0 gets {3,4,5}, agent 1 gets {0}, agent 2 gets {1,2}.
v1 = AdditiveValuation([20, 20, 20, 10, 10, 10])
v2 = AdditiveValuation([20, 10, 10,  1,  1,  1])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:mefs-not-eef-goods',
    instance   = Instance([v1, v2, v2]),
    allocation = Allocation(bundles=[{3, 4, 5}, {0}, {1, 2}]),
    witness    = 0,
    satisfies  = 'MEFS',
    violates   = 'EEF',
))

# MEFS does not imply EEF1 (chores).
# 3 agents, 12 chores. v1: items 0-2 have disutility 70, items 3-11 have disutility 10.
# v2 = v3: disutility 10 for each chore.
# Allocation: agent 0 gets {3,...,11}, agent 1 gets {0,1}, agent 2 gets {2}.
v1 = AdditiveValuation([-70] * 3 + [-10] * 9)
v2 = AdditiveValuation([-10] * 12)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:mefs-not-eef1-chores',
    instance   = Instance([v1, v2, v2]),
    allocation = Allocation(bundles=[set(range(3, 12)), {0, 1}, {2}]),
    witness    = 0,
    satisfies  = 'MEFS',
    violates   = 'EEF1',
))
