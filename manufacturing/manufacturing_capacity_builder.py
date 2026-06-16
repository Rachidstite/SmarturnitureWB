from manufacturing.manufacturing_capacity_report import (
    ManufacturingCapacityReport,
)


class ManufacturingCapacityBuilder:

    def build(self, duration_report, daily_capacity_hours=8.0):
        total_production_hours = duration_report.total_production_minutes / 60
        warnings = list(duration_report.warnings)

        if daily_capacity_hours > 0:
            estimated_days_required = total_production_hours / daily_capacity_hours
            capacity_utilization_percent = min(
                100.0, (estimated_days_required / 5.0) * 100
            )
            if capacity_utilization_percent < 50:
                capacity_status = "AVAILABLE"
            elif capacity_utilization_percent < 85:
                capacity_status = "LIMITED"
            else:
                capacity_status = "OVERLOADED"
        else:
            estimated_days_required = 0.0
            capacity_utilization_percent = 0.0
            capacity_status = "UNKNOWN"
            warnings.append("Daily capacity hours must be greater than zero.")

        return ManufacturingCapacityReport(
            total_production_hours=total_production_hours,
            daily_capacity_hours=daily_capacity_hours,
            estimated_days_required=estimated_days_required,
            capacity_utilization_percent=capacity_utilization_percent,
            capacity_status=capacity_status,
            warnings=warnings,
        )
