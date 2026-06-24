from manufacturing.drawer_decision_builder import DrawerDecisionBuilder
from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport
from manufacturing.drawer_structural_builder import DrawerStructuralBuilder


class DrawerIntelligenceBuilder:

    def build(self, validation_report):
        structural_report = DrawerStructuralBuilder().build(validation_report)
        decision_report = DrawerDecisionBuilder().build(validation_report)

        return DrawerIntelligenceReport(
            validation=validation_report,
            structural=structural_report,
            decision=decision_report,
        )
