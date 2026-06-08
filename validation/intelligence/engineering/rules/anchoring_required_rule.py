from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class AnchoringRequiredRule:

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
            height >= 3000
            and depth <= 400
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="ANCHOR_REQUIRED",
                message="Tall cabinet must be mechanically anchored to wall",
            )

        if (
            height >= 2500
            and depth <= 500
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="ANCHOR_RECOMMENDED",
                message="Wall anchoring strongly recommended",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="ANCHOR_OK",
            message="Cabinet stability acceptable",
        )
