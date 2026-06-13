from cost_intelligence.manufacturing_cost_insights import ManufacturingCostInsights


class ManufacturingCostInsightsBuilder:

    def build(self, context):
        insights = []

        if context.total_panels > 50:
            insights.append("High panel count")
        if context.total_edge_meters > 100:
            insights.append("High edge banding usage")
        if context.total_drilling_operations > 200:
            insights.append("High drilling complexity")
        if context.total_material_types > 3:
            insights.append("Multiple material types")
        if context.warnings_count > 0:
            insights.append("Manufacturing warnings detected")

        if len(insights) >= 3:
            risk_level = "HIGH"
        elif insights:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return ManufacturingCostInsights(
            insights=insights,
            risk_level=risk_level,
            warnings=context.warnings,
        )
