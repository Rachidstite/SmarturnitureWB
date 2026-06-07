from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)

from validation.intelligence.recommendation_engine import (
    RecommendationEngine,
)

from validation.intelligence.cost_impact_engine import (
    CostImpactEngine,
)


from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class ManufacturingIntelligenceReportBuilder:

    def build(
        self,
        panel_specs
    ):

        rule_engine = (
            ManufacturingRuleEngine()
        )

        results = (
            rule_engine.validate(
                panel_specs
            )
        )

        recommendations = (
            RecommendationEngine()
            .recommend(panel_specs)
        )

        cost_impacts = (
            CostImpactEngine()
            .estimate(panel_specs)
        )

        return ManufacturingIntelligenceReport(
            errors=rule_engine.errors(results),
            warnings=rule_engine.warnings(results),
            recommendations=recommendations,
            optimizations=rule_engine.optimizations(results),
            cost_impacts=cost_impacts,
            can_export=rule_engine.can_export(
                results
            ),
        )
