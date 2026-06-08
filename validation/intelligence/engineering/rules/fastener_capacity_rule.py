from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class FastenerCapacityRule:

    def validate(
        self,
        joint,
    ):

        load = getattr(
            joint,
            "load",
            0,
        )

        fasteners = getattr(
            joint,
            "fastener_count",
            0,
        )

        if load >= 120 and fasteners < 4:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="FASTENER_CAPACITY_ERROR",
                message="Joint requires additional fasteners",
            )

        if load >= 70 and fasteners < 3:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="FASTENER_CAPACITY_WARNING",
                message="Consider additional fasteners",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="FASTENER_OK",
            message="Fastener capacity acceptable",
        )
