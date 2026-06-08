from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)

from validation.intelligence.recommendation_engine import (
    RecommendationEngine,
)

from validation.intelligence.cost_impact_engine import (
    CostImpactEngine,
)

from validation.intelligence.manufacturing_score_engine import (
    ManufacturingScoreEngine,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)

from validation.intelligence.structural_warning_classifier import (
    StructuralWarningClassifier,
)

from validation.intelligence.result_aggregator import (
    ResultAggregator,
)


class ManufacturingIntelligenceReportBuilder:

    def build(
        self,
        panel_specs
    ):

        rule_engine = (
            ManufacturingRuleEngine()
        )

        results = ResultAggregator.aggregate(
            rule_engine.validate(
                panel_specs
            )
        )

        print("\n================ RULE FAILURES ================")

        for r in results:
            if not r.passed:
                print(
                    r.code,
                    "|",
                    r.message
                )

        print("==============================================\n")

        recommendations = (
            rule_engine.recommendations(
                results
            )
            +
            RecommendationEngine()
            .recommend(panel_specs)
        )

        cost_impacts = (
            CostImpactEngine()
            .estimate(panel_specs)
        )

        score = (
            ManufacturingScoreEngine()
            .calculate(
                ManufacturingIntelligenceReport(
                    errors=rule_engine.errors(results),
                    warnings=rule_engine.warnings(results),

                    structural_warnings=
                    StructuralWarningClassifier.classify(
                        results
                    ),

                    recommendations=recommendations,
                    optimizations=rule_engine.optimizations(results),
                    cost_impacts=cost_impacts,
                    score=None,
                    can_export=rule_engine.can_export(
                        results
                    ),
                )
            )
        )

        return ManufacturingIntelligenceReport(
            errors=rule_engine.errors(results),
            warnings=rule_engine.warnings(results),

            structural_warnings=
            StructuralWarningClassifier.classify(
                results
            ),

            recommendations=recommendations,
            optimizations=rule_engine.optimizations(results),
            cost_impacts=cost_impacts,
            score=score,
            can_export=rule_engine.can_export(
                results
            ),
        )
