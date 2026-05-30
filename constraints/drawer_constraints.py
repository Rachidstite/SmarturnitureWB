from .base_constraint import BaseConstraint
from shared.resolved_types import ResolvedSection; from shared.issues import ConstraintResult, GeometryIssue; from shared.enums import Domain
class DrawerDepthConstraint(BaseConstraint):
    def check(self, section: ResolvedSection, mat) -> ConstraintResult:
        issues = [GeometryIssue("ERROR", "DRAWER_DEPTH_INVALID", f"Drawer {i+1}: box depth ({d.box_d:.1f}mm) < 100mm.", domain=Domain.CONSTRAINT) for i, d in enumerate(section.drawers) if d.box_d < 100]
        return ConstraintResult(valid=len(issues)==0, issues=issues)
class DrawerWidthConstraint(BaseConstraint):
    def check(self, section: ResolvedSection, mat) -> ConstraintResult:
        if section.drawers and section.drawer_box_width < 200: return ConstraintResult(valid=False, issues=[GeometryIssue("ERROR", "DRAWER_TOO_NARROW", f"Drawer box width ({section.drawer_box_width:.1f}mm) is very narrow.", domain=Domain.CONSTRAINT)])
        return ConstraintResult(valid=True)
