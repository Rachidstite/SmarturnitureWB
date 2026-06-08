from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class CountertopSpanRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "countertop":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_COUNTERTOP",
                message="Not a countertop",
            )

        span = getattr(
            panel_spec,
            "span",
            0,
        )

        thickness = getattr(
            panel_spec,
            "thickness",
            0,
        )

        if (
            span >= 1800
            and thickness <= 36
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="COUNTERTOP_SPAN",
                message="Countertop requires intermediate support",
            )

        if (
            span >= 1400
            and thickness <= 36
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="COUNTERTOP_SPAN",
                message="Long countertop may require support",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Countertop span acceptable",
        )
