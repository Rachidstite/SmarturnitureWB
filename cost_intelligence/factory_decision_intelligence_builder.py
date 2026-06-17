from cost_intelligence.factory_decision_report import FactoryDecisionReport


class FactoryDecisionIntelligenceBuilder:

    def build(self, base_decision_report, factory_intelligence_report):
        report = FactoryDecisionReport(
            **{
                key: self._clone_value(value)
                for key, value in base_decision_report.__dict__.items()
            }
        )

        report.factory_capacity_status = (
            factory_intelligence_report.factory_capacity_report.status
        )
        report.factory_load_status = (
            factory_intelligence_report.factory_load_report.status
        )
        report.factory_bottleneck = (
            factory_intelligence_report.factory_load_report.bottleneck
        )

        if base_decision_report.decision_status == "BLOCKED":
            report.decision_status = "BLOCKED"
        elif report.factory_capacity_status == "OVERLOADED":
            report.decision_status = "REVIEW_REQUIRED"
        elif report.factory_load_status == "HIGH":
            report.decision_status = "REVIEW_REQUIRED"
        else:
            report.decision_status = base_decision_report.decision_status

        return report

    @staticmethod
    def _clone_value(value):
        if isinstance(value, list):
            return list(value)
        if isinstance(value, dict):
            return dict(value)
        return value
