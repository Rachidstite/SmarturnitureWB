from validation.intelligence.engineering.engineering_rule_engine import (
    EngineeringRuleEngine,
)

from validation.intelligence.engineering.engineering_rules_registry import (
    EngineeringRulesRegistry,
)

from validation.intelligence.engineering.engineering_report_builder import (
    EngineeringReportBuilder,
)

from validation.intelligence.engineering.engineering_score_engine import (
    EngineeringScoreEngine,
)


class EngineeringIntelligenceReportBuilder:

    def build(
        self,
        panel_specs,
    ):

        rules = (
            EngineeringRulesRegistry
            .get_rules()
        )

        results = (
            EngineeringRuleEngine(
                rules=rules
            )
            .validate(panel_specs)
        )

        report = (
            EngineeringReportBuilder()
            .build(results)
        )

        report.score = (
            EngineeringScoreEngine()
            .calculate(report)
        )

        return report
