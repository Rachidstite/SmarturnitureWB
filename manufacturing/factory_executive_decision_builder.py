from manufacturing.factory_executive_decision_report import (
    FactoryExecutiveDecisionReport,
)


class FactoryExecutiveDecisionBuilder:

    def build(
        self,
        profitability_report,
        factory_delivery_report,
        project_readiness_report,
    ):
        profitability_status = getattr(
            profitability_report,
            "profitability_status",
            "UNKNOWN",
        )
        delivery_status = getattr(
            factory_delivery_report,
            "delivery_status",
            "ON_TRACK",
        )
        readiness_status = getattr(
            project_readiness_report,
            "readiness_status",
            "READY",
        )

        if readiness_status == "BLOCKED":
            business_status = "REJECT"
            executive_recommendation = "Project should not enter production"
        elif profitability_status == "LOW":
            business_status = "REVIEW"
            executive_recommendation = (
                "Review profitability before production"
            )
        elif delivery_status == "DELAYED":
            business_status = "REVIEW"
            executive_recommendation = "Review delivery schedule before production"
        else:
            business_status = "APPROVED"
            executive_recommendation = ""

        return FactoryExecutiveDecisionReport(
            business_status=business_status,
            profitability_status=profitability_status,
            delivery_status=delivery_status,
            executive_recommendation=executive_recommendation,
        )
