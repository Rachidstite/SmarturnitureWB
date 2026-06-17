from manufacturing.factory_bottleneck_recommendation_report import (
    FactoryBottleneckRecommendationReport,
)


class FactoryBottleneckRecommendationBuilder:

    def build(self, factory_bottleneck_report):
        bottleneck = factory_bottleneck_report.bottleneck
        severity = factory_bottleneck_report.severity

        if bottleneck == "ASSEMBLY":
            primary = "Increase assembly capacity"
            secondary = [
                "Add assembly station",
                "Split project into smaller batches",
                "Reduce assembly minutes per panel",
            ]
            expected_impact = "Improves delivery reliability"
        elif bottleneck == "CNC":
            primary = "Increase CNC availability"
            secondary = [
                "Schedule CNC work earlier",
                "Reduce unnecessary drilling operations",
                "Batch similar CNC operations",
            ]
            expected_impact = "Reduces machining queue pressure"
        elif bottleneck == "EDGE_BANDING":
            primary = "Increase edge banding capacity"
            secondary = [
                "Batch panels by edge material",
                "Prepare edge rolls before production",
                "Reduce unnecessary edge banding",
            ]
            expected_impact = "Reduces finishing delays"
        else:
            primary = "No bottleneck detected"
            secondary = []
            expected_impact = "No immediate action required"

        return FactoryBottleneckRecommendationReport(
            bottleneck=bottleneck,
            severity=severity,
            primary_recommendation=primary,
            secondary_recommendations=list(secondary),
            expected_impact=expected_impact,
        )
