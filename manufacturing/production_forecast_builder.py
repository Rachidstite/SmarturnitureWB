from manufacturing.production_forecast_report import ProductionForecastReport


class ProductionForecastBuilder:

    def build(self, simulation_report, available_factory_minutes_per_day):
        required_factory_minutes = getattr(
            simulation_report,
            "estimated_total_factory_minutes",
            0.0,
        )

        if available_factory_minutes_per_day > 0:
            estimated_production_days = (
                required_factory_minutes / available_factory_minutes_per_day
            )
        else:
            estimated_production_days = 0.0

        if estimated_production_days > 10:
            forecast_status = "DELAY_RISK"
            forecast_recommendation = "Production completion risk detected"
        elif estimated_production_days > 5:
            forecast_status = "REVIEW"
            forecast_recommendation = "Review production planning"
        else:
            forecast_status = "ON_SCHEDULE"
            forecast_recommendation = ""

        return ProductionForecastReport(
            required_factory_minutes=required_factory_minutes,
            available_factory_minutes_per_day=available_factory_minutes_per_day,
            estimated_production_days=estimated_production_days,
            forecast_status=forecast_status,
            forecast_recommendation=forecast_recommendation,
        )
