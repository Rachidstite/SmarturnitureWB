from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class SidePanelSlendernessRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "side_panel":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_APPLICABLE",
                message="Not a side panel",
            )

        height = getattr(
            panel_spec,
            "height",
            0,
        )

        if height >= 3000:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="SIDE_PANEL_SLENDERNESS",
                message="Side panel excessively tall for MDF thickness",
            )

        if height >= 2600:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="SIDE_PANEL_SLENDERNESS",
                message="Side panel may require additional reinforcement",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Side panel stability acceptable",
        )
