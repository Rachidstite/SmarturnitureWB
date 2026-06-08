from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class HangingCabinetLoadRule:

    def validate(
        self,
        cabinet,
    ):

        if getattr(
            cabinet,
            "cabinet_type",
            "",
        ) != "wall_cabinet":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_WALL_CABINET",
                message="Not a wall cabinet",
            )

        width = getattr(
            cabinet,
            "width",
            0,
        )

        mounting_points = getattr(
            cabinet,
            "mounting_points",
            2,
        )

        if (
            width >= 1500
            and mounting_points <= 2
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="HANGING_CABINET_LOAD",
                message="Wall cabinet requires additional mounting support",
            )

        if (
            width >= 1100
            and mounting_points <= 2
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="HANGING_CABINET_LOAD",
                message="Consider additional mounting points",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Wall cabinet load acceptable",
        )
