from manufacturing.factory_bottleneck_intelligence_report import (
    FactoryBottleneckIntelligenceReport,
)


class FactoryBottleneckIntelligenceBuilder:

    def build(self, factory_load_report, production_schedule_report=None):
        bottleneck = factory_load_report.bottleneck

        load_percent_map = {
            "CNC": factory_load_report.cnc_load_percent,
            "ASSEMBLY": factory_load_report.assembly_load_percent,
            "EDGE_BANDING": factory_load_report.edge_banding_load_percent,
        }
        load_percent = load_percent_map.get(bottleneck, 0.0)

        if factory_load_report.status == "HIGH":
            severity = "HIGH"
        elif factory_load_report.status == "MEDIUM":
            severity = "MEDIUM"
        else:
            severity = "LOW"

        schedule_risk_level = getattr(
            production_schedule_report,
            "schedule_risk_level",
            "LOW",
        )
        if schedule_risk_level == "HIGH":
            if severity == "LOW":
                severity = "MEDIUM"
            elif severity == "MEDIUM":
                severity = "HIGH"

        if severity == "HIGH":
            impact = "DELIVERY_RISK"
        elif severity == "MEDIUM":
            impact = "CAPACITY_PRESSURE"
        else:
            impact = "NO_MAJOR_BOTTLENECK"

        recommendation_map = {
            "CNC": "Increase CNC availability",
            "ASSEMBLY": "Increase assembly capacity",
            "EDGE_BANDING": "Increase edge banding capacity",
        }
        recommendation = recommendation_map.get(
            bottleneck, "No bottleneck detected"
        )
        if (
            schedule_risk_level == "HIGH"
            and bottleneck
            and recommendation != "No bottleneck detected"
        ):
            recommendation = (
                f"{recommendation}; review production schedule for {bottleneck}"
            )

        return FactoryBottleneckIntelligenceReport(
            bottleneck=bottleneck,
            load_percent=load_percent,
            severity=severity,
            impact=impact,
            recommendation=recommendation,
        )
