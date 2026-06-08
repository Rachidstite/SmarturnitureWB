from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class TallDividerStabilityRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "divider":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_DIVIDER",
                message="Not a divider",
            )

        height = getattr(
            panel_spec,
            "height",
            0,
        )

        if height >= 2800:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="TALL_DIVIDER_STABILITY",
                message="Divider stability insufficient",
            )

        if height >= 2400:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="TALL_DIVIDER_STABILITY",
                message="Divider may require reinforcement",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Divider stability acceptable",
        )
