from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DoubleDoorAlignmentRule:

    def validate(
        self,
        panel_spec,
    ):

        if (
            getattr(
                panel_spec,
                "panel_category",
                "",
            ) != "door"
            or getattr(
                panel_spec,
                "door_count",
                1,
            ) < 2
        ):
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_DOUBLE_DOOR",
                message="Not a double door",
            )

        height = getattr(
            panel_spec,
            "height",
            0,
        )

        if height >= 2800:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="DOUBLE_DOOR_ALIGNMENT",
                message="Double door alignment risk",
            )

        if height >= 2400:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="DOUBLE_DOOR_ALIGNMENT",
                message="Double door may require alignment control",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Double door alignment acceptable",
        )
