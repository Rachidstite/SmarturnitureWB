from .base_constraint import BaseConstraint
from shared.resolved_types import ResolvedSection; from shared.issues import ConstraintResult, GeometryIssue; from shared.enums import Domain
class DoorCollisionConstraint(BaseConstraint):
    def check(self, section: ResolvedSection, mat) -> ConstraintResult:
        issues = []

        for i, d in enumerate(section.doors):

            if d.width > section.door_width + 40:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "DOOR_COLLISION",
                        f"Door {i+1}: width ({d.width:.1f}mm) exceeds opening ({section.door_width:.1f}mm).",
                        domain=Domain.CONSTRAINT
                    )
                )
        return ConstraintResult(valid=len(issues)==0, issues=issues)
