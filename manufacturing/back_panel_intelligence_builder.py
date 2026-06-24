from manufacturing.back_panel_decision_builder import BackPanelDecisionBuilder
from manufacturing.back_panel_intelligence_report import BackPanelIntelligenceReport
from manufacturing.back_panel_structural_builder import BackPanelStructuralBuilder
from manufacturing.back_panel_fixing_report import BackPanelFixingReport


class BackPanelIntelligenceBuilder:

    def build(
        self,
        hole_rules_report,
        manufacturing_intent_report,
        validation_report,
        commercial_risk_report,
        fixing_report=None,
    ):
        structural_report = BackPanelStructuralBuilder().build(
            validation_report,
            fixing_report or BackPanelFixingReport(),
        )
        decision_report = BackPanelDecisionBuilder().build(
            validation_report,
            structural_report,
        )

        return BackPanelIntelligenceReport(
            hole_rules=hole_rules_report,
            manufacturing_intent=manufacturing_intent_report,
            validation=validation_report,
            structural=structural_report,
            decision=decision_report,
            commercial_risk=commercial_risk_report,
        )
