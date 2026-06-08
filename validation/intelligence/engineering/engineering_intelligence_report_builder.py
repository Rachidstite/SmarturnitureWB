from validation.intelligence.engineering.engineering_rule_engine import (
    EngineeringRuleEngine,
)

from validation.intelligence.engineering.engineering_rules_registry import (
    EngineeringRulesRegistry,
)

from validation.intelligence.engineering.engineering_assembly_rule_engine import (
    EngineeringAssemblyRuleEngine,
)

from validation.intelligence.engineering.engineering_assembly_rules_registry import (
    EngineeringAssemblyRulesRegistry,
)

from validation.intelligence.engineering.engineering_report_builder import (
    EngineeringReportBuilder,
)

from validation.intelligence.engineering.engineering_score_engine import (
    EngineeringScoreEngine,
)

from validation.intelligence.engineering.recommendations.engineering_recommendation_engine import (
    EngineeringRecommendationEngine,
)

from validation.intelligence.engineering.recommendations.recommendation_sorter import (
    RecommendationSorter,
)

from validation.intelligence.engineering.cost.engineering_cost_engine import (
    EngineeringCostEngine,
)

from validation.intelligence.engineering.cost.engineering_cost_summary_engine import (
    EngineeringCostSummaryEngine,
)

from validation.intelligence.engineering.cost.engineering_cost_estimator import (
    EngineeringCostEstimator,
)


class EngineeringIntelligenceReportBuilder:

    def build(
        self,
        panel_specs,
        scene_graph=None,
    ):

        panel_results = (
            EngineeringRuleEngine(
                rules=
                EngineeringRulesRegistry.get_rules()
            )
            .validate(panel_specs)
        )

        assembly_results = []

        if scene_graph is not None:

            assembly_results = (
                EngineeringAssemblyRuleEngine(
                    rules=
                    EngineeringAssemblyRulesRegistry.get_rules()
                )
                .validate(scene_graph)
            )

        results = (
            panel_results
            +
            assembly_results
        )

        report = (
            EngineeringReportBuilder()
            .build(results)
        )

        warning_codes = [
            getattr(r, "code", None)
            for r in report.warnings
        ]

        error_codes = [
            getattr(r, "code", None)
            for r in report.errors
        ]

        report.recommendations = (
            RecommendationSorter()
            .sort(
                EngineeringRecommendationEngine()
                .generate(
                    warning_codes=
                    warning_codes + error_codes
                )
            )
        )

        cost_impacts = (
            EngineeringCostEngine()
            .calculate(
                warning_codes + error_codes
            )
        )

        report.cost_summary = (
            EngineeringCostSummaryEngine()
            .summarize(
                cost_impacts
            )
        )

        report.estimated_cost = (
            EngineeringCostEstimator()
            .estimate(
                report.cost_summary
            )
        )

        report.score = (
            EngineeringScoreEngine()
            .calculate(report)
        )

        return report
