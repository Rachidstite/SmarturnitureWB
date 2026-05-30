from .base_constraint import BaseConstraint
from shared.resolved_types import ResolvedSection; from shared.issues import ConstraintResult, GeometryIssue; from shared.enums import Domain
class ShelfSaggingConstraint(BaseConstraint):
    def check(self, section: ResolvedSection, mat) -> ConstraintResult:
        issues = [GeometryIssue("WARNING", "SHELF_SAGGING", f"Shelf {i+1}: width ({s.width:.1f}mm) > 900mm.", domain=Domain.CONSTRAINT) for i, s in enumerate(section.shelves) if s.width > 900]
        return ConstraintResult(valid=len(issues)==0, issues=issues)
