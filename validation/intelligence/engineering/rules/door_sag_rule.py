from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DoorSagRule:

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
                message="Not a door panel",
            )

        height = getattr(
            panel_spec,
            "height",
            0,
        )

        width = getattr(
            panel_spec,
            "width",
            0,
        )

        if (
            height >= 2700
            or width >= 700
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DOOR_SAG",
                message="Door sag risk is excessive",
            )

        if (
            height >= 2400
            or width >= 600
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DOOR_SAG",
                message="Door may require extra hinges",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Door sag acceptable",
        )
