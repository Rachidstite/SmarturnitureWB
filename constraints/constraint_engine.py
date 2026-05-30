from shared.resolved_types import ResolvedSection; from shared.issues import GeometryIssue; from shared.enums import Domain
from .drawer_constraints import DrawerDepthConstraint, DrawerWidthConstraint; from .door_constraints import DoorCollisionConstraint; from .shelf_constraints import ShelfSaggingConstraint
class ConstraintEngine:
    def __init__(self): self.constraints = [DrawerDepthConstraint(), DrawerWidthConstraint(), DoorCollisionConstraint(), ShelfSaggingConstraint()]
    def validate(self, resolved_sections: list, mat) -> list:
        issues = []
        for i, section in enumerate(resolved_sections):
            for constraint in self.constraints:
                result = constraint.check(section, mat)
                for issue in result.issues:
                    if hasattr(issue, 'section_index'): issue = GeometryIssue(issue.level, issue.code, issue.message, i, domain=issue.domain)
                    issues.append(issue)
        return issues
