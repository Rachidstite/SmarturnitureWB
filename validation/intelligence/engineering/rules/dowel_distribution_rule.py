from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DowelDistributionRule:

    def validate(
        self,
        joint,
    ):

        length = getattr(
            joint,
            "joint_length",
            0,
        )

        dowels = getattr(
            joint,
            "dowel_count",
            0,
        )

        if length >= 1400 and dowels < 4:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DOWEL_DISTRIBUTION_ERROR",
                message="Joint requires additional dowels",
            )

        if length >= 700 and dowels < 3:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DOWEL_DISTRIBUTION_WARNING",
                message="Consider additional dowels",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="DOWEL_OK",
            message="Dowel distribution acceptable",
        )
