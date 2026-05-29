"""
APS (Any Price Share) fairness notion.

APS_i is defined via the dual LP (Babaioff, Nisan, Talgam-Cohen):
    the largest z such that there exists x ∈ R_{≥0}^{S_z} with
        Σ_{S ∈ S_z}       x_S = 1
        Σ_{S ∈ S_z: j∈S}  x_S = w_i / W    for all items j
    where S_z = {S ⊆ [m] : v_i(S) ≥ z} and W = Σ_k w_k.

APS-fairness for agent i under allocation A is checked with a single LP solve:
let r = v_i(A_i) and s = min{v_i(S) : v_i(S) > r} (the smallest bundle value
strictly above r, or ∞ if none exists).  Since APS_i equals some bundle value,
APS_i ≥ s  iff  LP(s) is feasible, and APS_i < s  iff  APS_i ≤ r (fair).
Values in counterexample instances are small integers or simple fractions,
so floating-point errors are negligible.
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from collections.abc import Sequence

import numpy as np
from scipy.optimize import linprog

from valuation import Valuation, Rational
from .utils import all_subsets
from instance import Instance
from allocation import Allocation




def _lp_feasible(sz: list[frozenset[int]], m: int, budget: float) -> bool:
    """
    Return True iff there exists x ≥ 0 indexed by sz satisfying:
        Σ_S x_S = 1
        Σ_{S: j∈S} x_S = budget    for each item j in 0..m-1
    """
    k = len(sz)
    if k == 0:
        return False

    # A_eq @ x = b_eq:  row 0 is the normalisation constraint;
    # rows 1..m are the per-item coverage constraints.
    A = np.zeros((m + 1, k))
    b = np.zeros(m + 1)
    A[0, :] = 1.0
    b[0] = 1.0
    for j in range(m):
        for idx, S in enumerate(sz):
            if j in S:
                A[j + 1, idx] = 1.0
        b[j + 1] = budget

    res = linprog(np.zeros(k), A_eq=A, b_eq=b,
                  bounds=[(0.0, None)] * k, method='highs')
    return res.status == 0


def aps_ge(v: Valuation, b: Rational | float, z: Rational, subsets: Sequence[frozenset[int]] | None = None) -> bool:
    """Return True iff APS(v, b) ≥ z.

    v is the agent's valuation, b = w_i / W is the agent's normalized weight,
    and z is the threshold value to test against.

    `subsets` captures the family of allowed bundles. Defaults to all subsets of items.
    """
    m = v.n_items()
    sz = [S for S in (all_subsets(m) if subsets is None else subsets) if v(S) >= z]
    return _lp_feasible(sz, m, float(b))


def aps(v: Valuation, b: Rational | float, subsets: Sequence[frozenset[int]] | None = None) -> Rational:
    """Returns APS(v, b).

    v is the agent's valuation, b = w_i / W is the agent's normalized weight,
    and z is the threshold value to test against.

    `subsets` captures the family of allowed bundles. Defaults to all subsets of items.
    """
    m = v.n_items()
    _subsets = all_subsets(m) if subsets is None else subsets
    all_values = sorted({v(S) for S in _subsets}, reverse=True)
    # TODO: speed this up by using binary search instead
    for z in all_values:
        if aps_ge(v, b, z, _subsets):
            return z
    raise ValueError(f"Could not compute APS")
    # the above error should never happen if subsets is None


def aps_instance(instance: Instance, i: int) -> Rational:
    v, w = instance.valuations[i], instance.weights
    b = Fraction(w[i], sum(w))
    return aps(v, b)


def is_aps_to(instance: Instance, allocation: Allocation, i: int) -> bool:
    """
    Return True iff agent i is APS-fair under the given allocation.

    Let r = v_i(A_i) and s = min{v_i(S) : v_i(S) > r}.
    Because APS_i is always the value of some bundle:
      - LP(s) feasible  ⟺  APS_i ≥ s  ⟺  APS_i > r  (not fair)
      - LP(s) infeasible ⟺  APS_i < s  ⟺  APS_i ≤ r  (fair)
    If no bundle has value > r then APS_i ≤ r trivially.
    """
    v, w = instance.valuations[i], instance.weights
    b = Fraction(w[i], sum(w))

    r = v(allocation.bundle(i))
    subsets = all_subsets(v.n_items())
    above = [v(S) for S in subsets if v(S) > r]
    if not above:
        return True   # r is already the maximum possible value

    s = min(above)
    return not aps_ge(v, b, s, subsets)
