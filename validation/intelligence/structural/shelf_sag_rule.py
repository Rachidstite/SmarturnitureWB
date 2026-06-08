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


class ShelfSagRule(
    ManufacturingRule
):

    def validate(
        self,
        panel_spec,
        operation
    ):

        if getattr(
            panel_spec,
            "role",
            None
        ) != NodeRole.SHELF:
            return RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="SKIP",
                message="Not shelf"
            )

        span = getattr(
            panel_spec,
            "span",
            panel_spec.width
        )

        thickness = panel_spec.thickness

        if thickness <= 18 and span > 900:

            return RuleResult(
                passed=False,
                level=ResultLevel.WARNING,
                code="SHELF_SAG",
                message=(
                    f"Shelf span {span:.0f} mm "
                    f"may sag with {thickness:.0f} mm MDF"
                )
            )

        if thickness <= 25 and span > 1200:

            return RuleResult(
                passed=False,
                level=ResultLevel.WARNING,
                code="SHELF_SAG",
                message=(
                    f"Shelf span {span:.0f} mm "
                    f"requires reinforcement"
                )
            )

        return RuleResult(
            passed=True,
            level=ResultLevel.INFO,
            code="OK",
            message="Shelf span valid"
        )
