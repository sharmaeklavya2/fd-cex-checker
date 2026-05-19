"""
Counterexample for a non-implication between fairness notions.
"""

from __future__ import annotations

from dataclasses import dataclass

from instance import Instance
from allocation import Allocation
from notions import is_fair, is_fair_to


@dataclass
class Counterexample:
    id: str
    instance: Instance
    allocation: Allocation
    witness: int  # agent who witnesses the violation of `violates`

    def verify(self, satisfies: str, violates: str) -> list[str]:
        """
        Check that this is a valid counterexample for satisfies ⊄ violates.

        Returns a list of error descriptions; an empty list means all checks pass.
        """
        errors = []
        if not is_fair(self.instance, self.allocation, satisfies):
            errors.append(
                f"allocation does not satisfy '{satisfies}'")
        if is_fair_to(self.instance, self.allocation, self.witness, violates):
            errors.append(
                f"agent {self.witness} satisfies '{violates}' (expected violation)")
        return errors
