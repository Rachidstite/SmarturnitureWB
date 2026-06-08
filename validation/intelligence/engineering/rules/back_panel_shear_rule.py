from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class BackPanelShearRule:

    def validate(
        self,
        cabinet,
    ):

        if getattr(
            cabinet,
            "has_back_panel",
            False,
        ):
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="OK",
                message="Back panel present",
            )

        height = getattr(
            cabinet,
            "cabinet_height",
            0,
        )

        width = getattr(
            cabinet,
            "cabinet_width",
            0,
        )

        if (
            height >= 2800
            or width >= 1600
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="BACK_PANEL_SHEAR",
                message="Large cabinet requires back panel",
            )

        if (
            height >= 2400
            or width >= 1200
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="BACK_PANEL_SHEAR",
                message="Cabinet may require back panel",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Cabinet rigidity acceptable",
        )
