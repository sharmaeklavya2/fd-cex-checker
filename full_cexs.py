from collections.abc import Set
from fractions import Fraction

from valuation import Rational
from valuation import (AdditiveValuation, UnitDemandValuation, PmrfValuation, BinPackingValuation,
    IdenticalItemsValuation, GeneralValuation)
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
# ε=1/4, scaled to integers: v=[2t,2t,2t,3t], alloc=({3},{0,1,2}).
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
# Works for both additive and unit-demand valuations.
_alloc_gaps_not_propx = Allocation(bundles=[{0}, {1}, set()])
for Val, id_suffix in [(AdditiveValuation, 'additive'), (UnitDemandValuation, 'unit-demand')]:
    v = Val([50, 10])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:gaps-not-propx:' + id_suffix,
        instance   = Instance([v] * 3),
        allocation = _alloc_gaps_not_propx,
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
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:gmms-not-aps:' + label,
        instance   = Instance([v] * 3),
        allocation = _alloc_gmms,
        witness    = witness,
        satisfies  = 'GMMS',
        violates   = 'APS',
    ))

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
# 3 agents, 5 chores + 1 good. v=[-3,-3,-3,-3,-3,0.75] (ε=1/4 satisfies 0 < ε < 1/2).
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
# TODO: implement PROPm for mixed manna

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

#=[ Unequal Entitlements ]======================================================

# PROP1 does not imply M1S (n=2).
# 2 agents, 2 items of value t. Weights (2, 1) ≡ (2/3, 1/3). Agent 0 gets both items.
# Goods: agent 1 gets nothing; every EF1 gives them ≥1. Chores: agent 0 gets all; every EF1 gives them ≥−1.
for t, witness, label in [(1, 1, 'goods'), (-1, 0, 'chores')]:
    v = AdditiveValuation([t, t])
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:prop1-not-m1s-n2:' + label,
        instance   = Instance([v, v], weights=[2, 1]),
        allocation = Allocation(bundles=[{0, 1}, set()]),
        witness    = witness,
        satisfies  = 'PROP1',
        violates   = 'M1S',
    ))

# GAPS does not imply PROPx (n=2, unequal entitlements).
# 2 agents, 12 items: first 2 have value 10t, rest have value t. Weights (2, 3) ≡ (0.4, 0.6).
# Alloc=({0}, {1,...,11}).
# Goods: agent 0 gets 10 < PROP_0=12. Chores: agent 1 gets −20 < PROP_1=−18.
for t, witness, label in [(1, 0, 'goods'), (-1, 1, 'chores')]:
    v = AdditiveValuation([10*t, 10*t] + [t] * 10)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:gaps-not-propx-n2:' + label,
        instance   = Instance([v, v], weights=[2, 3]),
        allocation = Allocation(bundles=[{0}, set(range(1, 12))]),
        witness    = witness,
        satisfies  = 'GAPS',
        violates   = 'PROPx',
    ))

# cex:ef1-not-efx-mixed-ue: not appended — EFX for mixed manna is not yet implemented in the checker.
# 2 agents, 5 items: v=[1,1,1,1,−1]. Weights (4, 1) ≡ (4/5, 1/5).
# Alloc=({1,2,3,4},{0}). Witness=1.
v = AdditiveValuation([1, 1, 1, 1, -1])
_cex_ef1_not_efx_mixed_ue = Counterexample(
    id         = 'cex:ef1-not-efx-mixed-ue',
    instance   = Instance([v, v], weights=[4, 1]),
    allocation = Allocation(bundles=[{1, 2, 3, 4}, {0}]),
    witness    = 1,
    satisfies  = 'EF1',
    violates   = 'EFX',
)
# COUNTEREXAMPLES.append(_cex_ef1_not_efx_mixed_ue)
# TODO: implement EFX for mixed manna

# WMMS and M1S are incompatible for chores.
# 2 agents, 2 chores: v=[−1,−1]. Weights (9, 1) ≡ (0.9, 0.1).
v = AdditiveValuation([-1, -1])

# MMS (=WMMS) does not imply M1S.
# WMMS alloc: ({0,1},∅). Agent 0 gets −2 but every EF1 gives them ≥−1. Witness=0.
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:wmms-plus-m1s-chores:mms-not-m1s',
    instance   = Instance([v, v], weights=[9, 1]),
    allocation = Allocation(bundles=[{0, 1}, set()]),
    witness    = 0,
    satisfies  = 'MMS',
    violates   = 'M1S',
))

