from abc import ABC, abstractmethod
from shared.resolved_types import ResolvedSection; from shared.issues import ConstraintResult
class BaseConstraint(ABC):
    @abstractmethod
    def check(self, section: ResolvedSection, mat) -> ConstraintResult: pass
