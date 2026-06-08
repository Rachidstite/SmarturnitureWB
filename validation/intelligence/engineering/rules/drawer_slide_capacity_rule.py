from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DrawerSlideCapacityRule:

    def validate(
        self,
        drawer,
    ):

        if getattr(
            drawer,
            "panel_category",
            "",
        ) != "drawer":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_APPLICABLE",
                message="Not a drawer",
            )

        width = getattr(
            drawer,
            "width",
            0,
        )

        slide_type = getattr(
            drawer,
            "slide_type",
            "standard",
        )

        if (
            width >= 1200
            and slide_type == "standard"
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DRAWER_SLIDE_CAPACITY",
                message="Drawer requires heavy duty slides",
            )

        if (
            width >= 900
            and slide_type == "standard"
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DRAWER_SLIDE_CAPACITY",
                message="Drawer may require stronger slides",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Drawer slide capacity acceptable",
        )
