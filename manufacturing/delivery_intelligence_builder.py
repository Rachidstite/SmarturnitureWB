from manufacturing.delivery_intelligence_report import (
    DeliveryIntelligenceReport,
)


class DeliveryIntelligenceBuilder:

    def build(
        self,
        manufacturing_duration_report,
        factory_capacity_report,
        factory_bottleneck_intelligence_report,
    ):
        estimated_hours = (
            manufacturing_duration_report.total_production_minutes / 60.0
        )
        estimated_days = estimated_hours / 8.0

        capacity_status = factory_capacity_report.status
        bottleneck_severity = factory_bottleneck_intelligence_report.severity

        if capacity_status == "OVERLOADED" or bottleneck_severity == "HIGH":
            confidence = "LOW"
        elif capacity_status == "LIMITED":
            confidence = "MEDIUM"
        elif capacity_status == "AVAILABLE" and bottleneck_severity == "LOW":
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"

        delivery_risk = {
            "HIGH": "LOW",
            "MEDIUM": "MEDIUM",
            "LOW": "HIGH",
        }.get(confidence, "HIGH")

        if confidence == "HIGH":
            recommendation = "Delivery plan is stable"
        elif confidence == "MEDIUM":
            recommendation = "Monitor delivery plan closely"
        else:
            recommendation = "Review delivery risk immediately"

        return DeliveryIntelligenceReport(
            estimated_hours=estimated_hours,
            estimated_days=estimated_days,
            confidence=confidence,
            delivery_risk=delivery_risk,
            recommendation=recommendation,
        )
