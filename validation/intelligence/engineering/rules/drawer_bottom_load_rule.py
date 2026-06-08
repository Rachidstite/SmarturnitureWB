from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DrawerBottomLoadRule:

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
                code="NOT_APPLICABLE",
                message="Not a drawer bottom",
            )

        width = getattr(
            panel_spec,
            "width",
            0,
        )

        if width >= 1300:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DRAWER_BOTTOM_FAILURE",
                message=(
                    "Drawer bottom span too large. "
                    "Use thicker material or center support."
                ),
            )

        if width >= 1000:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DRAWER_BOTTOM_WARNING",
                message=(
                    "Drawer bottom may sag under load."
                ),
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="DRAWER_BOTTOM_OK",
            message="Drawer bottom load acceptable",
        )
