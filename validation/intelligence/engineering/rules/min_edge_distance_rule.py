from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class MinEdgeDistanceRule:

    def validate(
        self,
        joint,
    ):

        edge_distance = getattr(
            joint,
            "edge_distance",
            0,
        )

        if edge_distance >= 40:

            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="EDGE_OK",
                message="Edge distance acceptable",
            )

        if edge_distance >= 20:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="EDGE_WARNING",
                message="Edge distance is below recommended minimum",
            )

        return EngineeringResult(
            passed=False,
            level=EngineeringLevel.ERROR,
            code="EDGE_ERROR",
            message="Edge distance may cause MDF breakout",
        )
