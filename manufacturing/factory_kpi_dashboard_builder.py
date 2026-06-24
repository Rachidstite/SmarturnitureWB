from manufacturing.factory_kpi_dashboard_report import FactoryKPIDashboardReport


class FactoryKPIDashboardBuilder:

    def build(
        self,
        factory_executive_intelligence_report=None,
        factory_capacity_simulation_report=None,
        production_forecast_report=None,
        factory_delivery_report=None,
        factory_decision_report=None,
    ):
        factory_status = getattr(
            factory_executive_intelligence_report,
            "factory_status",
            "UNKNOWN",
        )
        capacity_usage_percent = getattr(
            factory_capacity_simulation_report,
            "capacity_usage_percent",
            0.0,
        )
        forecast_days = getattr(
            production_forecast_report,
            "estimated_production_days",
            0.0,
        )
        delivery_status = getattr(
            factory_delivery_report,
            "delivery_status",
            "UNKNOWN",
        )
        main_bottleneck = getattr(
            factory_executive_intelligence_report,
            "main_bottleneck",
            "",
        )
        total_manufacturing_cost = getattr(
            factory_decision_report,
            "total_manufacturing_cost",
            0.0,
        )
        hardware_cost = getattr(factory_decision_report, "hardware_cost", 0.0)
        waste_cost = getattr(factory_decision_report, "waste_cost", 0.0)
        recovered_value = getattr(
            factory_decision_report,
            "recovered_value",
            0.0,
        )

        if factory_status == "CRITICAL":
            dashboard_recommendation = (
                "Factory requires immediate management attention"
            )
        elif delivery_status in ("DELAYED", "AT_RISK"):
            dashboard_recommendation = "Delivery should be reviewed"
        elif capacity_usage_percent >= 80:
            dashboard_recommendation = "Capacity should be monitored"
        else:
            dashboard_recommendation = ""

        return FactoryKPIDashboardReport(
            factory_status=factory_status,
            capacity_usage_percent=capacity_usage_percent,
            forecast_days=forecast_days,
            delivery_status=delivery_status,
            main_bottleneck=main_bottleneck,
            total_manufacturing_cost=total_manufacturing_cost,
            hardware_cost=hardware_cost,
            waste_cost=waste_cost,
            recovered_value=recovered_value,
            dashboard_recommendation=dashboard_recommendation,
        )
