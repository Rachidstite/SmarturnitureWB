from manufacturing.panel_spec import PanelSpec
from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_panel_thickness_readiness(
    panel: PanelSpec,
    rule_id: str = "MANUFACTURING_PANEL_THICKNESS_READINESS",
    source: str = "panel-thickness-readiness-rule",
) -> OperationalRuleResult:
    if panel.thickness > 0:
        return OperationalRuleResult(
            rule_id=rule_id,
            capability="manufacturing_panel_thickness_readiness",
            component_id=panel.identity,
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="manufacturing_panel_thickness_readiness",
        component_id=panel.identity,
        passed=False,
        severity="error",
        message=(
            f"Panel {panel.identity} has invalid thickness: {panel.thickness}"
        ),
        source=source,
    )
