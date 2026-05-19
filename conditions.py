"""
Checks whether a fair division instance satisfies the conditions
specified in a JSON conditions dict (from setFamily.json).

Each key in the conditions dict is optional; absent keys impose no constraint.
Possible keys:
    valuation  str   valuation function type (e.g. 'additive', 'submod')
    marginal   str   marginal value type (e.g. 'nonneg', 'binary')
    identical  bool  all agents share the same valuation object
    twoAg      bool  exactly 2 agents
    eqEnt      bool  all agents have equal entitlements
"""

from __future__ import annotations

from typing import TypedDict

from valuation import Valuation, AdditiveValuation
from instance import Instance


class Conditions(TypedDict, total=False):
    valuation: str
    marginal: str
    identical: bool
    twoAg: bool
    eqEnt: bool


def _satisfies_marginal_type(v: Valuation, mtype: str) -> bool:
    """Return True iff valuation v satisfies the given marginal type."""
    has_neg, has_zero, has_pos = v.signs()
    min_val, max_val = v.marginal_range()

    match mtype:
        case 'general':
            return True

        case 'dblMono':
            # Goods have non-negative marginals, chores have non-positive marginals.
            # For additive valuations this is always true: partition items into
            # goods (value >= 0) and chores (value <= 0).
            if isinstance(v, AdditiveValuation):
                return True
            raise NotImplementedError(
                f"dblMono check not implemented for {type(v).__name__}")

        case 'dblStrMono':
            # Like dblMono but strictly positive for goods and strictly negative
            # for chores. For additive: equivalent to no item having value 0.
            if isinstance(v, AdditiveValuation):
                return not has_zero
            raise NotImplementedError(
                f"dblStrMono check not implemented for {type(v).__name__}")

        case 'nonneg':
            return not has_neg
        case 'nonpos':
            return not has_pos
        case 'positive':
            return has_pos and not has_neg and not has_zero
        case 'negative':
            return has_neg and not has_pos and not has_zero

        case 'nonnegBival':
            return not has_neg and v.is_k_val(2)
        case 'positiveBival':
            return has_pos and not has_neg and not has_zero and v.is_k_val(2)
        case 'nonposBival':
            return not has_pos and v.is_k_val(2)
        case 'negativeBival':
            return has_neg and not has_pos and not has_zero and v.is_k_val(2)
        case 'mixedBival':
            return has_neg and has_pos and v.is_k_val(2)
        case 'mixedBivalDblStrMono':
            if isinstance(v, AdditiveValuation):
                return has_neg and has_pos and not has_zero and v.is_k_val(2)
            raise NotImplementedError(
                f"mixedBivalDblStrMono check not implemented for {type(v).__name__}")

        case 'tribool':
            # All marginal values must lie in {-1, 0, 1}.
            # For <= 2 distinct values: checking min and max are in {-1, 0, 1} suffices.
            # For exactly 3 distinct values: we additionally need min == -1, max == 1,
            # and has_zero (forcing the three values to be exactly {-1, 0, 1}).
            if v.is_k_val(2):
                return min_val in (-1, 0, 1) and max_val in (-1, 0, 1)
            else:
                return v.is_k_val(3) and min_val == -1 and max_val == 1 and has_zero

        case 'binary':
            # All marginal values in {0, 1}.
            return (not has_neg
                    and min_val in (0, 1) and max_val in (0, 1)
                    and v.is_k_val(2))
        case 'negBinary':
            # All marginal values in {-1, 0}.
            return (not has_pos
                    and min_val in (-1, 0) and max_val in (-1, 0)
                    and v.is_k_val(2))
        case 'pm1':
            # All marginal values in {-1, 1}.
            return (not has_zero
                    and min_val in (-1, 1) and max_val in (-1, 1)
                    and v.is_k_val(2))
        case 'unit':
            # All marginal values equal 1.
            return v.is_k_val(1) and max_val == 1
        case 'negUnit':
            # All marginal values equal -1.
            return v.is_k_val(1) and min_val == -1

        case _:
            raise ValueError(f"Unknown marginal type: {mtype!r}")


def verify_conditions(instance: Instance, conditions: Conditions) -> list[str]:
    """
    Check that `instance` satisfies all conditions in `conditions`.
    Returns a list of error descriptions; an empty list means all pass.
    """
    errors = []

    if 'valuation' in conditions:
        expected = conditions['valuation']
        failing = [i for i, v in enumerate(instance.valuations)
                   if expected not in v.func_types()]
        if failing:
            errors.append(
                f"valuation '{expected}': not satisfied by agent(s) {failing}")

    if 'marginal' in conditions:
        expected = conditions['marginal']
        failing = [i for i, v in enumerate(instance.valuations)
                   if not _satisfies_marginal_type(v, expected)]
        if failing:
            errors.append(
                f"marginal '{expected}': not satisfied by agent(s) {failing}")

    if conditions.get('identical') and not instance.has_identical_valuations():
        errors.append(
            "'identical': agents do not share the same valuation object")

    if conditions.get('twoAg') and instance.n_agents() != 2:
        errors.append(
            f"'twoAg': expected 2 agents, got {instance.n_agents()}")

    if conditions.get('eqEnt') and not instance.has_equal_entitlements():
        errors.append(
            f"'eqEnt': weights are not equal: {instance.weights}")

    return errors
