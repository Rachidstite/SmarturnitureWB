from manufacturing.manufacturing_executive_report import (
    ManufacturingExecutiveReport,
)


class ManufacturingExecutiveBuilder:

    def build(
        self,
        manufacturing_model_report,
        factory_decision_report,
        factory_executive_intelligence_report,
        factory_delivery_report,
        production_forecast_report,
    ):
        decision_status = getattr(factory_decision_report, "decision_status", "UNKNOWN")
        manufacturing_status = getattr(
            manufacturing_model_report,
            "manufacturing_status",
            "UNKNOWN",
        )
        delivery_status = getattr(factory_delivery_report, "delivery_status", "UNKNOWN")
        production_forecast_status = getattr(
            production_forecast_report,
            "forecast_status",
            "UNKNOWN",
        )

        if decision_status == "BLOCKED":
            overall_status = "BLOCKED"
        elif delivery_status == "DELAYED":
            overall_status = "AT_RISK"
        elif production_forecast_status == "DELAY_RISK":
            overall_status = "AT_RISK"
        elif decision_status == "REVIEW_REQUIRED":
            overall_status = "REVIEW"
        else:
            overall_status = "READY"

        primary_factory_risk = self._primary_factory_risk(
            decision_status=decision_status,
            delivery_status=delivery_status,
            production_forecast_status=production_forecast_status,
            factory_executive_intelligence_report=factory_executive_intelligence_report,
        )
        recommended_action = self._recommended_action(
            factory_decision_report=factory_decision_report,
            factory_executive_intelligence_report=factory_executive_intelligence_report,
            factory_delivery_report=factory_delivery_report,
            production_forecast_report=production_forecast_report,
        )
        executive_summary = self._executive_summary(overall_status)

        return ManufacturingExecutiveReport(
            overall_status=overall_status,
            decision_status=decision_status,
            manufacturing_status=manufacturing_status,
            delivery_status=delivery_status,
            production_forecast_status=production_forecast_status,
            primary_factory_risk=primary_factory_risk,
            recommended_action=recommended_action,
            executive_summary=executive_summary,
        )

    @staticmethod
    def _primary_factory_risk(
        decision_status,
        delivery_status,
        production_forecast_status,
        factory_executive_intelligence_report,
    ):
        if decision_status == "BLOCKED":
            return "BLOCKED"
        if delivery_status == "DELAYED":
            return "DELAYED"
        if production_forecast_status == "DELAY_RISK":
            return "DELAY_RISK"
        if getattr(factory_executive_intelligence_report, "delivery_risk", "LOW") == "HIGH":
            return "HIGH_DELIVERY_RISK"
        if getattr(factory_executive_intelligence_report, "main_bottleneck", ""):
            return "BOTTLENECK"
        return "NONE"

    @staticmethod
    def _recommended_action(
        factory_decision_report,
        factory_executive_intelligence_report,
        factory_delivery_report,
        production_forecast_report,
    ):
        decision_recommendations = getattr(factory_decision_report, "recommendations", None)
        if decision_recommendations:
            if isinstance(decision_recommendations, list):
                return "; ".join(str(item) for item in decision_recommendations if item)
            return str(decision_recommendations)

        priority_action = getattr(factory_executive_intelligence_report, "priority_action", "")
        if priority_action:
            return priority_action

        delivery_recommendation = getattr(
            factory_delivery_report,
            "delivery_recommendation",
            "",
        )
        if delivery_recommendation:
            return delivery_recommendation

        forecast_recommendation = getattr(
            production_forecast_report,
            "forecast_recommendation",
            "",
        )
        if forecast_recommendation:
            return forecast_recommendation

        return ""

    @staticmethod
    def _executive_summary(overall_status):
        if overall_status == "READY":
            return "Factory ready for production."
        if overall_status == "REVIEW":
            return "Factory review required before production."
        if overall_status == "AT_RISK":
            return "Production or delivery risk detected."
        if overall_status == "BLOCKED":
            return "Manufacturing is blocked."
        return "Factory executive summary available."
