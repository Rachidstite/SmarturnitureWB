from manufacturing.factory_capacity_intelligence_report import (
    FactoryCapacityIntelligenceReport,
)


class FactoryCapacityIntelligenceBuilder:

    def build(self, factory_resource_report, manufacturing_duration_report):
        required_hours = (
            manufacturing_duration_report.total_production_minutes / 60.0
        )
        weekly_capacity_hours = factory_resource_report.weekly_capacity_hours

        if weekly_capacity_hours > 0:
            utilization_percent = (
                required_hours / weekly_capacity_hours * 100.0
            )
            remaining_capacity_hours = weekly_capacity_hours - required_hours
            if utilization_percent < 50:
                status = "AVAILABLE"
            elif utilization_percent <= 85:
                status = "LIMITED"
            else:
                status = "OVERLOADED"
        else:
            utilization_percent = 0.0
            remaining_capacity_hours = 0.0
            status = "UNKNOWN"

        return FactoryCapacityIntelligenceReport(
            required_hours=required_hours,
            weekly_capacity_hours=weekly_capacity_hours,
            utilization_percent=utilization_percent,
            remaining_capacity_hours=remaining_capacity_hours,
            status=status,
        )
