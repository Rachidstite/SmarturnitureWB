from shared.issues import GeometryIssue
from shared.enums import Domain

class PanelSpecValidator:

    def validate(self, panel_specs):

        issues = []

        for spec in panel_specs:

            if spec.width <= 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "WIDTH_INVALID",
                        f"{spec.identity}: width must be > 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if spec.height <= 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "HEIGHT_INVALID",
                        f"{spec.identity}: height must be > 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if spec.thickness <= 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "THICKNESS_INVALID",
                        f"{spec.identity}: thickness must be > 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if not spec.material:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "MATERIAL_MISSING",
                        f"{spec.identity}: material missing",
                        domain=Domain.MANUFACTURING
                    )
                )

        return issues
