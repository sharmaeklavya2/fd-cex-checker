from fractions import Fraction

from valuation import AdditiveValuation
from instance import Instance
from allocation import Allocation
from counterexample import Counterexample

COUNTEREXAMPLES = []

#-------------------------------------------------------------------------------
# Additive Valuations
#-------------------------------------------------------------------------------

#=[ Trivial Examples ]==========================================================

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

#=[ From EEF, MEFS, PROP ]======================================================

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

#=[ Two Equally-Entitled Agents ]===============================================

# EFX does not imply MMS.
# v=[3t,3t,2t,2t,2t], alloc=({0,2},{1,3,4}).
# For t=1: agent 0 gets 3+2=5 < MMS=6. For t=-1: agent 1 gets -3-2-2=-7 < MMS=-6.
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([3*t, 3*t, 2*t, 2*t, 2*t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:efx-not-mms:' + label,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0, 2}, {1, 3, 4}]),
        witness    = witness,
        satisfies  = 'EFX',
        violates   = 'MMS',
    ))

# EF1 does not imply PROPx or MXS.
# v=[4t,4t,t,t,t], alloc=({0},{1,2,3,4}).
# For t=1: agent 0 gets 4 < PROP=5.5. For t=-1: agent 1 gets -7 < PROP=-5.5.
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([4*t, 4*t, t, t, t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:ef1-not-propx-mxs:' + label,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0}, {1, 2, 3, 4}]),
        witness    = witness,
        satisfies  = 'EF1',
        violates   = 'MXS|PROPx',
    ))

# PROPx does not imply M1S.
# eps=1/4, scaled to integers: v=[2t,2t,2t,3t], alloc=({3},{0,1,2}).
# For t=1: agent 0 (witness). For t=-1: agent 1 (witness).
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([2*t, 2*t, 2*t, 3*t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:propx-not-m1s:' + label,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{3}, {0, 1, 2}]),
        witness    = witness,
        satisfies  = 'PROPx',
        violates   = 'M1S',
    ))

# MXS does not imply PROPx (n=2).
# v=[4t,4t,t,t,t,t,t], alloc=({0,2},{1,3,4,5,6}).
# For t=1: agent 0 gets 4+1=5 < PROP=6.5. For t=-1: agent 1 gets -4-4*1=-8 < PROP=-6.5.
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([4*t, 4*t] + [t] * 5)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:mxs-not-propx-n2:' + label,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0, 2}, {1, 3, 4, 5, 6}]),
        witness    = witness,
        satisfies  = 'MXS',
        violates   = 'PROPx',
    ))

# M1S does not imply PROP1.
# v=[t]*8+[4t], alloc=({8},{0,...,7}).
# For t=1: agent 0 gets 4 < PROP1 threshold. For t=-1: agent 1 gets -8 < PROP1 threshold.
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([t] * 8 + [4*t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:m1s-not-prop1:' + label,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{8}, set(range(8))]),
        witness    = witness,
        satisfies  = 'M1S',
        violates   = 'PROP1',
    ))

#=[ Three Equally-Entitled Agents ]=============================================

# GAPS does not imply PROPx.
# 3 agents, 2 goods [50, 10]. Agent 0 gets good 0, agent 1 gets good 1, agent 2 gets nothing.
v = AdditiveValuation([50, 10])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:gaps-not-propx:additive',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0}, {1}, set()]),
    witness    = 2,
    satisfies  = 'GAPS',
    violates   = 'PROPx',
))

# GMMS does not imply APS.
# 3 agents, 15 items. Leximin allocation: bundles sum to (97, 98, 96).
# APS=PROP=97 > MMS. For goods: agent 2 gets 96 < 97. For chores: agent 1 gets -98 < -97.
_v_gmms = [65, 31, 31, 31, 23, 23, 23, 17, 11, 7, 7, 7, 5, 5, 5]
_alloc_gmms = Allocation(bundles=[{0,8,9,10,11}, {1,2,3,14}, {4,5,6,7,12,13}])
for t, witness, label in [(1, 2, 'goods'), (-1, 1, 'chores')]:
    v = t * AdditiveValuation(_v_gmms)
    _cex = Counterexample(
        id         = 'cex:gmms-not-aps:' + label,
        instance   = Instance([v] * 3),
        allocation = _alloc_gmms,
        witness    = witness,
        satisfies  = 'GMMS',
        violates   = 'APS',
    )
    # COUNTEREXAMPLES.append(_cex)

# PMMS does not imply MMS.
# v=[6t,4t,3t,3t,2t,2t,t], alloc=({0},{2,3,4},{1,5,6}).
# For t=1: agent 0 gets 6 < MMS=7. For t=-1: agent 1 gets -8 < MMS=-7.
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([6*t, 4*t, 3*t, 3*t, 2*t, 2*t, t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:pmms-not-mms:' + label,
        instance   = Instance([v] * 3),
        allocation = Allocation(bundles=[{0}, {2, 3, 4}, {1, 5, 6}]),
        witness    = witness,
        satisfies  = 'PMMS',
        violates   = 'MMS',
    ))

# APS does not imply PROPm.
# 3 agents, 6 goods. v=[60,30,10,10,10,10]. alloc=({1},{2,3,4},{0,5}).
# Agent 0 gets item 1 (value 30). PROP=130/3≈43.3. Adding only small items (value 10) gives 40 < 43.3.
v = AdditiveValuation([60, 30, 10, 10, 10, 10])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:aps-not-propm',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{1}, {2, 3, 4}, {0, 5}]),
    witness    = 0,
    satisfies  = 'APS',
    violates   = 'PROPm',
))

# APS does not imply PROP1 (chores).
# 3 agents, 6 chores: v=[-18,-3,-3,-3,-3,-3]. alloc=({1,2,3,4,5},{0},∅).
# Agent 0 gets 5 small chores (value -15). PROP=-11. After removing any chore: -12 < -11.
v = AdditiveValuation([-18, -3, -3, -3, -3, -3])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:aps-not-prop1-chores',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{1, 2, 3, 4, 5}, {0}, set()]),
    witness    = 0,
    satisfies  = 'APS',
    violates   = 'PROP1',
))

# cex:propm-mixed-manna: not appended — PROPm for mixed manna is not yet implemented in the checker.
# 3 agents, 5 chores + 1 good. v=[-3,-3,-3,-3,-3,0.75] (eps=1/4 satisfies 0 < eps < 1/2).
# Case 2 allocation from proof: agent 0 gets 2 chores, agent 1 gets 2 chores + good, agent 2 gets 1 chore.
# Agent 0 adds the good: -6+0.75=-5.25 < PROP=-4.75. Not PROPm. Witness=0.
v = AdditiveValuation([-3, -3, -3, -3, -3, Fraction(3, 4)])
_cex_propm_mixed_manna = Counterexample(
    id         = 'cex:propm-mixed-manna',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0, 1}, {2, 3, 5}, {4}]),
    witness    = 0,
    satisfies  = 'GAPS',
    violates   = 'PROPm',
)
# COUNTEREXAMPLES.append(_cex_propm_mixed_manna)

# PROPm does not imply PROPavg.
# 3 agents, 3 goods. v=[60,60,30]. alloc=({2},{0,1},∅).
# Agent 2 gets nothing. Witness=2.
v = AdditiveValuation([60, 60, 30])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:propm-not-propavg',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{2}, {0, 1}, set()]),
    witness    = 2,
    satisfies  = 'PROPm',
    violates   = 'PROPavg',
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
