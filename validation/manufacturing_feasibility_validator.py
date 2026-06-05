from shared.issues import GeometryIssue
from shared.enums import Domain


class ManufacturingFeasibilityValidator:

    def validate(self, panel_specs):

        issues = []

        for spec in panel_specs:

            for op in getattr(spec, "cnc_operations", []):

                if (
                    hasattr(op, "z")
                    and getattr(op, "diameter", None) == 8
                    and getattr(op, "depth", None) == 30
                    and op.x >= 64
                    and spec.width < 64
                ):
                    issues.append(
                        GeometryIssue(
                            "ERROR",
                            "PANEL_TOO_SMALL_FOR_MINIFIX",
                            f"{spec.identity}: panel too small for minifix hardware",
                            domain=Domain.MANUFACTURING
                        )
                    )

        return issues