# EFX (=M1S) does not imply MMS.
# EFX alloc: ({0},{1}). Agent 1 gets −1 < WMMS_1=−2/9. Witness=1.
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:wmms-plus-m1s-chores:efx-not-mms',
    instance   = Instance([v, v], weights=[9, 1]),
    allocation = Allocation(bundles=[{0}, {1}]),
    witness    = 1,
    satisfies  = 'EFX',
    violates   = 'MMS',
))

# GMMS does not imply PROP1 for goods with unequal entitlements.
# 3 agents, 7 unit goods. Weights (14, 5, 5) ≡ (7/12, 5/24, 5/24).
# GMMS/EFX/M1S allocations have cardinality (3,2,2).
# APS_0=4; agent 0 gets 3 < 4. Not PROP1. Witness=0.
v = AdditiveValuation([1] * 7)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:prop1-plus-m1s-ue',
    instance   = Instance([v] * 3, weights=[14, 5, 5]),
    allocation = Allocation(bundles=[{0, 1, 2}, {3, 4}, {5, 6}]),
    witness    = 0,
    satisfies  = 'GMMS',
    violates   = 'PROP1',
))

# GMMS does not imply PROP1 for chores with unequal entitlements.
# 3 agents, 7 unit chores. Weights (18, 7, 7) ≡ (9/16, 7/32, 7/32).
# GWMMS allocations have cardinality (5,1,1). APS_0=−4; agent 0 gets −5. Not PROP1. Witness=0.
v = AdditiveValuation([-1] * 7)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:gwmms-nimpl-prop1-m1s-ue-chores',
    instance   = Instance([v] * 3, weights=[18, 7, 7]),
    allocation = Allocation(bundles=[{0, 1, 2, 3, 4}, {5}, {6}]),
    witness    = 0,
    satisfies  = 'GMMS',
    violates   = 'PROP1',
))

# PROP does not imply M1S for chores with unequal entitlements.
# 3 agents, 7 chores. Weights (8, 3, 3) ≡ (4/7, 3/14, 3/14).
# v_0=[−1]*7. v_1=v_2=[−1,−1,−1,−1,−ε,−ε,−ε]. A_0={0,1,2,3}, A_1={4,5,6}, A_2=∅. Witness=0.
_v0_pnm = AdditiveValuation([-1] * 7)
_alloc_pnm = Allocation(bundles=[{0, 1, 2, 3}, {4, 5, 6}, set()])
_weights_pnm = [8, 3, 3]

# negBinary: ε=0 → v_1=v_2=[−1,−1,−1,−1,0,0,0]
_v12_negbin = AdditiveValuation([-1, -1, -1, -1, 0, 0, 0])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:prop-not-m1s-chores:negBinary',
    instance   = Instance([_v0_pnm, _v12_negbin, _v12_negbin], weights=_weights_pnm),
    allocation = _alloc_pnm,
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'M1S',
))

# negative-bival: ε=1/7 → v_1=v_2=[−1,−1,−1,−1,−1/7,−1/7,−1/7]
_v12_negbiv = AdditiveValuation([-1, -1, -1, -1, Fraction(-1, 7), Fraction(-1, 7), Fraction(-1, 7)])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:prop-not-m1s-chores:negative-bival',
    instance   = Instance([_v0_pnm, _v12_negbiv, _v12_negbiv], weights=_weights_pnm),
    allocation = _alloc_pnm,
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'M1S',
))

#-------------------------------------------------------------------------------
# Non-Additive Valuations
#-------------------------------------------------------------------------------

#=[ Unit-Demand Valuations ]====================================================

# PROP does not imply M1S (unit-demand).
# v over 3 goods: v[0]=v[1]=4, v[2]=3. vhat(X) = v(X) + 2ε|X|, so shift = 2ε.
# 2 agents, alloc=({0,1},{2}). Witness=1 (EF1-satisfaction fails in every M1S certificate).
# nonneg: ε=0, shift=0. positive: ε=1/12 (< 1/6), shift=1/6.
for shift, id_suffix in [(0, 'nonneg'), (Fraction(1, 8), 'positive')]:
    v = UnitDemandValuation([4, 4, 3], shift=shift)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:prop-not-m1s-unit-demand:' + id_suffix,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0, 1}, {2}]),
        witness    = 1,
        satisfies  = 'PROP',
        violates   = 'M1S',
    ))

