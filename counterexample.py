"""
Counterexample for a non-implication between fairness notions.
"""

from __future__ import annotations

from dataclasses import dataclass

from instance import Instance
from allocation import Allocation
from notions.from_str import is_fair, is_fair_to


@dataclass
class Counterexample:
    id:         str
    instance:   Instance
    allocation: Allocation
    witness:    int   # agent who witnesses the violation of `violates`
    satisfies:  str   # fairness notion the allocation satisfies for all agents
    violates:   str   # fairness notion that `witness` does not satisfy

    def verify(self) -> list[str]:
        """
        Check that this is a valid counterexample.

        Returns a list of error descriptions; an empty list means all checks pass.
        """
        errors = []
        if not is_fair(self.instance, self.allocation, self.satisfies):
            errors.append(
                f"allocation does not satisfy '{self.satisfies}' for all agents")
        if is_fair_to(self.instance, self.allocation, self.witness, self.violates):
            errors.append(
                f"agent {self.witness} satisfies '{self.violates}' (expected violation)")
        return errors
