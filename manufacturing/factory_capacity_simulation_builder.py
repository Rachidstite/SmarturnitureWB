from manufacturing.factory_capacity_simulation_report import (
    FactoryCapacitySimulationReport,
)


class FactoryCapacitySimulationBuilder:

    def build(self, manufacturing_simulation_report, available_factory_minutes):
        required_factory_minutes = getattr(
            manufacturing_simulation_report,
            "estimated_total_factory_minutes",
            0.0,
        )

        if available_factory_minutes > 0:
            capacity_usage_percent = (
                required_factory_minutes / available_factory_minutes * 100.0
            )
        else:
            capacity_usage_percent = 0.0

        if available_factory_minutes <= 0 and required_factory_minutes > 0:
            capacity_status = "OVERLOADED"
        elif capacity_usage_percent >= 100.0:
            capacity_status = "OVERLOADED"
        elif capacity_usage_percent >= 80.0:
            capacity_status = "HIGH_LOAD"
        else:
            capacity_status = "AVAILABLE"

        if capacity_status == "OVERLOADED":
            capacity_recommendation = "Factory capacity exceeded"
        elif capacity_status == "HIGH_LOAD":
            capacity_recommendation = "Factory approaching capacity limit"
        else:
            capacity_recommendation = ""

        return FactoryCapacitySimulationReport(
            required_factory_minutes=required_factory_minutes,
            available_factory_minutes=available_factory_minutes,
            capacity_usage_percent=capacity_usage_percent,
            capacity_status=capacity_status,
            capacity_recommendation=capacity_recommendation,
        )
