"""
Fairness notions for fair division.
"""

from __future__ import annotations

from typing import Callable

from instance import Instance
from allocation import Allocation
from notions.basic import is_ef_to, is_prop_to, is_mms_to
from notions.aps import is_aps_to
from notions.up_to_one import is_ef1_to, is_prop1_to
from notions.up_to_any import is_efx_to, is_propx_to, is_propm_to, is_propavg_to

# Type alias for per-agent fairness checks.
AgentCheck = Callable[[Instance, Allocation, int], bool]

NOTIONS: dict[str, AgentCheck] = {
    'EF':   is_ef_to,
    'EF1':  is_ef1_to,
    'EFX':  is_efx_to,
    'PROP': is_prop_to,
    'PROP1': is_prop1_to,
    'PROPx': is_propx_to,
    'PROPm': is_propm_to,
    'PROPavg': is_propavg_to,
    'MMS':  is_mms_to,
    'APS':  is_aps_to,
}


def is_fair_to(instance: Instance, allocation: Allocation, agent: int, notion: str) -> bool:
    """
    Return True iff `allocation` satisfies `notion` for `agent`.

    Composite notions:
      'F1+F2'  – conjunction: both F1 and F2 must hold.
      'F1|F2'  – disjunction: at least one of F1 or F2 must hold.
    Mixing '+' and '|' in the same string is not supported.
    Whitespace around notion names is ignored.
    """
    has_and = '+' in notion
    has_or  = '|' in notion
    if has_and and has_or:
        raise ValueError(
            f"Notion {notion!r} mixes '+' and '|'; use separate checks instead")
    if has_and:
        return all(is_fair_to(instance, allocation, agent, n.strip())
                   for n in notion.split('+'))
    if has_or:
        return any(is_fair_to(instance, allocation, agent, n.strip())
                   for n in notion.split('|'))
    check = NOTIONS.get(notion.strip())
    if check is None:
        raise ValueError(f"Unknown fairness notion: {notion.strip()!r}")
    return check(instance, allocation, agent)


def is_fair(instance: Instance, allocation: Allocation, notion: str) -> bool:
    """
    Return True iff `allocation` satisfies `notion` for every agent.

    Supports the same composite notion syntax as `is_fair_to`.
    """
    return all(is_fair_to(instance, allocation, i, notion)
               for i in range(instance.n_agents()))