# PROP1 does not imply PROPm (unit-demand).
# v over 2 goods: v[0]=30, v[1]=10. 2 agents, alloc=({0,1},∅). Witness=1.
# Agent 1 gets nothing. PROP1 holds (adding item 0 gives 30 > 15 = PROP).
# PROPm fails: min claimable gain from agent 0's bundle is v[1]=10, and 10 < 15 = PROP.
v = UnitDemandValuation([30, 10])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:ud:prop1-not-propm',
    instance   = Instance([v, v]),
    allocation = Allocation(bundles=[{0, 1}, set()]),
    witness    = 1,
    satisfies  = 'PROP1',
    violates   = 'PROPm',
))

# PROP does not imply PPROP (unit-demand).
# v over 3 goods: v[0]=30, v[1]=v[2]=11. 3 agents, alloc=({0},{1},{2}). Witness=1.
# All agents satisfy PROP (PROP share = 30/3 = 10; each gets ≥10).
# Agent 1 fails PPROP: in the 2-agent sub-instance with items {0,1}, agent 1 gets 11 < max(30,11)/2 = 15.
v = UnitDemandValuation([30, 11, 11])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:ud:prop-not-pprop',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0}, {1}, {2}]),
    witness    = 1,
    satisfies  = 'PROP',
    violates   = 'PPROP',
))

# MMS does not imply EF1 or PROPm (unit-demand).
# v over 5 goods: v[0]=200, v[1]=30, v[2]=v[3]=v[4]=10. 4 agents. MMS=10.
# Alloc=({0,1},{2},{3},{4}). Witness=1: gets 10, EF1-envies agent 0 (max(200,30)∖one item = 30 > 10).
# PROPm also fails: PROP=200/4=50; min claimable gain from agent 0's bundle = 20 < 50.
v = UnitDemandValuation([200, 30, 10, 10, 10])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:ud:mms-not-ef1-propm',
    instance   = Instance([v] * 4),
    allocation = Allocation(bundles=[{0, 1}, {2}, {3}, {4}]),
    witness    = 1,
    satisfies  = 'MMS',
    violates   = 'EF1|PROPm',
))

# PROPm does not imply PROPavg (unit-demand).
# v over 3 goods: v[0]=75, v[1]=30, v[2]=10. 3 agents. PROP share = 75/3 = 25.
# Alloc=({0,2},{1},∅). Witness=2.
# PROPm: T=[min(75,10), 30]=[10,30]; max(T)=30 > 25. PROPm holds.
# PROPavg: avg(T)=20 < 25. PROPavg fails.
v = UnitDemandValuation([75, 30, 10])
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:ud:propm-not-propavg',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0, 2}, {1}, set()]),
    witness    = 2,
    satisfies  = 'PROPm',
    violates   = 'PROPavg',
))

#=[ PMRF Valuations (Partition Matroid Rank Functions) ]========================
# PmrfValuation(colors, default_cap=1, shift=ε) implements PMRF_{+ε}(P),
# where P is the partition induced by the color labels.
# Marginals are in {ε, 1+ε}: binary when ε=0, positive-bival when ε>0.

# EF does not imply MMS (PMRF).
# P = ({r1,r2}, {g1,g2}): items r1=0,r2=1,g1=2,g2=3, colors=[0,0,1,1].
# Allocation = P itself = ({0,1},{2,3}). Each bundle has 1 color → PMRF=1+2ε. EF holds.
# MMS: partition ({0,2},{1,3}) gives PMRF=2+2ε each. Witness=0 (1+2ε < 2+2ε).
for shift, id_suffix in [(0, 'binary'), (1, 'positive-bival')]:
    v = PmrfValuation([0, 0, 1, 1], default_cap=1, shift=shift)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:ef-not-mms-pmrf:' + id_suffix,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0, 1}, {2, 3}]),
        witness    = 0,
        satisfies  = 'EF',
        violates   = 'MMS',
    ))

# EF1 does not imply MXS (PMRF).
# P = ({r1,r2},{g1,g2},{b}): items r1=0,r2=1,g1=2,g2=3,b=4. colors=[0,0,1,1,2]. ε=0.
# A = ({0,1},{2,3,4}). Agent 0: PMRF=1. Agent 1: PMRF=2.
# EF1 ✓: remove b(4) from A_1 → {2,3}: PMRF=1 = agent 0. Witness=0 (MXS violated).
v = PmrfValuation([0, 0, 1, 1, 2], default_cap=1)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:ef1-not-mxs-pmrf',
    instance   = Instance([v, v]),
    allocation = Allocation(bundles=[{0, 1}, {2, 3, 4}]),
    witness    = 0,
    satisfies  = 'EF1',
    violates   = 'MXS',
))

