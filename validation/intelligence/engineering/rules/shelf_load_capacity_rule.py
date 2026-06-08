from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class ShelfLoadCapacityRule:

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
                code="NOT_APPLICABLE",
                message="Not a shelf",
            )

        span = getattr(
            panel_spec,
            "span",
            0,
        )

        if span >= 1500:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="SHELF_LOAD_CAPACITY",
                message="Shelf span exceeds safe load capacity",
            )

        if span >= 1100:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="SHELF_LOAD_CAPACITY",
                message="Shelf may require additional support",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Shelf load capacity acceptable",
        )
