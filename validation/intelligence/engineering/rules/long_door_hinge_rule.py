from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class LongDoorHingeRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "door":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_DOOR",
                message="Not a door",
            )

        height = getattr(
            panel_spec,
            "height",
            0,
        )

        hinge_count = getattr(
            panel_spec,
            "hinge_count",
            0,
        )

        if (
            height >= 2800
            and hinge_count < 5
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="LONG_DOOR_HINGES",
                message="Very tall door requires additional hinges",
            )

        if (
            height >= 2400
            and hinge_count < 4
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="LONG_DOOR_HINGES",
                message="Tall door may require additional hinges",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Door hinge count acceptable",
        )
