from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
)

from shared.roles import NodeRole


class DoorHingeRecommendationRule(
    ManufacturingRule
):

    def validate(
        self,
        panel_spec,
        operation
    ):

        if panel_spec.role != NodeRole.DOOR_PANEL:

            return RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="SKIP",
                message="Not door"
            )

        height = panel_spec.height

        if height <= 900:
            hinges = 2

        elif height <= 1600:
            hinges = 3

        elif height <= 2200:
            hinges = 4

        else:
            hinges = 5

        return RuleResult(
            passed=False,
            level=ResultLevel.RECOMMENDATION,
            code="HINGE_RECOMMENDATION",
            message=(
                f"Door height {height:.0f} mm "
                f"recommended hinges: {hinges}"
            )
        )
