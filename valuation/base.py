from abc import ABC, abstractmethod
from fractions import Fraction
from collections.abc import Set

Rational = int | Fraction

SUBMOD_FTYPES = frozenset({'submod', 'xos', 'subadd', 'general'})
ADD_FTYPES = SUBMOD_FTYPES | frozenset({'additive', 'cancelable', 'submodCanc', 'supermod', 'superadd'})
SI_FTYPES = ADD_FTYPES | frozenset({'unitDemand', 'singleItem'})

class Valuation(ABC):
    """Abstract base class for valuation functions over sets of items."""

    @abstractmethod
    def n_items(self) -> int:
        """Number of items in the ground set."""
        ...

    @abstractmethod
    def value(self, subset: Set[int]) -> Rational:
        """Value of an item or a set of items."""
        ...

    def __call__(self, subset: Set[int]) -> Rational:
        return self.value(subset)

    def marginal_gain(self, X: Set[int], S: Set[int]) -> Rational:
        """Marginal gain of adding `X` to `S`. v(X given S). X and S must be disjoint."""
        assert S.isdisjoint(X)
        return self.value(S | X) - self.value(S)

    def marginal_loss(self, X: Set[int], S: Set[int]) -> Rational:
        """Marginal loss of removing `X` from `S`. V(X given S-X). X must be a subset of S."""
        assert X <= S
        return self.value(S) - self.value(S - X)

    @abstractmethod
    def func_types(self) -> frozenset[str]:
        """
        The set of function-type labels that apply to this valuation.
        Returns the same frozenset object on every call.
        """
        ...

    @abstractmethod
    def signs(self) -> tuple[bool, bool, bool]:
        """
        Returns (has_neg, has_zero, has_pos): whether any marginal value is
        negative, zero, or positive respectively. Exact for this instance.
        """
        ...

    @abstractmethod
    def marginal_range(self) -> tuple[Rational, Rational]:
        """
        Returns (min_marginal, max_marginal): the minimum and maximum marginal
        values across all items and all subsets. Exact for this instance.
        """
        ...

    @abstractmethod
    def is_k_val(self, k: int) -> bool:
        """True iff there are at most k distinct marginal values."""
        ...
