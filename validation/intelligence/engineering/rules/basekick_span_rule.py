from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class BaseKickSpanRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "basekick":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_BASEKICK",
                message="Not a basekick",
            )

        span = getattr(
            panel_spec,
            "span",
            0,
        )

        if span >= 1800:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="BASEKICK_SPAN",
                message="Basekick requires additional support",
            )

        if span >= 1400:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="BASEKICK_SPAN",
                message="Basekick may require support",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Basekick span acceptable",
        )
