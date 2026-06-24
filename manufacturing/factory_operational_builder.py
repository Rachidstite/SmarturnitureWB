from manufacturing.factory_operational_report import FactoryOperationalReport


class FactoryOperationalBuilder:

    def build(self, readiness_report, schedule_report, bottleneck_report):
        if getattr(readiness_report, "readiness_status", "READY") == "BLOCKED":
            operational_status = "BLOCKED"
        else:
            operational_status = "READY"

        delivery_risk = (
            "HIGH"
            if getattr(schedule_report, "schedule_risk_level", "LOW") == "HIGH"
            else "LOW"
        )

        capacity_risk = (
            "HIGH"
            if getattr(bottleneck_report, "severity", "LOW") == "HIGH"
            else "LOW"
        )

        if operational_status == "BLOCKED":
            management_recommendation = "Project should not enter production"
        elif delivery_risk == "HIGH":
            management_recommendation = "Schedule review required"
        elif capacity_risk == "HIGH":
            management_recommendation = "Factory capacity review required"
        else:
            management_recommendation = ""

        return FactoryOperationalReport(
            operational_status=operational_status,
            delivery_risk=delivery_risk,
            capacity_risk=capacity_risk,
            management_recommendation=management_recommendation,
        )
