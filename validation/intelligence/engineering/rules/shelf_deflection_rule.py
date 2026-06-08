from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)

from validation.intelligence.engineering.engineering_rule import (
    EngineeringRule,
)


class ShelfDeflectionRule(
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
        ) != "shelf":
            return None

        span = getattr(
            panel_spec,
            "span",
            0
        )

        thickness = getattr(
            panel_spec,
            "thickness",
            18
        )

        if thickness <= 18:

            if span > 1200:
                return EngineeringResult(
                    passed=False,
                    level=EngineeringLevel.ERROR,
                    code="SHELF_DEFLECTION",
                    message="Shelf span exceeds safe limit",
                )

            if span > 900:
                return EngineeringResult(
                    passed=False,
                    level=EngineeringLevel.WARNING,
                    code="SHELF_DEFLECTION",
                    message="Shelf may deflect under load",
                )

        if thickness >= 25:

            if span > 1500:
                return EngineeringResult(
                    passed=False,
                    level=EngineeringLevel.ERROR,
                    code="SHELF_DEFLECTION",
                    message="Shelf span exceeds safe limit",
                )

            if span > 1200:
                return EngineeringResult(
                    passed=False,
                    level=EngineeringLevel.WARNING,
                    code="SHELF_DEFLECTION",
                    message="Shelf may deflect under load",
                )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Shelf deflection acceptable",
        )
