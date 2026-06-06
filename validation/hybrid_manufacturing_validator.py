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

        for op in operations:

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

        return issues
