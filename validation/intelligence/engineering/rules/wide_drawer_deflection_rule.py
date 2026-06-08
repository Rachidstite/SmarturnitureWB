from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class WideDrawerDeflectionRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "drawer_bottom":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_DRAWER_BOTTOM",
                message="Not a drawer bottom",
            )

        width = getattr(
            panel_spec,
            "width",
            0,
        )

        thickness = getattr(
            panel_spec,
            "thickness",
            0,
        )

        if (
            width >= 1200
            and thickness <= 6
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DRAWER_BOTTOM_DEFLECTION",
                message="Drawer bottom requires reinforcement",
            )

        if (
            width >= 900
            and thickness <= 6
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DRAWER_BOTTOM_DEFLECTION",
                message="Wide drawer bottom may deflect",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Drawer bottom acceptable",
        )