# MEFS does not imply EF1 (PMRF).
# P = ({a},{b},{c},{d},{e1,e2},{f1,f2},{g1,g2}): 10 items, colors=[0,1,2,3,4,4,5,5,6,6].
# A = ({a,e1,f1,g1},{b,c,d,e2,f2,g2}) = ({0,4,6,8},{1,2,3,5,7,9}). shift=ε (0 ≤ ε ≤ 1/2).
# v(A_0)=4+4ε, v(A_1)=6+6ε. Witness=0: even removing best item from A_1 leaves 5+5ε > 4+4ε.
# MEFS cert B=({0,1,2,3},{4,5,6,7,8,9}): v(B_0)=4+4ε=v(A_0), v(B_1)=3+6ε < 4+4ε for ε<1/2.
for shift, id_suffix in [(0, 'binary'), (Fraction(1, 2), 'positive-bival')]:
    v = PmrfValuation([0, 1, 2, 3, 4, 4, 5, 5, 6, 6], default_cap=1, shift=shift)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:mefs-not-ef1-pmrf:' + id_suffix,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[{0, 4, 6, 8}, {1, 2, 3, 5, 7, 9}]),
        witness    = 0,
        satisfies  = 'MEFS',
        violates   = 'EF1',
    ))

# EEF does not imply EF1 or PPROP (PMRF).
# M = {a_j}_{j=1}^6 ∪ {b_j}_{j=1}^6 ∪ {c_j}_{j=1}^4 (16 items). shift=ε (0 ≤ ε < 1/6).
# Parts: {a_j,b_j} for j∈[6] (each pair is one color) and {c_j} for j∈[4] (singletons).
# a_j = j-1, b_j = j+5, c_j = j+11. Colors: a_j and b_j share color j-1; c_j has color j+5.
# A = ({a_j},{b_j},{c_j}) = ({0..5},{6..11},{12..15}).
# v(A_0)=v(A_1)=6+6ε, v(A_2)=4+4ε. Witness=2: not EF1 (4+4ε < 5+5ε after removal).
# EEF cert for agent 2: B_1={0,1,2,6,7,8}, B_2={3,4,5,9,10,11}. v(B_1)=v(B_2)=3+6ε < 4+4ε.
_colors_eef_pmrf = [0,1,2,3,4,5, 0,1,2,3,4,5, 6,7,8,9]
for shift, id_suffix in [(0, 'binary'), (Fraction(1, 12), 'positive-bival')]:
    v = PmrfValuation(_colors_eef_pmrf, default_cap=1, shift=shift)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:eef-not-ef1-pprop-pmrf:' + id_suffix,
        instance   = Instance([v] * 3),
        allocation = Allocation(bundles=[set(range(6)), set(range(6, 12)), set(range(12, 16))]),
        witness    = 2,
        satisfies  = 'EEF',
        violates   = 'EF1|PPROP',
    ))

# PROP does not imply M1S (uniform matroid rank function).
# v(X) = min(6, |X|): uniform matroid of rank 6 over 10 items. Binary marginals (ε=0).
# Implemented as PmrfValuation with one color (cap=6): all items same color, cap 6.
# A = ({0,...,3},{4,...,9}). v(A_0)=4, v(A_1)=6. PROP=min(6,10)/2=3. Both satisfy PROP.
# Witness=0: M1S certificate must give agent 0 value ≥ 4, but every EF1 allocation gives ≤ ...
v = PmrfValuation([0] * 10, caps={0: 6})
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:prop-not-m1s-uniform-matroid:binary',
    instance   = Instance([v, v]),
    allocation = Allocation(bundles=[set(range(4)), set(range(4, 10))]),
    witness    = 0,
    satisfies  = 'PROP',
    violates   = 'M1S',
))

#=[ Subadditive Valuations ]====================================================
# BinPackingValuation(sizes, cap, shift): v(S) = min_bins(S) + |S|*shift.
# ceil(|S|/k) = BinPackingValuation([1]*m, cap=k): each item has size 1, bin capacity k.
# Scaling: sizes and cap can be scaled by any positive integer (same results).

