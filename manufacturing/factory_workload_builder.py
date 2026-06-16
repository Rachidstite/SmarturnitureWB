from manufacturing.factory_workload_report import FactoryWorkloadReport


class FactoryWorkloadBuilder:

    def build(self, production_schedule_reports):
        active_project_count = len(production_schedule_reports)
        total_required_work_days = sum(
            report.required_work_days
            for report in production_schedule_reports
        )

        if active_project_count:
            average_required_work_days = (
                total_required_work_days / active_project_count
            )
        else:
            average_required_work_days = 0.0

        risk_order = {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2,
        }

        highest_schedule_risk_level = "LOW"
        for report in production_schedule_reports:
            if (
                risk_order.get(report.schedule_risk_level, 0)
                > risk_order.get(highest_schedule_risk_level, 0)
            ):
                highest_schedule_risk_level = report.schedule_risk_level

        if total_required_work_days >= 10:
            factory_workload_status = "OVERLOADED"
        elif total_required_work_days >= 5:
            factory_workload_status = "BUSY"
        else:
            factory_workload_status = "AVAILABLE"

        warnings = []
        for report in production_schedule_reports:
            warnings.extend(report.warnings)

        return FactoryWorkloadReport(
            active_project_count=active_project_count,
            total_required_work_days=total_required_work_days,
            average_required_work_days=average_required_work_days,
            highest_schedule_risk_level=highest_schedule_risk_level,
            factory_workload_status=factory_workload_status,
            warnings=warnings,
        )
