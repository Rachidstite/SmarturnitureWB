from shared.issues import GeometryIssue
from shared.enums import Domain


class HybridManufacturingValidator:

    def validate(self, operations):

        issues = []

        SUPPORTED_AXES = {
            "X",
            "Y",
            "Z",
        }

        SUPPORTED_FACES = {
            "TOP",
            "BOTTOM",
            "LEFT",
            "RIGHT",
            "FRONT",
            "BACK",
        }

        face_drills = 0
        edge_drills = 0

        for op in operations:

            if op.operation_type == "FACE_DRILL":
                face_drills += 1

            if op.operation_type == "EDGE_DRILL":
                edge_drills += 1

            if not op.operation_type:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_TYPE_MISSING",
                        "operation type missing",
                        domain=Domain.MANUFACTURING
                    )
                )

            if not op.source:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_SOURCE_MISSING",
                        "operation source missing",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.axis not in SUPPORTED_AXES:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "INVALID_OPERATION_AXIS",
                        f"invalid axis: {op.axis}",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.face and op.face not in SUPPORTED_FACES:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "INVALID_OPERATION_FACE",
                        f"invalid face: {op.face}",
                        domain=Domain.MANUFACTURING
                    )
                )

            if (
                op.operation_type == "FACE_DRILL"
                and op.diameter != 15
            ):
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "INVALID_MINIFIX_FACE_DIAMETER",
                        "FACE_DRILL diameter must be 15mm",
                        domain=Domain.MANUFACTURING
                    )
                )

            if (
                op.operation_type == "EDGE_DRILL"
                and op.diameter != 8
            ):
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "INVALID_MINIFIX_EDGE_DIAMETER",
                        "EDGE_DRILL diameter must be 8mm",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.diameter < 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_DIAMETER_INVALID",
                        "diameter must be >= 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.depth < 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_DEPTH_INVALID",
                        "depth must be >= 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.x < 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_X_INVALID",
                        "x must be >= 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.y < 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_Y_INVALID",
                        "y must be >= 0",
                        domain=Domain.MANUFACTURING
                    )
                )

            if op.z < 0:
                issues.append(
                    GeometryIssue(
                        "ERROR",
                        "OPERATION_Z_INVALID",
                        "z must be >= 0",
                        domain=Domain.MANUFACTURING
                    )
                )

        if (
            face_drills > 0
            and edge_drills == 0
        ):
            issues.append(
                GeometryIssue(
                    "ERROR",
                    "INCOMPLETE_MINIFIX_SET",
                    "FACE_DRILL exists without EDGE_DRILL",
                    domain=Domain.MANUFACTURING
                )
            )

        return issues