# GAPS does not imply PROP1 or EF1 (subadditive, 2 agents).
# v(S) = ceil(|S|/4) over 9 items. A = ({0,1,2},{3,...,8}). Witness=0.
# v(A_0)=1, v(A_1)=2, v(M)=3. PROP=3/2.
# PROP1 fails: v(A_0 ∪ {g}) = ceil(4/4) = 1 ≤ 3/2 for all g ∉ A_0.
# EF1 fails: v(A_1 ∖ {g}) = ceil(5/4) = 2 > v(A_0) = 1 for all g ∈ A_1.
v = BinPackingValuation([1] * 9, cap=4)
COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:gaps-not-ef1-prop1-subadd',
    instance   = Instance([v, v]),
    allocation = Allocation(bundles=[set(range(3)), set(range(3, 9))]),
    witness    = 0,
    satisfies  = 'GAPS',
    violates   = 'PROP1|EF1',
))

# GAPS+PPROP does not imply PROP1 (subadditive, 3 agents, binary and positive-bival).
# Items: sizes [1,1,3,3,3,3], cap=5 (equiv. [1/5,1/5,3/5,3/5,3/5,3/5], cap=1).
# A = ({0,1},{2,3},{4,5}). Witness=0.
# v(A_0)=1 (1+1=2≤5), v(A_1)=v(A_2)=2 (3+3=6>5). v(M)=4. PROP=4/3.
# PROP1: v(A_0 ∪ {g}) = 1 bin (1+1+3=5≤5) → marginal gain 0. 1 ≯ 4/3 for any g ∉ A_0.
for shift, id_suffix in [(0, 'binary'), (Fraction(1, 4), 'positive-bival')]:
    v = BinPackingValuation([1, 1, 3, 3, 3, 3], cap=5, shift=shift)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:gaps-not-prop1-subadd:' + id_suffix,
        instance   = Instance([v] * 3),
        allocation = Allocation(bundles=[{0, 1}, {2, 3}, {4, 5}]),
        witness    = 0,
        satisfies  = 'GAPS+PPROP',
        violates   = 'PROP1',
    ))

# PAPS+PPROP does not imply PROPm or M1S (subadditive, 3 agents, binary).
# Items: 7 of size 3, 21 of size 2, 21 of size 2 (scaled 5×: original sizes 0.6, 0.4, 0.4). Cap=5.
# A = ({0,...,6},{7,...,27},{28,...,48}). Witness=0 (agent 1 in paper).
# v(A_0)=7, v(A_1)=v(A_2)=11. v(M)=25. PROP=25/3.
# PROPm: min claimable gain from A_1 (of size 2, adding to A_0 of size 3) = 0. 7+0 ≯ 25/3. Fails.
# M1S: any EF1 certificate B has |B_0| ≤ 14, leaving ≥ 35 items for others → some bundle ≥ 9 bins,
#       and removing one item drops by at most 1 → still ≥ 8 > 7 = v(A_0). Not EF1. Contradiction.
# cex:paps-pprop-not-propm-binary-subadd: not appended — 49 items causes OOM in checker.
v = BinPackingValuation([3] * 7 + [2] * 42, cap=5)
_cex_paps_pprop_not_propm_binary_subadd = Counterexample(
    id         = 'cex:paps-pprop-not-propm-binary-subadd',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[set(range(7)), set(range(7, 28)), set(range(28, 49))]),
    witness    = 0,
    satisfies  = 'PAPS+PPROP',
    violates   = 'PROPm|M1S',
)
# COUNTEREXAMPLES.append(_cex_paps_pprop_not_propm_binary_subadd)
# TODO: can we speed this up?

# GMMS does not imply APS (subadditive, binary).
# 15 items, same partition as the additive GMMS example (sizes scaled by 96: cap=96).
# APS ≥ 2 (from 6 sets each of size 97/96, hence value 2), MMS = 1 (total > 3 × 96/96).
# Leximin allocation: same bundles as additive case → v(A_0)=2, v(A_1)=2, v(A_2)=1. Witness=2.
# cex:gmms-not-aps-binary-subadd: not appended — GMMS check over 15 items causes OOM/timeout.
_sizes_gmms_subadd = [65, 31, 31, 31, 23, 23, 23, 17, 11, 7, 7, 7, 5, 5, 5]
v = BinPackingValuation(_sizes_gmms_subadd, cap=96)
_cex_gmms_not_aps_binary_subadd = Counterexample(
    id         = 'cex:gmms-not-aps-binary-subadd',
    instance   = Instance([v] * 3),
    allocation = Allocation(bundles=[{0,8,9,10,11}, {1,2,3,14}, {4,5,6,7,12,13}]),
    witness    = 2,
    satisfies  = 'GMMS',
    violates   = 'APS',
)
# COUNTEREXAMPLES.append(_cex_gmms_not_aps_binary_subadd)
# TODO: Can we speed this up?

