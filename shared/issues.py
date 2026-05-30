from dataclasses import dataclass, field
from .enums import Domain
@dataclass(frozen=True)
class ConstraintResult: valid: bool; issues: list = field(default_factory=list); warnings: list = field(default_factory=list); metadata: dict = field(default_factory=dict)
@dataclass(frozen=True)
class GeometryIssue: level: str; code: str; message: str; section_index: int = -1; component: str = ""; domain: Domain = Domain.GENERAL
@dataclass
class ValidationState:
    issues: list = field(default_factory=list)
    @property
    def has_errors(self): return any(i.level == "ERROR" for i in self.issues)
    @property
    def has_warnings(self): return any(i.level == "WARNING" for i in self.issues)
    def by_domain(self, domain: Domain): return [i for i in self.issues if i.domain == domain]
