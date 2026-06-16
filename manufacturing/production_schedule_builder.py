from manufacturing.production_schedule_report import ProductionScheduleReport


class ProductionScheduleBuilder:

    def build(self, duration_report, capacity_report):
        daily_capacity_minutes = capacity_report.daily_capacity_hours * 60.0

        if daily_capacity_minutes > 0:
            required_work_days = (
                duration_report.total_production_minutes
                / daily_capacity_minutes
            )
        else:
            required_work_days = 0.0

        required_machine_days = required_work_days
        required_operator_days = required_work_days

        capacity_utilization_percent = (
            capacity_report.capacity_utilization_percent
        )

        if capacity_utilization_percent >= 85:
            schedule_risk_level = "HIGH"
        elif capacity_utilization_percent >= 50:
            schedule_risk_level = "MEDIUM"
        else:
            schedule_risk_level = "LOW"

        warnings = list(duration_report.warnings)
        warnings.extend(capacity_report.warnings)

        return ProductionScheduleReport(
            required_work_days=required_work_days,
            required_machine_days=required_machine_days,
            required_operator_days=required_operator_days,
            capacity_utilization_percent=capacity_utilization_percent,
            schedule_risk_level=schedule_risk_level,
            warnings=warnings,
        )
