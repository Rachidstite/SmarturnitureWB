from manufacturing.panel_spec import PanelSpec
from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_panel_material_readiness(
    panel: PanelSpec,
    rule_id: str = "MANUFACTURING_PANEL_MATERIAL_READINESS",
    source: str = "panel-material-readiness-rule",
) -> OperationalRuleResult:
    if panel.material:
        return OperationalRuleResult(
            rule_id=rule_id,
            capability="manufacturing_material_readiness",
            component_id=panel.identity,
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="manufacturing_material_readiness",
        component_id=panel.identity,
        passed=False,
        severity="error",
        message=f"Panel {panel.identity} is missing material assignment",
        source=source,
    )
