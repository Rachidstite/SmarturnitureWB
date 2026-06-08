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


class BackPanelRequiredRule(
    ManufacturingRule
):

    LARGE_CABINET_WIDTH = 1000

    def validate(
        self,
        panel_spec,
        operation
    ):

        if getattr(
            panel_spec,
            "role",
            None
        ) != NodeRole.BACK_PANEL:
            return RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="SKIP",
                message="Not back panel"
            )

        return RuleResult(
            passed=True,
            level=ResultLevel.INFO,
            code="OK",
            message="Back panel present"
        )
