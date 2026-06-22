from manufacturing.back_panel_decision_builder import BackPanelDecisionBuilder
from manufacturing.back_panel_intelligence_report import BackPanelIntelligenceReport


class BackPanelIntelligenceBuilder:

    def build(
        self,
        hole_rules_report,
        manufacturing_intent_report,
        validation_report,
        commercial_risk_report,
    ):
        decision_report = BackPanelDecisionBuilder().build(validation_report)

        return BackPanelIntelligenceReport(
            hole_rules=hole_rules_report,
            manufacturing_intent=manufacturing_intent_report,
            validation=validation_report,
            decision=decision_report,
            commercial_risk=commercial_risk_report,
        )
