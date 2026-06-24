from manufacturing.factory_executive_intelligence_report import (
    FactoryExecutiveIntelligenceReport,
)


class FactoryExecutiveIntelligenceBuilder:

    def build(
        self,
        factory_capacity_report,
        factory_load_report,
        factory_bottleneck_report,
        delivery_intelligence_report,
        factory_capacity_simulation_report=None,
        production_forecast_report=None,
        factory_delivery_report=None,
    ):
        capacity_status = factory_capacity_report.status
        load_status = factory_load_report.status
        main_bottleneck = factory_bottleneck_report.bottleneck
        delivery_confidence = delivery_intelligence_report.confidence
        delivery_risk = delivery_intelligence_report.delivery_risk
        priority_action = factory_bottleneck_report.recommendation
        capacity_simulation_status = getattr(
            factory_capacity_simulation_report,
            "capacity_status",
            "AVAILABLE",
        )
        forecast_status = getattr(
            production_forecast_report,
            "forecast_status",
            "ON_SCHEDULE",
        )
        factory_delivery_status = getattr(
            factory_delivery_report,
            "delivery_status",
            "ON_TRACK",
        )

        if (
            capacity_status == "OVERLOADED"
            or delivery_risk == "HIGH"
            or capacity_simulation_status == "OVERLOADED"
            or forecast_status == "DELAY_RISK"
            or factory_delivery_status == "DELAYED"
        ):
            factory_status = "CRITICAL"
        elif (
            capacity_status == "LIMITED"
            or load_status == "HIGH"
            or delivery_confidence == "LOW"
            or capacity_simulation_status == "HIGH_LOAD"
            or forecast_status == "REVIEW"
            or factory_delivery_status == "AT_RISK"
        ):
            factory_status = "ATTENTION_REQUIRED"
        else:
            factory_status = "STABLE"

        if factory_status == "CRITICAL":
            summary = (
                f"Factory is critical due to {main_bottleneck or 'current load'} "
                f"and delivery risk."
            )
        elif factory_status == "ATTENTION_REQUIRED":
            summary = (
                f"Factory needs attention because capacity is {capacity_status.lower()} "
                f"and the main bottleneck is {main_bottleneck or 'not identified'}."
            )
        else:
            summary = (
                f"Factory is stable with {capacity_status.lower()} capacity and "
                f"{delivery_confidence.lower()} delivery confidence."
            )

        return FactoryExecutiveIntelligenceReport(
            factory_status=factory_status,
            capacity_status=capacity_status,
            load_status=load_status,
            main_bottleneck=main_bottleneck,
            delivery_confidence=delivery_confidence,
            delivery_risk=delivery_risk,
            priority_action=priority_action,
            summary=summary,
        )
