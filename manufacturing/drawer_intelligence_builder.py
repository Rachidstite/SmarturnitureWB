from manufacturing.drawer_decision_builder import DrawerDecisionBuilder
from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport


class DrawerIntelligenceBuilder:

    def build(self, validation_report):
        decision_report = DrawerDecisionBuilder().build(validation_report)

        return DrawerIntelligenceReport(
            validation=validation_report,
            decision=decision_report,
        )
