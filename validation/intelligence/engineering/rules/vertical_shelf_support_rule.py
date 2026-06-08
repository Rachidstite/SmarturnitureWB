from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class VerticalShelfSupportRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "shelf":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_SHELF",
                message="Not a shelf",
            )

        span = getattr(
            panel_spec,
            "span",
            0,
        )

        if span >= 1600:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="VERTICAL_SHELF_SUPPORT",
                message="Shelf requires vertical support",
            )

        if span >= 1200:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="VERTICAL_SHELF_SUPPORT",
                message="Shelf may require vertical support",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Shelf support acceptable",
        )
