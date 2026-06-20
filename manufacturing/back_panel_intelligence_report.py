from dataclasses import dataclass, field

from manufacturing.back_panel_commercial_risk_report import (
    BackPanelCommercialRiskReport,
)
from manufacturing.back_panel_decision_report import BackPanelDecisionReport
from manufacturing.back_panel_hole_rule_report import BackPanelHoleRuleReport
from manufacturing.back_panel_manufacturing_intent_report import (
    BackPanelManufacturingIntentReport,
)
from manufacturing.back_panel_validation_report import BackPanelValidationReport


@dataclass
class BackPanelIntelligenceReport:
    hole_rules: BackPanelHoleRuleReport = field(default_factory=BackPanelHoleRuleReport)
    manufacturing_intent: BackPanelManufacturingIntentReport = field(
        default_factory=BackPanelManufacturingIntentReport
    )
    validation: BackPanelValidationReport = field(default_factory=BackPanelValidationReport)
    decision: BackPanelDecisionReport = field(default_factory=BackPanelDecisionReport)
    commercial_risk: BackPanelCommercialRiskReport = field(
        default_factory=BackPanelCommercialRiskReport
    )
