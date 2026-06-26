from manufacturing.panel_spec import PanelSpec
from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_panel_edge_readiness(
    panel: PanelSpec,
    rule_id: str = "MANUFACTURING_PANEL_EDGE_READINESS",
    source: str = "panel-edge-readiness-rule",
) -> OperationalRuleResult:
    if panel.edge_spec.all_banded():
        return OperationalRuleResult(
            rule_id=rule_id,
            capability="manufacturing_panel_edge_readiness",
            component_id=panel.identity,
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="manufacturing_panel_edge_readiness",
        component_id=panel.identity,
        passed=False,
        severity="error",
        message=f"Panel {panel.identity} is missing edge-banding data",
        source=source,
    )
