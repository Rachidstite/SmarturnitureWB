from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)

from validation.intelligence.engineering.engineering_rule import (
    EngineeringRule,
)


class DividerBucklingRule(
    EngineeringRule
):

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            ""
        ) != "divider":
            return None

        height = getattr(
            panel_spec,
            "height",
            0
        )

        section_width = getattr(
            panel_spec,
            "section_width",
            0
        )

        thickness = getattr(
            panel_spec,
            "thickness",
            18
        )

        # MDF 18 mm baseline

        if (
            thickness <= 18
            and height > 2600
            and section_width > 700
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DIVIDER_BUCKLING",
                message="Divider has high buckling risk",
            )

        if (
            thickness <= 18
            and height > 2200
            and section_width > 600
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DIVIDER_BUCKLING",
                message="Divider may require reinforcement",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Divider stability acceptable",
        )
