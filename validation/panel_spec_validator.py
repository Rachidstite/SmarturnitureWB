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

            
            for op in getattr(spec, "cnc_operations", []):

                if hasattr(op, "diameter") and op.diameter <= 0:
                    issues.append(
                        GeometryIssue(
                            "ERROR",
                            "DRILL_DIAMETER_INVALID",
                            f"{spec.identity}: drill diameter must be > 0",
                            domain=Domain.CNC
                        )
                    )

                if hasattr(op, "depth") and op.depth <= 0:
                    issues.append(
                        GeometryIssue(
                            "ERROR",
                            "DRILL_DEPTH_INVALID",
                            f"{spec.identity}: drill depth must be > 0",
                            domain=Domain.CNC
                        )
                    )

                if hasattr(op, "x"):


                    if op.x < 0 or op.x > spec.width:
                        issues.append(
                            GeometryIssue(
                                "ERROR",
                                "DRILL_OUT_OF_BOUNDS",
                                f"{spec.identity}: drill X outside panel",
                                domain=Domain.CNC
                            )
                        )

                if hasattr(op, "y"):

                    if op.y < 0 or op.y > spec.height:
                        issues.append(
                            GeometryIssue(
                                "ERROR",
                                "DRILL_OUT_OF_BOUNDS",
                                f"{spec.identity}: drill Y outside panel",
                                domain=Domain.CNC
                            )
                        )

                if hasattr(op, "z"):

                    if op.z < 0 or op.z > spec.thickness:
                        issues.append(
                            GeometryIssue(
                                "ERROR",
                                "DRILL_OUT_OF_BOUNDS",
                                f"{spec.identity}: drill Z outside panel",
                                domain=Domain.CNC
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
