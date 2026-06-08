from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class CabinetOverturnRiskRule:

    def validate(
        self,
        cabinet,
    ):

        height = getattr(
            cabinet,
            "cabinet_height",
            0,
        )

        depth = getattr(
            cabinet,
            "cabinet_depth",
            0,
        )

        if (
            height >= 3200
            and depth <= 350
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="CABINET_OVERTURN_RISK",
                message="Cabinet has severe overturn risk",
            )

        if (
            height >= 2800
            and depth <= 450
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="CABINET_OVERTURN_RISK",
                message="Cabinet may require wall anchoring",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Cabinet stability acceptable",
        )
