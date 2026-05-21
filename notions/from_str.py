"""
Parse a fairness notion string into an AgentCheck function.

Supported syntax:
  'APS'       – single notion (dict lookup)
  'EFX|MMS'   – disjunction: at least one must hold
  'EFX+MMS'   – conjunction: all must hold

Mixing '|' and '+' in the same string raises NotImplementedError.
Whitespace around notion names is ignored.
"""

from __future__ import annotations

from instance import Instance
from allocation import Allocation

from notions.utils import AgentCheck, and_notions, or_notions
from notions.basic import is_ef_to, is_prop_to, is_mms_to
from notions.aps import is_aps_to
from notions.up_to_one import is_ef1_to, is_prop1_to
from notions.up_to_any import is_efx_to, is_propx_to, is_propm_to, is_propavg_to


NOTIONS: dict[str, AgentCheck] = {
    'EF':      is_ef_to,
    'EF1':     is_ef1_to,
    'EFX':     is_efx_to,
    'PROP':    is_prop_to,
    'PROP1':   is_prop1_to,
    'PROPx':   is_propx_to,
    'PROPm':   is_propm_to,
    'PROPavg': is_propavg_to,
    'MMS':     is_mms_to,
    'APS':     is_aps_to,
}


def notion_from_str(s: str) -> AgentCheck:
    """Return the AgentCheck corresponding to the notion string s."""
    has_and = '+' in s
    has_or  = '|' in s
    if has_and and has_or:
        raise NotImplementedError(f"Notion {s!r} mixes '+' and '|'; use separate checks instead")
    if has_and:
        return and_notions(notion_from_str(t.strip()) for t in s.split('+'))
    if has_or:
        return or_notions(notion_from_str(t.strip()) for t in s.split('|'))
    name = s.strip()
    if name not in NOTIONS:
        raise ValueError(f"Unknown fairness notion: {name!r}")
    return NOTIONS[name]


def is_fair_to(instance: Instance, allocation: Allocation, agent: int, notion: str) -> bool:
    """Check whether `allocation` satisfies `notion` for `agent`."""
    check = notion_from_str(notion)
    return check(instance, allocation, agent)


def is_fair(instance: Instance, allocation: Allocation, notion: str) -> bool:
    """Check whether `allocation` satisfies `notion` for every agent."""
    check = notion_from_str(notion)
    return all(check(instance, allocation, i) for i in range(instance.n_agents()))