#=[ Supermodular Valuations ]===================================================
# cex:ef-not-prop-supmod
# f(x) = x*ε + max(0, x-k), giving supermodular v(S) = f(|S|).
# Marginals: ε for |S| < k, 1+ε for |S| >= k (non-decreasing → supermodular).
# Allocation: each of n agents gets 4 goods.  PROP = f(4n)/n = 4ε + (4n-k)/n * [k<4n].

# n=2, k=5: 8 items.  PROP = 3/2 + 4ε.  f(4)=4ε < PROP.  f(5)=5ε < PROP.
# No agent can be PROP1 or PROPm satisfied with ≤ 4 items; some agent always gets ≤ 4.
for eps, id_suffix in [(0, 'n2-binary'), (Fraction(1, 28), 'n2-positive-bival')]:
    vals = [eps * i + max(0, i - 5) for i in range(9)]
    v = IdenticalItemsValuation(vals)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:ef-not-prop-supmod:' + id_suffix,
        instance   = Instance([v, v]),
        allocation = Allocation(bundles=[set(range(4)), set(range(4, 8))]),
        witness    = 0,
        satisfies  = 'EF+GAPS',
        violates   = 'PROP1|PROPm',
    ))

# n=3, k=8: 12 items.  PROP = 4/3 + 4ε.  f(4)=4ε < PROP.
# A is pairwise PROP (f(8)-f(4)=0 for binary; 4ε for positive-bival → f(4)+4ε=8ε < 4/3).
# f(5)=5ε < PROP → not PROP1.  f(9)=1+9ε < PROP → not PROPx.
# If ε=0: v(A_j | A_i) = f(8)-f(4)=0 for all i≠j → PROPavg.
for eps, id_suffix, satisfies, violates in [
        (0,              'n3-binary',        'PPROP+PROPavg', 'PROP1|PROPx'),
        (Fraction(1,28), 'n3-positive-bival','PPROP',         'PROP1'),
]:
    vals = [eps * i + max(0, i - 8) for i in range(13)]
    v = IdenticalItemsValuation(vals)
    COUNTEREXAMPLES.append(Counterexample(
        id         = 'cex:ef-not-prop-supmod:' + id_suffix,
        instance   = Instance([v] * 3),
        allocation = Allocation(bundles=[set(range(4)), set(range(4, 8)), set(range(8, 12))]),
        witness    = 0,
        satisfies  = satisfies,
        violates   = violates,
    ))

# ──────────────────────────────────────────────────────────────────────────────
# Submodular general valuation
# cex:mms-not-aps-n2-submod:positive
# C = {{0,1,2},{0,4,5},{1,3,5},{2,3,4}} (0-indexed; paper uses 1-indexed)
# vhat(X) = v(X) + |X|*eps, where:
#   v(X) = 0 if X=∅; 2 if |X|=1; 4 if |X|=2; 6 if X∈C or |X|≥4; 5 if |X|=3, X∉C
# Marginals: 2+eps (|X|≤1), {1+eps,2+eps} (|X|=2), {eps,1+eps} (|X|=3), eps (|X|=4).
# Non-increasing → submodular.  MMS = 5+3eps (best partition splits C-set / non-C-set).
# APS = 6+3eps (dual: set x_S=1/4 for S∈C).  No APS allocation exists.
# Allocation: A_0={0,1,2} (∈C, value 6+3eps), A_1={3,4,5} (∉C, value 5+3eps=MMS). Witness=1.
_C_submod = {frozenset({0,1,2}), frozenset({0,4,5}), frozenset({1,3,5}), frozenset({2,3,4})}
_eps_submod = Fraction(1, 4)

def _v_submod(X: Set[int]) -> Rational:
    s = frozenset(X)
    n = len(s)
    base = _eps_submod * n
    if n == 0: return 0
    if n == 1: return 2 + base
    if n == 2: return 4 + base
    if s in _C_submod or n >= 4: return 6 + base
    return 5 + base

COUNTEREXAMPLES.append(Counterexample(
    id         = 'cex:mms-not-aps-n2-submod:positive',
    instance   = Instance([GeneralValuation(6, _v_submod)] * 2),
    allocation = Allocation(bundles=[{0, 1, 2}, {3, 4, 5}]),
    witness    = 1,
    satisfies  = 'MMS',
    violates   = 'APS',
))
